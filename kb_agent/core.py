"""Core logic for the knowledge base agent."""

import os
import re
import shutil
from pathlib import Path
from urllib.request import urlopen

from . import llm

# Directories (relative to CWD)
DATA_DIR = Path(os.environ.get("KB_DATA_DIR", "data"))
RAW_DIR = DATA_DIR / "raw"
WIKI_DIR = DATA_DIR / "wiki"
OUTPUT_DIR = DATA_DIR / "output"
INDEX_FILE = WIKI_DIR / "INDEX.md"

MAX_RAW_CHARS = 100_000  # truncate oversized raw docs


def ensure_dirs():
    for d in (RAW_DIR, WIKI_DIR, OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)


def slugify(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")[:80]


def load_raw_docs() -> dict[str, str]:
    docs = {}
    for f in sorted(RAW_DIR.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            try:
                docs[f.name] = f.read_text(errors="replace")
            except Exception:
                pass
    return docs


def load_wiki_articles() -> dict[str, str]:
    articles = {}
    for f in sorted(WIKI_DIR.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        try:
            articles[f.stem] = f.read_text(errors="replace")
        except Exception:
            pass
    return articles


# ── PDF extraction ─────────────────────────────────────────────────────

def extract_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file. Returns markdown-formatted text."""
    try:
        import pymupdf
    except ImportError:
        raise RuntimeError(
            "pymupdf package required for PDF support. "
            "Install it with: pip install 'kb-agent[pdf]'"
        )

    doc = pymupdf.open(pdf_path)
    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text)
    doc.close()
    return "\n\n---\n\n".join(pages)


def _save_as_md(dest: Path, content: str) -> Path:
    """Save content as .md file, converting the extension if needed."""
    md_dest = dest.with_suffix(".md")
    md_dest.write_text(content)
    return md_dest


# ── Ingest ──────────────────────────────────────────────────────────────

def ingest(path: str):
    """Copy a local file or fetch a URL into raw/. PDFs are auto-converted to markdown."""
    ensure_dirs()
    if path.startswith("http://") or path.startswith("https://"):
        # simple URL fetch
        slug = slugify(path.split("/")[-1] or "page") + ".md"
        dest = RAW_DIR / slug
        with urlopen(path) as resp:
            data = resp.read()
        # Check if downloaded content is PDF
        if data[:5] == b"%PDF-":
            dest.write_bytes(data)
            text = extract_pdf(dest)
            dest.unlink()
            return _save_as_md(dest, text)
        else:
            dest.write_bytes(data)
            return dest
    else:
        src = Path(path).expanduser().resolve()
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src}")
        if src.suffix.lower() == ".pdf":
            text = extract_pdf(src)
            return _save_as_md(RAW_DIR / src.name, text)
        else:
            dest = RAW_DIR / src.name
            shutil.copy2(src, dest)
            return dest


def ingest_pdf_bytes(filename: str, data: bytes) -> Path:
    """Ingest PDF from raw bytes (used by web upload). Returns dest path."""
    ensure_dirs()
    tmp = RAW_DIR / filename
    tmp.write_bytes(data)
    text = extract_pdf(tmp)
    tmp.unlink()
    return _save_as_md(tmp, text)


# ── Compile ─────────────────────────────────────────────────────────────

COMPILE_SYSTEM = """\
You are a knowledge-base compiler. Convert the raw document into a well-structured \
wiki article in Markdown.

Rules:
- Use a clear H1 title.
- Write a concise summary paragraph at the top.
- Organize content with H2/H3 sections.
- At the bottom add a "## Categories" section with relevant tags as a comma list.
- At the bottom add a "## See Also" section with [[wikilinks]] to any related \
existing articles from the list provided. Only link articles that genuinely relate.
- Keep the article faithful to the source data; do not invent facts.
- Write in the same language as the source document.
- Output ONLY the raw markdown content. No code fences, no explanations, no preamble.
"""


def compile_article(raw_name: str, raw_content: str, existing_slugs: list[str]) -> str:
    content = raw_content[:MAX_RAW_CHARS]
    existing = ", ".join(existing_slugs) if existing_slugs else "(none yet)"
    prompt = (
        f"## Raw document: {raw_name}\n\n{content}\n\n"
        f"## Existing wiki articles (for backlinks): {existing}"
    )
    return llm.call_llm(COMPILE_SYSTEM, prompt)


def compile_all(force: bool = False):
    """Compile all raw docs into wiki articles. Returns list of created filenames."""
    ensure_dirs()
    raw_docs = load_raw_docs()
    existing = load_wiki_articles()
    created = []

    for raw_name, raw_content in raw_docs.items():
        slug = slugify(Path(raw_name).stem)
        if not force and slug in existing:
            continue
        article_md = compile_article(raw_name, raw_content, list(existing.keys()))
        dest = WIKI_DIR / f"{slug}.md"
        dest.write_text(article_md)
        existing[slug] = article_md  # available for backlinks in subsequent articles
        created.append(slug)

    if created:
        rebuild_index()
    return created


# ── Index ───────────────────────────────────────────────────────────────

INDEX_SYSTEM = """\
You are a wiki index generator. Given a list of article titles and their opening \
lines, produce a well-organized INDEX.md file.

Rules:
- Group articles by category/theme.
- Each entry: `- [Title](filename.md) — one-line summary`
- Add a H1 "Knowledge Base Index" header.
- Keep it concise. Write in the same language as the articles.
- Output ONLY the raw markdown content. No code fences, no explanations, no preamble.
"""


def rebuild_index() -> str:
    articles = load_wiki_articles()
    if not articles:
        INDEX_FILE.write_text("# Knowledge Base Index\n\n_No articles yet._\n")
        return "empty"

    snippets = []
    for slug, content in articles.items():
        first_lines = "\n".join(content.split("\n")[:5])
        snippets.append(f"### {slug}.md\n{first_lines}")

    prompt = "\n\n".join(snippets)
    index_md = llm.call_llm(INDEX_SYSTEM, prompt)
    INDEX_FILE.write_text(index_md)
    return index_md


# ── Search ──────────────────────────────────────────────────────────────

def search_wiki(query: str, top_n: int = 5) -> list[tuple[str, int]]:
    """Naive keyword search. Returns [(slug, score), ...] sorted by relevance."""
    tokens = set(query.lower().split())
    articles = load_wiki_articles()
    scored = []
    for slug, content in articles.items():
        lower = content.lower()
        score = sum(lower.count(t) for t in tokens)
        if score > 0:
            scored.append((slug, score))
    scored.sort(key=lambda x: -x[1])
    return scored[:top_n]


# ── Query ───────────────────────────────────────────────────────────────

QUERY_SYSTEM = """\
You are a knowledge-base research assistant. Answer the user's question using \
ONLY the wiki articles provided as context. Cite sources using [[article-slug]] \
notation. If the context is insufficient, say so honestly. Write in the same \
language as the question.
Output ONLY the raw markdown content. No code fences, no explanations, no preamble.
"""

INTEGRATE_SYSTEM = """\
You are a knowledge-base integrator. Given a question, an answer, and the existing \
wiki articles that were used as context, decide how to best integrate the new \
information into the knowledge base.

You MUST output a JSON object (no markdown fences, no extra text) with this structure:

Option A — Update an existing article:
{"action": "update", "slug": "<existing-article-slug>", "content": "<full updated article markdown>"}

Option B — Create a new article:
{"action": "create", "title": "<article title>", "content": "<full new article markdown>"}

Decision rules:
- If the answer mainly supplements, corrects, or deepens an existing article, \
choose "update" and return the FULL updated article with the new information \
merged naturally into the existing structure.
- If the answer covers a genuinely new topic not well-covered by any existing \
article, choose "create" and write a proper wiki article (H1 title, summary, \
H2/H3 sections, Categories, See Also with [[wikilinks]]).
- Prefer "update" when the information clearly belongs in an existing article. \
Only "create" when it would be a distinct, standalone topic.
- Keep articles faithful to facts; do not invent information beyond what the \
answer provides.
- Write in the same language as the question and answer.
"""


def _integrate_answer(question: str, answer: str, context_slugs: list[str],
                      articles: dict[str, str]) -> dict:
    """Ask LLM how to integrate the answer into the wiki. Returns action dict."""
    import json

    context_parts = []
    for slug in context_slugs:
        if slug in articles:
            context_parts.append(f"## {slug}.md\n\n{articles[slug]}")

    all_slugs = list(articles.keys())
    prompt = (
        f"## Question\n{question}\n\n"
        f"## Answer\n{answer}\n\n"
        f"## Existing articles used as context\n\n"
        + "\n\n---\n\n".join(context_parts)
        + f"\n\n## All wiki article slugs (for wikilinks): {', '.join(all_slugs)}"
    )

    raw = llm.call_llm(INTEGRATE_SYSTEM, prompt)

    # Strip potential markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    return json.loads(raw)


def query(question: str, save: bool = False) -> str:
    ensure_dirs()
    results = search_wiki(question, top_n=8)
    articles = load_wiki_articles()

    if not results:
        # fallback: use all articles if wiki is small
        if len(articles) <= 20:
            context = [f"# {s}\n\n{c}" for s, c in articles.items()]
            context_slugs = list(articles.keys())
        else:
            return "No relevant articles found. Try adding more data to the wiki."
    else:
        context = [f"# {slug}\n\n{articles[slug]}" for slug, _ in results if slug in articles]
        context_slugs = [slug for slug, _ in results if slug in articles]

    answer = llm.call_llm_with_context(QUERY_SYSTEM, context, question)

    save_info = None
    if save:
        try:
            decision = _integrate_answer(question, answer, context_slugs, articles)
        except Exception:
            # Fallback: save as new article if integration fails
            decision = {"action": "create", "title": question[:60],
                        "content": f"# {question}\n\n{answer}"}

        action = decision.get("action", "create")
        if action == "update" and decision.get("slug") in articles:
            slug = decision["slug"]
            dest = WIKI_DIR / f"{slug}.md"
            dest.write_text(decision["content"])
            save_info = {"action": "update", "slug": slug}
        else:
            title = decision.get("title", question[:60])
            slug = slugify(title)
            dest = WIKI_DIR / f"{slug}.md"
            dest.write_text(decision["content"])
            save_info = {"action": "create", "slug": slug}

        rebuild_index()

    return {"answer": answer, "save_info": save_info}


# ── Lint ────────────────────────────────────────────────────────────────

LINT_SYSTEM = """\
You are a knowledge-base quality auditor. Given the article titles and summaries, \
identify:
1. Potential inconsistencies or contradictions between articles.
2. Gaps in coverage — important related topics not yet covered.
3. Suggest 3-5 new article titles that would strengthen the knowledge base.
4. Any data integrity issues you notice.

Be specific and actionable. Write in the same language as the articles.
Output ONLY the raw markdown content. No code fences, no explanations, no preamble.
"""


def lint_wiki() -> dict:
    """Run structural + LLM-powered health checks."""
    articles = load_wiki_articles()
    findings = {"structural": [], "llm": ""}

    if not articles:
        findings["structural"].append("Wiki is empty — nothing to lint.")
        return findings

    # Structural checks
    all_slugs = set(articles.keys())
    for slug, content in articles.items():
        # broken wikilinks
        links = re.findall(r"\[\[([^\]]+)\]\]", content)
        for link in links:
            link_slug = slugify(link)
            if link_slug not in all_slugs:
                findings["structural"].append(
                    f"[{slug}] broken link: [[{link}]] (no article '{link_slug}')"
                )
        # missing categories
        if "## Categories" not in content and "## categories" not in content.lower():
            findings["structural"].append(f"[{slug}] missing Categories section")

    # Orphan detection
    linked_slugs = set()
    for content in articles.values():
        for link in re.findall(r"\[\[([^\]]+)\]\]", content):
            linked_slugs.add(slugify(link))
    for slug in all_slugs:
        if slug not in linked_slugs:
            findings["structural"].append(f"[{slug}] orphan article (not linked from anywhere)")

    # LLM analysis
    snippets = []
    for slug, content in articles.items():
        summary = "\n".join(content.split("\n")[:8])
        snippets.append(f"### {slug}\n{summary}")
    prompt = "\n\n".join(snippets)
    findings["llm"] = llm.call_llm(LINT_SYSTEM, prompt)

    return findings


# ── Fix ─────────────────────────────────────────────────────────────────

FIX_SYSTEM = """\
You are a knowledge-base editor. You will be given a wiki article and a list of \
issues found by a linter. Fix ALL the issues in the article and return the \
corrected full article.

Fix types:
- Broken links: remove the link or replace with a valid one from the existing articles list.
- Missing "## Categories" section: add one at the bottom with appropriate tags.
- Orphan articles: add a "## See Also" section with relevant [[wikilinks]] to existing articles.
- Content issues flagged by LLM analysis: fix inconsistencies, fill gaps, improve clarity.

Rules:
- Keep the article faithful to its original content; do not remove valid information.
- Write in the same language as the article.
- Output ONLY the corrected full markdown article. No code fences, no explanations.
"""


def fix_wiki() -> dict:
    """Run lint, then auto-fix each article with issues. Returns {slug: list of fixes}."""
    findings = lint_wiki()
    articles = load_wiki_articles()
    all_slugs = list(articles.keys())

    # Group structural issues by slug
    issues_by_slug: dict[str, list[str]] = {}
    for issue in findings["structural"]:
        # Issues are formatted as "[slug] description"
        if issue.startswith("["):
            bracket_end = issue.index("]")
            slug = issue[1:bracket_end]
            desc = issue[bracket_end + 2:]
            issues_by_slug.setdefault(slug, []).append(desc)

    # If LLM analysis mentions specific articles, apply to all articles
    llm_notes = findings.get("llm", "")

    fixed: dict[str, list[str]] = {}

    for slug, issue_list in issues_by_slug.items():
        if slug not in articles:
            continue

        prompt = (
            f"## Article: {slug}.md\n\n{articles[slug]}\n\n"
            f"## Existing articles (for valid links): {', '.join(all_slugs)}\n\n"
            f"## Issues to fix:\n" +
            "\n".join(f"- {i}" for i in issue_list)
        )
        if llm_notes:
            prompt += f"\n\n## Additional LLM analysis (fix if relevant to this article):\n{llm_notes}"

        new_content = llm.call_llm(FIX_SYSTEM, prompt)
        dest = WIKI_DIR / f"{slug}.md"
        dest.write_text(new_content)
        fixed[slug] = issue_list

    # Also fix articles that have no structural issues but LLM flagged problems
    # Only if there are specific mentions in the LLM analysis
    if llm_notes and not issues_by_slug:
        for slug, content in articles.items():
            slug_lower = slug.lower()
            if slug_lower in llm_notes.lower():
                prompt = (
                    f"## Article: {slug}.md\n\n{content}\n\n"
                    f"## Existing articles (for valid links): {', '.join(all_slugs)}\n\n"
                    f"## LLM analysis (fix issues relevant to this article):\n{llm_notes}"
                )
                new_content = llm.call_llm(FIX_SYSTEM, prompt)
                dest = WIKI_DIR / f"{slug}.md"
                dest.write_text(new_content)
                fixed[slug] = ["LLM-suggested improvements"]

    if fixed:
        rebuild_index()

    return fixed

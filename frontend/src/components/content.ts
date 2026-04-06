import { marked } from "marked";
import { api } from "../api";
import { setState } from "../state";
import { renderArticleList, loadArticles } from "./sidebar";
import type { SearchResult } from "../types";

const mainContent = () => document.getElementById("mainContent")!;
const statusBar = () => document.getElementById("statusBar")!;

// ── Markdown Rendering ─────────────────────

function renderMarkdown(md: string): string {
  // Convert [[wikilinks]] to markdown links
  const withLinks = md.replace(/\[\[([^\]]+)\]\]/g, "[$1]($1.md)");
  return marked.parse(withLinks) as string;
}

function setContent(html: string): void {
  mainContent().innerHTML = html;
}

function setStatus(msg: string): void {
  statusBar().textContent = msg;
}

export function showLoading(msg: string): void {
  setContent(`<div class="loading-msg"><div class="spinner"></div>${msg}</div>`);
}

// ── Article View ───────────────────────────

export async function showArticle(slug: string): Promise<void> {
  setState({ currentSlug: slug });
  renderArticleList();
  showLoading("Loading article...");

  try {
    const data = await api.getArticle(slug);
    setContent(`<div class="md-content">${renderMarkdown(data.content)}</div>`);
    setStatus(`wiki/${slug}.md`);
  } catch (e) {
    setContent(`<div class="panel error"><div class="panel-title">Error</div>${e}</div>`);
  }
}

// ── Index View ─────────────────────────────

export async function showIndex(): Promise<void> {
  setState({ currentSlug: null });
  renderArticleList();
  showLoading("Loading index...");

  try {
    const data = await api.getIndex();
    setContent(`<div class="md-content">${renderMarkdown(data.content)}</div>`);
    setStatus("wiki/INDEX.md");
  } catch (e) {
    setContent(`<div class="panel error"><div class="panel-title">Error</div>${e}</div>`);
  }
}

// ── Search Results ─────────────────────────

export function showSearchResults(query: string, results: SearchResult[]): void {
  if (results.length === 0) {
    setContent(
      '<div class="panel"><div class="panel-title">Search Results</div>No results found.</div>',
    );
    return;
  }

  const items = results
    .map(
      (r) =>
        `<div class="result-item" data-slug="${r.slug}">
        <span>${r.slug}</span>
        <span class="result-score">score: ${r.score}</span>
      </div>`,
    )
    .join("");

  setContent(
    `<div class="panel"><div class="panel-title">Search Results for "${query}"</div>${items}</div>`,
  );
  setStatus(`Search: ${query} — ${results.length} results`);
}

// ── Query Answer ───────────────────────────

export function showQueryAnswer(answer: string, saved: boolean): void {
  setContent(`<div class="md-content">${renderMarkdown(answer)}</div>`);
  setStatus(saved ? "Answer saved to wiki" : "Query complete");
}

// ── Compile ────────────────────────────────

export async function doCompile(force: boolean): Promise<void> {
  const btn = document.getElementById("btnCompile") as HTMLButtonElement;
  btn.disabled = true;
  showLoading("Compiling raw documents into wiki articles...");
  setStatus("Compiling...");

  try {
    const data = await api.compile(force);
    if (data.count === 0) {
      setContent(
        '<div class="panel"><div class="panel-title">Compile</div>Nothing new to compile.</div>',
      );
    } else {
      const list = data.created.map((s) => `<li><strong>${s}.md</strong></li>`).join("");
      setContent(
        `<div class="panel"><div class="panel-title">Compiled ${data.count} Articles</div><ul>${list}</ul></div>`,
      );
    }
    setStatus(`Compiled ${data.count} articles`);
    await loadArticles();
  } catch (e) {
    setContent(`<div class="panel error"><div class="panel-title">Error</div>${e}</div>`);
  } finally {
    btn.disabled = false;
  }
}

// ── Lint ────────────────────────────────────

export async function doLint(): Promise<void> {
  const btn = document.getElementById("btnLint") as HTMLButtonElement;
  btn.disabled = true;
  showLoading("Running health checks...");
  setStatus("Linting...");

  try {
    const data = await api.lint();
    let html = "";

    if (data.structural.length > 0) {
      const items = data.structural.map((s) => `<li>${s}</li>`).join("");
      html += `<div class="panel warn"><div class="panel-title">Structural Issues</div><ul>${items}</ul></div>`;
    } else {
      html += '<div class="panel"><div class="panel-title">Structural Issues</div>None found</div>';
    }

    if (data.llm) {
      html += `<div class="panel"><div class="panel-title">LLM Analysis</div><div class="md-content">${renderMarkdown(data.llm)}</div></div>`;
    }

    setContent(html);
    setStatus("Lint complete");
  } catch (e) {
    setContent(`<div class="panel error"><div class="panel-title">Error</div>${e}</div>`);
  } finally {
    btn.disabled = false;
  }
}

// ── Fix ────────────────────────────────────

export async function doFix(): Promise<void> {
  const btn = document.getElementById("btnFix") as HTMLButtonElement;
  btn.disabled = true;
  showLoading("Running lint + auto-fix... This may take a while.");
  setStatus("Fixing...");

  try {
    const data = await api.fix();
    if (data.count === 0) {
      setContent(
        '<div class="panel"><div class="panel-title">Fix</div>No issues to fix.</div>',
      );
    } else {
      const items = Object.entries(data.fixed)
        .map(
          ([slug, issues]) =>
            `<li><strong>${slug}.md</strong><ul>${issues.map((i) => `<li>${i}</li>`).join("")}</ul></li>`,
        )
        .join("");
      setContent(
        `<div class="panel"><div class="panel-title">Fixed ${data.count} Articles</div><ul>${items}</ul></div>`,
      );
    }
    setStatus(`Fixed ${data.count} articles`);
    await loadArticles();
  } catch (e) {
    setContent(`<div class="panel error"><div class="panel-title">Error</div>${e}</div>`);
  } finally {
    btn.disabled = false;
  }
}

// ── Link Interception ──────────────────────

export function initContentLinks(): void {
  document.addEventListener("click", (e) => {
    const a = (e.target as HTMLElement).closest(".md-content a") as HTMLAnchorElement | null;
    if (!a) return;
    const href = a.getAttribute("href");
    if (href?.endsWith(".md")) {
      e.preventDefault();
      const slug = href.replace(/\.md$/, "");
      showArticle(slug);
    }
  });

  // Search result click delegation
  document.addEventListener("click", (e) => {
    const item = (e.target as HTMLElement).closest(".result-item") as HTMLElement | null;
    if (item?.dataset.slug) {
      showArticle(item.dataset.slug);
    }
  });
}

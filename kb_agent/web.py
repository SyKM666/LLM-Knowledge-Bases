"""Flask web frontend for the knowledge base agent."""

import os
from pathlib import Path

from flask import Flask, request, jsonify, render_template

from . import core

# Ensure working directory is the project root
os.chdir(Path(__file__).resolve().parent.parent)

app = Flask(__name__, template_folder="../templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB upload limit


# ── Pages ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Read API ────────────────────────────────────────────────────────────

@app.route("/api/articles")
def list_articles():
    articles = core.load_wiki_articles()
    summaries = {}
    for slug, content in articles.items():
        lines = [l for l in content.split("\n") if l.strip()]
        # skip h1 title, take first non-empty line as summary
        summary = lines[1] if len(lines) > 1 else ""
        summaries[slug] = summary[:150]
    return jsonify({"articles": summaries})


@app.route("/api/articles/<slug>")
def get_article(slug):
    articles = core.load_wiki_articles()
    if slug not in articles:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"slug": slug, "content": articles[slug]})


@app.route("/api/index")
def get_index():
    core.ensure_dirs()
    if core.INDEX_FILE.exists():
        return jsonify({"content": core.INDEX_FILE.read_text()})
    return jsonify({"content": "_No index yet. Run compile first._"})


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": []})
    results = core.search_wiki(q)
    return jsonify({"results": [{"slug": s, "score": sc} for s, sc in results]})


@app.route("/api/raw")
def list_raw():
    core.ensure_dirs()
    files = sorted(f.name for f in core.RAW_DIR.iterdir() if f.is_file() and not f.name.startswith("."))
    return jsonify({"files": files})


# ── Write API ───────────────────────────────────────────────────────────

@app.route("/api/query", methods=["POST"])
def do_query():
    data = request.get_json()
    question = data.get("question", "").strip()
    save = data.get("save", False)
    if not question:
        return jsonify({"error": "Empty question"}), 400
    try:
        result = core.query(question, save=save)
        return jsonify({
            "answer": result["answer"],
            "saved": result["save_info"] is not None,
            "save_info": result["save_info"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compile", methods=["POST"])
def do_compile():
    data = request.get_json() or {}
    force = data.get("force", False)
    try:
        created = core.compile_all(force=force)
        return jsonify({"created": created, "count": len(created)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/lint", methods=["POST"])
def do_lint():
    try:
        findings = core.lint_wiki()
        return jsonify(findings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/fix", methods=["POST"])
def do_fix():
    try:
        fixed = core.fix_wiki()
        return jsonify({"fixed": fixed, "count": len(fixed)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/rebuild-index", methods=["POST"])
def do_rebuild_index():
    try:
        core.rebuild_index()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ingest/file", methods=["POST"])
def ingest_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "No filename"}), 400
    core.ensure_dirs()
    if f.filename.lower().endswith(".pdf"):
        dest = core.ingest_pdf_bytes(f.filename, f.read())
    else:
        dest = core.RAW_DIR / f.filename
        f.save(dest)
    return jsonify({"filename": dest.name, "path": str(dest)})


@app.route("/api/ingest/text", methods=["POST"])
def ingest_text():
    data = request.get_json()
    filename = data.get("filename", "").strip()
    content = data.get("content", "").strip()
    if not filename or not content:
        return jsonify({"error": "filename and content required"}), 400
    if not filename.endswith(".md"):
        filename += ".md"
    core.ensure_dirs()
    dest = core.RAW_DIR / filename
    dest.write_text(content)
    return jsonify({"filename": filename, "path": str(dest)})


@app.route("/api/articles/<slug>", methods=["DELETE"])
def delete_article(slug):
    path = core.WIKI_DIR / f"{slug}.md"
    if not path.exists():
        return jsonify({"error": "Not found"}), 404
    path.unlink()
    return jsonify({"ok": True})


# ── Entry point ─────────────────────────────────────────────────────────

def main():
    core.ensure_dirs()
    port = int(os.environ.get("KB_PORT", 5002))
    print(f"KB Agent Web UI → http://localhost:{port}")
    app.run(debug=True, port=port, use_reloader=False)


if __name__ == "__main__":
    main()

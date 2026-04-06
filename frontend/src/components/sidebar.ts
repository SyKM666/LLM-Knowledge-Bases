import { api } from "../api";
import { getState, setState } from "../state";
import { showArticle, showSearchResults, showQueryAnswer } from "./content";

// ── Article List ───────────────────────────

export async function loadArticles(): Promise<void> {
  try {
    const data = await api.listArticles();
    setState({ articles: data.articles });
    renderArticleList();
  } catch (e) {
    console.error("Failed to load articles", e);
  }
}

export function renderArticleList(): void {
  const list = document.getElementById("articleList")!;
  const { articles, currentSlug } = getState();
  const slugs = Object.keys(articles).sort();

  if (slugs.length === 0) {
    list.innerHTML = '<li class="empty">No articles yet</li>';
    return;
  }

  list.innerHTML = slugs
    .map(
      (slug) =>
        `<li class="${slug === currentSlug ? "active" : ""}" data-slug="${slug}" title="${articles[slug]}">${slug}</li>`,
    )
    .join("");
}

export function initSidebar(): void {
  // Article list click delegation
  document.getElementById("articleList")!.addEventListener("click", (e) => {
    const li = (e.target as HTMLElement).closest("li[data-slug]") as HTMLElement | null;
    if (li?.dataset.slug) {
      showArticle(li.dataset.slug);
    }
  });

  // Search
  const searchInput = document.getElementById("searchInput") as HTMLInputElement;
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") doSearch();
  });
  document.getElementById("btnSearch")!.addEventListener("click", doSearch);

  // Query
  document.getElementById("btnQuery")!.addEventListener("click", doQuery);
  (document.getElementById("queryInput") as HTMLTextAreaElement).addEventListener(
    "keydown",
    (e) => {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) doQuery();
    },
  );
}

// ── Search ─────────────────────────────────

async function doSearch(): Promise<void> {
  const input = document.getElementById("searchInput") as HTMLInputElement;
  const q = input.value.trim();
  if (!q) return;

  setState({ loading: true, loadingMessage: "Searching..." });
  try {
    const data = await api.search(q);
    showSearchResults(q, data.results);
  } catch (e) {
    console.error(e);
  } finally {
    setState({ loading: false });
  }
}

// ── Query ──────────────────────────────────

async function doQuery(): Promise<void> {
  const textarea = document.getElementById("queryInput") as HTMLTextAreaElement;
  const question = textarea.value.trim();
  if (!question) return;

  const save = (document.getElementById("querySave") as HTMLInputElement).checked;
  const btn = document.getElementById("btnQuery") as HTMLButtonElement;

  btn.disabled = true;
  setState({ loading: true, loadingMessage: "Researching your question..." });

  try {
    const data = await api.query(question, save);
    showQueryAnswer(data.answer, save);
    if (save) await loadArticles();
  } catch (e) {
    console.error(e);
  } finally {
    btn.disabled = false;
    setState({ loading: false });
  }
}

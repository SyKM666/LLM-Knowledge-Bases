import type {
  ArticleSummaries,
  ArticleDetail,
  IndexContent,
  SearchResponse,
  QueryResponse,
  CompileResponse,
  LintResponse,
  FixResponse,
  IngestResponse,
} from "./types";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const resp = await fetch(path, opts);
  const data = await resp.json();
  if (!resp.ok) {
    throw new ApiError(resp.status, data.error ?? `HTTP ${resp.status}`);
  }
  return data as T;
}

function postJSON<T>(path: string, body: Record<string, unknown>): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  listArticles(): Promise<ArticleSummaries> {
    return request("/api/articles");
  },

  getArticle(slug: string): Promise<ArticleDetail> {
    return request(`/api/articles/${encodeURIComponent(slug)}`);
  },

  getIndex(): Promise<IndexContent> {
    return request("/api/index");
  },

  search(q: string): Promise<SearchResponse> {
    return request(`/api/search?q=${encodeURIComponent(q)}`);
  },

  query(question: string, save: boolean): Promise<QueryResponse> {
    return postJSON("/api/query", { question, save });
  },

  compile(force: boolean): Promise<CompileResponse> {
    return postJSON("/api/compile", { force });
  },

  lint(): Promise<LintResponse> {
    return postJSON("/api/lint", {});
  },

  fix(): Promise<FixResponse> {
    return postJSON("/api/fix", {});
  },

  rebuildIndex(): Promise<{ ok: boolean }> {
    return postJSON("/api/rebuild-index", {});
  },

  async ingestFile(file: File): Promise<IngestResponse> {
    const form = new FormData();
    form.append("file", file);
    return request("/api/ingest/file", { method: "POST", body: form });
  },

  ingestText(filename: string, content: string): Promise<IngestResponse> {
    return postJSON("/api/ingest/text", { filename, content });
  },

  deleteArticle(slug: string): Promise<{ ok: boolean }> {
    return request(`/api/articles/${encodeURIComponent(slug)}`, {
      method: "DELETE",
    });
  },
};

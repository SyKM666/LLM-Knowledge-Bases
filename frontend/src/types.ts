export interface ArticleSummaries {
  articles: Record<string, string>;
}

export interface ArticleDetail {
  slug: string;
  content: string;
}

export interface IndexContent {
  content: string;
}

export interface SearchResult {
  slug: string;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
}

export interface QueryResponse {
  answer: string;
  saved: boolean;
}

export interface CompileResponse {
  created: string[];
  count: number;
}

export interface LintResponse {
  structural: string[];
  llm: string;
}

export interface FixResponse {
  fixed: Record<string, string[]>;
  count: number;
}

export interface IngestResponse {
  filename: string;
  path: string;
}

export interface RawFilesResponse {
  files: string[];
}

export interface ApiError {
  error: string;
}

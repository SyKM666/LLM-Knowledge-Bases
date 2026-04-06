type Listener = () => void;

export interface AppState {
  currentSlug: string | null;
  articles: Record<string, string>;
  loading: boolean;
  loadingMessage: string;
}

const state: AppState = {
  currentSlug: null,
  articles: {},
  loading: false,
  loadingMessage: "",
};

const listeners = new Set<Listener>();

export function getState(): Readonly<AppState> {
  return state;
}

export function setState(partial: Partial<AppState>): void {
  Object.assign(state, partial);
  listeners.forEach((fn) => fn());
}

export function subscribe(fn: Listener): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

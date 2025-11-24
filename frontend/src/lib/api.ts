import type {
  AdvancedSearchResponse,
  BookResponse,
  SearchResponse,
  SuggestionsResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080/api';

async function http<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message = errorBody?.detail ?? 'Unexpected API error';
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  search(query: string, size = 10) {
    const params = new URLSearchParams({ query, size: String(size) });
    return http<SearchResponse>(`/search?${params.toString()}`);
  },
  regex(regex: string, size = 10) {
    const params = new URLSearchParams({ regex, size: String(size) });
    return http<AdvancedSearchResponse>(`/search/advanced?${params.toString()}`);
  },
  book(id: string) {
    return http<BookResponse>(`/books/${id}`);
  },
  suggestions(bookId: string, limit = 5) {
    const params = new URLSearchParams({ book_id: bookId, limit: String(limit) });
    return http<SuggestionsResponse>(`/suggestions?${params.toString()}`);
  },
};



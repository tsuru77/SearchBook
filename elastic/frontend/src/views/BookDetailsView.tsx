import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { SuggestionsList } from '../components/SuggestionsList';
import { api } from '../lib/api';
import type { BookResponse, Suggestion } from '../types/api';

export function BookDetailsView() {
  const { bookId } = useParams<{ bookId: string }>();
  const [book, setBook] = useState<BookResponse | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [suggestionsError, setSuggestionsError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!bookId) return;
    setIsLoading(true);
    Promise.all([api.book(bookId), api.suggestions(bookId)])
      .then(([bookResponse, suggestionsResponse]) => {
        setBook(bookResponse);
        setSuggestions(suggestionsResponse.results);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Unable to fetch book.');
        setBook(null);
      })
      .finally(() => setIsLoading(false));
  }, [bookId]);

  const refreshSuggestions = async () => {
    if (!bookId) return;
    setSuggestionsError(null);
    try {
      const response = await api.suggestions(bookId);
      setSuggestions(response.results);
    } catch (err) {
      setSuggestionsError(err instanceof Error ? err.message : 'Unable to refresh suggestions');
    }
  };

  if (isLoading) {
    return <p className="muted">Loading book…</p>;
  }

  if (error || !bookId) {
    return (
      <section>
        <p className="error">
          {error ?? 'Missing book id'}
        </p>
      </section>
    );
  }

  return (
    <section className="book-view">
      <article>
        <header className="view-header">
          <div>
            <p className="eyebrow">Book Detail</p>
            <h1>{book?.title ?? 'Untitled book'}</h1>
            <p className="muted">{book?.author ?? 'Unknown author'}</p>
          </div>
          <div className="score-stack">
            <span className="score-chip">
              Word count: <strong>{book?.word_count ?? '—'}</strong>
            </span>
            <span className="score-chip secondary">
              Centrality: <strong>{book?.centrality_score?.toFixed(3) ?? '—'}</strong>
            </span>
          </div>
        </header>

        <section className="book-text">
          <pre>{book?.text ?? 'No text available.'}</pre>
        </section>
      </article>

      <aside className="panel">
        <div className="panel-header">
          <h3>Suggested books</h3>
          <button className="text-button" onClick={refreshSuggestions}>
            Refresh
          </button>
        </div>
        <SuggestionsList suggestions={suggestions} error={suggestionsError} />
      </aside>
    </section>
  );
}



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
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start', width: '100%' }}>
            {book?.image_url && (
              <img
                src={book.image_url}
                alt={`Cover of ${book.title}`}
                style={{
                  width: '200px',
                  aspectRatio: '2/3',
                  objectFit: 'cover',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                }}
              />
            )}
            <div style={{ flex: 1 }}>
              <p className="eyebrow">Book Detail</p>
              <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{book?.title ?? 'Untitled book'}</h1>
              <p className="muted" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>{book?.author ?? 'Unknown author'}</p>

              <div className="score-stack" style={{ flexDirection: 'row', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
                <span className="score-chip">
                  Word count: <strong>{book?.word_count?.toLocaleString() ?? '—'}</strong>
                </span>
                <span className="score-chip secondary">
                  Centrality: <strong>{book?.centrality_score?.toFixed(3) ?? '—'}</strong>
                </span>
                {book?.metadata && Object.entries(book.metadata).map(([key, value]) => (
                  <span key={key} className="score-chip" style={{ background: 'rgba(255, 255, 255, 0.05)' }}>
                    {key}: <strong>{value}</strong>
                  </span>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                {/* Gutenberg button removed as per user request */}
              </div>
            </div>
          </div>
        </header>

        <section className="book-text" style={{ background: 'transparent', padding: 0, marginTop: '2rem' }}>
          <div className="panel">
            <h3>Raw Text</h3>
            <p className="muted" style={{ marginBottom: '1rem' }}>
              The full text content of this book is available.
            </p>
            <button
              className="text-button"
              onClick={() => {
                if (book?.text) {
                  const blob = new Blob([book.text], { type: 'text/plain' });
                  const url = URL.createObjectURL(blob);
                  window.open(url, '_blank');
                }
              }}
            >
              Open Raw Text in New Tab ↗
            </button>
          </div>
        </section>
      </article>

      <aside className="panel" style={{ marginTop: '2rem' }}>
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



import { Link } from 'react-router-dom';

import type { SearchResult } from '../types/api';

type Props = {
  result: SearchResult;
};

export function SearchResultCard({ result }: Props) {
  const bookId = result.id ?? undefined;
  return (
    <article className="result-card">
      <header className="result-header">
        <div>
          <h3>{result.title ?? 'Untitled book'}</h3>
          <p className="muted">{result.author ?? 'Unknown author'}</p>
        </div>
        <div className="score-stack">
          <span className="score-chip">
            ES score: <strong>{result.score?.toFixed(2) ?? '—'}</strong>
          </span>
          <span className="score-chip secondary">
            Centrality: <strong>{result.centrality_score?.toFixed(3) ?? '—'}</strong>
          </span>
        </div>
      </header>
      <p className="snippet">{result.snippet ?? 'No snippet available.'}</p>
      {bookId && (
        <footer>
          <Link className="text-link" to={`/books/${bookId}`}>
            View book →
          </Link>
        </footer>
      )}
    </article>
  );
}



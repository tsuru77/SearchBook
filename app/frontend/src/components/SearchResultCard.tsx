import { Link } from 'react-router-dom';

import type { SearchResult } from '../types/api';

type Props = {
  result: SearchResult;
};

export function SearchResultCard({ result }: Props) {
  const bookId = result.id ?? undefined;
  return (
    <article className="result-card">
      <div className="result-body-vertical">
        {result.image_url ? (
          <img
            src={result.image_url}
            alt={`Cover of ${result.title}`}
            className="result-image"
          />
        ) : (
          <div className="result-image-placeholder">No Cover</div>
        )}

        <header className="result-header">
          <div>
            <h3>{result.title ?? 'Untitled book'}</h3>
            <p className="muted">{result.author ?? 'Unknown author'}</p>
          </div>
        </header>

        <div className="score-stack">
          <span className="score-chip">
            Score: <strong>{result.score?.toFixed(2) ?? '—'}</strong>
          </span>
          <span className="score-chip secondary">
            Centrality: <strong>{result.centrality_score?.toFixed(3) ?? '—'}</strong>
          </span>
        </div>

        {/* Snippet removed as per user request */}
      </div>
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



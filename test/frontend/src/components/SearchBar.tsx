/**
 * Composant SearchBar : barre de recherche avec toggle RegEx
 */
import React, { useState } from "react";
import { RankingType } from "../types/api";

interface SearchBarProps {
  onSearch: (query: string, isRegex: boolean) => void;
  rankingBy: RankingType;
  onRankingChange: (ranking: RankingType) => void;
  loading?: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  rankingBy,
  onRankingChange,
  loading = false,
}) => {
  const [query, setQuery] = useState("");
  const [isRegex, setIsRegex] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, isRegex);
    }
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              isRegex
                ? "Entrez une regex (ex: ^the.*ing$)"
                : "Chercher un livre ou un mot..."
            }
            disabled={loading}
            className="search-input"
          />
          <button type="submit" disabled={loading} className="search-btn">
            {loading ? "Recherche..." : "🔍 Chercher"}
          </button>
        </div>

        <div className="search-options">
          <label className="regex-toggle">
            <input
              type="checkbox"
              checked={isRegex}
              onChange={(e) => setIsRegex(e.target.checked)}
              disabled={loading}
            />
            <span>Mode RegEx</span>
          </label>

          <fieldset className="ranking-selector">
            <legend>Classer par :</legend>
            <label>
              <input
                type="radio"
                value="occurrences"
                checked={rankingBy === "occurrences"}
                onChange={(e) =>
                  onRankingChange(e.target.value as RankingType)
                }
                disabled={loading}
              />
              <span>Occurrences</span>
            </label>
            <label>
              <input
                type="radio"
                value="pagerank"
                checked={rankingBy === "pagerank"}
                onChange={(e) =>
                  onRankingChange(e.target.value as RankingType)
                }
                disabled={loading}
              />
              <span>PageRank</span>
            </label>
          </fieldset>
        </div>
      </form>
    </div>
  );
};

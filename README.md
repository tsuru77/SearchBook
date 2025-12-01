# 📚 SearchBook

SearchBook is a powerful search engine and digital library management system designed to ingest, index, and search through large collections of books. It features advanced search capabilities, including regex support, relevance ranking based on graph centrality, and intelligent book suggestions.

## ✨ Features

- **🔍 Full-Text Search**: Fast keyword search across thousands of books.
- **🧠 Advanced Regex Search**: Powerful regular expression search to find complex patterns within texts.
- **📊 Relevance Ranking**:
  - **BM25**: Industry-standard probabilistic information retrieval algorithm.
  - **Closeness Centrality**: Graph-based ranking to identify "central" or important books in the collection.
- **💡 Smart Suggestions**:
  - **Jaccard Similarity**: Suggests related books based on vocabulary overlap.
  - **Graph-Based Recommendations**: Finds neighbors in the similarity graph.
- **🚀 High-Performance Ingestion**:
  - **Project Gutenberg Integration**: Automatically download and process books.
  - **Local File Support**: Ingest your own `.txt` book collections.
  - **Parallel Processing**: Efficiently handles large datasets.

## 🛠️ Tech Stack

### Frontend
- **React**: Modern UI library for building interactive interfaces.
- **Vite**: Next-generation frontend tooling for fast builds.
- **TypeScript**: Type-safe code for better maintainability.
- **TailwindCSS**: Utility-first CSS framework for rapid UI development.

### Backend
- **FastAPI**: High-performance, easy-to-learn web framework for building APIs with Python.
- **NetworkX**: Python library for the creation, manipulation, and study of complex networks (used for centrality and similarity graphs).
- **Rank-BM25**: Library for BM25 ranking algorithms.
- **PostgreSQL**: Robust open-source relational database for storing book metadata, indices, and graph data.

### Infrastructure
- **Docker**: Containerization for consistent development and deployment environments.
- **Docker Compose**: Multi-container orchestration.

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.
- [Git](https://git-scm.com/) for cloning the repository.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/SearchBook.git
   cd SearchBook
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```
   This command will build the images and start the frontend, backend, and database services.

3. **Access the application**
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **Backend API**: [http://localhost:8000](http://localhost:8000)
   - **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📥 Data Ingestion

Before you can search, you need to populate the database with books. We provide a CLI tool for this.

### Quick Start (Project Gutenberg Download)
To download and index books directly from Project Gutenberg:

```bash
# Enter the backend container
docker-compose exec backend bash

# Run the ingestion wrapper script (handles dependencies and venv)
# Usage: ./ingestion/run_ingestion.sh [number_of_books]
./ingestion/run_ingestion.sh 50
```

### Local Corpus Ingestion
To ingest books from a local directory (containing `.txt` files):

```bash
# Ensure your local dataset is mounted or available in the container
# Example: Ingesting from the 'datasets' folder mounted in the container
python ingestion/load_books.py --path /app/datasets/sample_books
```

### Advanced Usage (Direct Python Script)
If you need more control (e.g., changing start_id), you can run the python script directly:

```bash
python ingestion/load_books.py --start_id 1 --num_texts 50 --min_words 10000
```

### Options
- `--path`: Path to a local directory containing `.txt` files (e.g., `pg123.txt`). If provided, Gutenberg download is skipped.
- `--start_id`: Gutenberg ID to start downloading from (default: 1).
- `--num_texts`: Number of books to process (default: 50).
- `--min_words`: Minimum word count to include a book (default: 10000).

For a full list of commands and workflows, check `app/QUICK_START.sh`.

## 🏗️ Architecture

The application follows a modern 3-tier architecture:

1.  **Client (Frontend)**: A React SPA that communicates with the backend via REST API. It handles user input for search queries and displays results and visualizations.
2.  **Server (Backend)**: A FastAPI service that:
    - Exposes endpoints for search and suggestions.
    - Orchestrates the ingestion pipeline.
    - Interfaces with the database.
3.  **Data Layer (Database)**: PostgreSQL database storing:
    - Raw book text and metadata.
    - Inverted index for fast full-text search.
    - Graph data (nodes and edges) for similarity and centrality calculations.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

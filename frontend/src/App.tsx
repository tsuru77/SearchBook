import { NavLink, Route, Routes } from 'react-router-dom'

import './App.css'
import { AdvancedRegexView } from './views/AdvancedRegexView'
import { BookDetailsView } from './views/BookDetailsView'
import { HomeSearchView } from './views/HomeSearchView'

function App() {
  return (
    <div className="app-shell">
      <nav className="top-nav">
        <div className="brand">SearchBook</div>
        <div className="nav-links">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/regex">Regex</NavLink>
        </div>
      </nav>
      <main className="container">
        <Routes>
          <Route path="/" element={<HomeSearchView />} />
          <Route path="/regex" element={<AdvancedRegexView />} />
          <Route path="/books/:bookId" element={<BookDetailsView />} />
        </Routes>
      </main>
    </div>
  )
}

export default App

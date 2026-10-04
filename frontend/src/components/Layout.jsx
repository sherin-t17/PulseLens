import { Link, NavLink, Outlet } from "react-router-dom";

const LINKS = [
  ["/", "🏠", "Home"],
  ["/measure", "🎥", "Measure"],
  ["/history", "🕘", "History"],
  ["/report", "📄", "Report"],
];

// On phones the menu becomes a bottom bar (see index.css).
export default function Layout() {
  return (
    <div className="app">
      <header className="topbar">
        <Link to="/" className="brand">❤️ PulseLens</Link>
        <nav className="nav">
          {LINKS.map(([to, icon, label]) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="content">
        <Outlet />
      </main>

      <footer className="footer">
        Prototype • Not a medical device · <Link to="/about">About &amp; method</Link>
      </footer>
    </div>
  );
}
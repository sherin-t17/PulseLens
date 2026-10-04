import { Link, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Measure from "./pages/Measure.jsx";
import Result from "./pages/Result.jsx";
import History from "./pages/History.jsx";
import Report from "./pages/Report.jsx";
import About from "./pages/About.jsx";

function NotFound() {
  return (
    <div className="card">
      <h2>Page not found</h2>
      <Link to="/" className="btn btn-primary">Go home</Link>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/measure" element={<Measure />} />
        <Route path="/result/:id" element={<Result />} />
        <Route path="/history" element={<History />} />
        <Route path="/report" element={<Report />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
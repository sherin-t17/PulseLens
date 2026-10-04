export default function QualityBadge({ label }) {
  const text = label ? label.charAt(0) + label.slice(1).toLowerCase() : "-";
  return (
    <span className={`badge badge-${(label || "").toLowerCase()}`}>
      Signal Quality: {text}
    </span>
  );
}
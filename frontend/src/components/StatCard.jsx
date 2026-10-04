export default function StatCard({ label, value, unit }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">
        {value ?? "-"}
        {value != null && unit ? <span className="stat-unit"> {unit}</span> : null}
      </div>
    </div>
  );
}
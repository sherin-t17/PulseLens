// A small dependency-free SVG line chart.
// xs/ys: arrays of numbers. markerX: optional vertical dashed line (used for the
// dominant frequency in the spectrum).

export default function LineChart({
  xs, ys, xLabel, yLabel,
  color = "#e11d48", markerX = null, markerLabel = "",
  showDots = false, xDecimals = 1,
}) {
  if (!xs || !ys || xs.length < 2) {
    return <p className="muted">Not enough data to draw a chart yet.</p>;
  }

  const W = 600, H = 240, L = 50, R = 14, T = 14, B = 44;
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  let minY = Math.min(...ys), maxY = Math.max(...ys);
  if (minY === maxY) { minY -= 1; maxY += 1; }
  const pad = (maxY - minY) * 0.08;
  minY -= pad; maxY += pad;

  // Convert data values into pixel positions inside the SVG
  const sx = (x) => L + ((x - minX) / (maxX - minX || 1)) * (W - L - R);
  const sy = (y) => T + (1 - (y - minY) / (maxY - minY)) * (H - T - B);

  const points = xs.map((x, i) => `${sx(x).toFixed(1)},${sy(ys[i]).toFixed(1)}`).join(" ");
  const xTicks = [0, 1, 2, 3, 4].map((i) => minX + (i / 4) * (maxX - minX));
  const yTicks = [0, 1, 2, 3].map((i) => minY + (i / 3) * (maxY - minY));
  const fmtY = (v) => (maxY - minY >= 10 ? v.toFixed(0) : v.toFixed(2));

  const hasMarker = markerX !== null && markerX >= minX && markerX <= maxX;
  const markerOnLeft = hasMarker && sx(markerX) > W - 90;
  const midY = (T + H - B) / 2;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img"
         aria-label={`${yLabel} versus ${xLabel}`}>
      {yTicks.map((v, i) => (
        <g key={"y" + i}>
          <line x1={L} x2={W - R} y1={sy(v)} y2={sy(v)} className="grid" />
          <text x={L - 6} y={sy(v) + 4} textAnchor="end" className="tick">{fmtY(v)}</text>
        </g>
      ))}
      {xTicks.map((v, i) => (
        <text key={"x" + i} x={sx(v)} y={H - B + 16} textAnchor="middle" className="tick">
          {v.toFixed(xDecimals)}
        </text>
      ))}

      <polyline points={points} fill="none" stroke={color} strokeWidth="1.8"
                strokeLinejoin="round" />
      {showDots && xs.map((x, i) => (
        <circle key={i} cx={sx(x)} cy={sy(ys[i])} r="3.5" fill={color} />
      ))}

      {hasMarker && (
        <g>
          <line x1={sx(markerX)} x2={sx(markerX)} y1={T} y2={H - B} className="marker" />
          <text x={sx(markerX) + (markerOnLeft ? -6 : 6)} y={T + 12}
                textAnchor={markerOnLeft ? "end" : "start"} className="marker-label">
            {markerLabel}
          </text>
        </g>
      )}

      <text x={(L + W - R) / 2} y={H - 6} textAnchor="middle" className="axis-label">{xLabel}</text>
      <text transform={`rotate(-90 12 ${midY})`} x="12" y={midY}
            textAnchor="middle" className="axis-label">{yLabel}</text>
    </svg>
  );
}
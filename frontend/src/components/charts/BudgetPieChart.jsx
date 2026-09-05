// Committed vs Achieved donut chart for the Budget Report page.
// Deliberately plain SVG (a single ring built with stroke-dasharray) —
// no charting library, per the hackathon-scope note this file used to
// carry as a TODO. `size` lets the same component work both as the
// small per-row "Progress" indicator and the larger page-level summary.
export default function BudgetPieChart({ committed, achieved, size = 96 }) {
  const committedNum = Number(committed) || 0
  const achievedNum = Number(achieved) || 0
  const pct = committedNum > 0 ? Math.min(achievedNum / committedNum, 1) : 0

  const stroke = Math.max(6, Math.round(size / 7.5))
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const achievedLength = circumference * pct
  const center = size / 2
  const exceeded = committedNum > 0 && achievedNum > committedNum

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={`${Math.round(pct * 100)}% achieved`}
    >
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="var(--color-border)"
        strokeWidth={stroke}
      />
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke={exceeded ? 'var(--color-danger)' : 'var(--color-primary)'}
        strokeWidth={stroke}
        strokeDasharray={`${achievedLength} ${circumference - achievedLength}`}
        strokeLinecap="butt"
        transform={`rotate(-90 ${center} ${center})`}
      />
      {size >= 60 && (
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={size / 5.5}
          fontWeight="700"
          fill="var(--color-text)"
        >
          {Math.round(pct * 100)}%
        </text>
      )}
    </svg>
  )
}

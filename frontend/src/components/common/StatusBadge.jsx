// TODO: color-coded badge for Draft/Confirmed/Posted/Cancelled/Paid/etc.
export default function StatusBadge({ status }) {
  return <span className={`status-badge status-${String(status).toLowerCase()}`}>{status}</span>
}

// Shell for the restricted Contact Portal — deliberately minimal nav
// (no master-data links), since contacts can only view+pay their own docs.
export default function PortalLayout({ children }) {
  return <div className="portal-layout">{children}</div>
}

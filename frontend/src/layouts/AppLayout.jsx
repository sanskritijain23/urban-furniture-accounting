// Shell for authenticated admin/accountant pages: sidebar/topbar with
// Sales/Purchase/Account/Report nav, matching the App Dashboard mockup.
// TODO: wrap page content with <Outlet /> once nested routing is wired.
export default function AppLayout({ children }) {
  return <div className="app-layout">{children}</div>
}

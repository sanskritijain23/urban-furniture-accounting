// Shell for authenticated admin/accountant pages: sidebar/topbar with
// Sales/Purchase/Account/Report nav, matching the App Dashboard mockup.
// Used as a layout route in App.jsx, so page content comes from <Outlet />.
import { Outlet } from 'react-router-dom'
import Sidebar from '../components/layout/Sidebar.jsx'
import Topbar from '../components/layout/Topbar.jsx'

export default function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Topbar />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

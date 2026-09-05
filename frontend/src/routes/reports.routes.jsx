import { Route } from 'react-router-dom'
import BudgetReport from '../pages/reports/BudgetReport.jsx'
import BalanceSheet from '../pages/reports/BalanceSheet.jsx'
import ProfitAndLoss from '../pages/reports/ProfitAndLoss.jsx'
import Ledger from '../pages/reports/Ledger.jsx'

export default [
  <Route key="reports-budget" path="/reports/budget" element={<BudgetReport />} />,
  <Route key="reports-balance-sheet" path="/reports/balance-sheet" element={<BalanceSheet />} />,
  <Route key="reports-pl" path="/reports/profit-loss" element={<ProfitAndLoss />} />,
  <Route key="reports-ledger" path="/reports/ledger" element={<Ledger />} />,
]

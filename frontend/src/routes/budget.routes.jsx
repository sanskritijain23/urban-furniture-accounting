import { Route } from 'react-router-dom'
import AnalyticAccountList from '../pages/budget/AnalyticAccountList.jsx'
import BudgetList from '../pages/budget/BudgetList.jsx'
import BudgetForm from '../pages/budget/BudgetForm.jsx'

export default [
  <Route key="analytics" path="/analytics" element={<AnalyticAccountList />} />,
  <Route key="budgets" path="/budgets" element={<BudgetList />} />,
  <Route key="budget-new" path="/budgets/new" element={<BudgetForm />} />,
  <Route key="budget" path="/budgets/:id" element={<BudgetForm />} />,
]

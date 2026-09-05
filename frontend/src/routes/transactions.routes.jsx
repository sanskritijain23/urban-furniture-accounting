import { Route } from 'react-router-dom'
import JournalEntryList from '../pages/accounting/JournalEntryList.jsx'
import JournalEntryForm from '../pages/accounting/JournalEntryForm.jsx'
import PurchaseOrderList from '../pages/purchases/PurchaseOrderList.jsx'
import PurchaseOrderForm from '../pages/purchases/PurchaseOrderForm.jsx'
import VendorBillForm from '../pages/purchases/VendorBillForm.jsx'
import SalesOrderList from '../pages/sales/SalesOrderList.jsx'
import SalesOrderForm from '../pages/sales/SalesOrderForm.jsx'
import CustomerInvoiceForm from '../pages/sales/CustomerInvoiceForm.jsx'

export default [
  <Route key="journal-entries" path="/journal-entries" element={<JournalEntryList />} />,
  <Route key="journal-entries-new" path="/journal-entries/new" element={<JournalEntryForm />} />,
  <Route key="purchase-orders" path="/purchases/orders" element={<PurchaseOrderList />} />,
  <Route key="purchase-order" path="/purchases/orders/:id" element={<PurchaseOrderForm />} />,
  <Route key="vendor-bill" path="/purchases/bills/:id" element={<VendorBillForm />} />,
  <Route key="sales-orders" path="/sales/orders" element={<SalesOrderList />} />,
  <Route key="sales-order" path="/sales/orders/:id" element={<SalesOrderForm />} />,
  <Route key="customer-invoice" path="/sales/invoices/:id" element={<CustomerInvoiceForm />} />,
]

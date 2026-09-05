import { Route } from 'react-router-dom'
import JournalEntryList from '../pages/accounting/JournalEntryList.jsx'
import JournalEntryForm from '../pages/accounting/JournalEntryForm.jsx'
import JournalEntryDetail from '../pages/accounting/JournalEntryDetail.jsx'
import PaymentList from '../pages/accounting/PaymentList.jsx'
import PurchaseOrderList from '../pages/purchases/PurchaseOrderList.jsx'
import PurchaseOrderForm from '../pages/purchases/PurchaseOrderForm.jsx'
import VendorBillList from '../pages/purchases/VendorBillList.jsx'
import VendorBillForm from '../pages/purchases/VendorBillForm.jsx'
import SalesOrderList from '../pages/sales/SalesOrderList.jsx'
import SalesOrderForm from '../pages/sales/SalesOrderForm.jsx'
import CustomerInvoiceList from '../pages/sales/CustomerInvoiceList.jsx'
import CustomerInvoiceForm from '../pages/sales/CustomerInvoiceForm.jsx'

export default [
  <Route key="journal-entries" path="/journal-entries" element={<JournalEntryList />} />,
  <Route key="journal-entries-new" path="/journal-entries/new" element={<JournalEntryForm />} />,
  <Route key="journal-entry" path="/journal-entries/:id" element={<JournalEntryDetail />} />,
  <Route key="payments" path="/payments" element={<PaymentList />} />,
  <Route key="purchase-orders" path="/purchases/orders" element={<PurchaseOrderList />} />,
  <Route key="purchase-order-new" path="/purchases/orders/new" element={<PurchaseOrderForm />} />,
  <Route key="purchase-order" path="/purchases/orders/:id" element={<PurchaseOrderForm />} />,
  <Route key="vendor-bills" path="/purchases/bills" element={<VendorBillList />} />,
  <Route key="vendor-bill" path="/purchases/bills/:id" element={<VendorBillForm />} />,
  <Route key="sales-orders" path="/sales/orders" element={<SalesOrderList />} />,
  <Route key="sales-order-new" path="/sales/orders/new" element={<SalesOrderForm />} />,
  <Route key="sales-order" path="/sales/orders/:id" element={<SalesOrderForm />} />,
  <Route key="customer-invoices" path="/sales/invoices" element={<CustomerInvoiceList />} />,
  <Route key="customer-invoice" path="/sales/invoices/:id" element={<CustomerInvoiceForm />} />,
]

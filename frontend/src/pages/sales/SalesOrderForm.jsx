// Routes: /sales/orders/new, /sales/orders/:id
//
// /new renders an editable creation form (Customer, SO Date, Reference,
// product/qty/unit-price/analytic-account line grid).
// /:id renders a read-only detail view (no SalesOrder update endpoint
// exists in services/sales.service.js) with:
//   - Confirm button while status is Draft (confirming a Sales Order
//     does NOT create a Journal Entry — see sales.service.js /
//     CustomerInvoiceForm for where accounting actually happens)
//   - Create Customer Invoice button once the SO is Confirmed, opening
//     a small modal (invoice date / due date / reference) that calls
//     createInvoiceFromSO and navigates to the new invoice's detail page.
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import FormField from '../../components/forms/FormField.jsx'
import Button from '../../components/common/Button.jsx'
import Modal from '../../components/common/Modal.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import {
  getSalesOrder,
  createSalesOrder,
  confirmSalesOrder,
  createInvoiceFromSO,
} from '../../services/sales.service.js'
import { listContacts } from '../../services/contact.service.js'
import { listProducts } from '../../services/product.service.js'
import { listAnalyticAccounts } from '../../services/analyticAccount.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

function emptyLine() {
  return { product_id: '', quantity: 1, unit_price: '', analytic_account_id: '' }
}

function lineAmount(line) {
  const qty = Number(line.quantity) || 0
  const price = Number(line.unit_price) || 0
  return qty * price
}

// ---------- Create mode ----------

function SalesOrderCreateForm() {
  const navigate = useNavigate()
  const [customers, setCustomers] = useState([])
  const [products, setProducts] = useState([])
  const [analyticAccounts, setAnalyticAccounts] = useState([])

  const [customerId, setCustomerId] = useState('')
  const [soDate, setSoDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [reference, setReference] = useState('')
  const [lines, setLines] = useState([emptyLine()])

  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    listContacts()
      .then((result) => {
        const customerContacts = (result ?? []).filter((c) =>
          ['customer', 'both'].includes(String(c.type).toLowerCase())
        )
        setCustomers(customerContacts)
      })
      .catch(() => setCustomers([]))
    listProducts().then((result) => setProducts(result ?? [])).catch(() => setProducts([]))
    listAnalyticAccounts()
      .then((result) => setAnalyticAccounts(result ?? []))
      .catch(() => setAnalyticAccounts([]))
  }, [])

  const total = useMemo(() => lines.reduce((sum, l) => sum + lineAmount(l), 0), [lines])

  function updateLine(index, field, value) {
    setLines((prev) => {
      const next = [...prev]
      const line = { ...next[index], [field]: value }
      if (field === 'product_id') {
        const product = products.find((p) => String(p.id) === String(value))
        if (product && (line.unit_price === '' || line.unit_price == null)) {
          line.unit_price = product.sales_price ?? product.cost ?? ''
        }
      }
      next[index] = line
      return next
    })
  }

  function addLine() {
    setLines((prev) => [...prev, emptyLine()])
  }

  function removeLine(index) {
    setLines((prev) => (prev.length === 1 ? prev : prev.filter((_, i) => i !== index)))
  }

  function validate() {
    if (!customerId) return 'Customer is required.'
    if (!soDate) return 'SO date is required.'
    const validLines = lines.filter((l) => l.product_id)
    if (validLines.length === 0) return 'Add at least one product line.'
    for (const l of validLines) {
      if (!l.quantity || Number(l.quantity) <= 0) return 'Each line needs a quantity greater than 0.'
      if (l.unit_price === '' || Number.isNaN(Number(l.unit_price))) return 'Each line needs a unit price.'
    }
    return ''
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }
    setError('')
    setSaving(true)
    const payload = {
      customer_id: customerId,
      so_date: soDate,
      reference: reference || null,
      lines: lines
        .filter((l) => l.product_id)
        .map((l) => ({
          product_id: l.product_id,
          quantity: Number(l.quantity),
          unit_price: Number(l.unit_price),
          analytic_account_id: l.analytic_account_id || null,
        })),
    }
    try {
      const created = await createSalesOrder(payload)
      navigate(created?.id ? `/sales/orders/${created.id}` : '/sales/orders')
    } catch (err) {
      setError(err.message || 'Could not create this sales order.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <PageShell title="New Sales Order" description="Draft a sales order for a customer.">
      <form className="detail-card" onSubmit={handleSubmit} style={{ maxWidth: 760 }}>
        {error && <div className="form-error-banner">{error}</div>}

        <div className="form-row">
          <FormField label="Customer" htmlFor="customer_id">
            <select id="customer_id" value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
              <option value="">Select a customer...</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </FormField>
          <FormField label="SO Date" htmlFor="so_date">
            <input
              id="so_date"
              type="date"
              value={soDate}
              onChange={(e) => setSoDate(e.target.value)}
            />
          </FormField>
        </div>

        <FormField label="Reference (optional)" htmlFor="reference">
          <input
            id="reference"
            type="text"
            value={reference}
            onChange={(e) => setReference(e.target.value)}
          />
        </FormField>

        <table className="line-items-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th>Analytic Account</th>
              <th className="text-right">Amount</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {lines.map((line, i) => (
              <tr key={i}>
                <td>
                  <select
                    value={line.product_id}
                    onChange={(e) => updateLine(i, 'product_id', e.target.value)}
                  >
                    <option value="">Select product...</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </td>
                <td>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={line.quantity}
                    onChange={(e) => updateLine(i, 'quantity', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={line.unit_price}
                    onChange={(e) => updateLine(i, 'unit_price', e.target.value)}
                  />
                </td>
                <td>
                  <select
                    value={line.analytic_account_id}
                    onChange={(e) => updateLine(i, 'analytic_account_id', e.target.value)}
                  >
                    <option value="">None</option>
                    {analyticAccounts.map((a) => (
                      <option key={a.id} value={a.id}>{a.name}</option>
                    ))}
                  </select>
                </td>
                <td className="text-right">{formatCurrency(lineAmount(line))}</td>
                <td>
                  <button
                    type="button"
                    className="link-action danger"
                    onClick={() => removeLine(i)}
                    disabled={lines.length === 1}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
            <tr className="line-items-total-row">
              <td colSpan={4}>
                <button type="button" className="link-action" onClick={addLine}>+ Add line</button>
              </td>
              <td className="text-right">{formatCurrency(total)}</td>
              <td></td>
            </tr>
          </tbody>
        </table>

        <div className="form-actions">
          <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Sales Order'}
          </Button>
          <Link to="/sales/orders"><Button type="button" variant="secondary">Cancel</Button></Link>
        </div>
      </form>
    </PageShell>
  )
}

// ---------- Detail (view) mode ----------

function CreateInvoiceModal({ open, onClose, soId, onCreated }) {
  const [invoiceDate, setInvoiceDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [dueDate, setDueDate] = useState('')
  const [reference, setReference] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleCreate() {
    if (!invoiceDate) {
      setError('Invoice date is required.')
      return
    }
    setError('')
    setSaving(true)
    try {
      const invoice = await createInvoiceFromSO(soId, {
        invoice_date: invoiceDate,
        due_date: dueDate || null,
        reference: reference || null,
      })
      onCreated(invoice)
    } catch (err) {
      setError(err.message || 'Could not create the customer invoice.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose}>
      <h3 style={{ marginTop: 0 }}>Create Customer Invoice</h3>
      {error && <div className="form-error-banner">{error}</div>}
      <FormField label="Invoice Date" htmlFor="invoice_date">
        <input id="invoice_date" type="date" value={invoiceDate} onChange={(e) => setInvoiceDate(e.target.value)} />
      </FormField>
      <FormField label="Due Date (optional)" htmlFor="due_date">
        <input id="due_date" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
      </FormField>
      <FormField label="Invoice Reference (optional)" htmlFor="invoice_reference">
        <input id="invoice_reference" type="text" value={reference} onChange={(e) => setReference(e.target.value)} />
      </FormField>
      <div className="form-actions">
        <Button type="button" onClick={handleCreate} disabled={saving}>
          {saving ? 'Creating...' : 'Create Invoice'}
        </Button>
        <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
      </div>
    </Modal>
  )
}

function SalesOrderDetail({ id }) {
  const navigate = useNavigate()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')
  const [confirming, setConfirming] = useState(false)
  const [invoiceModalOpen, setInvoiceModalOpen] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    getSalesOrder(id)
      .then((result) => { if (!cancelled) setOrder(result) })
      .catch((err) => { if (!cancelled) setError(err.message || 'Could not load this sales order.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id, reloadKey])

  async function handleConfirm() {
    setActionError('')
    setConfirming(true)
    try {
      await confirmSalesOrder(id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not confirm this sales order.')
    } finally {
      setConfirming(false)
    }
  }

  if (loading) {
    return (
      <PageShell title="Sales Order">
        <p className="card-empty">Loading sales order...</p>
      </PageShell>
    )
  }

  if (error) {
    return (
      <PageShell title="Sales Order">
        <div className="form-error-banner">{error}</div>
      </PageShell>
    )
  }

  const status = String(order?.status ?? 'draft').toLowerCase()
  const lines = order?.lines ?? []
  const total = order?.total_amount ?? lines.reduce((sum, l) => sum + Number(l.amount ?? lineAmount(l)), 0)
  const customerName = order?.customer_name ?? order?.customer?.name ?? order?.customer_id
  // Backend response shape for "does this SO already have an invoice" is
  // not confirmed — check the couple of shapes that would make sense
  // (a single linked invoice, or a list of invoices) before offering
  // "Create Customer Invoice".
  const existingInvoiceId =
    order?.invoice_id ?? order?.customer_invoice_id ?? order?.invoices?.[0]?.id ?? order?.invoice?.id ?? null

  return (
    <PageShell
      title={`Sales Order ${order?.reference ? `— ${order.reference}` : `#${order?.id ?? id}`}`}
      actions={<Link to="/sales/orders"><Button variant="secondary">Back to list</Button></Link>}
    >
      {actionError && <div className="form-error-banner">{actionError}</div>}

      <div className="detail-card">
        <div className="detail-grid">
          <div>
            <div className="detail-field-label">Status</div>
            <StatusBadge status={toDisplayLabel(DOC_STATUS_MAP, status)} />
          </div>
          <div>
            <div className="detail-field-label">Customer</div>
            <div className="detail-field-value">{customerName ?? '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">SO Date</div>
            <div className="detail-field-value">{formatDate(order?.so_date ?? order?.order_date)}</div>
          </div>
          <div>
            <div className="detail-field-label">Reference</div>
            <div className="detail-field-value">{order?.reference || '—'}</div>
          </div>
        </div>

        <table className="line-items-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th className="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {lines.length === 0 && (
              <tr><td colSpan={4} className="card-empty">No lines on this sales order.</td></tr>
            )}
            {lines.map((l, i) => (
              <tr key={l.id ?? i}>
                <td>{l.product_name ?? l.product?.name ?? l.product_id}</td>
                <td>{l.quantity}</td>
                <td>{formatCurrency(l.unit_price)}</td>
                <td className="text-right">{formatCurrency(l.amount ?? lineAmount(l))}</td>
              </tr>
            ))}
            <tr className="line-items-total-row">
              <td colSpan={3}>Total</td>
              <td className="text-right">{formatCurrency(total)}</td>
            </tr>
          </tbody>
        </table>

        <div className="form-actions">
          {status === 'draft' && (
            <Button type="button" onClick={handleConfirm} disabled={confirming}>
              {confirming ? 'Confirming...' : 'Confirm'}
            </Button>
          )}
          {status === 'confirmed' && !existingInvoiceId && (
            <Button type="button" onClick={() => setInvoiceModalOpen(true)}>Create Customer Invoice</Button>
          )}
          {existingInvoiceId && (
            <Link to={`/sales/invoices/${existingInvoiceId}`}>
              <Button type="button" variant="secondary">View Customer Invoice</Button>
            </Link>
          )}
        </div>
      </div>

      <CreateInvoiceModal
        open={invoiceModalOpen}
        soId={id}
        onClose={() => setInvoiceModalOpen(false)}
        onCreated={(invoice) => {
          setInvoiceModalOpen(false)
          navigate(invoice?.id ? `/sales/invoices/${invoice.id}` : '/sales/invoices')
        }}
      />
    </PageShell>
  )
}

export default function SalesOrderForm() {
  const { id } = useParams()
  if (!id) return <SalesOrderCreateForm />
  return <SalesOrderDetail id={id} />
}

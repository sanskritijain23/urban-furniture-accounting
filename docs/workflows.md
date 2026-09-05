# Workflows

## User Creation Paths

1. **Admin "Create User" form** (`/admin/users/new`, admin role
   required) — creates a User with role `admin` or `accountant`.
2. **Public Sign-Up** (`/signup`) — always creates role `accountant`,
   regardless of any role field the client might send.
3. **Contact Master creation** (`POST /contacts/`) — auto-creates a
   linked User with role `contact`, giving that person access to the
   restricted Contact Portal only.

## Purchase Flow

```
Purchase Order (Draft)
   |  confirm  -- NO Journal Entry
   v
Purchase Order (Confirmed)
   |  "Create Bill"
   v
Vendor Bill (Draft, pre-filled from PO)
   |  confirm  -- Journal Entry: Debit Purchase Expense / Credit Creditors
   v
Vendor Bill (Confirmed)
   |  "Pay" (amount defaults to Amount Due, editable)
   v
Payment (Confirmed) -- SEPARATE Journal Entry: Debit Creditors / Credit Bank or Cash
```

A non-blocking "exceeds approved budget" warning may appear at PO or
Bill confirmation time if the line's analytic account's actuals would
exceed its Budget's committed_amount. This never blocks the
transaction.

## Sales Flow

```
Sales Order (Draft)
   |  confirm  -- NO Journal Entry
   v
Sales Order (Confirmed)
   |  "Create Invoice"
   v
Customer Invoice (Draft, pre-filled from SO)
   |  confirm  -- Journal Entry: Debit Debtors / Credit Sales Income
   v
Customer Invoice (Confirmed)
   |  "Pay" (amount defaults to Amount Due, editable)
   v
Payment (Confirmed) -- SEPARATE Journal Entry: Debit Bank or Cash / Credit Debtors
```

## Manual Journal Entry (MUST HAVE)

```
User selects Journal + Accounting Date
   |
   v
User enters Account / Partner / Debit / Credit lines
   |
   v
"Post" clicked
   |
   v
BLOCKED if SUM(debit) != SUM(credit)  -- hard validation error
   |
   v
Posted (visible in Journal Entries list)
```

## Budget Lifecycle (MUST HAVE)

```
Draft --confirm--> Confirmed --revise--> [new linked Budget record, status=Confirmed]
                       |                          (original stays linked via revision_of_id)
                       |
                    cancel
                       v
                   Cancelled
```

Achieved Amount / Achieved % / Amount to Achieve are only shown once
a Budget is Confirmed, and are always computed at read time — never
stored.

## Contact Portal Flow

```
Contact logs in (auto-created login from Contact Master)
   |
   v
Sees ONLY their own Customer Invoices / Vendor Bills (read-only)
   |
   v
Clicks "Pay" -> Payment Modal -> confirms payment
   |
   v
Payment (Confirmed) -- creates a Journal Entry, same as the admin/accountant flow
```

Contacts cannot create/edit Contacts, Products, Chart of Accounts,
Journals, Purchase/Sales Orders, or any other master/business record.

## 24-Hour Implementation Priority

### Tier 1 — Must work for demo
- Login + public Signup
- Contact, Product, Chart of Accounts, Journal — CRUD, List view
- Purchase Order -> Vendor Bill (confirm) -> Payment (confirm)
- Sales Order -> Customer Invoice (confirm) -> Payment (confirm)
- Journal Entries list showing auto-generated entries with correct status
- Balance Sheet + Profit & Loss, computed live, year filter

### Tier 2 — Should work
- Manual Journal Entry screen
- Analytic Account + Budget (Draft/Confirm)
- Non-blocking "exceeds budget" warning
- Contact Portal (view + pay)
- Kanban view toggle for Contact/Product/Analytic Account

### Tier 3 — Only if time remains
- Budget Revise workflow with linked records
- Achieved Amount / % / Amount to Achieve computation
- Budget Report pie chart
- PDF export of reports
- Admin "Create User" screen (vs. seeding an admin directly in the DB)
- Real profile image upload (vs. URL placeholder)

## Critical Vertical Demo Flow

Follow the Problem Statement's own worked example (Section 7) exactly:

1. Add Contacts: **Azure Furniture** (vendor), **Nimesh Pathak**
   (customer). Add Product: **Wooden Chair** / **Office Chair**.
2. Create a Purchase Order for Azure Furniture -> convert to Vendor
   Bill -> Confirm (watch the Journal Entry appear: Purchase Expense
   Dr / Creditors Cr) -> Pay via Bank (second Journal Entry: Creditors
   Dr / Bank Cr).
3. Create a Sales Order for Nimesh Pathak, 5 Office Chairs -> generate
   Customer Invoice -> Confirm (Debtors Dr / Sales Income Cr) -> Pay
   (Bank Dr / Debtors Cr).
4. Open Balance Sheet and Profit & Loss — both should reflect the
   transactions just recorded, in real time.

This proves the full stack end-to-end (Frontend -> API -> Service ->
Accounting Engine -> Journal Entry -> Ledger -> Report) using the
exact example from the official spec, so it can be checked
line-by-line against the Problem Statement during judging.

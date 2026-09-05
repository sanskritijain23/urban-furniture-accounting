# Database Design

PostgreSQL, managed via SQLAlchemy models (`backend/app/models/`) and
Alembic migrations (`database/migrations/`).

## Entities

### User
- Purpose: login + role gating (admin / accountant / contact)
- Key fields: login_id (unique, 6-12 chars), email (unique), password_hash, role, contact_id (nullable)
- PK: id | FK: contact_id -> Contact
- Notes: three creation paths — admin "Create User" form (admin/accountant), public signup (accountant only), auto-created on Contact creation (contact)

### Contact
- Purpose: Customer / Vendor / Both master; backs a Contact-role login
- Key fields: name, type, email (unique), mobile, address_city/state/pincode, profile_image_url
- PK: id
- Relationships: 1-many to PurchaseOrder/SalesOrder/VendorBill/CustomerInvoice/Payment/Budget(responsible); 1-1 to User (when role=contact)

### Product / ProductCategory
- Purpose: Goods/Service/Combo master; category is a lightweight, inline-creatable lookup
- Key fields (Product): name, type, sales_price, cost, category_id
- Key fields (ProductCategory): name (unique)
- PK: id (each) | FK: Product.category_id -> ProductCategory

### Account (Chart of Accounts)
- Purpose: ledger classification bucket, feeds every JournalEntryLine
- Key fields: name (unique), type (Asset/Liability/Bank/Cash/Capital/Income/Expenses/Other Expenses), status (Draft/Confirmed/Archived)
- PK: id
- Notes: pre-seeded (see `database/seed/seed_data.py`)

### Journal
- Purpose: groups transaction types (Sales/Purchase/Bank/Cash), carries a Default Account
- Key fields: name, type, default_account_id
- PK: id | FK: default_account_id -> Account

### JournalEntry / JournalEntryLine
- Purpose: the centralized accounting record (only written by accounting_engine.py)
- JournalEntry fields: journal_id, accounting_date, status (Draft/Posted/Cancelled), source_type (manual/vendor_bill/customer_invoice/payment), source_id, reference_no
- JournalEntryLine fields: journal_entry_id, account_id, partner_id (nullable), debit, credit
- PK: id (each) | FK: JournalEntry.journal_id -> Journal; JournalEntryLine.journal_entry_id -> JournalEntry, account_id -> Account, partner_id -> Contact
- Constraint: SUM(debit) == SUM(credit) across a JournalEntry's lines before it can be Posted (enforced in accounting_engine.py, not a DB-level constraint since it spans multiple rows)

### PurchaseOrder / PurchaseOrderLine
- Purpose: vendor commitment, NO accounting impact
- PurchaseOrder fields: po_no (auto, unique), vendor_id, po_date, status (Draft/Confirmed/Cancelled)
- PurchaseOrderLine fields: product_id, analytic_account_id (nullable), qty, unit_price, total
- PK: id (each) | FK: vendor_id -> Contact; line.product_id -> Product, line.analytic_account_id -> AnalyticAccount

### VendorBill / VendorBillLine
- Purpose: triggers a Journal Entry on confirmation (Debit Purchase Expense / Credit Creditors)
- VendorBill fields: bill_no (auto, unique), reference (free text), vendor_id, purchase_order_id (nullable), bill_date, due_date, status, payment_status
- VendorBillLine fields: product_id, account_id (defaults to Purchase Expense), analytic_account_id (nullable), qty, unit_price, total
- PK: id (each) | FK: vendor_id -> Contact, purchase_order_id -> PurchaseOrder; line.product_id -> Product, line.account_id -> Account, line.analytic_account_id -> AnalyticAccount

### SalesOrder / SalesOrderLine
- Purpose: customer commitment, NO accounting impact
- SalesOrder fields: so_no (auto, unique), customer_id, so_date, status
- SalesOrderLine fields: product_id, analytic_account_id (nullable), qty, unit_price, total
- PK: id (each) | FK: customer_id -> Contact; line.product_id -> Product, line.analytic_account_id -> AnalyticAccount

### CustomerInvoice / CustomerInvoiceLine
- Purpose: triggers a Journal Entry on confirmation (Debit Debtors / Credit Sales Income)
- CustomerInvoice fields: invoice_no (auto, unique), reference (free text), customer_id, sales_order_id (nullable), invoice_date, due_date, status, payment_status
- CustomerInvoiceLine fields: product_id, account_id (defaults to Sales Income), analytic_account_id (nullable), qty, unit_price, total
- PK: id (each) | FK: customer_id -> Contact, sales_order_id -> SalesOrder; line.product_id -> Product, line.account_id -> Account, line.analytic_account_id -> AnalyticAccount

### Payment
- Purpose: settles a VendorBill or CustomerInvoice; ALWAYS creates its own separate Journal Entry
- Key fields: payment_type (Send/Receive), payment_via (Cash/Bank), date, partner_id, amount, note, status, source_type (VendorBill/CustomerInvoice), source_id
- PK: id | FK: partner_id -> Contact; source_id -> VendorBill or CustomerInvoice (polymorphic, no formal FK constraint since it can point to either table)

### AnalyticAccount
- Purpose: financial marker for grouping income/expense by project/department; assigned per LINE ITEM on PO/SO/Bill/Invoice
- Key fields: name (unique), type (Income/Expense)
- PK: id
- Relationships: 1-many to Budget; referenced by every *Line table

### Budget
- Purpose: planned vs actual tracking, with a revisable lifecycle
- Key fields: name, period_start, period_end, responsible_id (nullable), analytic_account_id, committed_amount, status (Draft/Confirmed/Revised/Cancelled), revision_of_id (self-referential, nullable)
- PK: id | FK: responsible_id -> Contact, analytic_account_id -> AnalyticAccount, revision_of_id -> Budget
- Computed (NOT stored): achieved_amount, achieved_percentage, amount_to_achieve — derived at read-time by `budget_service.compute_achieved()` from CustomerInvoiceLine/VendorBillLine rows sharing the same analytic_account_id within the budget's period

## Not Included

No `InventoryStock` / `StockMovement` table — the PS mentions "stock
reports" once in its overview, but no screen, field, or workflow in
the MVP supports a standalone inventory module. Treat "stock reports"
as covered by the Balance Sheet / P&L outputs.

## Module Dependency Order

```
Auth
  |
  +--> Contact, Product, Chart of Accounts, Journal   (masters, independent of each other)
         |
         +--> Purchase Order --> Vendor Bill --> Payment
         +--> Sales Order    --> Customer Invoice --> Payment
                |
                v
         Accounting Engine (writes Journal Entries for Bill/Invoice/Payment confirmations)
                |
                v
              Ledger
                |
       +--------+--------+
       v                 v
  Balance Sheet /     Budget Report
      P&L          (also needs AnalyticAccount + Budget)
```

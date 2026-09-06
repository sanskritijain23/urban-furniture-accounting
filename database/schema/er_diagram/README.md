# Entity Relationship Diagram

```mermaid
erDiagram

    CONTACTS {
        int id PK
        string name
        enum type
        string email UK
        string mobile
        string address_city
        string address_state
        string address_pincode
        string profile_image_url
    }

    USERS {
        int id PK
        string login_id UK
        string email UK
        string password_hash
        enum role
        int contact_id FK
    }

    PRODUCT_CATEGORIES {
        int id PK
        string name UK
    }

    PRODUCTS {
        int id PK
        string name
        enum type
        decimal sales_price
        decimal cost
        int category_id FK
    }

    ACCOUNTS {
        int id PK
        string name UK
        enum type
        enum status
    }

    JOURNALS {
        int id PK
        string name
        enum type
        int default_account_id FK
    }

    JOURNAL_ENTRIES {
        int id PK
        int journal_id FK
        date accounting_date
        enum status
        enum source_type
        int source_id
        string reference_no
    }

    JOURNAL_ENTRY_LINES {
        int id PK
        int journal_entry_id FK
        int account_id FK
        int partner_id FK
        decimal debit
        decimal credit
    }

    ANALYTIC_ACCOUNTS {
        int id PK
        string name UK
        enum type
    }

    SALES_ORDERS {
        int id PK
        string so_no UK
        int customer_id FK
        date so_date
        enum status
    }

    SALES_ORDER_LINES {
        int id PK
        int sales_order_id FK
        int product_id FK
        int analytic_account_id FK
        decimal qty
        decimal unit_price
        decimal total
    }

    PURCHASE_ORDERS {
        int id PK
        string po_no UK
        int vendor_id FK
        date po_date
        enum status
    }

    PURCHASE_ORDER_LINES {
        int id PK
        int purchase_order_id FK
        int product_id FK
        int analytic_account_id FK
        decimal qty
        decimal unit_price
        decimal total
    }

    VENDOR_BILLS {
        int id PK
        string bill_no UK
        string reference
        int vendor_id FK
        int purchase_order_id FK
        date bill_date
        date due_date
        enum status
        enum payment_status
    }

    VENDOR_BILL_LINES {
        int id PK
        int vendor_bill_id FK
        int product_id FK
        int account_id FK
        int analytic_account_id FK
        decimal qty
        decimal unit_price
        decimal total
    }

    CUSTOMER_INVOICES {
        int id PK
        string invoice_no UK
        string reference
        int customer_id FK
        int sales_order_id FK
        date invoice_date
        date due_date
        enum status
        enum payment_status
    }

    CUSTOMER_INVOICE_LINES {
        int id PK
        int customer_invoice_id FK
        int product_id FK
        int account_id FK
        int analytic_account_id FK
        decimal qty
        decimal unit_price
        decimal total
    }

    PAYMENTS {
        int id PK
        enum payment_type
        enum payment_via
        date date
        int partner_id FK
        decimal amount
        string note
        enum status
        enum source_type
        int source_id
    }

    BUDGETS {
        int id PK
        string name
        date period_start
        date period_end
        int responsible_id FK
        int analytic_account_id FK
        decimal committed_amount
        enum status
        int revision_of_id FK
    }


    CONTACTS ||--o| USERS : "has"

    PRODUCT_CATEGORIES ||--o{ PRODUCTS : "contains"

    CONTACTS ||--o{ SALES_ORDERS : "customer"
    SALES_ORDERS ||--|{ SALES_ORDER_LINES : "contains"
    PRODUCTS ||--o{ SALES_ORDER_LINES : "product"
    ANALYTIC_ACCOUNTS ||--o{ SALES_ORDER_LINES : "analytic"

    CONTACTS ||--o{ PURCHASE_ORDERS : "vendor"
    PURCHASE_ORDERS ||--|{ PURCHASE_ORDER_LINES : "contains"
    PRODUCTS ||--o{ PURCHASE_ORDER_LINES : "product"
    ANALYTIC_ACCOUNTS ||--o{ PURCHASE_ORDER_LINES : "analytic"

    CONTACTS ||--o{ VENDOR_BILLS : "vendor"
    PURCHASE_ORDERS ||--o| VENDOR_BILLS : "creates"
    VENDOR_BILLS ||--|{ VENDOR_BILL_LINES : "contains"
    PRODUCTS ||--o{ VENDOR_BILL_LINES : "product"
    ACCOUNTS ||--o{ VENDOR_BILL_LINES : "account"
    ANALYTIC_ACCOUNTS ||--o{ VENDOR_BILL_LINES : "analytic"

    CONTACTS ||--o{ CUSTOMER_INVOICES : "customer"
    SALES_ORDERS ||--o| CUSTOMER_INVOICES : "creates"
    CUSTOMER_INVOICES ||--|{ CUSTOMER_INVOICE_LINES : "contains"
    PRODUCTS ||--o{ CUSTOMER_INVOICE_LINES : "product"
    ACCOUNTS ||--o{ CUSTOMER_INVOICE_LINES : "account"
    ANALYTIC_ACCOUNTS ||--o{ CUSTOMER_INVOICE_LINES : "analytic"

    CONTACTS ||--o{ PAYMENTS : "partner"

    ACCOUNTS ||--o{ JOURNALS : "default_account"
    JOURNALS ||--o{ JOURNAL_ENTRIES : "contains"
    JOURNAL_ENTRIES ||--|{ JOURNAL_ENTRY_LINES : "contains"
    ACCOUNTS ||--o{ JOURNAL_ENTRY_LINES : "account"
    CONTACTS ||--o{ JOURNAL_ENTRY_LINES : "partner"

    CONTACTS ||--o{ BUDGETS : "responsible"
    ANALYTIC_ACCOUNTS ||--o{ BUDGETS : "tracks"
    BUDGETS ||--o{ BUDGETS : "revised_from"
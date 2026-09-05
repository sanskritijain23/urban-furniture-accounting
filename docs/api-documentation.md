# API Documentation

Base URL: `http://localhost:8000/api/v1`

All routes are currently placeholders (`raise NotImplementedError`)
— this document describes the intended contract for the team to
implement against.

## Auth (`/auth`)
| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Login with `login_id` + `password`, returns a JWT |
| POST | `/auth/signup` | Public signup — always creates role=accountant |

## Users (`/users`) — admin only
| Method | Path | Description |
|---|---|---|
| POST | `/users/` | Admin-only create user (role: admin or accountant) |
| GET | `/users/` | List users |

## Contacts (`/contacts`)
| Method | Path | Description |
|---|---|---|
| GET | `/contacts/` | List contacts (backs both List and Kanban views) |
| POST | `/contacts/` | Create contact — may auto-create a linked User(role=contact) |
| GET | `/contacts/{id}` | Get one contact |
| PUT | `/contacts/{id}` | Update contact |

## Products (`/products`)
| Method | Path | Description |
|---|---|---|
| GET | `/products/` | List products |
| POST | `/products/` | Create product |
| GET | `/products/{id}` | Get one product |
| PUT | `/products/{id}` | Update product |
| POST | `/products/categories` | Inline-create a category |
| GET | `/products/categories` | List categories |

## Chart of Accounts (`/accounts`)
| Method | Path | Description |
|---|---|---|
| GET | `/accounts/` | List accounts |
| POST | `/accounts/` | Create account |
| PUT | `/accounts/{id}` | Update account (incl. Confirm/Archive status) |

## Journals (`/journals`)
| Method | Path | Description |
|---|---|---|
| GET | `/journals/` | List journals |
| POST | `/journals/` | Create journal |

## Journal Entries (`/journal-entries`)
| Method | Path | Description |
|---|---|---|
| GET | `/journal-entries/` | List all entries (manual + auto-generated) |
| GET | `/journal-entries/{id}` | Get one entry |
| POST | `/journal-entries/` | Create a manual entry (Draft) |
| POST | `/journal-entries/{id}/post` | Post an entry — blocks if debit != credit |

## Purchase Orders (`/purchase-orders`)
| Method | Path | Description |
|---|---|---|
| GET | `/purchase-orders/` | List POs |
| POST | `/purchase-orders/` | Create PO |
| GET | `/purchase-orders/{id}` | Get one PO |
| POST | `/purchase-orders/{id}/confirm` | Confirm — no accounting entry created |
| POST | `/purchase-orders/{id}/create-bill` | Create a Vendor Bill from this PO |

## Vendor Bills (`/vendor-bills`)
| Method | Path | Description |
|---|---|---|
| GET | `/vendor-bills/` | List bills |
| GET | `/vendor-bills/{id}` | Get one bill |
| POST | `/vendor-bills/{id}/confirm` | Confirm — creates a Journal Entry |
| POST | `/vendor-bills/{id}/pay` | Register a payment — creates a separate Journal Entry |

## Sales Orders (`/sales-orders`)
| Method | Path | Description |
|---|---|---|
| GET | `/sales-orders/` | List SOs |
| POST | `/sales-orders/` | Create SO |
| GET | `/sales-orders/{id}` | Get one SO |
| POST | `/sales-orders/{id}/confirm` | Confirm — no accounting entry created |
| POST | `/sales-orders/{id}/create-invoice` | Create a Customer Invoice from this SO |

## Customer Invoices (`/customer-invoices`)
| Method | Path | Description |
|---|---|---|
| GET | `/customer-invoices/` | List invoices |
| GET | `/customer-invoices/{id}` | Get one invoice |
| POST | `/customer-invoices/{id}/confirm` | Confirm — creates a Journal Entry |
| POST | `/customer-invoices/{id}/pay` | Register a payment — creates a separate Journal Entry |

## Payments (`/payments`)
| Method | Path | Description |
|---|---|---|
| GET | `/payments/` | List payments |
| GET | `/payments/{id}` | Get one payment |
| POST | `/payments/{id}/confirm` | Confirm — creates a Journal Entry |

## Analytic Accounts (`/analytic-accounts`)
| Method | Path | Description |
|---|---|---|
| GET | `/analytic-accounts/` | List (backs List + Kanban views) |
| POST | `/analytic-accounts/` | Create |

## Budgets (`/budgets`)
| Method | Path | Description |
|---|---|---|
| GET | `/budgets/` | List budgets |
| POST | `/budgets/` | Create budget (Draft) |
| GET | `/budgets/{id}` | Get one budget, incl. computed achieved fields if Confirmed |
| POST | `/budgets/{id}/confirm` | Confirm |
| POST | `/budgets/{id}/revise` | Creates a NEW linked budget record |
| POST | `/budgets/{id}/cancel` | Cancel |

## Reports (`/reports`)
| Method | Path | Description |
|---|---|---|
| GET | `/reports/balance-sheet?year=` | Balance Sheet for the given year |
| GET | `/reports/profit-loss?year=` | Profit & Loss for the given year |
| GET | `/reports/budget?year=` | Budget Report for the given year |

## Auth Header

All routes except `/auth/login` and `/auth/signup` require:
```
Authorization: Bearer <token>
```

## Contact Portal

The Contact Portal (`/portal` on the frontend) does not have its own
dedicated backend module — it consumes the existing
`/customer-invoices/`, `/vendor-bills/`, and `/payments/` endpoints,
scoped server-side to the logged-in contact's own `partner_id`/
`customer_id`/`vendor_id`. Contacts never get access to create/update
endpoints for master data.

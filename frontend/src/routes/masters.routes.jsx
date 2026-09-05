import { Route } from 'react-router-dom'
import ContactList from '../pages/masters/contacts/ContactList.jsx'
import ContactForm from '../pages/masters/contacts/ContactForm.jsx'
import ProductList from '../pages/masters/products/ProductList.jsx'
import ProductForm from '../pages/masters/products/ProductForm.jsx'
import ProductCategoryList from '../pages/masters/products/ProductCategoryList.jsx'
import AccountList from '../pages/masters/chart-of-accounts/AccountList.jsx'
import JournalList from '../pages/masters/journals/JournalList.jsx'

export default [
  <Route key="contacts" path="/contacts" element={<ContactList />} />,
  <Route key="contacts-new" path="/contacts/new" element={<ContactForm />} />,
  <Route key="contacts-edit" path="/contacts/:id" element={<ContactForm />} />,
  <Route key="products" path="/products" element={<ProductList />} />,
  <Route key="products-new" path="/products/new" element={<ProductForm />} />,
  <Route key="products-categories" path="/products/categories" element={<ProductCategoryList />} />,
  <Route key="products-edit" path="/products/:id" element={<ProductForm />} />,
  <Route key="accounts" path="/accounts" element={<AccountList />} />,
  <Route key="journals" path="/journals" element={<JournalList />} />,
]

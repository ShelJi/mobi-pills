Create a full-stack Mobile Shop Sales & Billing Web Application using Django (backend) and HTML, CSS, JavaScript (frontend).

The application should be production-ready, responsive, and optimized for both desktop and mobile usage.

Core Requirements:

1. Authentication System:
- User login/logout (admin/staff roles)
- Secure authentication using Django built-in auth
- Role-based access (admin can manage everything, staff limited to billing)

2. Dashboard:
- Show total sales (daily, weekly, monthly)
- Display recent transactions
- Low stock alerts
- Quick actions (Add Product, New Bill)

3. Product Management:
- Add, edit, delete products
- Fields: product name, brand, IMEI (optional), price, stock quantity, category
- Image upload support
- Search and filter products
- Stock tracking with alerts

4. Billing System:
- Create new bill with multiple products
- Auto calculation of total, tax (GST), discount
- Generate invoice number automatically
- Print/download invoice (PDF)
- Add customer details (name, phone)

5. Sales Management:
- View all transactions
- Filter by date, customer, product
- Daily and monthly reports
- Export reports (CSV/PDF)

6. UI/UX:
- Use modern responsive design (prefer Tailwind CSS)
- Clean dashboard layout
- Fast and smooth interactions using JavaScript (AJAX/fetch)
- Mobile-friendly billing interface

7. Backend (Django):
- Use Django REST Framework for APIs
- Models: Product, Customer, Order, OrderItem, User
- Use serializers and API views

8. Additional Features:
- Dark mode toggle
- Notifications for low stock
- Auto-save draft bills

10. Deployment Ready:
- Environment variables support
- Static and media file handling

Deliverables:
- Complete Django project structure
- Frontend templates and static files
- Sample data
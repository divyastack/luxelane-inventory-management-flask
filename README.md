# 👗 Fashion Store Inventory Management System

A complete inventory + billing system built with Flask, MySQL, and a dark modern UI.

---

## 🗂 Project Structure

```
fashion_inventory/
├── app.py                   # Flask app (all routes)
├── database.sql             # Database schema + sample data
├── requirements.txt         # Python dependencies
├── static/css/
│   └── style.css            # Dark fashion UI stylesheet
└── templates/
    ├── base.html            # Shared sidebar layout
    ├── login.html           # Login page
    ├── dashboard.html       # Dashboard with category cards
    ├── categories.html      # Category list
    ├── add_category.html    # Add category form
    ├── products.html        # Product list with filter
    ├── add_product.html     # Add product form
    ├── edit_product.html    # Edit product form
    ├── billing.html         # Invoice list
    ├── new_bill.html        # Create new invoice (with live calculation)
    └── view_bill.html       # View / print GST invoice
```

---

## ⚡ Quick Start (WAMP)

### 1. Set up the database
- Open phpMyAdmin → SQL tab
- Paste the full contents of `database.sql` → Click Go
- Database `fashion_inventory` will be created automatically

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Gmail credentials in app.py
```python
GMAIL_ADDRESS  = "your_email@gmail.com"
GMAIL_APP_PASS = "xxxx xxxx xxxx xxxx"   # App Password
```

### 4. Update your store info in app.py
```python
STORE_NAME       = "Your Store Name"
STORE_ADDRESS    = "Your Address"
STORE_PHONE      = "+91 XXXXX XXXXX"
STORE_GST_NUMBER = "Your GST Number"
```

### 5. Run the app
```bash
python app.py
```
Open → **http://127.0.0.1:5000**
Login → **admin / admin123**

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Login | Session-based authentication |
| 📊 Dashboard | Stats, category overview, low-stock alerts |
| 🏷️ Categories | 8 fashion categories with emoji icons |
| 👗 Products | Full CRUD with SKU, size, color, category |
| 🔍 Search | Filter by name and category |
| ⚠️ Alerts | Email alert when stock < 5 units |
| 🧾 Billing | GST invoice with customer details |
| 💰 Live Calc | Real-time subtotal, GST, grand total |
| 🖨️ Print | Print-ready invoice layout |
| ↓ Export | CSV export of all products |

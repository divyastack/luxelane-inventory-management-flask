"""
Fashion Store Inventory Management System
Flask + MySQL | Gmail Alerts | GST Billing
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
import mysql.connector
import csv, io, smtplib, threading, random, string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fashion_store_secret_2024"

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
GMAIL_ADDRESS       = "yourgmail@gmail.com"    # ← your Gmail
GMAIL_APP_PASS      = "xxxx xxxx xxxx"     # ← App Password
ALERT_RECIPIENT     = "yourgmail8@gmail.com"    # ← alert recipient

STORE_NAME          = "LuxeLane Fashion Store"
STORE_ADDRESS       = "18,Roja Street, Lakshmi Nagar, Virudhunagar - 626001"
STORE_PHONE         = "+91 6381584343"
STORE_GST_NUMBER    = "33AAAAA0000A1Z5"         # ← your GST number
DEFAULT_GST_RATE    = 5.0                       # fashion items = 5% GST

# UPI Payment Details — fill these in!
UPI_ID              = "divya@upi"            # ← your UPI ID (e.g. divya@okaxis)
UPI_PHONE           = "987654321"              # ← your UPI linked phone number
UPI_NAME            = "LuxeLane Fashion Store"     # ← name shown on UPI payment screen

LOW_STOCK_THRESHOLD = 5

# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fashion_inventory"
    )

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def generate_invoice_number():
    """Generate unique invoice number like INV-20240507-AB12"""
    date_part = datetime.now().strftime("%Y%m%d")
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"INV-{date_part}-{rand_part}"

# ─────────────────────────────────────────────
#  EMAIL ALERT
# ─────────────────────────────────────────────
def send_email_alert(low_stock_items):
    try:
        subject = f"⚠ Low Stock Alert — {STORE_NAME}"
        rows = "".join(
            f"<tr><td style='padding:8px;border:1px solid #ddd'>{p['name']}</td>"
            f"<td style='padding:8px;border:1px solid #ddd'>{p['category_name']}</td>"
            f"<td style='padding:8px;border:1px solid #ddd;color:red'><b>{p['quantity']}</b></td>"
            f"<td style='padding:8px;border:1px solid #ddd'>₹{p['price']:.2f}</td></tr>"
            for p in low_stock_items
        )
        html = f"""<html><body style="font-family:Arial,sans-serif;padding:20px">
          <h2 style="color:#e74c3c">⚠ Low Stock Alert — {STORE_NAME}</h2>
          <p>The following products have dropped below <b>{LOW_STOCK_THRESHOLD} units</b>:</p>
          <table style="border-collapse:collapse;width:100%">
            <thead><tr style="background:#f0f0f0">
              <th style="padding:8px;border:1px solid #ddd;text-align:left">Product</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:left">Category</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:left">Qty</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:left">Price</th>
            </tr></thead>
            <tbody>{rows}</tbody>
          </table>
          <p style="color:#888;font-size:13px;margin-top:20px">— {STORE_NAME} Inventory System</p>
        </body></html>"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = ALERT_RECIPIENT
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            s.sendmail(GMAIL_ADDRESS, ALERT_RECIPIENT, msg.as_string())
        print(f"[Email] Alert sent for {len(low_stock_items)} item(s).")
    except Exception as e:
        print(f"[Email] Failed: {e}")

def trigger_alerts(new_quantity):
    if new_quantity >= LOW_STOCK_THRESHOLD:
        return
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.name, p.quantity, p.price, c.name AS category_name
        FROM products p JOIN categories c ON p.category_id = c.id
        WHERE p.quantity < %s ORDER BY p.quantity ASC
    """, (LOW_STOCK_THRESHOLD,))
    low_items = cursor.fetchall()
    cursor.close(); db.close()
    if low_items:
        threading.Thread(target=send_email_alert, args=(low_items,), daemon=True).start()

# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close(); db.close()
        if user:
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html", store_name=STORE_NAME)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM products")
    total_products = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(quantity),0) AS total FROM products")
    total_stock = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM bills")
    total_bills = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(total),0) AS total FROM bills")
    total_revenue = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT p.*, c.name AS category_name, c.icon
        FROM products p JOIN categories c ON p.category_id = c.id
        WHERE p.quantity < %s ORDER BY p.quantity ASC
    """, (LOW_STOCK_THRESHOLD,))
    low_stock = cursor.fetchall()

    # Category-wise product count and stock
    cursor.execute("""
        SELECT c.id, c.name, c.icon,
               COUNT(p.id) AS product_count,
               COALESCE(SUM(p.quantity),0) AS total_stock,
               COALESCE(SUM(CASE WHEN p.quantity < %s THEN 1 ELSE 0 END),0) AS low_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id, c.name, c.icon
        ORDER BY c.name
    """, (LOW_STOCK_THRESHOLD,))
    categories = cursor.fetchall()

    # Recent bills
    cursor.execute("SELECT * FROM bills ORDER BY created_at DESC LIMIT 5")
    recent_bills = cursor.fetchall()

    cursor.close(); db.close()
    return render_template("dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        total_bills=total_bills,
        total_revenue=total_revenue,
        low_stock=low_stock,
        categories=categories,
        recent_bills=recent_bills,
        threshold=LOW_STOCK_THRESHOLD,
        store_name=STORE_NAME,
    )

# ─────────────────────────────────────────────
#  CATEGORIES
# ─────────────────────────────────────────────
@app.route("/categories")
@login_required
def category_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, COUNT(p.id) AS product_count,
               COALESCE(SUM(p.quantity),0) AS total_stock
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id ORDER BY c.name
    """)
    cats = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("categories.html", categories=cats, store_name=STORE_NAME)

@app.route("/categories/add", methods=["GET","POST"])
@login_required
def add_category():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        desc = request.form.get("description","").strip()
        icon = request.form.get("icon","🏷️").strip()
        if not name:
            flash("Category name is required.", "error")
            return redirect(url_for("add_category"))
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO categories (name,description,icon) VALUES (%s,%s,%s)",
                           (name, desc, icon))
            db.commit()
            flash(f'Category "{name}" added!', "success")
        except:
            flash("Category name already exists.", "error")
        cursor.close(); db.close()
        return redirect(url_for("category_list"))
    return render_template("add_category.html", store_name=STORE_NAME)

@app.route("/categories/delete/<int:cat_id>", methods=["POST"])
@login_required
def delete_category(cat_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS c FROM products WHERE category_id=%s", (cat_id,))
    if cursor.fetchone()["c"] > 0:
        flash("Cannot delete category with products. Remove products first.", "error")
    else:
        cursor.execute("DELETE FROM categories WHERE id=%s", (cat_id,))
        db.commit()
        flash("Category deleted.", "success")
    cursor.close(); db.close()
    return redirect(url_for("category_list"))

# ─────────────────────────────────────────────
#  PRODUCTS
# ─────────────────────────────────────────────
@app.route("/products")
@login_required
def products():
    search   = request.args.get("search","").strip()
    cat_id   = request.args.get("category","")
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """SELECT p.*, c.name AS category_name, c.icon
               FROM products p JOIN categories c ON p.category_id=c.id WHERE 1=1"""
    params = []
    if search:
        query += " AND p.name LIKE %s"
        params.append(f"%{search}%")
    if cat_id:
        query += " AND p.category_id = %s"
        params.append(cat_id)
    query += " ORDER BY c.name, p.name"
    cursor.execute(query, params)
    items = cursor.fetchall()

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("products.html", products=items, categories=categories,
                           search=search, selected_cat=cat_id,
                           threshold=LOW_STOCK_THRESHOLD, store_name=STORE_NAME)

@app.route("/products/add", methods=["GET","POST"])
@login_required
def add_product():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    if request.method == "POST":
        name     = request.form.get("name","").strip()
        cat_id   = request.form.get("category_id")
        price    = request.form.get("price","0")
        quantity = request.form.get("quantity","0")
        size     = request.form.get("size","Free Size").strip()
        color    = request.form.get("color","").strip()
        sku      = request.form.get("sku","").strip()
        qty = int(quantity)

        cursor2 = db.cursor()
        cursor2.execute(
            "INSERT INTO products (name,category_id,price,quantity,size,color,sku) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (name, cat_id, float(price), qty, size, color, sku)
        )
        db.commit()
        cursor2.close(); cursor.close(); db.close()

        trigger_alerts(qty)
        flash(f'Product "{name}" added!', "success")
        if qty < LOW_STOCK_THRESHOLD:
            flash(f'⚠ "{name}" has low stock. Email alert sent!', "warning")
        return redirect(url_for("products"))

    cursor.close(); db.close()
    return render_template("add_product.html", categories=categories, store_name=STORE_NAME)

@app.route("/products/edit/<int:pid>", methods=["GET","POST"])
@login_required
def edit_product(pid):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    if request.method == "POST":
        name     = request.form.get("name","").strip()
        cat_id   = request.form.get("category_id")
        price    = request.form.get("price","0")
        quantity = request.form.get("quantity","0")
        size     = request.form.get("size","").strip()
        color    = request.form.get("color","").strip()
        sku      = request.form.get("sku","").strip()
        qty = int(quantity)

        cursor.execute(
            "UPDATE products SET name=%s,category_id=%s,price=%s,quantity=%s,size=%s,color=%s,sku=%s WHERE id=%s",
            (name, cat_id, float(price), qty, size, color, sku, pid)
        )
        db.commit(); cursor.close(); db.close()
        trigger_alerts(qty)
        flash(f'Product "{name}" updated!', "success")
        if qty < LOW_STOCK_THRESHOLD:
            flash(f'⚠ "{name}" is now low stock. Email alert sent!', "warning")
        return redirect(url_for("products"))

    cursor.execute("SELECT * FROM products WHERE id=%s", (pid,))
    product = cursor.fetchone()
    cursor.close(); db.close()
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products"))
    return render_template("edit_product.html", product=product, categories=categories,
                           store_name=STORE_NAME)

@app.route("/products/delete/<int:pid>", methods=["POST"])
@login_required
def delete_product(pid):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name FROM products WHERE id=%s", (pid,))
    p = cursor.fetchone()
    if p:
        cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
        db.commit()
        flash(f'Product "{p["name"]}" deleted.', "success")
    cursor.close(); db.close()
    return redirect(url_for("products"))

@app.route("/products/export")
@login_required
def export_csv():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""SELECT p.id,p.name,c.name AS category,p.price,p.quantity,
                             p.size,p.color,p.sku,p.created_at
                      FROM products p JOIN categories c ON p.category_id=c.id ORDER BY c.name,p.name""")
    items = cursor.fetchall()
    cursor.close(); db.close()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id","name","category","price","quantity","size","color","sku","created_at"])
    writer.writeheader()
    writer.writerows(items)
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=products.csv"})

# ─────────────────────────────────────────────
#  BILLING
# ─────────────────────────────────────────────
@app.route("/billing")
@login_required
def billing():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bills ORDER BY created_at DESC")
    bills = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("billing.html", bills=bills, store_name=STORE_NAME)

@app.route("/billing/new", methods=["GET","POST"])
@login_required
def new_bill():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""SELECT p.*, c.name AS category_name FROM products p
                      JOIN categories c ON p.category_id=c.id
                      WHERE p.quantity > 0 ORDER BY c.name, p.name""")
    products_list = cursor.fetchall()

    if request.method == "POST":
        customer_name    = request.form.get("customer_name","").strip()
        customer_phone   = request.form.get("customer_phone","").strip()
        customer_email   = request.form.get("customer_email","").strip()
        customer_address = request.form.get("customer_address","").strip()
        gst_rate         = float(request.form.get("gst_rate", DEFAULT_GST_RATE))
        discount         = float(request.form.get("discount", 0))
        payment_method   = request.form.get("payment_method","Cash")

        product_ids = request.form.getlist("product_id[]")
        quantities  = request.form.getlist("qty[]")

        if not customer_name or not product_ids:
            flash("Customer name and at least one product are required.", "error")
            cursor.close(); db.close()
            return render_template("new_bill.html", products=products_list,
                                   store_name=STORE_NAME, gst_rate=DEFAULT_GST_RATE)

        # Calculate totals — convert Decimal to float to avoid TypeError
        subtotal = 0.0
        bill_items = []
        for pid, qty_str in zip(product_ids, quantities):
            qty = int(qty_str)
            if qty <= 0:
                continue
            cursor.execute("SELECT * FROM products WHERE id=%s", (pid,))
            prod = cursor.fetchone()
            if prod:
                unit_price = float(prod["price"])   # Decimal -> float
                line_total = unit_price * qty
                subtotal  += line_total
                bill_items.append({
                    "product_id":   prod["id"],
                    "product_name": prod["name"],
                    "quantity":     qty,
                    "unit_price":   unit_price,
                    "total_price":  line_total
                })

        subtotal   = round(subtotal, 2)
        gst_amount = round((subtotal - discount) * gst_rate / 100, 2)
        total      = round(subtotal - discount + gst_amount, 2)
        invoice_no = generate_invoice_number()

        # Insert bill
        cursor2 = db.cursor()
        cursor2.execute("""INSERT INTO bills
            (invoice_number,customer_name,customer_phone,customer_email,customer_address,
             subtotal,gst_rate,gst_amount,discount,total,payment_method,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Paid')""",
            (invoice_no, customer_name, customer_phone, customer_email,
             customer_address, subtotal, gst_rate, gst_amount, discount, total, payment_method))
        bill_id = cursor2.lastrowid

        # Insert items and deduct stock
        for item in bill_items:
            cursor2.execute("""INSERT INTO bill_items
                (bill_id,product_id,product_name,quantity,unit_price,total_price)
                VALUES (%s,%s,%s,%s,%s,%s)""",
                (bill_id, item["product_id"], item["product_name"],
                 item["quantity"], item["unit_price"], item["total_price"]))
            cursor2.execute("UPDATE products SET quantity=quantity-%s WHERE id=%s",
                           (item["quantity"], item["product_id"]))
            # Check for low stock after sale
            cursor.execute("SELECT quantity FROM products WHERE id=%s", (item["product_id"],))
            new_qty = cursor.fetchone()["quantity"]
            trigger_alerts(new_qty)

        db.commit()
        cursor2.close(); cursor.close(); db.close()
        flash(f"Invoice {invoice_no} created successfully!", "success")
        return redirect(url_for("view_bill", bill_id=bill_id))

    cursor.close(); db.close()
    return render_template("new_bill.html", products=products_list,
                           store_name=STORE_NAME, gst_rate=DEFAULT_GST_RATE,
                           upi_id=UPI_ID, upi_phone=UPI_PHONE, upi_name=UPI_NAME)

@app.route("/billing/<int:bill_id>")
@login_required
def view_bill(bill_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bills WHERE id=%s", (bill_id,))
    bill = cursor.fetchone()
    if not bill:
        flash("Invoice not found.", "error")
        return redirect(url_for("billing"))
    cursor.execute("SELECT * FROM bill_items WHERE bill_id=%s", (bill_id,))
    items = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("view_bill.html", bill=bill, items=items,
                           store_name=STORE_NAME, store_address=STORE_ADDRESS,
                           store_phone=STORE_PHONE, store_gst=STORE_GST_NUMBER,
                           store_upi_id=UPI_ID, store_upi_name=UPI_NAME)

@app.route("/billing/delete/<int:bill_id>", methods=["POST"])
@login_required
def delete_bill(bill_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM bills WHERE id=%s", (bill_id,))
    db.commit()
    cursor.close(); db.close()
    flash("Invoice deleted.", "success")
    return redirect(url_for("billing"))

# ─────────────────────────────────────────────
#  API — get product price for billing JS
# ─────────────────────────────────────────────
@app.route("/api/product/<int:pid>")
@login_required
def api_product(pid):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id,name,price,quantity FROM products WHERE id=%s", (pid,))
    p = cursor.fetchone()
    cursor.close(); db.close()
    if p:
        return jsonify(p)
    return jsonify({}), 404

# ─────────────────────────────────────────────
#  MANUAL ALERT
# ─────────────────────────────────────────────
@app.route("/alerts/send", methods=["POST"])
@login_required
def send_alerts_now():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""SELECT p.name, p.quantity, p.price, c.name AS category_name
                      FROM products p JOIN categories c ON p.category_id=c.id
                      WHERE p.quantity < %s ORDER BY p.quantity ASC""", (LOW_STOCK_THRESHOLD,))
    low_items = cursor.fetchall()
    cursor.close(); db.close()
    if not low_items:
        flash("No low-stock products. No alert sent.", "info")
    else:
        threading.Thread(target=send_email_alert, args=(low_items,), daemon=True).start()
        flash(f"✓ Email alert sent for {len(low_items)} low-stock item(s)!", "success")
    return redirect(url_for("dashboard"))

# ─────────────────────────────────────────────
#  UPI QR DATA API
# ─────────────────────────────────────────────
@app.route("/api/upi-string")
@login_required
def upi_string():
    """Return UPI payment string for QR generation."""
    amount = request.args.get("amount", "0")
    invoice = request.args.get("invoice", "")
    # Standard UPI deep link format
    upi_url = (
        f"upi://pay?pa={UPI_ID}"
        f"&pn={UPI_NAME.replace(' ', '%20')}"
        f"&am={amount}"
        f"&cu=INR"
        f"&tn=Invoice%20{invoice}"
    )
    from flask import jsonify
    return jsonify({
        "upi_url": upi_url,
        "upi_id": UPI_ID,
        "upi_phone": UPI_PHONE,
        "upi_name": UPI_NAME,
        "amount": amount,
        "invoice": invoice
    })

if __name__ == "__main__":
    app.run(debug=True)

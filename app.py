from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from models import db, User, Product, StockTransaction, Supplier

app = Flask(__name__)

app.secret_key = "inventory-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            return redirect(url_for("dashboard"))

        else:
            error = "Invalid username or password"

    return render_template(
        "login.html",
        error=error
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    products = Product.query.all()

    total_products = Product.query.count()

    total_stock = sum(
        product.quantity for product in products
    )

    low_stock_list = [
        product for product in products
        if product.quantity <= 5
    ]

    low_stock_products = len(low_stock_list)

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock_products=low_stock_products,
        low_stock_list=low_stock_list
    )


# ---------------- INVENTORY ----------------

@app.route("/inventory")
def inventory():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    if search:

        products = Product.query.filter(
            Product.name.ilike(f"%{search}%")
        ).all()

    else:

        products = Product.query.all()

    return render_template(
        "inventory.html",
        products=products,
        search=search
    )


# ---------------- ADD PRODUCT ----------------

@app.route("/add-product", methods=["GET", "POST"])
def add_product():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]

        product = Product(
            name=name,
            quantity=int(quantity),
            price=float(price)
        )

        db.session.add(product)
        db.session.commit()

        return redirect(url_for("inventory"))

    return render_template("add_product.html")


# ---------------- EDIT PRODUCT ----------------

@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    product = db.session.get(Product, id)

    if product is None:
        return "Product not found"

    if request.method == "POST":

        product.name = request.form["name"]
        product.quantity = int(request.form["quantity"])
        product.price = float(request.form["price"])

        db.session.commit()

        return redirect(url_for("inventory"))

    return render_template(
        "edit_product.html",
        product=product
    )


# ---------------- DELETE PRODUCT ----------------

@app.route("/delete-product/<int:id>")
def delete_product(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    product = db.session.get(Product, id)

    if product:

        db.session.delete(product)
        db.session.commit()

    return redirect(url_for("inventory"))


# ---------------- STOCK IN / STOCK OUT ----------------

@app.route("/stock", methods=["GET", "POST"])
def stock():

    if "user_id" not in session:
        return redirect(url_for("login"))

    products = Product.query.all()

    error = None

    if request.method == "POST":

        product_id = int(request.form["product_id"])
        transaction_type = request.form["transaction_type"]
        quantity = int(request.form["quantity"])

        product = db.session.get(Product, product_id)

        if product is None:

            error = "Product not found"

        elif quantity <= 0:

            error = "Quantity must be greater than 0"

        elif transaction_type == "OUT" and quantity > product.quantity:

            error = "Not enough stock available"

        elif transaction_type not in ["IN", "OUT"]:

            error = "Invalid transaction type"

        else:

            if transaction_type == "IN":
                product.quantity += quantity

            elif transaction_type == "OUT":
                product.quantity -= quantity

            transaction = StockTransaction(
                product_id=product.id,
                transaction_type=transaction_type,
                quantity=quantity
            )

            db.session.add(transaction)

            db.session.commit()

            return redirect(url_for("inventory"))

    return render_template(
        "stock.html",
        products=products,
        error=error
    )


# ---------------- SUPPLIERS ----------------

@app.route("/suppliers", methods=["GET", "POST"])
def suppliers():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"]
        contact = request.form["contact"]
        email = request.form["email"]

        supplier = Supplier(
            name=name,
            contact=contact,
            email=email
        )

        db.session.add(supplier)
        db.session.commit()

        return redirect(url_for("suppliers"))

    suppliers = Supplier.query.all()

    return render_template(
        "suppliers.html",
        suppliers=suppliers
    )


# ---------------- STOCK HISTORY ----------------

@app.route("/stock-history")
def stock_history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    transactions = StockTransaction.query.order_by(
        StockTransaction.id.desc()
    ).all()

    return render_template(
        "stock_history.html",
        transactions=transactions
    )


# ---------------- REPORTS ----------------

@app.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect(url_for("login"))

    products = Product.query.all()

    total_products = Product.query.count()

    total_stock = sum(
        product.quantity for product in products
    )

    total_stock_in = sum(
        transaction.quantity
        for transaction in StockTransaction.query.filter_by(
            transaction_type="IN"
        ).all()
    )

    total_stock_out = sum(
        transaction.quantity
        for transaction in StockTransaction.query.filter_by(
            transaction_type="OUT"
        ).all()
    )

    low_stock_products = sum(
        1 for product in products
        if product.quantity <= 5
    )

    return render_template(
        "reports.html",
        products=products,
        total_products=total_products,
        total_stock=total_stock,
        total_stock_in=total_stock_in,
        total_stock_out=total_stock_out,
        low_stock_products=low_stock_products
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
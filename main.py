from flask import Flask, render_template
from database import get_db_connection
from flask import request

app = Flask(__name__, static_url_path="/src", static_folder="src")

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/catalog", methods=["GET"])
def catalog():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()
    return render_template(
        "catalog.html", catalog=data
    )


@app.route("/add_item", methods=["POST"])
def add_item():
    title = request.form["title"]
    description = request.form["description"]
    try:
        price = float(request.form["price"])
    except ValueError:
        return "Введено неправильний формат ціни", 400

    image_url = request.form["image_url"]
    category = request.form["category"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (title, description, price, image_url, category) VALUES (?, ?, ?, ?, ?)",
        (title, description, price, image_url, category),
    )
    conn.commit()
    conn.close()
    return render_template("add_item.html"), 201

# Сортування за категорією
@app.route("/sort_by_category", methods=["GET"])
def sort_by_category():
    category = request.args.get("category", None)

    conn = get_db_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()
    return render_template("catalog.html", catalog=data)


# Сортування за ціною
@app.route("/sort_by_price", methods=["GET"])
def sort_by_price():
    order_direction = request.args.get("order", "ASC")

    if order_direction not in ["ASC", "DESC"]:
        order_direction = "ASC"

    conn = get_db_connection()
    cursor = conn.cursor()

    sql_query = f"SELECT * FROM products ORDER BY price {order_direction}"

    cursor.execute(sql_query)

    data = cursor.fetchall()
    conn.close()

    return render_template("catalog.html", catalog=data)


@app.route("/remove_item/<int:id>", methods=["POST"])
def remove_item(id):
    item_id = id

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return render_template("remove_item.html"), 200


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html"), 404

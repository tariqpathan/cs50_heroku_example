import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("postgres://cezodtnwmyvbhz:8155b6c6a9070c6b49ab1734425f4ed3d6d2b8d75a273faf4299ba8ac4ff64ca@ec2-176-34-183-20.eu-west-1.compute.amazonaws.com:5432/d2s1ov8hnefscj")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    rows = db.execute("SELECT * FROM owned WHERE user_id = :user_id", user_id=session["user_id"])
    user_data = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
    cash = user_data[0]["cash"]
    total_assets = cash

    # Obtain data from IEX and update dictionary
    for row in rows:
        stock_data = lookup(row["symbol"])
        row["name"] = (stock_data["name"])
        row["price"] = (stock_data["price"])
        value = float(stock_data["price"]) * float(row["shares"])
        row["value"] = (value)
        total_assets += value
    return render_template("index.html", rows=rows, cash=cash, total_assets=total_assets)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        stock_data = lookup(request.form.get("symbol"))
        if not str.isdigit(request.form.get("shares")):
            return apology("Numeb", 400)
        else:
            shares = int(request.form.get("shares"))

        if not stock_data:
            return apology("Check symbol", 400)

        if (shares < 1) or (shares % 1 != 0):
            return apology("Check number", 400)

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        stock_cost = float(stock_data["price"]) * float(request.form.get("shares"))

        if rows[0]["cash"] < stock_cost:
            return apology("Ya pleb", 400)

        else:
            new_cash = rows[0]["cash"] - stock_cost

            # Change users table and set new cash amount
            db.execute("UPDATE OR ABORT users SET cash = :cash WHERE id = :id",
                       cash=new_cash, id=session["user_id"])

            # Add transaction to ledger
            db.execute("INSERT INTO transactions (user_id, symbol, bought, amount, shares)"
                       " VALUES (:user_id, :symbol, 1, :amount, :shares)",
                       user_id=session["user_id"], symbol=stock_data["symbol"], amount=stock_cost,
                       shares=int(request.form.get("shares")))

            # Update owned table - not using SQL to do this because UPSERT not available in v3.22
            result = db.execute("UPDATE OR ABORT owned SET shares = shares + :new_shares"
                                " WHERE user_id = :user_id AND symbol = :symbol",
                                user_id=session["user_id"], symbol=stock_data["symbol"],
                                new_shares=int(request.form.get("shares")))

            # Insert a new entry into owned table if update fails
            if not result:
                db.execute("INSERT INTO owned (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)",
                           user_id=session["user_id"], symbol=stock_data["symbol"],
                           shares=request.form.get("shares"))

            return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    username = request.args.get("username")
    registered_users = db.execute("SELECT * FROM users WHERE username = :username",
                                  username=username)

    if (len(username) > 0 and not registered_users):
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    rows = db.execute("SELECT * FROM transactions WHERE user_id = :user_id ORDER BY Timestamp ASC",
                      user_id=session["user_id"])
    for row in rows:
        stock_data = lookup(row["symbol"])
        row["name"] = (stock_data["name"])
        row["price"] = (float(row["amount"]) / float(row["shares"]))
        if row["bought"] == 1:
            row["bought"] = "Buy"
        else:
            row["bought"] = "Sell"

    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        stock_data = lookup(request.form.get("symbol"))
        if not stock_data:
            return apology("Try again loser", 400)

        return render_template("quoted.html", stock=stock_data)

    elif request.method == "GET":
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget user_id
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("username", 400)

        elif not request.form.get("password"):
            return apology("password", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords must match", 400)

        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                            username=request.form.get("username"),
                            hash=generate_password_hash(request.form.get("password")))

        # Return error if username is duplicate
        if not result:
            return apology("Username taken", 400)

        # Get the new users id
        user_row = db.execute("SELECT id FROM users WHERE username = :username",
                              username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = user_row[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET method (by clicking register)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "GET":
        """
        Get data on which stocks a user owns.
        Pass that data into the form
        """
        rows = db.execute("SELECT * FROM owned WHERE user_id = :user_id", user_id=session["user_id"])

        if not rows:
            return apology("You own nothing", 400)

        # Obtain data from IEX and update dictionary
        for row in rows:
            stock_data = lookup(row["symbol"])
            row["name"] = (stock_data["name"])
            row["price"] = (stock_data["price"])

        return render_template("sell.html", rows=rows)

    elif request.method == "POST":

        # Getting data to verify stock owned by user
        selling_stock = db.execute("SELECT * FROM owned WHERE user_id = :user_id AND symbol = :symbol",
                                   user_id=session["user_id"], symbol=request.form.get("symbol"))

        print(request.form.get("shares"))
        if selling_stock[0]["shares"] < int(request.form.get("shares")):
            return apology("Theif", 400)

        # Need to get cash to add to user once we sell stock
        user_data = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        cash = user_data[0]["cash"]

        stock_data = lookup(request.form.get("symbol"))
        sold_stock_value = float(stock_data["price"]) * float(request.form.get("shares"))

        # Change users table and set new cash amount
        db.execute("UPDATE OR ABORT users SET cash = cash + :sold WHERE id = :id",
                   sold=sold_stock_value, id=session["user_id"])

        # Add transaction to ledger
        db.execute("INSERT INTO transactions (user_id, symbol, bought, amount, shares)"
                   " VALUES (:user_id, :symbol, 0, :amount, :shares)",
                   user_id=session["user_id"], symbol=stock_data["symbol"], amount=sold_stock_value,
                   shares=int(request.form.get("shares")))

        # Update owned table - not using SQL to do this because UPSERT not available in v3.22
        db.execute("UPDATE OR ABORT owned SET shares = shares - :new_shares"
                   " WHERE user_id = :user_id AND symbol = :symbol",
                   user_id=session["user_id"], symbol=stock_data["symbol"],
                   new_shares=int(request.form.get("shares")))

        # Cleanup owned table to remove instances where shares = 0
        db.execute("DELETE FROM owned WHERE user_id = :user_id AND shares = 0",
                   user_id=session["user_id"])

        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

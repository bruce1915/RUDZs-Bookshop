from flask import Flask, render_template, request, session, redirect, flash
import json
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from q import run
from datetime import datetime
import math
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import pymysql
import random
import bcrypt

with open("config.json", "r") as c:
    params = json.load(c)["params"]

app = Flask(__name__)

app.secret_key = "super-secret-key"
# app.config['UPLOAD_FOLDER'] = params['upload_location']

app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME="brucethomaswayne1915@gmail.com",
    MAIL_PASSWORD="ksoz qsde qypk doyg",
)
mail = Mail(app)

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root@localhost/bookstore"
app.jinja_env.globals.update(getattr=getattr)
db = SQLAlchemy(app)

# migrate = Migrate(app, db)
location, os_info = run()
# db.init_app(app)


class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(500), nullable=False)
    pw = db.Column(db.String(70), nullable=False)
    date = db.Column(db.String(100), nullable=True)


class Stationary(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(1000), nullable=False)
    img_file = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(100), nullable=True)


class Author(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    dob = db.Column(db.String(100), nullable=False)
    years_active = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(1000), nullable=False)
    bio = db.Column(db.String(5000), nullable=False)
    genres = db.Column(db.String(2500), nullable=False)
    awards = db.Column(db.String(5000), nullable=False)
    date = db.Column(db.Date, nullable=True)


class Publisher(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    logo = db.Column(db.String(1000), nullable=False)
    type = db.Column(db.String(1000), nullable=False)
    iimprints = db.Column(db.String(1500), nullable=False)
    books = db.Column(db.String(5000), nullable=False)
    authors = db.Column(db.String(2000), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    loc = db.Column(db.String(500), nullable=False)
    member_since = db.Column(db.Date, nullable=False)


class Book(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1000), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    author_id = db.Column(db.Integer, nullable=False, index=True)
    total_sells = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(2500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300), nullable=False)
    date = db.Column(db.Date, nullable=True)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    msg = db.Column(db.String(2000), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/")
def home():
    books = Book.query.all()
    total_books = len(books)
    r1 = random.randint(1, int(total_books // 2))
    r2 = random.randint(int(total_books // 2) + 1, total_books)

    b1 = Book.query.get_or_404(r1)
    b2 = Book.query.get_or_404(r2)

    u = session.get("user")
    e = session.get("email")

    if e is None:
        message = f"Someone just landed on your page from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
    else:
        message = f"{e} - {u} just landed on your page from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
    mail.send_message(
        subject="RUDZ Bookstore - Alert!!!",
        sender="brucethomaswayne1915@gmail.com",
        recipients=["uchhas.saha@g.bracu.ac.bd", "debasmita.paul@g.bracu.ac.bd"],
        body=message,
    )

    return render_template("index.html", book1=b1, book2=b2)


@app.route("/search")
def search():
    query = request.args.get("query")
    if not query:
        return redirect("/")

    search_result = Book.query.filter(Book.name.like(f"%{query}%")).all()
    return render_template("search_results.html", books=search_result, query=query)
# SELECT * FROM Book WHERE name LIKE '%query%';


@app.route("/featured")
def featured():
    sort_order = request.args.get("sort")

    if sort_order == "asc":
        featured_books = Book.query.order_by(Book.price.asc()).all()
        #SELECT * FROM book ORDER BY price ASC;
    elif sort_order == "desc":
        featured_books = Book.query.order_by(Book.price.desc()).all()
        #SELECT * FROM book ORDER BY price DESC;
    else:
        featured_books = Book.query.all()
        #SELECT * FROM book;

    return render_template(
        "featured.html", books=featured_books, selected_sort=sort_order)

# @app.route('/featured')
# def featured():
#     featured_books = Book.query.all()
#     return render_template('featured.html', books=featured_books)
# Select*from Book;

@app.route("/popular")
def popular():
    popular_books = Book.query.order_by(Book.total_sells.desc()).limit(3).all()
    return render_template("popular.html", popular_books=popular_books)
# SELECT * FROM Book ORDER BY total_sells DESC LIMIT 3;


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)
# SELECT * FROM Book WHERE id = book_id;

@app.route("/author")
def author():
    authors = Author.query.all()
    return render_template("author.html", authors=authors)


@app.route("/author/<int:sno>")
def author_detail(sno):
    author = Author.query.get_or_404(sno)
    return render_template("author_detail.html", author=author)


@app.route("/publisher")
def publisher():
    p = Publisher.query.all()
    return render_template("publisher.html", pub=p)


@app.route("/publisher/<int:sno>")
def publisher_detail(sno):
    pd = Publisher.query.get_or_404(sno)
    return render_template("publisher_detail.html", pd=pd)


@app.route("/stationary")
def stationary():
    sort_order = request.args.get("sort")

    if sort_order == "asc":
        st = Stationary.query.order_by(Stationary.price.asc()).all()
        #SELECT * FROM stationary ORDER BY price ASC;
    elif sort_order == "desc":
        st = Stationary.query.order_by(Stationary.price.desc()).all()
        #SELECT * FROM stationary ORDER BY price DESC;
    else:
        st = Stationary.query.all()
        #SELECT * FROM stationary;

    return render_template("stationary.html", st=st, selected_sort=sort_order)


@app.route("/wishlist")
def wishlist():
    if "user" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")

    else:
        user_email = User.query.filter_by(email=session["email"]).first().email
        #SELECT email FROM user WHERE email = '<session_email>' LIMIT 1;
        wishlist_items = Wishlist.query.filter_by(user_email=user_email).all()
        #SELECT * FROM wishlist WHERE user_email = '<user_email>';

        detailed_items = []
        for item in wishlist_items:
            if item.product_type == "book":
                product = Book.query.get(item.product_id)
                #SELECT * FROM book WHERE id = <product_id>;
            else:
                product = Stationary.query.get(item.product_id)
                #SELECT * FROM stationary WHERE id = <product_id>;
            detailed_items.append(
                {"item": product, "type": item.product_type, "wishlist_id": item.id}
            )

        return render_template("wishlist.html", items=detailed_items)


@app.route("/add_to_wishlist/<string:product_type>/<int:product_id>")
def add_to_wishlist(product_type, product_id):
    if "user" not in session:
        # flash("Please login first!", "warning")
        return redirect("/login")
    else:
        user_email = User.query.filter_by(email=session["email"]).first().email
        #SELECT email FROM user WHERE email = '<session_email>' LIMIT 1;

        exists = Wishlist.query.filter_by(
            user_email=user_email, product_type=product_type, product_id=product_id
        ).first()
        #SELECT * FROM wishlist WHERE user_email = '<user_email>' AND product_type = '<product_type>' AND product_id = <product_id> LIMIT 1;
        if exists:
            flash("Already in Wishlist!", "warning")
        else:
            wishlist_item = Wishlist(
                user_email=user_email, product_type=product_type, product_id=product_id
            )
            db.session.add(wishlist_item)
            db.session.commit()
            #INSERT INTO wishlist (user_email, product_type, product_id, date_added) VALUES ('<user_email>', '<product_type>', <product_id>, NOW());
            flash("Added to Wishlist!", "success")

        return redirect(request.referrer)


@app.route("/remove_from_wishlist/<int:wishlist_id>")
def remove_from_wishlist(wishlist_id):
    if "user" in session:
        item = Wishlist.query.get_or_404(wishlist_id)
        #SELECT * FROM wishlist WHERE id = <wishlist_id> LIMIT 1;
        db.session.delete(item)
        #DELETE FROM wishlist WHERE id = <wishlist_id>;
        db.session.commit()
        flash("Removed from Wishlist!", "success")
    return redirect("/wishlist")


# Hashing function
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["pass"]

        user = User.query.filter_by(email=email).first()
        if user:
            if verify_password(password, user.pw):
                session["user"] = user.name
                session["email"] = user.email
                message = f"{user.name} - {user.email}, logged in the bookstore from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
                mail.send_message(
                    subject="RUDZ Bookstore - Alert!!!",
                    sender="brucethomaswayne1915@gmail.com",
                    recipients=[
                        "uchhas.saha@g.bracu.ac.bd",
                        "debasmita.paul@g.bracu.ac.bd",
                    ],
                    body=message,
                )
                return redirect("/")
            else:
                flash("Invalid Password!!!", "warning")
                message = f"{email} is trying to log in the bookstore with password: {password}, from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
                mail.send_message(
                    subject="RUDZ Bookstore - Alert!!!",
                    sender="brucethomaswayne1915@gmail.com",
                    recipients=[
                        "uchhas.saha@g.bracu.ac.bd",
                        "debasmita.paul@g.bracu.ac.bd",
                    ],
                    body=message,
                )

        else:
            flash("User don't exist or wrong email!!!", "warning")
            message = f"{email} with password: {password} failed to log in the bookstore from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
            mail.send_message(
                subject="RUDZ Bookstore - Alert!!!",
                sender="brucethomaswayne1915@gmail.com",
                recipients=[
                    "uchhas.saha@g.bracu.ac.bd",
                    "debasmita.paul@g.bracu.ac.bd",
                ],
                body=message,
            )
            return redirect("/login")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("pass")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists. Please use a different one.", "danger")
            return redirect("/signup")
        else:
            p = hash_password(password)
            entry = User(name=name, email=email, pw=p, date=datetime.now())
            db.session.add(entry)
            db.session.commit()
            session["user"] = name
            session["email"] = email
            message = f"{email} {user} created an account to log in the bookstore from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
            mail.send_message(
                subject="RUDZ Bookstore - Alert!!!",
                sender="brucethomaswayne1915@gmail.com",
                recipients=[
                    "uchhas.saha@g.bracu.ac.bd",
                    "debasmita.paul@g.bracu.ac.bd",
                ],
                body=message,
            )
            return redirect("/")

    return render_template("signup.html")


@app.route("/forgotpass", methods=["GET", "POST"])
def forgotpass():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            code = str(random.randint(100000, 999999))
            session["reset_code"] = code
            session["reset_email"] = email

            message = f"Your password reset code is: {code}"
            mail.send_message(
                subject="RUDZ Bookstore - Password Reset Code",
                sender="brucethomaswayne1915@gmail.com",
                recipients=[email],
                body=message,
            )
            flash("A reset code has been sent to your email.", "success")
            return redirect("/verifycode")
        else:
            flash("Email not found.", "danger")
            return redirect("/forgotpass")
    return render_template("forgotpass.html")


@app.route("/verifycode", methods=["GET", "POST"])
def verifycode():
    if request.method == "POST":
        code = request.form.get("code")
        if code == session.get("reset_code"):
            flash("Code verified. You can now reset your password.", "success")
            return redirect("/resetpass")
        else:
            flash("Invalid code. Please try again.", "danger")
            return redirect("/verifycode")
    return render_template("verifycode.html")


@app.route("/resetpass", methods=["GET", "POST"])
def resetpass():
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("New password did not match with confirmation.", "danger")
            return redirect("/resetpass")

        email = session.get("reset_email")
        if not email:
            flash("Session expired or invalid access.", "danger")
            return redirect("/forgotpass")

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User not found.", "danger")
            return redirect("/forgotpass")

        user.pw = hash_password(new_password)
        db.session.commit()
        flash("Password changed successfully.", "success")
        return redirect("/login")

    return render_template("resetpass.html")


@app.route("/profile")
def profile():
    if "user" not in session:
        flash("Login first!!", "warning")
        return redirect("/login")

    e = session.get("email")
    u = User.query.filter_by(email=e).first()
    return render_template("profile.html", user=u)


@app.route("/cngpassword", methods=["GET", "POST"])
def cngpassword():
    if "user" not in session:
        flash("Login first!!", "warning")
        return redirect("/login")

    email = session.get("email")
    user = User.query.filter_by(email=email).first()

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not verify_password(current_password, user.pw):
            flash("Current password is incorrect!", "error")
            return redirect("/cngpassword")

        if new_password != confirm_password:
            flash("New password and confirmation do not match!", "error")
            return redirect("/cngpassword")

        user.pw = hash_password(new_password)
        db.session.commit()
        flash("Password changed successfully!", "success")
        return redirect("/profile")

    return render_template("cngpassword.html")


@app.route("/admin", methods=["GET", "POST"])
def dashboard():
    if "user" in session and session["user"] == params["admin_user"]:
        # post = Posts.query.all()
        message = f"{session['user']} landed on the bookstore admin panel from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
        mail.send_message(
            subject="RUDZ Bookstore - Alert!!!",
            sender="brucethomaswayne1915@gmail.com",
            recipients=["uchhas.saha@g.bracu.ac.bd", "debasmita.paul@g.bracu.ac.bd"],
            body=message,
        )

        return render_template("dashboard.html", params=params)

    if request.method == "POST":
        useremail = request.form.get("email")
        userpass = request.form.get("pass")

        if useremail == params["admin_user"] and userpass == params["admin_pass"]:
            session["user"] = useremail
            # post = Posts.query.all()
            message = f"{session['user']} is trying to log in the bookstore admin panel from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
            mail.send_message(
                subject="RUDZ Bookstore - Alert!!!",
                sender="brucethomaswayne1915@gmail.com",
                recipients=[
                    "uchhas.saha@g.bracu.ac.bd",
                    "debasmita.paul@g.bracu.ac.bd",
                ],
                body=message,
            )
            return render_template("dashboard.html", params=params)
        else:
            message = f"{useremail} failed to log in the bookstore admin panel with password: {userpass} from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
            mail.send_message(
                subject="RUDZ Bookstore - Alert!!!",
                sender="brucethomaswayne1915@gmail.com",
                recipients=[
                    "uchhas.saha@g.bracu.ac.bd",
                    "debasmita.paul@g.bracu.ac.bd",
                ],
                body=message,
            )
            return redirect("/admin")

    else:
        return render_template("admin.html", params=params)





@app.route("/logout")
def logout():
    message = f"{session['user']} logged out from the bookstore from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
    mail.send_message(
        subject="RUDZ Bookstore - Alert!!!",
        sender="brucethomaswayne1915@gmail.com",
        recipients=["uchhas.saha@g.bracu.ac.bd", "debasmita.paul@g.bracu.ac.bd"],
        body=message,
    )
    session.pop("user")
    # session.pop("email")
    flash("Logged out successfully!!!", "success")
    return redirect("/")


@app.route('/admin/<string:table>/edit/<int:sno>', methods=['GET', 'POST'])
def edit_item(table, sno):
    store = {"books": Book,"authors": Author,"publishers": Publisher,"stationaries": Stationary,"contacts": Contact}

    if table in store:
        model = store[table]
        item = model.query.filter_by(sno=sno).first()
        if request.method == 'POST':
            for j in model.__table__.columns:
                up_value = request.form.get(j.name) #update value
                if up_value:
                    setattr(item, j.name, up_value)

           
            db.session.commit()

            
            return redirect(f'/admin/{table}')

        return render_template('edit.html', items=item, t=table.upper(), sno=sno)
    else:
        return render_template('404.html')


@app.route("/admin/<string:table>/delete/<int:sno>")
def delete_item(table, sno):
    store = {
        "books": Book,
        "authors": Author,
        "publishers": Publisher,
        "stationaries": Stationary,
        "contacts": Contact,
    }

    if "user" in session and session["user"] == params["admin_user"]:
        if table in store:
            model = store[table]
            items = model.query.filter_by(sno=sno).first()
            db.session.delete(items)  # deletion code
            db.session.commit()
            return redirect(f"/admin/{table}")

        else:
            return render_template("404.html")


@app.route('/admin/<string:table>/add', methods=['GET', 'POST'])
def add_item(table):
    store = {"books": Book,"authors": Author,"publishers": Publisher,"stationaries": Stationary,"contacts": Contact}
    #use dictionary 
    if table in store:
        model = store[table]
        new_item = model() #empty obj
        if request.method == 'POST':
            for i in model.__table__.columns:
                new_value = request.form.get(i.name)
                if new_value:
                    setattr(new_item, i.name, new_value)
            db.session.add(new_item)
            db.session.commit() 
            
            return redirect(f'/admin/{table}')  

        return render_template('add.html', item=new_item, t=table.upper())  
    else:
        return render_template('404.html')



@app.route("/offer")
def offer():
    txt1 = "Why do u need offer to read books bro. 😎"
    txt2 = "Remember, money can't buy u intelligence. 🧠"
    txt3 = "Konolege izzz weasdom!!!🤘🏻"
    img = "static/images/meme offer.jpg"
    return render_template("meme.html", t1=txt1, t2=txt2, image_url=img)
    # return render_template('subscribe.html')


@app.route("/career")
def career():
    txt1 = "Man we're the one who need a job. 😢"
    txt2 = "Give us a job peleg.🙏🏻"
    txt3 = "SKills: I can print hello world in python 😎"
    img = "static/images/meme job.jpg"
    return render_template("meme.html", t1=txt1, t2=txt2, t3=txt3, image_url=img)


@app.route("/articles")
def articles():
    txt1 = "We're on it!!! ✍🏻"
    txt2 = "I'll write an article on....💥 HOW TO OVERCOME THE POPULATION PROBLEM IN THE WORLD 💥"
    txt3 = "First get, make or steal a bo... 👮🏻🚨🚔"
    img = "static/images/meme articles.png"
    return render_template("meme.html", t1=txt1, t2=txt2, t3=txt3, image_url=img)


@app.route("/vision")
def vision():
    txt1 = "I don't know about others, but"
    txt2 = "I, Uchhas Saha have a vision 😀"
    txt3 = "One day I will own an animal farm & live peacefully with them 🐏"
    img = "static/images/meme vision.jpg"
    return render_template("meme.html", t1=txt1, t2=txt2, t3=txt3, image_url=img)


@app.route("/terms")
def terms():
    txt1 = "What do u think we're Facebook 🤨"
    txt2 = "We don't steal data 😎 🦇"
    txt3 = "We simply swap your data with our books. Books give u infos. And u give us info. ✌🏻"
    img = "static/images/meme terms.png"
    return render_template("meme.html", t1=txt1, t2=txt2, t3=txt3, image_url=img)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        entry = Contact(name=name, email=email, msg=message, date=datetime.now())

        db.session.add(entry)
        db.session.commit()

        mail.send_message(
            "New message from " + name,
            sender=email,
            recipients=["brucethomaswayne1915@gmail.com"],
            body=message,
        )

        flash("Thanks for your feedback. We'll get back to u soon!", "success")
    return render_template("contact.html", params=params)

@app.route("/admin/<string:table>")
def adminView(table):
    store = {
        "books": Book,
        "authors": Author,
        "publishers": Publisher,
        "stationaries": Stationary,
        "contacts": Contact,
    }
    message = f"{session['user']} is viewing the {table} admin panel from\nFormatted Location Info:\n{location}\n\nUsing an OS of \n{os_info}"
    mail.send_message(
        subject="RUDZ Bookstore - Alert!!!",
        sender="brucethomaswayne1915@gmail.com",
        recipients=["uchhas.saha@g.bracu.ac.bd", "debasmita.paul@g.bracu.ac.bd"],
        body=message,
    )

    if table in store:
        model = store[table]
        items = model.query.all()
        return render_template("table.html", items=items, t=table.upper())

    else:
        return render_template("404.html")
@app.route("/working")
def working():
    return render_template("working.html")


@app.route("/test")
def test():
    return render_template("test.html")


if (__name__) == "__main__":
    app.run(debug=False, port=8000)

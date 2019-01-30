import os
import hashlib
import requests
import json
from flask import Flask, session, render_template, request, url_for, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():
   return render_template("index.html")


@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        username = request.form.get("username")
        email=request.form.get("email")
        user_password=request.form.get("password")
        salt="5gz"
        db_password = user_password+salt
        h=hashlib.md5(db_password.encode())
        h=h.hexdigest()
        result = db.execute(f"SELECT * FROM users WHERE username= '{username}'").fetchall()
        if len(result)>0:
            flash("Account Already Exists. Please Log In to continue")
            return redirect(url_for("login"))
        db.execute("INSERT INTO users(username, email, password) VALUES (:username, :email, :password)",{"username":username, "email":email, "password":h})
        db.commit()
        flash("Successfully Registered. Please Log In to Continue")
        return redirect(url_for("index"))


@app.route("/search", methods=["GET", "POST"])
def search():
    username = session.get("username")
    if not username:
        return redirect(url_for(login))
    if request.method == "GET":
        return render_template("search.html")
    else:
        val = request.form.get("search")
        result = db.execute("SELECT * FROM books WHERE isbn ILIKE '%"+val+"%' OR title ILIKE '%"+val+"%' OR author ILIKE '%"+val+"%' ").fetchall()
        if len(result)==0:
            flash("No data found. Please search something else")
            return redirect(url_for(search))
        session["books"]=[]
        for book in result:
            session["books"].append(book)
        return render_template("results.html", books  = session["books"])
        
@app.route("/book/<string:isbn>", methods=["POST", "GET"])
def book(isbn):
    username = session.get("username")
    checkreview = db.execute("SELECT review FROM reviews WHERE isbn=:isbn AND username = :username",{"isbn":isbn,"username":username}).fetchall()
    bookdetails = db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn})
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "GlrgX5sln0VtDindBgTSHQ", "isbns": isbn})
    average_rating = res.json()['books'][0]['average_rating']
    work_ratings_count = res.json()['books'][0]['work_ratings_count']
    if request.method == "GET":
        return render_template("book.html", bookdetails=bookdetails, review = checkreview ,average_rating = average_rating, work_ratings_count = work_ratings_count)
    session["review"]=""
    if request.method == "POST":
        if len(checkreview)==0:
            reviews = request.form.get("userreview")
            rating = request.form.get("rating")
            session["review"] = reviews
            db.execute("INSERT INTO reviews(isbn, review, rating, username) VALUES (:isbn, :review, :rating, :username)", {"isbn":isbn, "review":reviews, "rating": rating,"username":username})
            db.commit()
        else:
            flash("You have already reviewed!")
        return render_template("book.html", bookdetails=bookdetails, review = session["review"] ,average_rating = average_rating, work_ratings_count = work_ratings_count)




@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    data=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    if data==None:
        return render_template('message.html', message = "404 Not Found!")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "GlrgX5sln0VtDindBgTSHQ", "isbns": isbn})
    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']
    x = {
    "title": data.title,
    "author": data.author,
    "year": data.year,
    "isbn": isbn,
    "review_count": work_ratings_count,
    "average_score": average_rating
    }
    api=json.dumps(x)
    return render_template("api.json",api=api)    
    


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        user_password=request.form.get("password")
        salt="5gz"
        db_password = user_password+salt
        h=hashlib.md5(db_password.encode())
        hpassword=h.hexdigest()
        checkpassword = db.execute(f"SELECT password FROM users WHERE username = '{username}'").fetchone()
        if hpassword != checkpassword[0]:
            flash("Please enter the correct password")
            return redirect(url_for("login"))
        session["username"]=username
        flash("Successfully Logged In")
        return redirect(url_for("search"))



@app.route("/logout")
def logout():
    session.clear()
    redirect(url_for("login"))

#postgres://lcglhurepowqxw:04cf0b1ef9f5c99f3f0fc53b3d55225f451dbf843de53b279b507bb753d86a28@ec2-54-225-89-195.compute-1.amazonaws.com:5432/dai06lbnt1qrjj

if __name__=="__main__":
    app.run()
import os
import hashlib
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
        h=h.hexdigest()
        checkpassword = db.execute(f"SELECT password FROM users WHERE username = '{username}'").fetchone()
        if h!=checkpassword:
            flash("Please enter the correct password")
            return redirect(url_for("login"))
        flash("Successfully Logged In")
        return redirect(url_for("index"))


#postgres://mwrxluqitxdiod:31c78054bc4f15c4a2f8f4a4bfecb9f92356548bc9d241a0f380ab1c8b5c7d5a@ec2-54-227-246-152.compute-1.amazonaws.com:5432/d62vu3sdajlb18


if __name__=="__main__":
    app.run()
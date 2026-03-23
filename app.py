from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS urunler (id INTEGER PRIMARY KEY, ad TEXT, stok INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS hareketler (id INTEGER PRIMARY KEY, urun_id INTEGER, miktar INTEGER, tarih TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    db.execute("INSERT INTO users (username,password) VALUES ('admin','1234')")
    db.commit()

init_db()

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        db = get_db()
        result = db.execute("SELECT * FROM users WHERE username=? AND password=?", (user,pw)).fetchone()

        if result:
            session["user"] = user
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    db = get_db()
    urunler = db.execute("SELECT * FROM urunler").fetchall()
    return render_template("index.html", urunler=urunler)

@app.route("/ekle", methods=["POST"])
def ekle():
    db = get_db()
    db.execute("INSERT INTO urunler (ad, stok) VALUES (?,?)",
               (request.form["ad"], request.form["stok"]))
    db.commit()
    return redirect("/")

@app.route("/giris", methods=["POST"])
def giris():
    db = get_db()
    urun_id = request.form["id"]
    miktar = int(request.form["miktar"])

    db.execute("UPDATE urunler SET stok = stok + ? WHERE id=?", (miktar, urun_id))
    db.execute("INSERT INTO hareketler (urun_id, miktar, tarih) VALUES (?,?,?)",
               (urun_id, miktar, datetime.now()))
    db.commit()
    return redirect("/")

@app.route("/cikis", methods=["POST"])
def cikis():
    db = get_db()
    urun_id = request.form["id"]
    miktar = int(request.form["miktar"])

    db.execute("UPDATE urunler SET stok = stok - ? WHERE id=?", (miktar, urun_id))
    db.execute("INSERT INTO hareketler (urun_id, miktar, tarih) VALUES (?,?,?)",
               (urun_id, -miktar, datetime.now()))
    db.commit()
    return redirect("/")

@app.route("/analiz")
def analiz():
    db = get_db()
    hareketler = db.execute("SELECT miktar FROM hareketler").fetchall()
    toplam = sum([h[0] for h in hareketler])
    return render_template("analiz.html", toplam=toplam)

app.run(host="0.0.0.0", port=5000)

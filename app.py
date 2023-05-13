from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'expenseease_db'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
mysql = MySQL(app)

@app.route('/')
def index():
    if not session.get("login"):
        return redirect("/login")
    else:
        cursor = mysql.connection.cursor()
        print(session.get("user_id"))
        cursor.execute("SELECT * FROM boards WHERE user_id=%s",(session.get("user_id"),))
        user_board = cursor.fetchone()
        mysql.connection.commit()
        cursor.close()
    return render_template('index.html', user=session['login'], board=user_board)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        now = datetime.now()
        created = now.strftime("%Y/%m/%d %H:%M:%S")
        cursor = mysql.connection.cursor()
        user = cursor.execute("SELECT login, password FROM users WHERE login=%s AND password=%s",(login,password))
        if not user:
            cursor.execute("INSERT INTO users (login,password,created) VALUES(%s,%s,%s)",(login,password,created))     
            mysql.connection.commit()
            cursor.close()
            flash('Account created succesfully!', 'success')
        else:
            flash('Account with given data exists!', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, login FROM users WHERE login=%s AND password=%s",(login,password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session["user_id"] = user[0]
            session["login"] = user[1]
            return redirect('/')
        else:
            flash('Given data are incorrect. Try again!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():    
    session.pop('login', None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
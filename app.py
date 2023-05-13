from flask import Flask, render_template, request, redirect, url_for, session
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
    return render_template('index.html', user=session['login'])

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
            # //TO DO - add to every error flash messages
            # 'given user exists'
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('login'))
        else:
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():    
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        user = cursor.execute("SELECT login, password FROM users WHERE login=%s AND password=%s",(login,password))
        cursor.close()
        if user:
            session["login"] = request.form['login']
            return redirect('/')
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():    
    session.pop('login', None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
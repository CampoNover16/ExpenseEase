from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from flask_mysqldb import MySQL
from datetime import datetime,date
import string, random

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
    second_user = None
    users = 1
    if not session.get("login"):
        return redirect("/login")
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.user_id=%s",(session.get("user_id"),))
        user_board = cursor.fetchone()
        if user_board:
            cursor.execute("SELECT login FROM users JOIN board_users ON users.id = board_users.user_id WHERE board_users.board_id=%s and login!=%s",(user_board[0],session.get("login")))
            second_user = cursor.fetchone()
            if second_user:
                users += 1
        mysql.connection.commit()
        cursor.close()
        print(user_board)
    return render_template('index.html', user=session, board=user_board, second_user = second_user, users_count = users)

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

def createCodeToBoard():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

@app.route('/joinBoard', methods=['POST','GET'])
def joinBoard():
    user_id = session.get("user_id")
    message = None
    req = request.get_json()

    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name, invite_code FROM boards WHERE invite_code=%s and can_join=%s",(req['boardCode'],1))
        checkUserBoard = cursor.fetchone()
        cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.user_id=%s",(session.get("user_id"),))
        userBoardToDelete = cursor.fetchone()
        if userBoardToDelete:
            # TO DO 
            # Delete user from board and if it was only user drop board and all data
            cursor.execute("DELETE FROM board_users WHERE board_users.user_id=%s and board_users.board_id=%s",(session.get("user_id"),userBoardToDelete[0]))
            mysql.connection.commit()
        if checkUserBoard:
            cursor.execute("INSERT INTO board_users (board_id, user_id) VALUES(%s,%s)",(checkUserBoard[0], user_id))
            cursor.execute("UPDATE boards SET can_join=%s WHERE id=%s",(0,checkUserBoard[0]))
            mysql.connection.commit()
            message = 'Succesfully joined to your friend\' board!'
        else:
            message = 'Something went wrong!'
        cursor.close()
    return {"message": message}

@app.route('/createBoard', methods=['POST','GET'])
def createBoard():
    user_id = session.get("user_id")
    message = None
    default_board_name = "Default board name 1"
    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.user_id=%s",(session.get("user_id"),))
        checkUserBoard = cursor.fetchone()
        if not checkUserBoard:
            cursor.execute("INSERT INTO boards (name, invite_code, can_join) VALUES(%s,%s,%s)",(default_board_name, createCodeToBoard(), 1))
            cursor.execute("SELECT id FROM boards ORDER BY ID DESC LIMIT 1")
            findBoard = cursor.fetchone()
            cursor.execute("INSERT INTO board_users (board_id, user_id) VALUES(%s,%s)",(findBoard[0], user_id))
            mysql.connection.commit()
            message = 'Succesfully created your board!'
        else:
            message = 'Something went wrong!'
        cursor.close()
    return {"message": message}

@app.route('/addExpense', methods=['POST','GET'])
def addExpense():
    user_id = session.get("user_id")
    message = None
    createDate = datetime.now()
    req = request.get_json()
    year, month, day = str(req['date']).split("-")
    if session.get("login"):
       cursor = mysql.connection.cursor() 
       cursor.execute("SELECT `board_id` FROM `board_users` WHERE `user_id`=%s",(user_id,))
       userboardId = cursor.fetchone()
       cursor.execute("INSERT INTO `board_data`(`board_id`, `param`, `value`, `day`, `month`, `year`, `created`, `modified`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(userboardId[0],req['name'],req['price'],day,month,year,createDate,createDate))
       mysql.connection.commit()
    return {"message": message}

@app.route('/logout')
def logout():    
    session.pop('login', None)
    session.pop('user_id', None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify, send_file
from flask_session import Session
from flask_mysqldb import MySQL
from datetime import datetime
from io import BytesIO
import string, random
import xlsxwriter

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
    validCode = False
    while(validCode == False):
        generatedCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM boards WHERE invite_code=%s",(generatedCode,))
        checkIfBoardExists = cursor.fetchone()
        if not checkIfBoardExists:
            validCode = True
    return generatedCode

@app.route('/createInvfromReq', methods=['GET','POST'])
def createInvFromReq():
    req = request.get_json()
    if(req):
        newBoardCode = createCodeToBoard()
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.user_id=%s",(session.get("user_id"),))
        userBoard = cursor.fetchone()
        cursor.execute("UPDATE boards SET invite_code=%s WHERE id=%s",(newBoardCode,userBoard[0]))
        mysql.connection.commit()
        cursor.close()
        res = make_response(jsonify({'newBoardCode': newBoardCode}))
    return res

@app.route('/deleteUserBoard', methods=['GET','POST'])
def deleteUserBoard():
    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.user_id=%s",(session.get("user_id"),))
        allBoardUsers = len(cursor.fetchall())
        cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.user_id=%s",(session.get("user_id"),))
        userBoardData = cursor.fetchone()
        if(allBoardUsers == 1):
            cursor.execute("DELETE FROM board_data WHERE board_data.board_id=%s",(userBoardData[0],))
            cursor.execute("DELETE FROM board_users WHERE board_users.user_id=%s and board_users.board_id=%s",(session.get("user_id"),userBoardData[0]))
            cursor.execute("DELETE FROM boards WHERE boards.id=%s",(userBoardData[0],))
            mysql.connection.commit()
            cursor.close()
            res = make_response(jsonify({"message": "Your board has been successfully removed", "type": 'success'}))
        else:
            res = make_response(jsonify({"message": "Your cannot delete board where there is more then one user on board!", "type": 'danger`'}))
        return res

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
            cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.board_id=%s",(userBoardToDelete[0],))
            rows_affected = len(cursor.fetchall())
            if rows_affected > 1:
                cursor.execute("UPDATE boards SET can_join=%s WHERE id=%s",(1,userBoardToDelete[0]))
                cursor.execute("DELETE FROM board_users WHERE board_users.user_id=%s and board_users.board_id=%s",(session.get("user_id"),userBoardToDelete[0]))
                mysql.connection.commit()
            else:
                cursor.execute("DELETE FROM board_data WHERE board_data.board_id=%s",(userBoardToDelete[0],))
                cursor.execute("DELETE FROM board_users WHERE board_users.user_id=%s and board_users.board_id=%s",(session.get("user_id"),userBoardToDelete[0]))
                cursor.execute("DELETE FROM boards WHERE boards.id=%s",(userBoardToDelete[0],))
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
       cursor.execute("INSERT INTO `board_data`(`board_id`, `param`, `value`,`category`,`data_type`, `day`, `month`, `year`, `created`, `modified`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(userboardId[0],req['name'],req['price'],req['category'],req['expenseOrIncome'],day,month,year,createDate,createDate))
       mysql.connection.commit()
    return {"message": message}

@app.route('/changeExpense', methods=['POST','GET'])
def changeExpense():
    user_id = session.get("user_id")
    message = None
    updateDate = datetime.now()
    req = request.get_json()
    year, month, day = str(req['date']).split("-")

    if session.get("login"):
        if (request.method == 'POST'):
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE `board_data` SET `param`=%s,`value`=%s,`category`=%s,`data_type`=%s,`day`=%s,`month`=%s,`year`=%s,`modified`=%s WHERE `id`=%s",(req['name'],req['price'],req['category'],req['expenseOrIncome'],day,month,year,updateDate,req['id']))
            mysql.connection.commit()

    return {"message": message}

@app.route('/getExpense', methods=['POST','GET'])
def getExpense():
    message = None
    req = request.get_json()

    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM `board_data` WHERE `id`=%s",(req,))
        data = cursor.fetchone()
        expenseDate =("%s-%s-%s" % (data[6],data[7],data[8]))
        expense = {
            "id": data[0],
            "name": data[2],
            "category": data[4],
            "data_type": data[5],
            "price": data[3],
            "date": expenseDate
        }
        mysql.connection.commit()
        res = make_response(jsonify(expense))

        return res

    return{"message": message}

@app.route('/deleteExpense', methods=['POST','GET'])
def deleteExpense():
    message = None
    req = request.get_json()

    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM `board_data` WHERE `id`=%s",(req,))
        mysql.connection.commit()

    return{"message": message}


@app.route('/getAllExpenses', methods=['POST','GET'])
def getAllExpenses():
    user_id = session.get("user_id")
    dataArray = []
    current_month = datetime.now().month
    current_year = datetime.now().year
    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT `board_id` FROM `board_users` WHERE `user_id`=%s",(user_id,))
        userboardId = cursor.fetchone()
        cursor.execute("SELECT * FROM `board_data` WHERE `board_id`=%s and `month`=%s and `year`=%s ORDER BY day",(userboardId[0],current_month,current_year))
        boardData = cursor.fetchall()
        for data in boardData:
            expenseDate =("%s-%s-%s" % (data[6],data[7],data[8]))
            expense = {
                "id": data[0],
                "name": data[2],
                "category": data[4],
                "data_type": data[5],
                "price": data[3],
                "date": expenseDate
            }
            dataArray.append(expense)
        mysql.connection.commit()
        res = make_response(jsonify(dataArray))
    return res

@app.route('/getPreviousMonthExpenses', methods=['GET'])
def getPreviousMonthExpenses():
    user_id = session.get("user_id")
    dataArray = []
    current_month = datetime.now().month
    current_year = datetime.now().year
    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT `board_id` FROM `board_users` WHERE `user_id`=%s",(user_id,))
        userboardId = cursor.fetchone()
        # TO TEST
        # I dont know how its going to be when current month will be january
        cursor.execute("SELECT * FROM `board_data` WHERE `board_id`=%s and `month`=%s and `year`=%s ORDER BY day",(userboardId[0],current_month-1,current_year))
        boardData = cursor.fetchall()
        for data in boardData:
            expenseDate =("%s-%s-%s" % (data[5],data[6],data[7]))
            expense = {
                "id": data[0],
                "name": data[2],
                "category": data[4],
                "price": data[3],
                "date": expenseDate
            }
            dataArray.append(expense)
        mysql.connection.commit()
        res = make_response(jsonify(dataArray))
    return res

@app.route('/saveUserBoardName', methods=['POST','GET'])
def saveUserBoardName():
    req = request.get_json()
    message = None
    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM boards JOIN board_users ON boards.id=board_users.board_id WHERE board_users.user_id=%s",(session.get("user_id"),))
        userBoard = cursor.fetchone()
        if userBoard:
            cursor.execute("UPDATE boards SET name=%s WHERE id=%s",(req['newName'],userBoard[0]))
            mysql.connection.commit()
            cursor.close()
    return {"message": message}

@app.route('/getDateForUsersBoardData', methods=['GET'])
def getDateForUsersBoardData():
    user_id = session.get("user_id")
    dataArray = []
    if session.get("login"):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT `board_id` FROM `board_users` WHERE `user_id`=%s",(user_id,))
        userBoard = cursor.fetchone()
        if userBoard:
            cursor.execute("SELECT DISTINCT(month),year FROM board_data WHERE board_id=%s ORDER BY month,year ASC",(userBoard[0],))
            selectData = cursor.fetchall()
            for data in selectData:
                data = {"month": data[0], "year": data[1]}
                dataArray.append(data)
            mysql.connection.commit()
            cursor.close()
            res = make_response(jsonify(dataArray))
        return res

@app.route('/download_excel_api', methods=['POST','GET'])
def downloadExcelApi():
    req = request.get_json()
    apiResponse = createApiResponse(req)
    return apiResponse

def createApiResponse(req):
    bufferFile = writeBufferExcelFile(req)
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return send_file(bufferFile,mimetype=mimetype)

def writeBufferExcelFile(req):
    user_id = session.get("user_id")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT `board_id` FROM `board_users` WHERE `user_id`=%s",(user_id,))
    userboardId = cursor.fetchone()
    if userboardId:
        cursor.execute("SELECT * FROM `board_data` WHERE `board_id`=%s and `month`=%s and `year`=%s ORDER BY day, month ASC",(userboardId[0],req['month'],req['year']))
        boardData = cursor.fetchall()
        cursor.execute("SELECT category, SUM(value) FROM board_data WHERE board_id=%s and month=%s and year=%s and data_type=1 GROUP BY category;",(userboardId[0],req['month'],req['year']))
        categoryResults = cursor.fetchall()
        cursor.execute("SELECT day, CAST(AVG(value) AS DECIMAL(5, 2)) FROM board_data WHERE board_id=%s and month=%s and year=%s GROUP BY day;",(userboardId[0],req['month'],req['year']))
        dailyResults = cursor.fetchall()
        if boardData:
            buffer = BytesIO()
            workbook = xlsxwriter.Workbook(buffer)
            worksheet = workbook.add_worksheet()

            bold = workbook.add_format({'bold': True})
            format1 = workbook.add_format({'num_format': '@'})

            worksheet.set_column('A:A', 20)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('G:G', 17)
            worksheet.set_column('J:J', 20)

            worksheet.write('A1', 'Name', bold)
            worksheet.write('B1', 'Cost', bold)
            worksheet.write('C1', 'Category', bold)
            worksheet.write('D1', '+/-', bold)
            worksheet.write('E1', 'Date', bold)
            worksheet.write('G1', 'Category expenses', bold)
            worksheet.write('H1', 'Cost', bold)

            row = 1
            col = 0

            sumIncome = 0
            sumExpenses = 0
            for items in (boardData):
                date = datetime(items[8], items[7], items[6], 0, 0, 0)
                worksheet.write(row, col, items[2], format1)
                worksheet.write(row, col + 1, items[3])
                worksheet.write(row, col + 2, items[4])

                if(items[5] == 1):
                    worksheet.write(row, col + 3, 'Expense')
                    sumExpenses += items[3]
                else:
                    worksheet.write(row, col + 3, 'Income')
                    sumIncome += items[3]

                worksheet.write(row, col + 4, date.strftime("%Y/%m/%d"))
                row += 1

            row2 = 1
            col2 = 6
            for items2 in (categoryResults):
                worksheet.write(row2, col2, items2[0], format1)
                worksheet.write(row2, col2+1, items2[1])
                row2 += 1
            
            avgDaily = 0
            for item3 in (dailyResults):
                avgDaily += int(item3[1])
            avgDaily = avgDaily/len(dailyResults)

            worksheet.write('J2', 'Total incomes', bold)
            worksheet.write('J3', 'Total expenses', bold)
            worksheet.write('J4', 'AVG daily expenses', bold)
            worksheet.write('J5', 'Total cash flow', bold)
            worksheet.write('K2', sumIncome)
            worksheet.write('K3', sumExpenses)
            worksheet.write('K4', avgDaily)
            worksheet.write('K5', sumIncome + sumExpenses)
            workbook.close()
            buffer.seek(0)  
            
            return buffer

@app.route('/logout')
def logout():    
    session.pop('login', None)
    session.pop('user_id', None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
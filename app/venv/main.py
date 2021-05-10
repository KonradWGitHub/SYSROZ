from flask import Flask, render_template, url_for, redirect, request, session
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = "123412341234"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysqlroot"
app.config["MYSQL_DB"] = "users"

db = MySQL(app)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'register' in request.form:
            register = request.form['register']
            if register == "Create an account":
                return redirect(url_for('signup'))
        if 'login' in request.form and 'password' in request.form and 'email' in request.form:
            password = request.form['password']
            email = request.form['email']
            submit_login = request.form['login']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE email=%s AND  password=%s", (email, password))
            info = cursor.fetchone()
            if submit_login == "Log me in":
                if info is not None:
                    return redirect(url_for('reg_suc'))
                else:
                    return render_template("login.html", error=1)
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if 'signup_submit' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'password2' in request.form:
            email = request.form['email']
            password = request.form['password']
            password2 = request.form['password2']
            username = request.form['username']
            submit = request.form['signup_submit']
            if submit == "Sign me up" and (email, password, username, password2) is not None:
                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM users WHERE username= %s AND email=%s AND  password=%s",
                               (username, email, password))
                info = cursor.fetchone()
                if info is not None:
                    return render_template("register.html", error=1)

                elif password != password2:
                    return render_template("register.html", error=2)
                elif username != "" and email != "" and password != "" and password2 != "":
                    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                                   (username, email, password))
                    db.connection.commit()
                    return redirect(url_for('login'))
                else:
                    return render_template("register.html", error=3)
    return render_template("register.html")


@app.route('/register/success')
def reg_suc():
    return render_template("main_page.html")


if __name__ == '__main__':
    app.run(debug=True)

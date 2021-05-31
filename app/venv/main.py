from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, emit, join_room
from venv.database import Database
import MySQLdb
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = "123412341234"

# database config
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysqlroot"
app.config["MYSQL_DB"] = "users"
db = MySQL(app)

# globals
active_users = []
ses = ""

# SETUP
socketio = SocketIO(app)  # used for user communication


@app.route('/')
def index():
    return redirect(url_for('login'))


# ----------LOGIN----------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('email'):
        return redirect(url_for('log_suc'))
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
                    session['email'] = email
                    fm = "logged in as {0}".format(email)
                    flash(fm, 1)
                    return redirect(url_for('log_suc'))
                else:
                    flash("Wrong email/password. Fill blanks with the correct", 0)
                    return render_template("login.html")
    return render_template("login.html")


# ----------REGISTER----------------------------------------------------------------------------
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
                cursor.execute("SELECT * FROM users WHERE username= %s OR email=%s",
                               (username, email))
                info = cursor.fetchone()
                if info is not None:
                    flash("Username/email already taken.", 0)
                    return render_template("register.html")
                elif password != password2:
                    flash("Retype the same password.", 0)
                    return render_template("register.html")
                elif username != "" and email != "" and password != "" and password2 != "":
                    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                                   (username, email, password))
                    db.connection.commit()
                    flash("Registered successfully!", 1)
                    return redirect(url_for('login'))
                else:
                    flash("Fill blanks.", 0)
                    return render_template("register.html")
    return render_template("register.html")


# ----------LOGIN-SUCCESS-(MAIN-PAGE)-------------------------------------------------------------------------
@app.route('/home', methods=['GET', 'POST'])
def log_suc():
    if session.get('email'):
        if session['email']:
            email = session['email']
            session.permament = True
            app.permanent_session_lifetime = timedelta(minutes=5)
            users = []
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT username FROM users")
            info = cursor.fetchall()
            for user in range(len(info)):
                users.append(info[user]['username'])
            cursor.execute("SELECT username FROM users WHERE email= %s", (email, ))
            info = cursor.fetchone()
            users.remove(info['username'])
            return render_template('main_page.html', Users=users)
    else:
        return redirect(url_for('login'))


# ----------LOGOUT----------------------------------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


# -----------CHANGE-PASSWORD----------------------------------------------------------------
@app.route('/manage_account', methods=['GET', 'POST'])
def manage_account():
    if session.get('email'):
        if session['email']:
            email = session['email']
            if 'delete_submit' in request.form:
                delete_submit = request.form['delete_submit']
                if delete_submit == "Delete account":
                    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("DELETE FROM users WHERE email=%s", (email,))
                    db.connection.commit()
                    flash("Successfully deleted the account.", 1)
                    return redirect(url_for('logout'))
            if 'submit' in request.form and 'password' in request.form and 'new_password' in request.form:
                submit = request.form['submit']
                password = request.form['password']
                new_password = request.form['new_password']
                if submit == "Change password":
                    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
                    info = cursor.fetchone()
                    if info is not None:
                        if password != "" and new_password != "":
                            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                            cursor.execute("UPDATE users SET password=%s WHERE email=%s",
                                           (new_password, email,))
                            db.connection.commit()
                            flash("Password changed!", 1)
                            return redirect(url_for('log_suc'))
                    else:
                        flash("Fill blanks.", 0)
                        return render_template("manage_account")
            return render_template('manage_account.html')
    else:
        return redirect(url_for('login'))


# ------SOCKET-IO-------------------------------------------------------------------------------------
@socketio.on('connect', namespace='/home')
def on_connect():
    """
    initializes user that join its room
    :emit: None
    """
    global ses
    email = session['email']
    my_id = Database.get_id(db, email)
    ses = my_id
    join_room(my_id)
    if my_id not in active_users:
        active_users.append(my_id)
    print(active_users)
    emit('update_active_users', active_users, broadcast=True)


@socketio.on('on_disconnect', namespace='/home')
def on_disconnect():
    """
    pops session when disconnected
    """
    global ses
    active_users.remove(ses)
    ses = ""
    emit('update_users', active_users, broadcast=True, include_self=False)


@socketio.on('private_message', namespace='/home')
def send_message(r_id, message):
    """
    handles sending messages
    :param r_id: str, recipient id
    :param message: str, content of a message
    :emit: 'new_private_message', (current_time, my_id, message) to recipient
    :emit: 'append_on_list',  (current_time, my_id, r_id, message) to itself
    """
    email = session['email']
    my_id = Database.get_id(db, email)
    time = datetime.now()
    current_time = time.strftime("%H:%M:%S")
    current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
    Database.save_message(db, message, my_id, r_id, current_datetime)
    emit('new_private_message', (current_time, my_id, message), room=r_id)
    emit('append_on_list', (current_time, my_id, r_id, message), room=my_id)


@socketio.on('get_history', namespace='/home')
def get_history(r_id):
    """
    handles getting history
    :param r_id:
    :emit: 'history_display' , history to itself
    """
    email = session['email']
    my_id = Database.get_id(db, email)
    history = Database.get_all_messages(db, 100, my_id, r_id)
    print(history)
    emit('history_display', history,  room=my_id)


# MAINLINE
if __name__ == "__main__":  # start the web server
    socketio.run(app, debug=True)

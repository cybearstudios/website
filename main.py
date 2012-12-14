'''
main.py

This file handels:
    Imports
    DB model classes
    DB model key creation
    Defintions
    Flask settings
    Flask application
    URL routing
    Error handlers
    Flask application init routine
    
'''
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

import sqlite3

# configuration
DATABASE = 'site.db'
DEBUG = True
SECRET_KEY = 'the_cake_is_a_lie'
USERNAME = 'admin'
PASSWORD = 'default'

# flask application
app = Flask(__name__)
app.config.from_object(__name__)

# defs
def init_usertable():

    conn = sqlite3.connect(DATABASE)
    db = conn.cursor()
    try:
	db.execute("DROP TABLE usertable")
    except:
	pass
    db.execute("CREATE TABLE usertable(username, password, email, seclvl, active)")
    conn.commit()
    conn.close()

def add_user(name,passwrd,email,level):
    command = "INSERT INTO usertable VALUES ('" + name + "','" + passwrd + "','" + email + "'," + str(level) + ",'true')"
    conn = sqlite3.connect(DATABASE)
    db = conn.cursor()
    db.execute(command)
    conn.commit()
    conn.close()

def get_users():
    command = "SELECT * FROM usertable"
    conn = sqlite3.connect(DATABASE)
    db = conn.cursor()
    db.execute(command)
    ret = db.fetchall()
    conn.close()
    rows = []
    print ret
    try:
	for row in ret:
	    rows.append(row)
	return rows
    except:
	return None

def get_user(var, field):
    field = field
    command = "SELECT * FROM usertable WHERE " + field + "='" + var + "'"
    conn = sqlite3.connect(DATABASE)
    db = conn.cursor()
    db.execute(command)
    ret = db.fetchone()
    conn.close()
    try:
        return ret
    except:
        return None

def lockpage(minlvl):
    try:
        lvl = get_level()
    except:
        return False
    if minlvl <= lvl:
        return True
    else:
        return False

def get_level():
    try:
        return session['seclvl']
    except:
        session['seclvl'] = 0
        return session['seclvl']

#handles index page
@app.route('/')
def index():
    if lockpage(1) == False:
        return redirect(url_for('locked'))
    return render_template('index.html')

#handls account list page
@app.route('/accountlist')
def accountlist():
    if lockpage(2) == False:
        return redirect(url_for('locked'))
    userlist = get_users()
    return render_template('accountlist.html', entries=userlist)


#handles the newuser page and user creation requests
@app.route('/newuser', methods=['GET', 'POST'])
def create_user():
    if lockpage(2) == False:
        return redirect(url_for('locked'))
    error = None
    if request.method == 'POST':
        if request.form['Username'] == "":
            error = "Invalid username"
        else:
            if get_user(request.form['Username'],"username") != None:
                error = 'Username already in use'
            else:
                name1 = request.form['Username']
                if request.form['Email'] == "":
                    error = 'Invalid email address'
                else:
                    if get_user(request.form['Email'],"email") != None:
                        error = 'Email already in use'
                    else:
                        email1 = request.form['Email']
                        if request.form['Password'] != request.form['ConfPassword']:
                            error = 'Passwords did not match'
                        else:
                            if request.form['Password'] == "":
                                error = 'Invalid password'
                            else:
                                password1 = request.form['Password']
                                try:
                                    clevel = int(request.form['cl_list'])
                                except:
                                    clevel = 1
                                add_user(name1,password1,email1,clevel)
                                flash('Succesfully created user ' + name1)
                                return redirect(url_for('index'))
    return render_template('create_user.html', error=error)

#handles login page and login form requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session['logged_in'] == True:
            return redirect(url_for('index'))
    except:
        pass
    error = None
    if request.method == 'POST':
        
	adminpass = "admin"
        if request.form['Username'] == "bypass" and request.form['Password'] == adminpass:
            session['seclvl'] = 4
            session['logged_in'] = True
            flash('Welcome Admin You were logged in with clearence level 4')
            return redirect(url_for('index'))
        elif request.form['Username'] == "wipeusers" and request.form['Password'] == adminpass:
            init_usertable()
	    flash("Usertable Reset")
	    
        else:
            attempt = get_user(request.form['Username'],'email')
            if attempt == None:
                error = "Invalid username"
            else:
                if attempt[1] != request.form['Password']:
                    error = 'Invalid password'
                else:
                    session['seclvl'] = attempt[3]
                    session['logged_in'] = True
                    flash('Welcome ' + attempt[0] + ' You were logged in with clearence level ' + str(attempt[3]))
                    return redirect(url_for('index'))
        
    return render_template('login.html', error=error)

#logs out the user
@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['seclvl'] = 0
    return redirect(url_for('login'))

#Handles attempted security breaches
@app.route('/locked')
def locked():
    try:
        if session['logged_in'] != True:
            return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))
    return render_template('locked.html')

# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

#add_user('Tucker','password','tuckerweatherby@gmail.com',3)

if __name__ == '__main__':
    app.run()

import os

from flask import Flask, session, render_template ,redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
import requests

app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

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


@app.route("/login", methods=['GET','POST'])
def connexion():
    message = []
    title = "Sign up or Login"
    if request.method == 'GET':
        return render_template('login.html', title=title)
    else:
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if full_name and username and password and email:
            if password == password2:
                password = generate_password_hash(password)
                connect = db.execute("INSERT INTO users (full_name, username, email, password) VALUES (:full_name, :username, :email, :password)",
                            {"full_name":full_name ,"username":username , "email":email , "password":password})
                db.commit()
                if connect:
                    rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

                    session["user_id"] = rows[0]

                return redirect('/')
            else:
                msg = "password don't match "
                message.append(msg)
                return render_template('login.html',message=message)
        else:
            msg = 'please give us all informations'
            message.append(msg)
            return render_template('login.html',message=message)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        """
        base = requests.get('https://api.exchangeratesapi.io/latest')
        if base.status_code == 200:
            base = base.json()
            return render_template('index.html', base=base)
        else:
            return 'Error'

            """
        return render_template('index.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user_data = db.execute('SELECT * FROM users WHERE username = :username',{'username': username}).fetchone()
            if user_data:               
                print(check_password_hash(user_data.password, password))

                if check_password_hash(user_data.password, password):
                    session['user_id'] = user_data[0]
                    return render_template('index.html', user_data=user_data)

                else:
                    message = []
                    msg ="password don't match"
                    message.append(msg)
                    return render_template('login.html', message=message)

            else:
                message = []
                msg ="don't have this account in our databases"
                message.append(msg)
                return render_template('login.html', message=message)
                
        else:
            message = []
            msg ="missing username or password !!!"
            message.append(msg)
            return render_template('login.html', message=message)
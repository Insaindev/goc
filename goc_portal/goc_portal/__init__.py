import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
# set secret key
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# set sqldb
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# set bcrypt
bcrypt = Bcrypt(app)

# set login manager
login_manager = LoginManager(app)
# if user is not logged in redirect to login page automatically
login_manager.login_view = 'login'
# bootstrap design
login_manager.login_message_category = 'info'

# set mail server
app.config['MAIL_SERVER'] = 'smtp.m1.websupport.sk'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config['MAIL_USERNAME'] = "zoltanhalasz@insaindev.com"
app.config['MAIL_PASSWORD'] = "Br41nD4m4ge"
mail = Mail(app)

# hot fix
from goc_portal import routes

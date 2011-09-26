#!/usr/bin/env python
# Ricky Saltzer
from flask import Flask, render_template, flash, redirect, url_for, jsonify, flash, request, Response, json
from flaskext.sqlalchemy import SQLAlchemy 
from flaskext.login import LoginManager, login_user, login_required, current_user, logout_user
from flaskext.wtf import Form, TextField, Required, PasswordField, TextArea
from flaskext.bcrypt import bcrypt_init, generate_password_hash, check_password_hash
from flaskext.assets import Environment, Bundle
from flaskext.debugtoolbar import DebugToolbarExtension
from flaskext.script import Manager
from flaskext.mongoalchemy import MongoAlchemy
import os, datetime

#------------
# App Config
#------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "asdf"
app.config['DEBUG'] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["CACHE_TYPE"] = 'simple'
toolbar = DebugToolbarExtension(app)

# Database URI - sqlite3 for testing
app.config['MONGOALCHEMY_DATABASE'] = 'tweeter'

# Password hashing configuration
app.config['BCRYPT_SALT_ROUNDS'] = 12

# Declare database object
db = MongoAlchemy(app)

# Setup login managers
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"


#---------------
# JS/CSS Assets
#---------------
assets = Environment(app)
js = Bundle('jquery.js','messages.js')
assets.register('js_all', js)

#--------
# NEW DB
#--------
class Users(db.Document):
	username = db.StringField()
	email = db.StringField()
	password = db.StringField()

	def is_active(self):
		return True

	def is_authenticated(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.mongo_id
	
	def hash_password(self, password):
		return generate_password_hash(password,rounds=app.config['BCRYPT_SALT_ROUNDS'])

	def check_password(self, password):
		return check_password_hash(self.password, password)


class Tweets(db.Document):
	user = db.DocumentField(Users)
	message = db.StringField()
	created = db.DateTimeField()		

#---------------
# Database Model
#---------------
@login_manager.user_loader
def load_user(id):
	user = Users.query.get(id)
	return user

#-------------
# Form Models
#-------------
# User registration form
class User_Registration(Form):
	username = TextField('Username', validators=[Required()])
	email = TextField('Email', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])

class Login_Form(Form):
	username = TextField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])

class Tweet_Form(Form):
	tweet = TextField('Message', validators=[Required()])

#---------
# Web Code
#---------
@app.route('/')
def index():
	tweets = get_all_tweets()
	return render_template('index.html',tweets=tweets)
	#return render_template('hello.html')

@app.route('/login', methods=["GET","POST"])
def login():
	form = Login_Form()

	if form.validate_on_submit():
		username = form.username.data
		user = Users.query.filter(Users.username == username).first()
		if not user:
			flash("Invalid Login")
			return redirect(url_for("login"))

		if user.check_password(form.password.data):
			login_user(user)
			flash("Logged In!")
		else:
			flash("Invalid Login")
			return redirect(url_for("login"))

		return redirect(request.args.get("next") or url_for("index"))

	return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash("Logged Out!")
	return redirect(url_for('index'))

@app.route('/register', methods=["GET","POST"])
def register():
	form = User_Registration()
	
	if form.validate_on_submit():
		user = Users()
		user.username = form.username.data
		user.email = form.email.data
		user.password = user.hash_password(form.password.data)
		user.save()
		login_user(user)

		flash("Registered!")
		return redirect(url_for("index"))

	return render_template('register.html',form=form)

@app.route('/tweet', methods=["GET","POST"])
@login_required
def submit_tweet():
	form = Tweet_Form(csrf_enabled=False)
	
	if form.validate_on_submit():
		tweet = Tweets()
		tweet.message = form.tweet.data
		tweet.user = Users.query.get(current_user.mongo_id)
		tweet.created = datetime.datetime.now()
		tweet.save()
		return redirect(url_for('index'))

	return render_template('tweet.html',form=form)

@app.route('/tweets.json')
def tweets_json():
	dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
	jdata = {}
	for tweet in get_all_tweets(limit=None):
		jdata[str(tweet.mongo_id)] = dict(user=tweet.user.username, date=json.dumps(tweet.created, default=dthandler), message=tweet.message)

	return jsonify(jdata)

def get_all_tweets(limit=10):
	if limit:
        	tweets = Tweets.query.descending(Tweets.created).limit(limit)
	else:
		tweets = Tweets.query.descending(Tweets.created).all()

        return tweets

#-----------
# Main Loop
#-----------
if __name__ == "__main__":
	manager = Manager(app)
	manager.run()

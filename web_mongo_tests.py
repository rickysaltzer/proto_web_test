#!/usr/bin/env python 
# Ricky Saltzer
import warnings
with warnings.catch_warnings():
	warnings.filterwarnings("ignore",category=DeprecationWarning)
	import re, base64, urlparse, posixpath, md5, sha, sys, copy 
from flaskext.testing import TestCase, Twill, unittest
import web_mongo as web, datetime

class Tests(TestCase):
	web.app.config['MONGOALCHEMY_DATABASE'] = 'tweeter_unittest'
	web.app.config['BCRYPT_SALT_ROUNDS'] = 1

	def create_app(self):
		app = web.app
		app.config['TESTING'] = True
		return app
	
	def setUp(self):
		pass

	def tearDown(self):
		for user in web.Users.query.all():
			user.remove()
			user.save()
		for tweet in web.Tweets.query.all():
			tweet.remove()
			tweet.save()

	def test_index(self):
		response = self.client.get("/")
		self.assert200(response)

	def test_404(self):
		response = self.client.get("/mofo")
		self.assert404(response)

	def register(self, username, password, email):
		self.app.config['CSRF_ENABLED'] = False
		return self.client.post("/register", data=dict(
			username = username,
			password = password,
			email = email),follow_redirects=True)

	def login(self, username, password):
		self.app.config['CSRF_ENABLED'] = False
		return self.client.post("/login", data=dict(
			username = username,
			password = password), follow_redirects=True)
	
	def logout(self):
		return self.client.get("/logout", follow_redirects=True)

	def tweet(self, message):
		return self.client.post("/tweet", data=dict(
			tweet = message), follow_redirects=True)

	def test_login_registration(self):
		# Register and log in
		for i in range(0,5):
			response = self.register("test"+str(i),"password"+str(i),"test"+str(i)+"@domain.com")
			assert "Registered!" in response.data
		
		for i in range(0,5):
			# Login User
			response = self.login("test"+str(i), "password"+str(i))
			assert "Logged In!" in response.data

			# Logout User
			response = self.logout()
			assert "Logged Out!" in response.data

		response = self.login("fail","fail")
		assert "Invalid Login" in response.data

	def test_tweets(self):
		response = self.register("test_user", "password", "test_user@domain.com")
		assert "Registered!" in response.data

		response = self.login("test_user","password")
		assert "Logged In!" in response.data

		response = self.tweet("test tweet")
		assert "test_user" in response.data and "test tweet" in response.data
		assert datetime.datetime.now().strftime("%H:%M") in response.data

		response = self.logout()
		assert "Logged Out!" in response.data

if __name__ == "__main__":
	unittest.main()

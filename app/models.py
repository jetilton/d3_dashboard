from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login 


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
    
	def __repr__(self):
		return '<User {}>'.format(self.username)    

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Cbt(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	cbt = db.Column(db.String(64), unique=True)
	name = db.Column(db.String(64), unique = True)
	latitude = db.Column(db.Float)
	longitude = db.Column(db.Float)

	def __repr__(self):
		return "<Project {}>".format(self.name)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))


class Path(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cbt_id = db.Column(db.Integer, db.ForeignKey('cbt.id'),
        nullable=False)
	path = db.Column(db.String(128), unique = True)
	value = db.Column(db.Float)
	date = db.Column(db.DateTime)	


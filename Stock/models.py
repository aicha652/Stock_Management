from Stock import db, login_manager
from flask_login import UserMixin
from .tools import hash_pass

# Define the user loader function for flask-login
@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


# Define the User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(500), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    phone = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# Define the Product model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    image_1 = db.Column(db.String(256), nullable=False, default='image1.jpg')

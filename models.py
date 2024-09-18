from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from extensions import db
from flask_login import UserMixin
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(10))
    # classes_enrolled = db.Column(db.String(200))


class Chef(UserMixin, db.Model):
    __tablename__ = 'chef'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(100), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    order_location = db.Column(db.String(100))
    start_time = db.Column(db.String(100), default='09:00')  # Default start time is 9am
    end_time = db.Column(db.String(100), default='21:00')    # Default end time is 9pm
    about_me = db.Column(db.Text)  
    profile_url = db.Column(db.String(200)) 
    food_choice1_image_url = db.Column(db.String(200)) 
    food_choice2_image_url = db.Column(db.String(200))  
    food_choice3_image_url = db.Column(db.String(200))  

class Food(UserMixin, db.Model):
    __tablename__ = 'food'
    foodID = db.Column(db.Integer, primary_key=True)
    foodName = db.Column(db.String(100), nullable=False)
    dietary_category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))
    chef_id = db.Column(db.Integer, ForeignKey('chef.id'), nullable=False)
    chef = db.relationship('Chef', backref=db.backref('foods', lazy=True))

class CookingClass(UserMixin, db.Model):
    __tablename__ = 'class'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    className = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text(), nullable=False)
    usersEnrolled = db.Column(db.Integer)
    category = db.Column(db.Text(), nullable=False)
    hostChef = db.Column(db.String(36))
    # steps is JSON consisting of multiple steps for a cooking class
    ingredients = db.Column(db.Text())
    steps = db.Column(db.Text())
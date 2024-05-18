from flask import send_from_directory, render_template, url_for, flash, redirect, request, jsonify, abort, current_app, session
from flask_login import login_user, current_user, logout_user, login_required
from Stock import app, db, bcrypt, photos
from Stock.models import User
from Stock.forms import LoginForm, UserForm
import os, secrets, re
from functools import wraps

















#Default route, redirects to the login page
@app.route('/')
def route_default():
    return redirect(url_for('login'))

#Login route, handles user login
@app.route('/login', methods=['GET', "POST"])
def login():
    msg=""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            msg = "Login unsuccessful, please check your credentials"
    return render_template('login.html', msg=msg, form=form)
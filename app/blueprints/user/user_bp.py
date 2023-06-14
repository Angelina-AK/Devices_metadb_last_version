
from flask import Blueprint, redirect, render_template, request
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.exceptions import abort

from app.models import *

user_bp = Blueprint('user_bp', __name__, template_folder='templates', static_folder='static')


@user_bp.route('/profile', methods=('GET', 'POST'))
@register_breadcrumb(user_bp, 'home', 'profile')
@login_required
def profile():
    user = get_user(current_user.id)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        timezone = request.form['timezone']

        #user.username = username
        user.email = email
        user.timezone = timezone
        db.session.commit()

    return render_template('profile.html', user=user)


@user_bp.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')

    return render_template('login.html')


@user_bp.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return ('Email already Present')

        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')


@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


@user_bp.route('/users/<id>')
@login_required
def get_user(id):
    user = User.query.get(id)
    if user is None:
        abort(404)
    return user



def get_user(id):
    user = User.query.get(id)
    if user is None:
        abort(404)
    return user

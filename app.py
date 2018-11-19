from flask import Flask, render_template, request, session, url_for, redirect
from db import login_user, register_user

import os

app = Flask(__name__)


@app.route('/')
def index():
    if not session['email']:
        return render_template('index.html')

    email = session['email']
    # posts = get_posts(email)
    return render_template('home.html', email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']

    if not login_user(email, password):
        error = 'Invalid email or password'
        return render_template('login.html', error=error)

    session['email'] = email
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    email = request.form['email']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']
    confirm = request.form['confirm']

    if password != confirm:
        error = 'Password does not match'
        return render_template('register.html', error=error)

    if not register_user(email, password, fname, lname):
        error = 'Email already exists'
        return render_template('register.html', error=error)

    session['email'] = email
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')

#
# @app.route('/bloggers')
# def bloggers():
#     users = get_users()
#     return render_template('bloggers.html', user_list=users)
#
#
# @app.route('/post', methods=['POST'])
# def post():
#     username = session['username']
#     create_post(username)
#     return redirect('/')
#
#
# @app.route('/posts')
# def posts():
#     poster = request.args['poster']
#     posts = get_posts(poster)
#     return render_template('posts.html', poster_name=poster, posts=posts)
#


app.secret_key = os.urandom(24)
if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)

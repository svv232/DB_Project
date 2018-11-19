from flask import Flask, render_template, request, session, url_for, redirect
from db import login_user, register_user, get_public_content, post_content
from utilities import login_required

import os

app = Flask(__name__)


@app.route('/')
def index():
    if 'email' not in session:
        return render_template('index.html')

    _, posts = get_public_content()
    return render_template('index.html', email=session['email'],
                           fname=session['fname'], lname=session['lname'],
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']

    success, data = login_user(email, password)

    if not success:
        return render_template('login.html', error=data)

    session['email'] = email
    session['fname'] = data['fname']
    session['lname'] = data['lname']
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

    success, message = register_user(email, password, fname, lname)
    if not success:
        return render_template('register.html', error=message)

    session['email'] = email
    session['fname'] = fname
    session['lname'] = lname
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')


@app.route('/post', methods=['POST'])
@login_required
def post():
    email = session['email']
    post_content(email, 'test', 'file_contents_i_guess', True)
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


#
# @app.route('/bloggers')
# def bloggers():
#     users = get_users()
#     return render_template('bloggers.html', user_list=users)
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

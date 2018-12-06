from flask import Flask, render_template, request, session, url_for, redirect
from db import login_user, register_user, get_public_content, post_content
from db import create_friend_group, get_my_content, get_my_friend_groups
from db import get_content
from utilities import login_required

import os
import json

app = Flask(__name__)


@app.route('/')
def index():
    if 'email' not in session:
        _, posts = get_public_content()
        return render_template('index.html', posts=posts)

    _, posts = get_my_content(session['email'])
    _, groups = get_my_friend_groups(session['email'])
    return render_template('index.html', email=session['email'],
                           fname=session['fname'], lname=session['lname'],
                           posts=posts, groups=groups)


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
    post = request.form.get('submission-text')
    post_content(email, 'test', post, True)
    return redirect('/')


@app.route('/get_post', methods=['POST'])
@login_required
def get_post():
    item_id = request.get_json().get('item_id')
    _, post = get_content(session['email'], item_id)
    post['post_time'] = str(post['post_time'])
    return json.dumps(post)


@app.route('/posts')
def get_posts():
    # Optional Feature 7 (Sai)
    # Optional Feature 8 (Sai)
    # Filtering stuff
    # Modify get_my_content in db.py
    # Return Value: Posts in a list in the correct filtered order
    pass


def rate():
    # Optional Feature 1 (Person 2)
    # Modify db.py
    # Idk add rating
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Post does not exist')
    pass


def tag():
    # Required Feature 6 (tag person)
    # Optional Feature 4 (tag group) (Person 2)
    # Modify db.py
    # Idk add tagging groups
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Post does not exist')
    pass


def accept_tag():
    # Required Feature 4
    pass


def comment():
    # Optional Feature 2 (Roy)
    pass


@app.route('/group/create', methods=['POST'])
@login_required
def create_group():
    fg_name = request.form['fg_name']
    desc = request.form['fg_description']
    success, message = create_friend_group(session['email'], fg_name, desc)
    return redirect('/')


def invite_group():
    # Required Feature 7
    pass


@app.route('/group/leave', methods=['POST'])
@login_required
def leave_group():
    group = request.form['group']
    # Optional Feature 3 (Person 4)
    # Remove from Belongs Table
    # Modify db.py
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Group Doesn't Exist')
    pass


@app.route('/group/best', methods=['POST'])
@login_required
def best_group():
    group = request.form['group']
    # Optional Feature 6 (Person 5)
    # Probably new table (but you can implement however you want)
    # Add group to best friends table
    # Modify db.py
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Group Doesn't Exist')
    pass


@app.route('/profile', methods=['POST'])
@login_required
def edit_profile():
    email = request.form['email']
    fname = request.form['fname']
    lname = request.form['lname']
    # Optional Feature 5 (Person 4)
    # Update Queries for User
    # Modify db.py
    # Assume params are accurate
    #   (if not changing fname, it'll be original fname)
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Email already exists')
    pass


# Done:
# Required Features: 1, 2, 3, 5

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.secret_key = os.urandom(24)
if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)

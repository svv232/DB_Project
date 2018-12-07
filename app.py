from flask import Flask, render_template, request, session, url_for, redirect
from db import login_user, register_user, get_public_content, post_content, get_user, update_user, remove_user_from_group
from utilities import login_required

import os

app = Flask(__name__)


@app.route('/')
def index():
    _, posts = get_public_content()

    if 'email' not in session:
        return render_template('index.html', posts=posts)

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
    post = request.form.get('submission-text')
    post_content(email, 'test', post, True)
    return redirect('/')


@app.route('/posts')
def get_posts():
    # Optional Feature 7 (Person 1)
    # Optional Feature 8 (Person 1)
    # Modify
    # Return Value: Posts in a list in the correct filtered order
    # Filtering stuff
    pass


def rate():
    # Optional Feature 1 (Person 2)
    pass


def tag():
    # Required Feature 6
    # Optional Feature 4 (tag group) (Person 2)
    pass


def accept_tag():
    # Required Feature 4
    pass


def comment():
    # Optional Feature 2 (Roy)
    pass


def create_group():
    # Required Feature 7
    pass


def invite_group():
    # Required Feature 7
    pass


@app.route('/group/leave', methods=['POST'])
@login_required
def leave_group():
    group = request.form['group']
    remove_user_from_group(group=group, email=session['email'])
    return redirect('/')
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
    user = get_user(session['email'])
    db_email = user['email']
    db_first = user['fname']
    db_last = user['lname']

    new_email = request.form.get('email') if request.form.get('email') != db_email else None
    new_first = request.form.get('fname') if request.form.get('fname') != db_first else None
    new_last = request.form.get('lname') if request.form.get('lname') != db_last else None

    status = update_user(db_email, new_email=new_email, new_first=new_first, new_last=new_last)

    if status[0]:
        if new_email:
            user = get_user(new_email)
        else:
            user = get_user(session['email'])

        session['email'] = user['email']
        session['fname'] = user['fname']
        session['lname'] = user['lname']

    return redirect('/')
    # Optional Feature 5 (Person 4)
    # Update Queries for User
    # Modify db.py
    # Assume params are accurate
    #   (if not changing fname, it'll be original fname)
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Email already exists')


# Done:
# Required Features: 1, 2, 3, 5

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.secret_key = os.urandom(24)
if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)

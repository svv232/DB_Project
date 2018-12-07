from flask import Flask, render_template, request, session, url_for, redirect
from db import login_user, register_user, get_public_content, post_content
from db import create_friend_group, get_my_content, get_my_friend_groups
from db import get_content, get_friend_group, add_friend, get_my_tags
from db import tag_content_item, remove_tag_on_content_item
from db import accept_tag_on_content_item, get_friend_group_members
from db import get_tags_from_item_id, ratings_on_content, add_rating
from db import get_user, update_user, remove_user_from_group, share_with_group
from db import add_comment, get_comments
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
    _, tags = get_my_tags(session['email'])
    return render_template('index.html', email=session['email'],
                           fname=session['fname'], lname=session['lname'],
                           posts=posts, groups=groups, tags=tags)


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
    title = request.form.get('submission-title')
    post = request.form.get('submission-text')
    private = request.form.get('private')
    if private == 'True':
        share = request.form.get('share')
        if share and share != '':
            share = share.split(',')
            share = [x.split(':') for x in share]
        private = True
    elif private == 'False':
        private = False
    success, id, msg = post_content(email, title, post, not private)

    if private:
        share_with_group(share[0][1], share[0][0], id)
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


@app.route('/rate')
@login_required
def rate():
    item_id = request.args['item_id']
    emoji = request.args['emoji']
    if emoji == '0':
        emoji = '👍'
    elif emoji == '1':
        emoji = '😮'
    elif emoji == '2':
        emoji = '😥'
    elif emoji == '3':
        emoji = '😡'
    elif emoji == '4':
        emoji = '😂'

    add_rating(session['email'], item_id, emoji)
    return redirect('/')


@app.route('/rate/get', methods=['POST'])
@login_required
def ratings():
    item_id = request.get_json().get('item_id')
    _, content = ratings_on_content(item_id, session['email'])
    return json.dumps(content)


@app.route('/tag', methods=['POST'])
@login_required
def tag():
    item_id = request.form.get('item_id')
    email_tagged = request.form.get('tagged-email')
    tag_content_item(email_tagged, session['email'], item_id)
    # Optional Feature 4 (tag group) (Person 2)
    # Modify db.py
    # Idk add tagging groups
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Post does not exist')
    return redirect('/')


@app.route('/tag/get', methods=['POST'])
@login_required
def get_tag():
    item_id = request.get_json().get('item_id')
    err, content = get_tags_from_item_id(session['email'], item_id)
    for tag in content:
        tag['tagtime'] = str(tag['tagtime'])
    # Optional Feature 4 (tag group) (Person 2)
    # Modify db.py
    # Idk add tagging groups
    # Return Value: Success or Error Message
    # i.e. (True, 'Success') or (False, 'Post does not exist')
    return json.dumps(content)


@app.route('/tag/review')
@login_required
def accept_tag():
    item_id = request.args['item_id']
    email_tagger = request.args['email_tagger']
    status = request.args['status']

    if status == 'delete':
        remove_tag_on_content_item(session['email'], email_tagger, item_id)

    if status == 'accept':
        accept_tag_on_content_item(session['email'], email_tagger, item_id)

    return redirect('/')


@app.route('/comment/get', methods=['POST'])
@login_required
def comments():
    item_id = request.get_json().get('item_id')
    _, content = get_comments(item_id, session['email'])
    return json.dumps(content)


@app.route('/comment', methods=['POST'])
@login_required
def comment():
    item_id = request.form['item_id']
    comment = request.form['comment']
    print('item', item_id)
    add_comment(item_id, comment, session['email'])
    return redirect('/')


@app.route('/group/create', methods=['POST'])
@login_required
def create_group():
    fg_name = request.form['fg_name']
    desc = request.form['fg_description']
    success, message = create_friend_group(session['email'], fg_name, desc)
    return redirect('/')


@app.route('/group/get', methods=['POST'])
@login_required
def get_group():
    fg_name = request.get_json().get('fg_name')
    owner_email = request.get_json().get('owner_email')
    _, content = get_friend_group(session['email'], fg_name, owner_email)
    return json.dumps(content)


@app.route('/group/members', methods=['POST'])
@login_required
def get_group_members():
    fg_name = request.get_json().get('fg_name')
    owner = request.get_json().get('owner_email')
    _, content = get_friend_group_members(session['email'], owner, fg_name)
    return json.dumps(content)


@app.route('/group/invite', methods=['POST'])
@login_required
def invite_group():
    fg_name = request.form['fg_name']
    owner_email = request.form['owner_email']
    fname = request.form['fname']
    lname = request.form['lname']
    add_friend(fname, lname, session['email'], owner_email, fg_name)
    return redirect('/')


@app.route('/group/leave', methods=['POST'])
@login_required
def leave_group():
    group = request.form['fg_name']
    owner_email = request.form['owner_email']
    remove_user_from_group(
        group=group, owner_email=owner_email, email=session['email'])
    return redirect('/')


@app.route('/group/best', methods=['POST'])
@login_required
def best_group():
    fg_name = request.form['fg_name']
    owner_email = request.form['owner_email']
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

    new_email = request.form.get('email') if request.form.get(
        'email') != db_email else None
    new_first = request.form.get('fname') if request.form.get(
        'fname') != db_first else None
    new_last = request.form.get('lname') if request.form.get(
        'lname') != db_last else None

    status = update_user(db_email, new_email=new_email,
                         new_first=new_first, new_last=new_last)

    if status[0]:
        if new_email:
            user = get_user(new_email)
        else:
            user = get_user(session['email'])

        session['email'] = user['email']
        session['fname'] = user['fname']
        session['lname'] = user['lname']

    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.secret_key = 'keyboardcat'
if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)

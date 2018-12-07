import pymysql.cursors
from hashlib import sha256

conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='PriCoSha',
                       password='YES',
                       db='PriCoSha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


def login_user(email, password):
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE email = %s and password = %s'
    password = sha256(password.encode('utf-8')).hexdigest()

    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    cursor.close()
    res = user is not None
    message = user if res else 'Invalid Username or Password'
    return res, message


def register_user(email, password, fname, lname):
    if len(email) > 20 or len(fname) > 20 or len(lname) > 20:
        return False, 'All field lengths must be less than 20 characters'

    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()

    if data:
        return False, 'User already exists'

    INSERT = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
    password = sha256(password.encode('utf-8')).hexdigest()
    cursor.execute(INSERT, (email, password, fname, lname))
    conn.commit()
    cursor.close()

    return True, 'User successfully registered'


def get_public_content():
    cursor = conn.cursor()
    query = ('SELECT item_id, email_post, post_time, file_path, item_name '
             'FROM ContentItem WHERE is_pub = TRUE AND post_time >= now() - '
             'INTERVAL 1 DAY ORDER BY post_time DESC')
    cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()
    return True, posts


def post_content(email_post, item_name, file_path, is_pub):
    cursor = conn.cursor()
    query = ('INSERT INTO ContentItem (email_post, post_time, file_path, '
             'item_name, is_pub) VALUES (%s, NOW(), %s, %s, %s)')
    cursor.execute(query, (email_post, file_path, item_name, is_pub))
    conn.commit()
    cursor.close()
    return True, 'Item Successfully Posted'


def get_my_content(email):
    cursor = conn.cursor()
    query = ('SELECT DISTINCT * FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub OR email_post=%s '
             'ORDER BY post_time DESC')
    cursor.execute(query, (email, email))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def get_content(email, item_id):
    cursor = conn.cursor()
    query = ('SELECT * FROM (SELECT * FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub OR email_post=%s) AS my_content WHERE item_id=%s')
    cursor.execute(query, (email, email, item_id))
    content = cursor.fetchall()
    cursor.close()
    if not content:
        return False, 'Item not visible or does not exist'
    return True, content[0]


def create_friend_group(owner_email, fg_name, description):
    cursor = conn.cursor()
    query = ('INSERT INTO Friendgroup'
             '(owner_email, fg_name, description) VALUES (%s, %s, %s)')
    cursor.execute(query, (owner_email, fg_name, description))
    conn.commit()
    cursor.close()
    return True, 'Successfully Created FriendGroup'

def get_my_friend_groups(email):
    cursor = conn.cursor()
    query = ('SELECT fg_name, owner_email FROM Friendgroup WHERE '
             'owner_email=%s UNION SELECT fg_name, owner_email '
             'FROM Belong WHERE email=%s')
    cursor.execute(query, (email, email))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def get_my_content_ids(email):
    cursor = conn.cursor()
    query = ('SELECT DISTINCT item_id FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub OR email_post=%s ')

    cursor.execute(query, (email, email))
    content = cursor.fetchall()

    cursor.close()
    return content, 'Successfully Got Content!'


def count_tags(item_id):
    cursor = conn.cursor()
    query = ('SELECT COUNT(*) FROM Tag WHERE item_id=%s')
    cursor.execute(query, (item_id))
    content = cursor.fetchall()
    cursor.close()
    return content, f'found tag number for item_id {item_id}'


def get_tags_from_item_id(item_id):
    cursor = conn.cursor()
    query = ('SELECT * FROM Tag WHERE item_id=%s')
    cursor.execute(query, (item_id))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def get_friend_group(email, fg_name, owner):
    cursor = conn.cursor()
    query = ('SELECT * FROM Friendgroup WHERE owner_email=%s AND fg_name=%s '
             'AND fg_name IN (SELECT fg_name FROM Friendgroup '
             'WHERE owner_email=%s UNION SELECT fg_name '
             'FROM Belong WHERE email=%s)')
    cursor.execute(query, (owner, fg_name, email, email))
    print('hello')
    content = cursor.fetchall()
    cursor.close()
    print(content)
    return True, content[0]

def get_emails_false_tags(email_tagged):
    cursor = conn.cursor()
    query = ("SELECT email_tagged from Tag WHERE status=FALSE " 
            "AND email_tagged=%s")
    cursor.execute(query, email_tagged)
    content = cursor.fetchall()
    cursor.close()
    return True, f"Successfully got tags where email_tagged {email_tagged}"


def get_friend_group_members(email, owner, fg_name):
    cursor = conn.cursor()
    query = ('SELECT email FROM Belong WHERE owner_email=%s AND fg_name=%s '
             'AND fg_name IN (SELECT fg_name FROM Friendgroup '
             'WHERE owner_email=%s UNION SELECT fg_name '
             'FROM Belong WHERE email=%s)')
    query = ('SELECT email FROM Belong WHERE owner_email=%s AND fg_name=%s')
    print(owner, fg_name)
    cursor.execute(query, (owner, fg_name))
    content = cursor.fetchall()
    cursor.close()
    print(content)
    return True, content


def accept_tag_on_content_item(email_tagged, email_tagger, item_id):
    cursor = conn.cursor()
    query = ('UPDATE Tag SET status=TRUE WHERE email_tagged=%s AND'
             'email_tagger=%s AND item_id=%s')
    cursor.execute(query, (email_tagged, email_tagger, item_id))
    conn.commit()
    cursor.close()
    return True, 'Successfully updated tag on content item'


def remove_tag_on_content_item(email_tagged, email_tagger, item_id):
    cursor = conn.cursor()
    query = ('DELETE FROM tag WHERE email_tagged=%s '
             'AND email_tagger=%s AND item_id=%s')
    cursor.execute(query, (email_tagged, email_tagger, item_id))
    conn.commit()
    cursor.close()
    return True, 'Successfully deleted content item'


def tag_content_item(email_tagged, email_tagger, item_id):
    visibility, _ = get_content(email_tagger, item_id)

    if not visibility:
        return False, 'ContentItem is not accessible to the current tagger'

    if email_tagged == email_tagger:
        query = ('INSERT INTO Tag '
                 '(email_tagged, email_tagger, item_id, status, tagtime) '
                 'VALUES (%s, %s, %s, TRUE, NOW())')
    else:
        query = ('INSERT INTO Tag '
                 '(email_tagged, email_tagger, item_id, status, tagtime) '
                 'VALUES (%s, %s, %s, FALSE, NOW())')

    cursor = conn.cursor()
    cursor.execute(query, (email_tagged, email_tagger, item_id))
    conn.commit()
    cursor.close()
    return True, 'Successfully tagged ContentItem'


def add_friend(fname, lname, email, owner_email, fg_name): 
    cursor = conn.cursor()
    query = ('SELECT fg_name FROM Friendgroup WHERE owner_email=%s')
    cursor.execute(query, (owner_email,))
    content = cursor.fetchall()
    print(content)
    if len([g for g in content if g['fg_name'] == fg_name]) == 0:
        print('Failed to insert -- not owner')
        return False, "You can only insert in groups you own"

    query = ('SELECT email FROM Person WHERE fname=%s AND lname=%s')
    cursor.execute(query, (fname, lname))

    content = cursor.fetchall()
    print(content)
    if not len(content):
        return False, "A Person with this email does not exist"
    if len(content) > 1:
        return False, "Multiple People with this name exist"

    print(content)
    new_member_email = content[0]['email']

    query = ("SELECT email from Belong WHERE owner_email=%s "
             "AND fg_name=%s")
    cursor.execute(query, (owner_email, fg_name))
    content = cursor.fetchall()
    print(content)
    if len([e for e in content if e['email'] == new_member_email]):
        print('Duplicate add')
        return False, "This Person is already in this friend group"

    query = ('INSERT into Belong (email, owner_email, fg_name) '
             'VALUES (%s, %s, %s)')

    cursor.execute(query, (new_member_email, owner_email, fg_name))
    conn.commit()
    cursor.close()
    print('Finished')
    return True, 'Successfully added user to friend group'


def get_my_tags(email):
    cursor = conn.cursor()
    query = ('SELECT * FROM Tag WHERE email_tagged=%s AND status=FALSE')
    cursor.execute(query, (email))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def filter_by_date(email, timestamp):
    cursor = conn.cursor()
    query = ('SELECT * FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub AND post_time=%s')
    cursor.execute(query, (email, timestamp))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def filter_by_group(email, fg_name):
    cursor = conn.cursor()
    query = ('SELECT * FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s '
             'AND fg_name=%s)')
    cursor.execute(query, (email, fg_name))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def share_with_group(email, fg_name, item_id):
    cursor = conn.cursor()
    insert = ('INSERT INTO Share VALUES ((SELECT owner_email from Belong '
              'WHERE email=%s), %s, %s)')
    cursor.execute(insert, (email, fg_name, item_id))
    conn.commit()
    cursor.close()
    return True, "Success"


# def get_pending_tag(user, action):
#     cursor = conn.cursor()
#     message = f'{action} for tag was successfully done!!'#     if action == 'accept':
#         status, query = (''),
#     elif action == 'decline':
#         status, query = (''),
#     elif action == 'remove':
#         status, query = ('')
#     else:
#         message = 'An action was not decided'
#         status, query = ('')
#
#     cursor.execute(query)
#     tag = cursor.fetchall()
#     cursor.close()
#     return status, tag


def get_user(email):
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE email=%s'
    cursor.execute(query, email)
    user = cursor.fetchone()
    cursor.close()
    return user


def update_user(email, new_email=None, new_first=None, new_last=None):
    cursor = conn.cursor()
    if new_email:
        query = 'SELECT * FROM Person WHERE email = %s'
        cursor.execute(query, new_email)
        data = cursor.fetchone()
        if data:
            return False, "User with that email already exists"
    parameters = ', '.join(list(filter(None, (
        'fname=%s' if new_first else None,
        'lname=%s' if new_last else None,
        'email=%s' if new_email else None,
    ))))
    values = tuple(filter(None, (new_first, new_last, new_email, email)))
    query = 'UPDATE Person SET ' + parameters + ' WHERE email=%s'
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    return True, 'Success'


def remove_user_from_group(group, owner_email, email):
    cursor = conn.cursor()
    query = 'SELECT * FROM Friendgroup WHERE fg_name = %s AND owner_email=%s'
    cursor.execute(query, (group, owner_email))
    data = cursor.fetchone()
    if not data:
        return False, "Group Doesn't Exist"

    query = 'SELECT * FROM Friendgroup WHERE fg_name = %s AND owner_email=%s'
    cursor.execute(query, (group, email))
    data = cursor.fetchone()
    if data:
        query = 'DELETE FROM Friendgroup WHERE fg_name=%s AND owner_email=%s'
        cursor.execute(query, (group, email))
        return True, "Success"

    query = 'DELETE FROM Belong WHERE fg_name=%s AND email=%s AND owner_email=%s'
    cursor.execute(query, (group, email, owner_email))
    conn.commit()
    cursor.close()
    return True, 'Success'


# def get_users(email):
#     cursor = conn.cursor()
#     query = 'SELECT DISTINCT email FROM blog'
#     cursor.execute(query)
#     users = cursor.fetchall()
#     cursor.close()
#
#     return users

def count_ratings_on_content(item_id):
    cursor = conn.cursor()
    query = ('SELECT count(item_id) FROM Rate WHERE ID = %s GROUP BY item_id')
    cursor.execute(query, (item_id))
    content = cursor.fetchall()
    cursor.close()
    return content, f"found rating number for item_id {item_id}"


def add_rating(rater_email, item_id, emoji):
    cursor = conn.cursor()
    query = ('INSERT INTO Rate VALUES(%s, %s, NOW(), %s)')
    cursor.execute(query, (rater_email, item_id, emoji))
    conn.commit()
    cursor.close()
    return True, "Success"


def add_comment(commenter_email, item_id):
    pass


def get_comments(item_id):
    pass

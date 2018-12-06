import pymysql.cursors
from hashlib import sha256

conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='PriCoSha',
                       password='PriCoSha',
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

    insert = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
    password = sha256(password.encode('utf-8')).hexdigest()
    cursor.execute(insert, (email, password, fname, lname))
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
             'item_name, is_pub) values (%s, NOW(), %s, %s, %s)')
    cursor.execute(query, (email_post, file_path, item_name, is_pub))
    conn.commit()
    cursor.close()
    return True, 'Item Successfully Posted'


def get_my_content(email):
    cursor = conn.cursor()
    query = ('SELECT * FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub ORDER BY post_time DESC')
    cursor.execute(query, (email))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def get_content(email, item_id):
    cursor = conn.cursor()
    query = ('SELECT * FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub AND item_id=%s')
    cursor.execute(query, (email, item_id))
    content = cursor.fetchall()
    cursor.close()
    if not content:
        return False, 'Item not visible or does not exist'
    return True, content[0]


def create_friend_group(owner_email, fg_name, description):
    cursor = conn.cursor()
    query = ('INSERT INTO Friendgroup'
             '(owner_email, fg_name, description) values (%s, %s, %s)')
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
    query = ('SELECT item_id FROM ContentItem WHERE'
             'item_id IN (SELECT item_id FROM Share INNER JOIN Belong ON'
             'Belong.fg_name=Share.fg_name AND'
             'Belong.owner_email=Share.owner_email AND Belong.email=%s))'
             'OR is_pub')

    cursor.execute(query, (email, ))
    content = cursor.fetchall()

    cursor.close()
    return content, 'Successfully Got Content!'

def remove_tag_on_content_item(email_tagged, email_tagger, item_id):
    cursor = conn.cursor()
    query = ("DELETE FROM Tag WHERE email_tagged=%s " +
            "AND email_tagger=%s AND item_id=%s")
    query.execute(query, (email_tagged, email_tagger, item_id))
    cursor.close()
    return True, "Successfully deleted content item"


def tag_content_item(email_tagged, email_tagger, item_id):
    my_ids, _ = get_my_content_ids(email_tagger)
    visibility = (item_id,) in get_my_content_ids(item_id)
    if not visibility:
        return None, 'ContentItem is not accessible to the current tagger'
    if email_tagged == email_tagger:
        query = ('INSERT INTO Tag' +
                 '(email_tagged, email_tagger, item_id, status, tagtime)' +
                 'values (%s, %s, %s, TRUE, NOW())')
    else:
        query = ('insert into tag' +
                '(email_tagged, email_tagger, item_id, status, tagtime) ' +
                'values (%s, %s, %s, FALSE, NOW())')

    query = ('INSERT INTO Tag'
             '(email_tagged, email_tagger, item_id, status, tagtime)'
             'values (%s, %s, %s, %s, NOW())')

    cursor = conn.cursor()
    cursor.execute(query, (email_tagged, email_tagger, item_id, status))
    content = cursor.fetchall()
    cursor.close()
    return content, 'Successfully Created FriendGroup'


def add_friend(email, owner_email, fg_name):
    cursor = conn.cursor()
    query = ('INSERT into Belong (email, owner_email, fg_name)'
             'VALUES (%s, %s, %s)')
    cursor.execute(query, (email, owner_email, fg_name))
    # TODO: err check here to see if primary key collisions?
    # if true rollback to prev state
    cursor.close()
    return True, 'Successfully added user to friend group'

def filter_by_date(email, timestamp):
    cursor = conn.cursor()
    query = ('SELECT * FROM ContentItem WHERE item_id IN ' +
             '(SELECT item_id FROM Share INNER JOIN Belong ON ' +
             'Belong.fg_name=Share.fg_name AND ' +
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) ' +
             'OR is_pub AND post_time=%s')
    cursor.execute(query, (email, timestamp))
    content = cursor.fetchall()
    cursor.close()
    return True, content

def filter_by_group(email, fg_name):
    cursor = conn.cursor()
    query = ('SELECT * FROM ContentItem WHERE item_id IN ' +
             '(SELECT item_id FROM Share INNER JOIN Belong ON ' +
             'Belong.fg_name=Share.fg_name AND ' +
             'Belong.owner_email=Share.owner_email AND Belong.email=%s '
             'AND fg_name=%s;')
    cursor.execute(query, (email, fg_name))
    content = cursor.fetchall()
    cursor.close()
    return True, content

# def get_pending_tag(user, action):
#     cursor = conn.cursor()
#     message = f'{action} for tag was successfully done!!'
#     if action == 'accept':
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



# def get_users(email):
#     cursor = conn.cursor()
#     query = 'SELECT DISTINCT email FROM blog'
#     cursor.execute(query)
#     users = cursor.fetchall()
#     cursor.close()
#
#     return users

import pymysql.cursors
from hashlib import sha256

conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='password',
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
    message = user if res else "Invalid Username or Password"
    return res, message


def register_user(email, password, fname, lname):
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()

    if data:
        return False, "User already exists"

    insert = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
    password = sha256(password.encode('utf-8')).hexdigest()
    cursor.execute(insert, (email, password, fname, lname))
    conn.commit()
    cursor.close()

    return True, "User successfully registered"


def get_public_content():
    cursor = conn.cursor()
    query = ('SELECT item_id, email_post, post_time, file_path, item_name ' +
             'FROM ContentItem WHERE is_pub = TRUE AND post_time <= now() + ' +
             'INTERVAL 1 DAY')
    cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()
    return True, posts


def post_content(email_post, item_name, file_path, is_pub):
    cursor = conn.cursor()
    query = ('INSERT INTO ContentItem (email_post, post_time, file_path, ' +
             'item_name, is_pub) values (%s, NOW(), %s, %s, %s)')
    cursor.execute(query, (email_post, file_path, item_name, is_pub))
    conn.commit()
    cursor.close()
    return True, "Item Sucessfully Posted"


def get_my_content(email):
    cursor = conn.cursor()
    query = "select * from ContentItem WHERE item_id in (select item_id from Share inner join Belong on Belong.fg_name=Share.fg_name AND Belong.owner_email =Share.owner_email AND Belong.email=%s)) OR is_pub"
    cursor.execute(query)
    content = cursor.fetchall()
    cursor.close()
    return content, "Successfully Got Content!"

def create_friend_group(owner_email, fg_name, description):
    cursor = conn.cursor()
    query = ("INSERT INTO Friendgroup" + 
            "(owner_email,fg_name,description) values (%s, %s, %s)")
    cursor.execute(query, (owner_email, fg_name, description))
    content = cursor.fetchall()
    cursor.close()
    return content, "Successfully Created FriendGroup"

def get_my_content_ids(email):
    cursor = conn.cursor()
    query = ("select item_id from ContentItem where" +
    "item_id in (select item_id from Share inner join Belong on" + 
    "Belong.fg_name=Share.fg_name AND Belong.owner_email =Share.owner_email AND Belong.email=%s)) OR is_pub")

    cursor.execute(query, (email, ))
    content = cursor.fetchall()

    cursor.close()
    return content, "Successfully Got Content!"

def tag_content_item(email_tagged, email_tagger, 
        item_id,status):

    my_ids, _ = get_my_content_ids(email_tagger)
    visibility = (item_id,) in get_my_content_ids(item_id)
    if not visibility:
        return None, "ContentItem is not accessible to the current tagger"
    query = ("INSERT INTO Tag" + 
    "(email_tagged, email_tagger, item_id, status, tagtime)" + "values (%s, %s, %s, %s, NOW())")
    cursor = conn.cursor()
    cursor.execute(query,(email_tagged,email_tagger,item_id,status))
    content = cursor.fetchall()
    cursor.close()
    return content, "Successfully Created FriendGroup"

def add_friend(email, owner_email, fg_name):
    cursor = conn.cursor()
    query = "INSERT into Belong (email, owner_email, fg_name) VALUES (%s, %s, %s)"
    cursor.execute(query, (email, owner_email, fg_name))
    # TODO: err check here to see if primary key collisions? if true rollback to prev state
    cursor.close()
    return True, "Successfully added user to friend group"


# def get_pending_tag(user, action):
#     cursor = conn.cursor()
#     message = f"{action} for tag was successfully done!!"
#     if action == "accept":
#         status, query = (""),
#     elif action == "decline":
#         status, query = (""),
#     elif action == "remove":
#         status, query = ("")
#     else:
#         message = "An action was not decided"
#         status, query = ("")
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


def remove_user_from_group(group, email):
    cursor = conn.cursor()
    query = 'SELECT * FROM Friendgroup WHERE fg_name = %s'
    cursor.execute(query, group)
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

    query = 'SELECT owner_email FROM Friendgroup WHERE fg_name=%s'
    cursor.execute(query, group)
    owner_email = cursor.fetchone()
    query = 'DELETE FROM Belong WHERE fg_name=%s AND email=%s AND owner_email=%s'
    cursor.execute(query, (group, email, owner_email))
    conn.commit()
    cursor.close()
    return True, 'Success'

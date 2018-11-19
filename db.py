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
    query = 'SELECT * FROM person WHERE email = %s and password = %s'
    password = sha256(password).hexdigest()

    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    res = data
    message = "Logged In!!" if res else "Not Logged In ):"
    return res


def register_user(email, password, fname, lname):
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()

    if data:
        return False, "User could not be registered"

    insert = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
    password = sha256(password).hexdigest()
    cursor.execute(insert, (email, password, fname, lname))
    conn.commit()
    cursor.close()

    return True, "User was successfully registered!"


def get_public_content():
    cursor = conn.cursor()
    query = ('SELECT item_id, email_post, post_time, file_path, item_name' +
             'FROM ContentItem WHERE is_pub = TRUE AND post_time >= now() + ' +
             'INTERVAL 1 DAY')
    cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()

    return posts


def get_my_content(friend_group):
    cursor = conn.cursor()
    query = (f'')
    cursor.execute(query)
    content = cursor.fetchall()
    cursor.close()
    return content, "Successfully Got Content!"


def get_pending_tag(user, action):
    cursor = conn.cursor()
    message = f"{action} for tag was successfully done!!"
    if action == "accept":
        status, query = (""), 
    elif action == "decline":
        status, query = (""), 
    elif action == "remove":
        status, query = ("")
    else:
        message = "An action was not decided"
        status, query = ("")
    
    cursor.execute(query)
    tag = cursor.fetchall()
    cursor.close()
    return status, tag

def post_content(email, item_id, 
        email_post, post_time, file_path, 
        item_name, is_pub ):
    cursor = conn.cursor()
    query = f'INSERT INTO ContentItem ({item_id},
    {email_post}, {post_time}, {file_path}, 
    {item_name}, {is_pub}) VALUES(%s, %s, %s, %s, %s, %s);'
    cursor.execute(query, (email, content))
    conn.commit()
    cursor.close()

    return "Item Sucessfully Posted", True


def tag_content(content, tagged):
    pass


def add_friend(user, friend):
    pass


# def get_users(email):
#     cursor = conn.cursor()
#     query = 'SELECT DISTINCT email FROM blog'
#     cursor.execute(query)
#     users = cursor.fetchall()
#     cursor.close()
#
#     return users

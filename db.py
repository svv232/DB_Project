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
    password = sha256(password.encode('utf-8')).hexdigest()

    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    return data


def register_user(email, password, fname, lname):
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()

    if data:
        return False

    insert = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
    password = sha256(password.encode('utf-8')).hexdigest()
    cursor.execute(insert, (email, password, fname, lname))
    conn.commit()
    cursor.close()

    return True


def get_public_content():
    cursor = conn.cursor()
    query = ('SELECT item_id, email_post, post_time, file_path, item_name' +
             'FROM ContentItem WHERE is_pub = TRUE AND post_time >= now() + ' +
             'INTERVAL 1 DAY')
    cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()

    return posts


def get_my_content():
    pass


def get_pending_tag():
    pass


def post_content(email, content):
    cursor = conn.cursor()
    query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
    cursor.execute(query, (email, content))
    conn.commit()
    cursor.close()

    return True


def tag_content(content, tagged):
    pass


def add_friend(friend):
    pass


# def get_users(email):
#     cursor = conn.cursor()
#     query = 'SELECT DISTINCT email FROM blog'
#     cursor.execute(query)
#     users = cursor.fetchall()
#     cursor.close()
#
#     return users

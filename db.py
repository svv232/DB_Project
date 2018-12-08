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
    return True, cursor.lastrowid, 'Item Successfully Posted'


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
             'FROM Belong WHERE email=%s AND fg_name != "Best Friends"')
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


def get_tags_from_item_id(email, item_id):
    cursor = conn.cursor()
    query = ('SELECT * FROM Tag WHERE item_id=%s AND status AND item_id IN '
             '(SELECT DISTINCT item_id FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub OR email_post=%s)')
    cursor.execute(query, (item_id, email, email))
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
    content = cursor.fetchall()
    cursor.close()
    return True, content[0]


def get_emails_false_tags(email_tagged):
    cursor = conn.cursor()
    query = ("SELECT email_tagged from Tag WHERE status=FALSE "
             "AND email_tagged=%s")
    cursor.execute(query, email_tagged)
    content = cursor.fetchall()
    cursor.close()
    return True, content


def get_friend_group_members(email, owner, fg_name):
    cursor = conn.cursor()
    query = ('SELECT email FROM Belong WHERE owner_email=%s AND fg_name=%s '
             'AND fg_name IN (SELECT fg_name FROM Friendgroup '
             'WHERE owner_email=%s UNION SELECT fg_name '
             'FROM Belong WHERE email=%s)')
    cursor.execute(query, (owner, fg_name, email, email))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def accept_tag_on_content_item(email_tagged, email_tagger, item_id):
    cursor = conn.cursor()
    query = ('UPDATE Tag SET status=TRUE WHERE email_tagged=%s AND '
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


def tag_group_members(owner_email, fg_name, email_tagger, item_id):
  query = ('SELECT email FROM Belong WHERE fg_name=%s AND owner_email=%s')
  cursor = conn.cursor()
  cursor.execute(query, (fg_name, owner_email))
  members = cursor.fetchall()
  print(members)
  for member in members:
      insert = ('INSERT INTO Tag '
                '(email_tagged, email_tagger, item_id, status, tagtime) '
                'VALUES(%s, %s, %s, FALSE, NOW())')
      cursor.execute(insert, (member, email_tagger, item_id))
  cursor.close()
  return True, "Success"


def check_tagged_group_post_visibility(owner_email, fg_name, item_id):
    query = ('SELECT email, status FROM Belong WHERE fg_name=%s AND owner_email=%s')
    cursor = conn.cursor()
    cursor.execute(query, (fg_name, owner_email))
    members = cursor.fetchall()
    group_visibility = True
    for member in members:
        group_visibility = group_visibility and member[0][1]
    cursor.close()
    return group_visibility


def tag_content_item(email_tagged, email_tagger, item_id):
    tagger_visible, _ = get_content(email_tagger, item_id)

    if not tagger_visible:
        return False, 'ContentItem is not accessible to the current tagger'

    tagged_visible, _ = get_content(email_tagged, item_id)

    if not tagged_visible:
        return False, 'ContentItem is not accessible to the tagged person'

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
    if len([g for g in content if g['fg_name'] == fg_name]) == 0:
        return False, "You can only insert in groups you own"

    query = ('SELECT email FROM Person WHERE fname=%s AND lname=%s')
    cursor.execute(query, (fname, lname))

    content = cursor.fetchall()
    if not len(content):
        return False, "A Person with this email does not exist"
    if len(content) > 1:
        return False, "Multiple People with this name exist"

    new_member_email = content[0]['email']

    query = ("SELECT email from Belong WHERE owner_email=%s "
             "AND fg_name=%s")
    cursor.execute(query, (owner_email, fg_name))
    content = cursor.fetchall()
    if len([e for e in content if e['email'] == new_member_email]):
        return False, "This Person is already in this friend group"

    query = ('INSERT into Belong (email, owner_email, fg_name) '
             'VALUES (%s, %s, %s)')

    cursor.execute(query, (new_member_email, owner_email, fg_name))
    conn.commit()
    cursor.close()
    return True, 'Successfully added user to friend group'


def get_my_tags(email):
    cursor = conn.cursor()
    query = ('SELECT * FROM Tag WHERE email_tagged=%s AND status=FALSE')
    cursor.execute(query, (email))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def filter_by_date(email):
    cursor = conn.cursor()
    query = ('SELECT * FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub ORDER BY post_time DESC')
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
    insert = ('INSERT INTO Share VALUES (%s, %s, %s)')
    cursor.execute(insert, (email, fg_name, item_id))
    conn.commit()
    cursor.close()
    return True, "Success"


def get_user(email):
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE email=%s'
    cursor.execute(query, email)
    user = cursor.fetchone()
    cursor.close()
    return user


def update_user(email, new_email=None, new_first=None, new_last=None):
    if not new_email and not new_first and not new_last:
        return False, "No parameters to update"
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

    query = ('DELETE FROM Belong WHERE fg_name=%s AND email=%s AND '
             'owner_email=%s')
    cursor.execute(query, (group, email, owner_email))
    conn.commit()
    cursor.close()
    return True, 'Success'


def ratings_on_content(email, item_id):
    cursor = conn.cursor()
    query = ('SELECT * FROM Rate WHERE item_id = %s and item_id in '
             '(SELECT DISTINCT item_id FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub OR email_post=%s)')
    cursor.execute(query, (item_id, email, email))
    content = cursor.fetchall()
    cursor.close()
    return True, content


def add_rating(rater_email, item_id, emoji):
    cursor = conn.cursor()
    check = ('SELECT emoji FROM Rate WHERE item_id =%s and email=%s')
    cursor.execute(check, (item_id, rater_email))
    content = cursor.fetchall()
    print(content)
    if not len(content):
        query = ('INSERT INTO Rate '
                 '(email, item_id, rate_time, emoji) '
                 'VALUES(%s, %s, NOW(), %s)')
        cursor.execute(query, (rater_email, item_id, emoji))
    else:
        query = ('UPDATE Rate SET emoji=%s WHERE item_id=%s')
        cursor.execute(query, (emoji, item_id))
    conn.commit()
    cursor.close()
    return True, "Success"


def add_comment(item_id, comment, commenter_email):
    # First check if item_id is actually visible to the commenter
    # First result of get_content is the status
    #   (whether it found anything or not)
    visible, _ = get_content(commenter_email, item_id)

    # Return if item_id is not visible
    if not visible:
        return False, 'ContentItem is not accessible to the current commenter'

    # Ensure that comment is not greater than DB VARCHAR
    if len(comment) > 256:
        return False, 'Comment is too long'

    # Execute the INSERT query
    cursor = conn.cursor()
    query = ('INSERT INTO Comment '
             '(item_id, comment, commenter_email, comment_time)'
             'VALUES(%s, %s, %s, NOW())')
    cursor.execute(query, (item_id, comment, commenter_email))
    conn.commit()
    cursor.close()

    # Should always work since error checks prior
    return True, "Success"


def create_best_friends_group(owner_email):
    res, _ = check_for_best_friends(owner_email)
    if not res:
        cursor = conn.cursor()
        query = ('INSERT INTO Friendgroup'
                 '(owner_email, fg_name, description, best_friend) VALUES (%s, %s, %s, TRUE)')

        cursor.execute(query, (owner_email, "Best Friends" , "This group contains your very best friends!"))
        conn.commit()
        cursor.close()
    return True, "Success"

def check_for_best_friends(owner_email):
    cursor = conn.cursor()
    query = 'SELECT * FROM Friendgroup WHERE owner_email=%s AND best_friend=TRUE'
    cursor.execute(query, (owner_email))
    result = cursor.fetchone()
    cursor.close()
    exists = result is not None
    message = "Best friends group does not exist" 
    if exists:
        message = "Success"
    return exists, message

def get_my_best_friend_group(email):
    cursor = conn.cursor()
    query = ('SELECT fg_name, owner_email FROM Friendgroup WHERE '
             '(owner_email=%s AND best_friend=TRUE) UNION SELECT fg_name, owner_email '
             'FROM Belong WHERE email=%s')
    cursor.execute(query, (email, email))
    content = cursor.fetchall()
    cursor.close()
    if not content:
        create_best_friends_group(email)
        return get_my_best_friend_group(email)
    return True, content

def get_best_friends(email):
    res, best_friend_group = get_my_best_friend_group(email)
    res, members = get_friend_group_members(email, email, best_friend_group[0]['fg_name'])
    return res, members

def get_comments(item_id, email):
    # Get comments but also check that item_id is visible to the user
    cursor = conn.cursor()
    query = ('SELECT * FROM Comment WHERE item_id=%s AND item_id IN '
             '(SELECT DISTINCT item_id FROM ContentItem WHERE item_id IN '
             '(SELECT item_id FROM Share INNER JOIN Belong ON '
             'Belong.fg_name=Share.fg_name AND '
             'Belong.owner_email=Share.owner_email AND Belong.email=%s) '
             'OR is_pub OR email_post=%s) ORDER BY comment_time DESC')
    cursor.execute(query, (item_id, email, email))
    content = cursor.fetchall()
    cursor.close()

    # Should always work, returns nothing in content if nothing found
    return True, content

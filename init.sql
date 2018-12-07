CREATE TABLE Comment (
    item_id int,
    comment VARCHAR(256),
    commenter_email VARCHAR(20),
    comment_id int AUTO_INCREMENT,
    comment_time Timestamp,
    PRIMARY KEY(comment_id, item_id, commenter_email),
    FOREIGN KEY(commenter_email) REFERENCES Person(email),
    FOREIGN KEY(item_id) REFERENCES ContentItem(item_id)
)

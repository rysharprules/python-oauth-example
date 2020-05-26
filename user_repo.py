from db import get_db
from user import User


def fetch_user(user_id):
    db = get_db()
    user = db.execute(
        "SELECT * FROM user where id = ?", (str(user_id),)
    ).fetchone()

    if not user:
        return None

    return User(
        user_id=user[0],
        name=user[1],
        profile_image=user[2]
    )


def create_user(user):
    db = get_db()
    db.execute(
        "INSERT INTO user (id, name, profile_image) "
        "VALUES (?, ?, ?) ",
        (user.id, user.name, user.profile_image)
    )
    db.commit()


def ensure_user_exists(user):
    if not fetch_user(user.id):
        create_user(user)

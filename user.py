from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, name, profile_image):
        self.id = user_id
        self.name = name
        self.profile_image = profile_image

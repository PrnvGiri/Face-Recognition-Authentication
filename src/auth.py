import os

class AuthSystem:
    def __init__(self):
        self.face_data_path = 'src/FaceData'
        self.default_password = 'INTELLIPAAT'

    def get_users(self):
        """Returns a set of valid usernames (folder names)."""
        if not os.path.exists(self.face_data_path):
            return set()
        
        users = set()
        for item in os.listdir(self.face_data_path):
            if os.path.isdir(os.path.join(self.face_data_path, item)):
                users.add(item)
        return users

    def verify_password(self, username, password):
        """
        Verifies if the user exists (has a folder) and password matches the default.
        Case-insensitive username check, but stored names are preferred.
        """
        valid_users = self.get_users()
        
        # Check if username exists (case-insensitive)
        user_exists = False
        for valid_user in valid_users:
            if valid_user.lower() == username.lower():
                user_exists = True
                break
        
        if user_exists and password == self.default_password:
            return True
        return False
        
    def user_exists(self, username):
        valid_users = self.get_users()
        for valid_user in valid_users:
            if valid_user.lower() == username.lower():
                return True
        return False


import random
import string

from .constants import SUPER_USER_ROLES

class UserClass:

    @staticmethod
    # This function validates the user dict having required keys or not
    def isValidUser(user):
        if type(user) ==  dict:
            return user.get('status').upper() ==  "ACTIVE"   
        return False

    @staticmethod
    def UserIsManagerOrIsOwner(user):
        # check if the user is owner and 
        if 'is_owner' in user and user['is_owner']:
            return True
        if 'is_manager' in user and user['is_manager']:
            return True
        return False

    @staticmethod
    def UserIsSuperUser(user):
        # check if the user is owner and 
        if UserClass.isValidUser(user):
            if  type(user['role']) == str and user['role'] in SUPER_USER_ROLES:
                return True
            elif type(user['role']) == list and any([role in SUPER_USER_ROLES for role in user['role']]):
                return True
        return False


class RandomStringGenerator:
    # This function generates random string
    @staticmethod
    def randomstring(stringLength = None):
        N = stringLength if stringLength else 12
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(N)])      
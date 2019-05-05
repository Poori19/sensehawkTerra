
def getAllTheWriteUsers(obj):
    users = []
    try:
        for eachUser in obj.writeUsers:
            users.append(eachUser['uid'])
    except Exception as e: 
        print(e)
    return users


def getAllTheReadUsers(obj):
    users = []
    try:
        for eachUser in obj.readUsers:
            users.append(eachUser['uid'])
    except Exception as e: 
        print(e)
    return users

def checkUserIsOwner(obj,user):

    if user.get('uid', None) and obj.owner.get('uid', None)  and user['uid'] == obj.owner['uid']:
        return True
    return False


def checkUserInReadUsers(obj,user):
    users = getAllTheReadUsers(obj)
    if user.get('uid', None) and user['uid'] in users:
        return True
    return False

def checkUserInWriteUsers(obj,user):
    users = getAllTheWriteUsers(obj)
    if user.get('uid', None) and user['uid'] in users:
        return True
    return False

def checkUserLabelInObjReadLables(obj,user):
    
    for label in list(user['labels']):
        if label in obj.readLabels:
            return True
    return False

def checkUserLabelInObjWriteLables(obj,user):
    try:
        for label in list(user['labels']):
            if label in obj.writeLabels:
                return True
    except Exception as e: 
        print(e)
    return False

def checkUserHasWritePermission(obj,user):
    if checkUserLabelInObjWriteLables(obj,user) or  checkUserInWriteUsers(obj,user):
        return True
    return False


def checkUserHasReadPermission(obj,user):
    
    if checkUserHasWritePermission(obj,user):
        return True
    if checkUserLabelInObjReadLables(obj,user) or checkUserInReadUsers(obj,user):
        return True
    return False




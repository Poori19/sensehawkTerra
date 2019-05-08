from .models import Organization,OrganizationGroup,OrganizationProject
from .serializers import OrganizationSerializer,OrganizationGroupSerializer,OrganizationProjectSerializer


class OrganizationMethods:

    @staticmethod
    def CreateOrUpdateOrg(orgDict):

        from .serializers import OrganizationSerializer
        # orgKeys =  ['description', 'active', 'owner', 'readUsers', 'writeUsers', 'readLabels', 'writeLabels' ]
        # orgKeysDefaultValue = {'owner' : {} , 'description':'Test Description', 'active':True,'readUsers':[], 'writeUsers':[], 'readLabels':[], 'writeLabels':[] }
        
        # for key in orgKeys:
        #     if key not in orgDict:
        #         orgDict[key] = orgKeysDefaultValue[key]

        # if not orgDict.get('owner', None):
        #     orgDict['owner'] = {}

        # update
        if Organization.objects.filter(uid = orgDict['uid']).exists():
            orgInstance = Organization.objects.filter(uid = orgDict['uid']).first()
            org = OrganizationSerializer(orgInstance,data =orgDict )
        # create
        else:
            org = OrganizationSerializer(data =orgDict )

        if org.is_valid():
            orgObj = org.save()
        else:
            return {'error':org.errors}
        return orgObj
       

class OrganizationGroupMethods:

    @staticmethod
    def CreateOrUpdateGroup(groupDict):

        # groupKeys =  ['uid','name', 'description', 'owner', 'active', 'readUsers', 'writeUsers', 'readLabels', 'writeLabels', 'containerView' ]
        # groupKeysDefaultValue = {'uid' : None, 'description':"test description", 'active':True, 'owner':{}, 'readUsers':[], 'writeUsers':[], 'readLabels':[], 'writeLabels':[], 'containerView':None }

        # for key in groupKeys:
        #     if key not in groupDict:
        #         groupDict[key] = groupKeysDefaultValue[key]

        # if not groupDict.get('owner', None):
        #     groupDict['owner'] = {}
        
        if 'description' in groupDict and not groupDict['description']:
            groupDict['description'] = 'test description'

        if OrganizationGroup.objects.filter(uid = groupDict['uid']).exists():
            groupInstance = OrganizationGroup.objects.filter(uid = groupDict['uid']).first()
            group = OrganizationGroupSerializer(groupInstance,data =groupDict )
        else:
            group = OrganizationGroupSerializer(data =groupDict )

        if group.is_valid():
            groupObj = group.save()
        else:
            return {'error':group.errors}
        return groupObj

        
    @staticmethod
    def GetGroupUidsUserHasWritePermission(user,org):
        # gets all the groups user has write permission  
        groupUids = []
        groups = OrganizationGroup.objects.filter(organization__in = org).values('uid', 'writeUsers', 'readUsers', 'readLabels', 'writeLabels')
        for group in groups:
            if (user['uid'] in list(map(lambda d: d['uid'], group['writeUsers']))) or (any( elem in group['writeLabels']  for elem in user['labels'])):
                groupUids.append(group['uid'])
        return groupUids

class OrganizationProjectMethods:

    @staticmethod
    def CreateOrUpdateProject(projectDict):
        
        # projectKeys =  ['uid','name','group', 'description', 'active', 'owner', 'readUsers', 'writeUsers', 'readLabels', 'writeLabels' ]
        # projectKeysDefaultValue = {'name':" ",'description':"test description", 'active':True, 'owner':{}, 'readUsers':{}, 'writeUsers':{}, 'readLabels':{}, 'writeLabels':{} }
        
        # if 'uid' in projectDict and 'group' in projectDict and projectDict['group']:
        #     for key in projectKeys:
        #         if key not in projectDict:
        #             projectDict[key] = projectKeysDefaultValue[key]

        #     if not projectDict.get('owner', None):
        #         projectDict['owner'] = []

        if OrganizationProject.objects.filter(uid = projectDict['uid']).exists():
            projectInstance = OrganizationProject.objects.filter(uid = projectDict['uid']).first()
            project = OrganizationProjectSerializer(projectInstance,data =projectDict )
        else:
            project = OrganizationProjectSerializer(data =projectDict )

        if project.is_valid():
            projectObj = project.save()
        else:
            return {'error':project.errors}

        return projectObj

       

    @staticmethod
    def GetProjectUidsUserHasWritePermission(user,org):
        # gets all the groups user has write permission  
        
        projectUids = []
        projects = OrganizationProject.objects.filter(group__organization__in = org).values('uid', 'writeUsers', 'readUsers', 'readLabels', 'writeLabels')
        for project in projects:
            if (user['uid'] in list(map(lambda d: d['uid'], project['writeUsers']))) or (any( elem in project['writeLabels']  for elem in user['labels'])):
                projectUids.append(project['uid'])
        return projectUids




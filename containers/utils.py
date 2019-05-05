from dependantmodels.models import ContainerView
from .serializers import ContainerViewSerializer

class ContainerViewMethods:

    @staticmethod 
    def CreateorUpdateContainerView(data):
        if data.get('uid', None):
            containerKeys =  ['uid','name', 'description', 'active', 'owner', 'readUsers', 'writeUsers', 'readLabels', 'writeLabels' ]
            containerKeysDefaultValue = {'description':'Test Description', 'active':True, 'owner':[], 'readUsers':[], 'writeUsers':[], 'readLabels':[], 'writeLabels':[] }
                
            for key in containerKeys:
                if key not in data:
                    data[key] = containerKeysDefaultValue[key]
            if not data.get('owner', None):
                data['owner'] = {}

            containerViews = ContainerView.objects.filter(uid = data['uid'])

            # update
            if containerViews.exists():
                containerInstance = containerViews.first()
                containerInstance.organizationgroup_set.remove(*containerInstance.organizationgroup_set.all())
                containerData = ContainerViewSerializer(containerInstance, data = data)
            # create
            else:
                containerData = ContainerViewSerializer(data = data)

            if containerData.is_valid():
                containerObj = containerData.save()
            else:
                return {'error':containerData.errors}
            return containerObj
        else:
            return {'error':'uid doesnot contain'}



        

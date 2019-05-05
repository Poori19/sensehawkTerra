class OrganizationProjectData:

    @staticmethod
    def sendUrls(data):
        Corekeys = ['thermalOrthoTiles', 'thermalDSM']
        mapkeys = {'thermalOrthoTiles': 'thermalOrthoTiles', 'thermalDSM': 'thermalOrthoTiles'}
        returnData = {}
        for corekey in Corekeys:
            if data.get(corekey): 
                dataElement = data.get(corekey)
                if not dataElement.get('service') and dataElement.get('path'):
                    returnData[mapkeys[corekey]] =  dataElement.get('path')
        return returnData
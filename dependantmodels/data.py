import boto3
from accounts.constants import SIGNED_URL_EXPIRATION_TIME
 
class AWSSignedUrl():

    @staticmethod
    def get_s3_connected(region):
        s3 = boto3.client('s3',region_name=region)
        return s3

    @staticmethod
    def get_signed_url(bucketName,key,region,expirationTime):

        s3 = AWSSignedUrl.get_s3_connected(region)
        returnUrl = ""
        try:
            url = s3.generate_presigned_url( 
                ClientMethod='get_object', 
                Params={ 
                    'Bucket': bucketName, 
                    'Key': key    
                    }, 
                ExpiresIn =  expirationTime
            )
            returnUrl = url
        except Exception as e: 
            print(str(e))
            
        return returnUrl

class OrganizationProjectData:

    @staticmethod
    def aws_get_signed_urls(dataElement):
        url = ""
        if dataElement.get('bucket') and dataElement.get('key'):
            url = AWSSignedUrl.get_signed_url(dataElement.get('bucket'),dataElement.get('key'),dataElement.get('region') ,SIGNED_URL_EXPIRATION_TIME)
        
        return url

    @staticmethod
    def send_urls_and_pre_signed_urls_data(data):
        
        dataList = [{'name': eachData.get('report_type'), 'service': eachData.get('service')} for eachData in data]    
        returnData = {}

        for dataElement in dataList:
            name = dataElement.get('name')
            if dataElement.get('service', {}).get('name') == 'aws_s3':
                returnData[name] = OrganizationProjectData.aws_get_signed_urls(dataElement.get('service'))

        return returnData
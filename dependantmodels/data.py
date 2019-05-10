import boto3, botocore 
from botocore.client import Config 
from accounts.constants import SIGNED_URL_EXPIRATION_TIME,PRE_SIGNED_URL_REPORTSTYPE,ORTHO_TILES_URL
import environ
env = environ.Env()

class AWSSignedUrl():

    @staticmethod
    def get_aws_session():
        session = boto3.session.Session(aws_access_key_id = env.str('aws_access_key_id'), aws_secret_access_key = env.str('aws_secret_access_key')) 
        return session

    @staticmethod
    def get_s3_connected(region):
        session = AWSSignedUrl.get_aws_session()
        s3 = session.client('s3', config=Config(signature_version='s3v4', region_name=region)) 
        return s3

    # @staticmethod
    # def get_s3_connected(region):
    #     s3 = boto3.client('s3',region_name=region)
    #     return s3

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

        #dataList = [{'report_type': eachData.get('report_type'), 'service': eachData.get('service')} for eachData in data if eachData.get('report_type') in PRE_SIGNED_URL_REPORTSTYPE ]    
        returnData = {}
        for reportType in PRE_SIGNED_URL_REPORTSTYPE:
            returnData[reportType] = {}
            dataElement = data.get(reportType,None)
            if dataElement:
                eachReturnData = {}
                eachReturnData['uid'] = dataElement.get('uid',None)
                eachReturnData['name'] = dataElement.get('name',None)

                service = dataElement.get('service',{})
                if service.get('name',None) == 'aws_s3':
                    eachReturnData['url'] = OrganizationProjectData.aws_get_signed_urls(service)
                if reportType in ['orthotiles']:
                    eachReturnData['tile_url'] =  ORTHO_TILES_URL + dataElement.get('uid')
                returnData[reportType] = eachReturnData
        return returnData
import logging
import json
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeVSwitchesRequest import DescribeVSwitchesRequest
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupsRequest import DescribeSecurityGroupsRequest
from aliyunsdkecs.request.v20140526.RunCommandRequest import RunCommandRequest
from aliyunsdkecs.request.v20140526.DeleteInstancesRequest import DeleteInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeInstanceAttributeRequest import DescribeInstanceAttributeRequest
from aliyunsdkecs.request.v20140526.InvokeCommandRequest import InvokeCommandRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s [%(levelname)s]: %(message)s",
                    datefmt='%m-%d %H:%M')

logger = logging.getLogger()

def get_default_credential():
    return AccessKeyCredential('%ACCESS_KEY%', '%ACCESS_SECRET%')

def get_client(region_id="ap-southeast-1"):
    credentials = get_default_credential()
    return AcsClient(region_id=region_id, credential=credentials)

def do_action_return_json(client, request):
    response = client.do_action_with_exception(request)
    json_reponse = json.loads(str(response, encoding='utf-8'))
    return json_reponse

class InstanceSettings:
    def __init__(self):
        pass

    def set_system_disk_size(self, system_disk_size):
        self.system_disk_size = system_disk_size
        
    def set_system_disk_performance_level(self, system_disk_performance_level):
        self.system_disk_performance_level = system_disk_performance_level

    def set_system_disk_category(self, system_disk_category):
        self.system_disk_category = system_disk_category

    def set_instance_type(self, instance_type):
        self.instance_type = instance_type
    
    def set_dns_rr(self, dns_rr):
        self.dns_rr = dns_rr

    def set_tag_key(self, tag_key):
        self.tag_key = tag_key

    def set_tag_value(self, tag_value):
        self.tag_value = tag_value
        
    def set_default_region(self, default_region):
        self.default_region = default_region
    
    def set_security_group_id(self, security_group_id):
        self.security_group_id = security_group_id

    def set_vswitch_id (self, vswitch_id):
        self.vswitch_id = vswitch_id

    def set_vswitch_id (self, vswitch_id):
        self.vswitch_id = vswitch_id

    def set_host_name (self, host_name):
        self.host_name = host_name

    def set_image_id(self, image_id):
        self.image_id = image_id
    
    def set_password(self, password):
        self.password = password

    def set_spot_strategy(self, spot_strategy):
        self.spot_strategy = spot_strategy

def run_instance(settings:InstanceSettings):
    client = get_client()
    run_instances_request = RunInstancesRequest()
    run_instances_request.set_accept_format('json')
    run_instances_request.set_ImageId(settings.image_id)
    run_instances_request.set_InstanceType(settings.instance_type)
    run_instances_request.set_SystemDiskCategory(settings.system_disk_category)
    run_instances_request.set_SystemDiskPerformanceLevel(settings.system_disk_performance_level)
    run_instances_request.set_SystemDiskSize(settings.system_disk_size)
    run_instances_request.set_SecurityGroupId(settings.security_group_id)
    run_instances_request.set_VSwitchId(settings.vswitch_id)
    run_instances_request.set_InstanceName(settings.host_name)
    run_instances_request.set_InternetMaxBandwidthOut(100)
    run_instances_request.set_HostName(settings.host_name)
    run_instances_request.set_Password(settings.password)
    run_instances_request.set_SpotStrategy(settings.spot_strategy)
    run_instances_request.set_Tags([
    {
        "Key": settings.tag_key,
        "Value": settings.tag_value
    }
    ])

    run_instances_response = client.do_action_with_exception(run_instances_request)
    run_instances_response_json = json.loads(str(run_instances_response, encoding='utf-8'))
    instance_id = run_instances_response_json['InstanceIdSets']['InstanceIdSet'][0]

    return instance_id

def delete_instance_if_exists():
    client = get_client()
    running_inst = get_running_instance()

    if running_inst == None:
        return

    delete_instance_request = DeleteInstancesRequest()
    delete_instance_request.set_accept_format('json')
    delete_instance_request.set_InstanceIds([running_inst["InstanceId"]])
    delete_instance_request.set_Force(True)

    delete_instance_response = client.do_action_with_exception(delete_instance_request)


def get_default_vswitch_id():
    client = get_client()
    request = DescribeVSwitchesRequest()
    request.set_accept_format('json')
    json_response = do_action_return_json(client, request)

    if len(json_response['VSwitches']['VSwitch']):
        return json_response['VSwitches']['VSwitch'][0]['VSwitchId']
    
    return 'na'

def get_default_security_group_id():
    client = get_client()
    request = DescribeSecurityGroupsRequest()
    request.set_accept_format('json')
    json_response = do_action_return_json(client, request)

    if len(json_response['SecurityGroups']['SecurityGroup']):
        return json_response['SecurityGroups']['SecurityGroup'][0]['SecurityGroupId']
    
    return None

def run_command(instance_id, cmdcontent):
    try:
        client = get_client()
        request = RunCommandRequest()
        request.set_accept_format('json')
        request.set_Type("RunShellScript")
        request.set_CommandContent(cmdcontent)
        request.set_InstanceIds([instance_id])
        request.set_Timeout(600)
      
        response = client.do_action_with_exception(request)
        invoke_id = json.loads(response).get("InvokeId")
        return invoke_id
      
    except Exception as e:
        logger.error("run command failed")

def get_running_instance():
    client = get_client()
    describe_instance_request = DescribeInstancesRequest()
    describe_instance_request.set_accept_format('json')
    describe_instance_request.set_Tags([
    {
        "Key": "role",
        "Value": "proxy-node"
    }
    ])

    describe_instance_response = client.do_action_with_exception(describe_instance_request)
    json_reponse = json.loads(str(describe_instance_response, encoding='utf-8'))

    instances = json_reponse['Instances']['Instance']

    if len(instances) < 1:
        return None
    else:
        return {
          "InstanceId": instances[0]['InstanceId'],
          "PublicIpAddress": instances[0]['PublicIpAddress']['IpAddress'][0]
        }
      
def create_default_settings():
    default_vswitch_id = get_default_vswitch_id()
    default_security_group_id = get_default_security_group_id()

    settings = InstanceSettings()
  
    settings.set_security_group_id(default_security_group_id)
    settings.set_vswitch_id(default_vswitch_id)

    settings.set_tag_key('role')
    settings.set_tag_value('proxy-node')
    settings.set_default_region('ap-southeast-1')
    settings.set_host_name('sg-001')
    settings.set_image_id("aliyun_3_x64_20G_qboot_alibase_20230727.vhd")
    settings.set_password("Aliyun$2022!")
    settings.set_instance_type("ecs.g6.xlarge")
    settings.set_system_disk_size(80)
    settings.set_system_disk_category("cloud_essd")
    settings.set_system_disk_performance_level("PL0")
    settings.set_spot_strategy("NoSpot")
    
    return settings

CMD_INSTALL_DOCKER = """
#!/bin/bash
yum install epel-release -y
yum install docker -y
systemctl start docker
"""

def stop():
    delete_instance_if_exists()

def start():
    settings = create_default_settings()
    delete_instance_if_exists() 
    run_instance(settings)

    # wait for init
    time.sleep(30)
    
    inst = get_running_instance()
    run_command(inst["InstanceId"], CMD_INSTALL_DOCKER)
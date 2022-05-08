import logging
import random
import dotenv
import grpc
import config_pb2
import config_pb2_grpc
from datetime import datetime
import json 
import os

dotenv_file=dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

def run():
    with grpc.insecure_channel('192.168.0.21:50055') as channel: 
        stub = config_pb2_grpc.ConfigStub(channel)
        response = stub.GetConfigDetails(config_pb2.getConfigRequest(dummy='')) 
        config_deets=json.loads(response.configdetails)
        print(type(config_deets))
        for item, val in config_deets.items():
            os.environ[item] = val
            dotenv.set_key(dotenv_file, item, os.environ[item])
    
    with grpc.insecure_channel('192.168.0.21:50055') as channel: 
        stub = config_pb2_grpc.ConfigStub(channel)
        response = stub.RemoveOrderHost(config_pb2.removeOrderHostRequest(value='4')) 
        print(response.status)

    with grpc.insecure_channel('192.168.0.21:50055') as channel:
        stub = config_pb2_grpc.ConfigStub(channel)
        response = stub.AddToConf(config_pb2.addToConfRequest(keyName='LEADER',value='192.168.0.16:50060',order_host_id='10')) 
        print(response.status)


if __name__ == '__main__':
    logging.basicConfig()
    run()
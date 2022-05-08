import logging
import random
import dotenv
import grpc
import config_pb2
import config_pb2_grpc
import catalog_pb2
import catalog_pb2_grpc
import order_pb2
import order_pb2_grpc
import frontend_pb2
import frontend_pb2_grpc
from datetime import datetime
import json 
import os

dotenv_file=dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

def run():
    with grpc.insecure_channel('192.168.0.21:50051') as channel: 
        stub = catalog_pb2_grpc.CatalogStub(channel)
        response = stub.LeaderNotification(catalog_pb2.LeaderNotificationRequest(leaderaddress='192.168.0.21:50050')) 
        # config_deets=json.loads(response.configdetails)
        print("LeaderNotification status: ",response.status)

        response = stub.Query(catalog_pb2.QueryRequest(toy='Tux')) 
        print("Query status: ",response.status)
        toy='Whale'
        num=5
        response = stub.Update(catalog_pb2.UpdateRequest(toy=toy, num=num)) 
        print("Update status: ",response.status)

if __name__ == '__main__':
    logging.basicConfig()
    run()
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from threading import *
import logging
from concurrent import futures
from datetime import datetime
import grpc
# from frontend_microservice.frontend_pb2_grpc import CacheServicer
# import frontend_pb2
# import frontend_pb2_grpc
import order_pb2
import order_pb2_grpc
# import catalog_pb2
# import catalog_pb2_grpc
import config_pb2
import config_pb2_grpc
import dotenv

global lock
order_host_var = "ORDER_HOST"
leader_ip = "LEADER_IP"
leader_id = "LEADER_ID"
frontend_host_var = "FRONTEND_HOST"
catalog_host_var = "CATALOG_HOST"
leader_var = "LEADER"
lock = Lock()

global dotenv_file 
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

class Config():
    
    def AddToConf(self, request, context):
        lock.acquire()
        keyName, value, order_host_id = request.keyName, request.value, request.order_host_id
        leader_id_to_send, leader_ip_to_send = "", ""
        ip_str = context.peer()
        ip = ip_str.split(":")[1]
        ip_with_port = ip + ":" + value
        status = 0
        if keyName == leader_var:
            # set leader vars
            # lock.acquire()
            if value == "" or order_host_id == "":
                os.environ[leader_id] = ""
                os.environ[leader_ip] = ""
            else:
                os.environ[leader_id] = order_host_id
                os.environ[leader_ip] = value

            dotenv.set_key(dotenv_file, leader_id, os.environ[leader_id])
            dotenv.set_key(dotenv_file, leader_ip, os.environ[leader_ip])
            # lock.release()
            status=1
        elif keyName == order_host_var:
            print("Connected, in AddToConf: order host adding")
            # add to order_host, assuming value in format of {ID:IP}
            order_host_to_add_ = {order_host_id:ip_with_port}
            order_host_to_add = json.dumps(order_host_to_add_)
            hosts = json.loads(os.environ[order_host_var])
            hosts.update(order_host_to_add_)
            os.environ[order_host_var] = json.dumps(hosts)
            # lock.acquire()
            dotenv.set_key(dotenv_file, order_host_var, os.environ[order_host_var])
            # lock.release()
            if os.environ[leader_ip] != '':
                leader_id_to_send = os.environ[leader_id]
                leader_ip_to_send = os.environ[leader_ip]
                with grpc.insecure_channel(leader_ip_to_send) as channel:
                    stub = order_pb2_grpc.OrderStub(channel)
                    start = datetime.now()
                    print("Before GiveFollowersNodesInfo")
                    hosts_json = json.dumps(hosts)
                    response = stub.GiveFollowersNodesInfo(order_pb2.FollowersNodesInfoRequest(nodes = hosts_json)) 
                    print("After GiveFollowersNodesInfo")
                    end = datetime.now()
                status=1
            # lock.acquire()
            dotenv.set_key(dotenv_file, order_host_var, os.environ[order_host_var])
            # lock.release()
        else:
            print("Updating env: ", ip_with_port, " keyName: ", keyName)
            os.environ[keyName] = ip_with_port
            status=1
            # lock.acquire()
            dotenv.set_key(dotenv_file, keyName, os.environ[keyName])
        lock.release()
        
        return config_pb2.addToConfReply(status=status,leaderid=leader_id_to_send, leaderip=leader_ip_to_send)
    
    def RemoveOrderHost(self, request, context):
        id_remove = request.value
        hosts = json.loads(os.environ[order_host_var])
        status = 0
        if id_remove in hosts.keys():
            del hosts[id_remove]
            status = 1
            hosts_ = json.dumps(hosts)
            lock.acquire()
            os.environ[order_host_var] = hosts_
            dotenv.set_key(dotenv_file, order_host_var, os.environ[order_host_var])
            lock.release()
        else:
            status = 0
        
        return config_pb2.removeOrderHostReply(status=status)

    def GetConfigDetails(self, request, context):
        lock.acquire()
        dotenv.load_dotenv(dotenv_file)
        json_config = {}
        json_config[catalog_host_var] = os.environ[catalog_host_var]
        json_config[order_host_var] = os.environ[order_host_var]
        json_config[frontend_host_var] = os.environ[frontend_host_var]
        json_config[leader_id] = os.environ[leader_id]
        json_config[leader_ip] = os.environ[leader_ip]
        json_config_packet = json.dumps(json_config)
        lock.release()
        return config_pb2.getConfigDetailsReply(configdetails=json_config_packet)


def startConfig():
    lock.acquire()
    dotenv.set_key(dotenv_file, order_host_var, "{}")
    dotenv.set_key(dotenv_file, catalog_host_var, "")
    dotenv.set_key(dotenv_file, frontend_host_var, "")
    dotenv.set_key(dotenv_file, leader_id, "")
    dotenv.set_key(dotenv_file, leader_ip, "")
    dotenv.load_dotenv(dotenv_file)
    lock.release()
    return


def serve():
    print("Config service up and running")
    # print(os.environ['HOME'])
    startConfig()
    # print(os.environ['HOME'])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    config_pb2_grpc.add_ConfigServicer_to_server(Config(), server)
    server.add_insecure_port('[::]:50055')
    server.start()
    server.wait_for_termination()


if __name__=='__main__':
	
	# catalog_host = "localhost"
	logging.basicConfig()
	serve() 


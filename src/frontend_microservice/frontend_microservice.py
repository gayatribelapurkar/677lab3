#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import grpc
# from frontend_microservice.frontend_pb2_grpc import CacheServicer
import frontend_pb2
import frontend_pb2_grpc
import order_pb2
import order_pb2_grpc
import catalog_pb2
import catalog_pb2_grpc
import config_pb2
import config_pb2_grpc
import dotenv
import config_pb2
import config_pb2_grpc
from threading import *
from concurrent import futures
import datetime 
import time

# HOST = "192.168.0.21"
PORT = 8000
# PORT_GRPC = 9000
global order_leader_lock
order_leader_lock = Lock()
leader_ID = None
leader_IP = None

global lock
lock = Lock()

global cache_lock
cache_lock = Lock()

# catalog_host = os.getenv("CATALOG_HOST", "catalog") #for containerization
# order_host = os.getenv("ORDER_HOST", "order") #for containerization
global cache
cache = {}
# catalog_host = "localhost" #without containerization, give IP of catalog
# catalog_host = "192.168.0.21"
# order_host = "localhost"
config_host = "192.168.0.21:50055"  #without containerization, give IP of order
order_host_env = "ORDER_HOST"
catalog_host_env = "CATALOG_HOST"
frontend_host_var = "FRONTEND_HOST"
leader_id_var = "LEADER_ID"
leader_ip_var = "LEADER_IP"
order_leader = None
leader_IP = None
leader_ID = None
global dotenv_file
dotenv_file = None
global port_grpc
port_grpc = None

# status
# -2: invalid toy
# 0: toy out of stock
# -1: not as many toys in stock as you want to buy
# 1: buy successful 
class Cache(frontend_pb2_grpc.CacheServicer):
    def InvalidateCache(self, request, context):
        global cache
        print("Cache invalidated")
        print("Received: ", request.toylist)
        lis=json.loads(request.toylist)
        print(lis)
        lis = lis['1']
        print("Received: ", lis)
        cache_lock.acquire()
        print("Cache before: ", cache)
        #remove from cache
        for toy in lis:
            if toy in cache.keys():
                del cache[toy]
        print("Cache after: ", cache)
        cache_lock.release()
        status=1
        return frontend_pb2.InvalidateReply(status=status)

class requestHandler(BaseHTTPRequestHandler):

    def _set_response(self, code):
        # print(self.request_version)
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        # self.send_header("Connection", "keep-alive")
        # self.send_header("keep-alive", "timeout=1, max=2")
        self.end_headers()

    def do_GET(self):
        print(self.path)
        global cache
        path = self.path.split("/")
        i = 0
        while path[i] == "":
            path.pop(0)
        print(path)
        print("Cache at this instant: ", cache)
        if path and path[0] == "products":
            if path[1]:
                product = path[1]
                cache_lock.acquire()
                if product not in cache.keys():
                    
                # if product_cache == "":
                    #get details from catalog microservice, update in cache and send it to the client
                    print("Getting data from catalog microservice")
                    catalog_channel = os.environ[catalog_host_env] #code for containerized execution
                    # , options=(('grpc.enable_http_proxy', 0),)
                    with grpc.insecure_channel(catalog_channel) as channel: 
                        stub = catalog_pb2_grpc.CatalogStub(channel)
                        response = stub.Query(catalog_pb2.QueryRequest(toy=product)) 

                        price = response.price
                        quantity = response.quantity

                        if quantity == -1:
                            #send error response for poorly formed request
                            send_resp = {"error": {"code": 404, "message": "product not found"}}
                            json_response = json.dumps(send_resp)
                            self._set_response(404)
                            # message = "Product not found"
                            self.wfile.write(bytes(json_response, "utf8"))

                        else:
                            self._set_response(200)
                            cache[product] = (price, quantity)
                            send_resp = {"data": {"name": product, "price": price, "quantity": quantity}}
                            json_response = json.dumps(send_resp)
                            # message = "Hello, World! Here is a GET response"
                            self.wfile.write(bytes(json_response, "utf8"))
                else:
                    #if product exists in cache
                    print("Getting data from cache")
                    product_cache = cache.get(product)
                    self._set_response(200)
                    price, quantity = product_cache[0], product_cache[1]
                    print("Data in cache: ", cache.get(product), " price: ", price, " quantitiy: ", quantity)
                    send_resp = {"data": {"name": product, "price": price, "quantity": quantity}}
                    json_response = json.dumps(send_resp)
                    # message = "Hello, World! Here is a GET response"
                    self.wfile.write(bytes(json_response, "utf8"))
                cache_lock.release()
                
            else:
                #send error response for poorly formed request
                send_resp = {"error": {"code": 404, "message": "Malformed get request"}}
                json_response = json.dumps(send_resp)

                self._set_response(404)

                # message = "Product not found"
                self.wfile.write(bytes(json_response, "utf8"))
        
        elif path and path[0] == "orders":
            if path[1]:
                print(path)
                print(type(path))
                print(type(path[1]))
                order_number = int(path[1])

                # Tester code for client frontend communication
                # self._set_response(200)
                # ordernum_recv = 1
                # order_name = "Test"
                # order_quantity = 100
                # send_resp = {"data": {"order_number": ordernum_recv, "name": order_name, "quantity": order_quantity}}
                # json_response = json.dumps(send_resp)
                # self.wfile.write(bytes(json_response, "utf8"))
                lock.acquire()
                leader_IP = os.environ["LEADER_IP"] 
                while leader_IP == "":
                    utils = Utils()
                    utils.electNewLeader()
                    leader_IP = os.environ["LEADER_IP"]
                    # , options=(('grpc.enable_http_proxy', 0),)
                print("Sending order details request to: ", leader_IP)
                with grpc.insecure_channel(leader_IP) as channel: 
                    stub = order_pb2_grpc.OrderStub(channel)
                    response = stub.GetOrderDetails(order_pb2.GetOrderDetailsRequest(ordernum=order_number))

                    ordernum_recv = response.ordernum
                    order_name = response.name
                    order_quantity = response.quantity
                    print("Received details: ", ordernum_recv, " ", order_name, " ", order_quantity)

                    if ordernum_recv == -1:
                        #send error response for order not found
                        send_resp = {"error": {"code": 404, "message": "order not found"}}
                        json_response = json.dumps(send_resp)
                        self._set_response(404)
                        self.wfile.write(bytes(json_response, "utf8"))

                    elif ordernum_recv == order_number:
                        self._set_response(200)
                    
                        send_resp = {"data": {"order_number": str(ordernum_recv), "name": order_name, "quantity": str(order_quantity)}}
                        json_response = json.dumps(send_resp)
                        # message = "Hello, World! Here is a GET response"
                        self.wfile.write(bytes(json_response, "utf8"))

                    else:
                        #if some other order's data is received due to some error
                        send_resp = {"error": {"code": 404, "message": "Some error oocurred"}}
                        json_response = json.dumps(send_resp)
                
                lock.release()
                
            else:
                #send error response for poorly formed request
                send_resp = {"error": {"code": 404, "message": "Malformed get request"}}
                json_response = json.dumps(send_resp)
                self._set_response(404)
                # message = "Product not found"
                self.wfile.write(bytes(json_response, "utf8"))
              
        else:
            #send error response for poorly formed request
            send_resp = {"error": {"code": 404, "message": "product not found"}}
            json_response = json.dumps(send_resp)

            self._set_response(404)

            # message = "Product not found"
            self.wfile.write(bytes(json_response, "utf8"))


    def do_POST(self):
        path = self.path.split("/")
        i = 0
        while path[i] == "":
            path.pop(0)
        print(path)
        if path and path[0] == "orders":

            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
            print(type(data))
            product = data["name"]
            quantity = data["quantity"]
            is_request_sent_successfully = False
            response = None
            lock.acquire()
            while not is_request_sent_successfully:
                order_leader_lock.acquire()
                leader_IP = os.environ["LEADER_IP"]
                order_channel = leader_IP
                order_leader_lock.release()
                leader_is_alive = False
                # , options=(('grpc.enable_http_proxy', 0),)
                try:
                    with grpc.insecure_channel(order_channel) as channel: 
                        stub = order_pb2_grpc.OrderStub(channel)
                        # time_sent = datetime.datetime.now()
                        # end_time = time_sent + datetime.timedelta(seconds=5)
                        response = stub.Buy(order_pb2.BuyRequest(toy = product, num = quantity)) #For buy requests, response will store the status i.e 1,0 or -1 representing buy request successful, item out of stock and invalid item respectively
                        leader_is_alive = True
                        is_request_sent_successfully = True
                except:
                    try:
                        ping = stub.IsAlive(order_pb2.IsAliveRequest(alivereq = "Are you alive?"))
                        if ping:
                            continue
                    except:
                        utils = Utils()
                        utils.electNewLeader()
                        
                    print("Received: ", product, ", ", quantity)

            status = response.status
            order_number = response.ordernum
            order_name = response.name
            order_quantity = response.quantity
            if status == 0:
                #item out of stock
                send_resp = {"error": {"code": 404, "message": "Item out of stock"}}
                json_response = json.dumps(send_resp)
                self._set_response(404)
                self.wfile.write(bytes(json_response, "utf8"))
            
            elif status == -1:
                #buy unsuccessful
                send_resp = {"error": {"code": 404, "message": "Buy unsuccessful, there aren't as many toys as you requested to buy"}}
                json_response = json.dumps(send_resp)
                self._set_response(404)
                self.wfile.write(bytes(json_response, "utf8"))
            
            elif status == -2:
                #buy unsuccessful
                send_resp = {"error": {"code": 404, "message": "Buy unsuccessful, invalid toy name"}}
                json_response = json.dumps(send_resp)
                self._set_response(404)
                self.wfile.write(bytes(json_response, "utf8"))

            else:
                #successful buy
                self._set_response(200)
                post_response = {"data": {"order_number": order_number, "name": order_name, "quantity": order_quantity}}
                json_response = json.dumps(post_response)
                self.wfile.write(bytes(json_response, "utf8"))
            lock.release()
        else:
            send_resp = {"error": {"code": 404, "message": "Malformed post request"}}
            json_response = json.dumps(send_resp)

            self._set_response(404)

            # message = "Product not found"
            self.wfile.write(bytes(json_response, "utf8"))

class Utils:

    def ping(self, order_channel):
        with grpc.insecure_channel(order_channel) as channel: 
            stub = order_pb2_grpc.OrderStub(channel)
            try:
                ping = stub.IsAlive(order_pb2.IsAliveRequest(alivereq = "Are you alive?"))
                if ping:
                    return True
                return False
            except:
                return False
                
     
    def electNewLeader(self):

        self.getEnv(port_grpc)
        out_json = self.getEnvVar(order_host_env)
        hosts = json.loads(out_json)
        list_ids = [int(key) for key in hosts]
        list_ids.sort(reverse = True)
        new_list_ids = list_ids.copy()
        leader_elected = False
        print(list_ids)
        for host_id in list_ids:
            print("Host pinging: ", host_id)
            if self.ping(hosts[str(host_id)]) == True:
                #set leader as this host_id and save in env
                leader_elected = True
                json_packet = {host_id: hosts[str(host_id)]}
                json_ = json.dumps(json_packet)
                order_leader_lock.acquire()
                order_leader = hosts[str(host_id)]
                leader_ID = str(host_id)
                leader_IP = hosts[str(host_id)]
                order_leader_lock.release()
                print("Leader decided and stored", leader_ID, leader_IP)
                os.environ[leader_ip_var] = leader_IP
                dotenv.set_key(dotenv_file, leader_ip_var, os.environ[leader_ip_var])
                os.environ[leader_id_var] = leader_ID
                dotenv.set_key(dotenv_file, leader_id_var, os.environ[leader_id_var])
                print("Leader decided and stored", leader_ID, leader_IP)
                hosts_ = json.dumps(hosts)
                # self.setInEnv(order_host_env, hosts_)
                os.environ[order_host_env] = hosts_
                dotenv.set_key(dotenv_file, order_host_env, os.environ[order_host_env])
                # print(hosts)
                # print(type(hosts))
                # get order host list from config and notify the replicas; lock
                utils = Utils()
                # utils.getEnv("50052")
                # hosts = os.environ[order_host_env]
                for h_id, h_ip in hosts.items():
                    h_id = int(h_id)
                    print(leader_ID, leader_IP)
                    # notify leader, send this json_ packet to other replicas; this tells them who the leader is
                    try:
                        print("Sending leader info to order hosts")
                        with grpc.insecure_channel(h_ip) as channel: 
                            stub = order_pb2_grpc.OrderStub(channel)
                            stub.GiveLeaderInfo(order_pb2.GiveLeaderInfoRequest(leaderid = leader_ID, leaderip = leader_IP))
                    except:
                        print("Unable to connect to a node")
                # also tell catalog about the new leader
                catalog_host = os.environ[catalog_host_env]
                print("CATALOG_HOST: ", catalog_host)
                print(type(catalog_host))
                try:
                    print("Leader: ", leader_IP)
                    with grpc.insecure_channel(catalog_host) as channel: 
                        print("Sending leader info to catalog")
                        stub = catalog_pb2_grpc.CatalogStub(channel)
                        print("Opened channel")
                        response = stub.Query(catalog_pb2.QueryRequest(toy="Whale")) 
                        print("Resp received for query: ", response.price)
                        response = stub.LeaderNotification(catalog_pb2.LeaderNotificationRequest(leaderadderss=leader_IP)) #For buy requests, response will store the status i.e 1,0 or -1 representing buy request successful, item out of stock and invalid item respectively
                        print(response.status)
                except:
                    print("Unable to connect to catalog")
                
                # tell env about new leader; send leaderip:port in value
                try:
                    with grpc.insecure_channel(config_host) as channel: 
                        stub = config_pb2_grpc.ConfigStub(channel)
                        ip_full = leader_IP
                        response = stub.AddToConf(config_pb2.addToConfRequest(keyName = "LEADER", value = leader_IP, order_host_id = leader_ID))
                except:
                    print("Unable to connect to config")
                    # pass
                    # Tsend hosts to newly elected leader; method call
                    try:
                        with grpc.insecure_channel(leader_IP) as channel: 
                            stub = order_pb2_grpc.OrderStub(channel)
                            print("Leader connected: ", leader_IP)
                            ip_full = leader_IP
                            print(type(hosts_))
                            response = stub.GiveFollowersNodesInfo(order_pb2.FollowersNodesInfoRequest(nodes=hosts_))
                            print("After response")
                    except:
                        print("Leader chosen but it crashed")
                        continue
                break
            else:
                del hosts[str(host_id)]
                hosts_ = json.dumps(hosts)
                # self.setInEnv(order_host_env, hosts_)
                os.environ[order_host_env] = hosts_
                dotenv.set_key(dotenv_file, order_host_env, os.environ[order_host_env])

        if not leader_elected:
            print("No order service replica is up yet.")
            try:
                with grpc.insecure_channel(config_host) as channel: 
                    stub = config_pb2_grpc.ConfigStub(channel)
                    ip_full = leader_IP
                    response = stub.AddToConf(config_pb2.addToConfRequest(keyName = "LEADER", value = "", order_host_id = ""))
            except:
                print("Unable to connect to config")
            

    def setInEnv(self, key, val):
        os.environ[key] = val
        dotenv.set_key(dotenv_file, key, os.environ[key])

    def getEnvVar(self, key):
        return os.environ[key]

    def getEnv(self, port):
        global port_grpc
        with grpc.insecure_channel(config_host) as channel: 
            stub = config_pb2_grpc.ConfigStub(channel)
            response = stub.AddToConf(config_pb2.addToConfRequest(keyName = "FRONTEND_HOST", value = str(port_grpc), order_host_id = ""))
            
            env_vars_json = stub.GetConfigDetails(config_pb2.getConfigRequest(dummy="")) #For buy requests, response will store the status i.e 1,0 or -1 representing buy request successful, item out of stock and invalid item respectively
            env_vars = json.loads(env_vars_json.configdetails)
            for item, val in env_vars.items():
                os.environ[item] = val
                dotenv.set_key(dotenv_file, item, os.environ[item])
            dotenv.load_dotenv(dotenv_file)


def startConfig():
    lock.acquire()
    dotenv.set_key(dotenv_file, order_host_env, "{}")
    dotenv.set_key(dotenv_file, catalog_host_env, "")
    dotenv.set_key(dotenv_file, frontend_host_var, "")
    dotenv.set_key(dotenv_file, leader_id_var, "")
    dotenv.set_key(dotenv_file, leader_ip_var, "")
    dotenv.load_dotenv(dotenv_file)
    lock.release()
    return


def runHTTP():
    with ThreadingHTTPServer(('', PORT), requestHandler) as server:
        print("Starting HTTP")
        server.serve_forever()


def runGRPC():
    global port_grpc
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frontend_pb2_grpc.add_CacheServicer_to_server(Cache(), server)
    port_grpc = server.add_insecure_port('0.0.0.0')
    print("GRPC port started on: ", port_grpc)
    # server.add_insecure_port('[::]:50052')
    print("Starting GRPC")
    server.start()
    server.wait_for_termination()

def startRunning():
    time.sleep(10)
    global dotenv_file
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    startConfig()
    utils = Utils()
    # utils.getEnv("50052")
    utils.electNewLeader()
    

# startRunning()
# runHTTP()


thread_GRPC = Thread(target=runGRPC)
thread_HTTP = Thread(target=runHTTP)
thread_Main = Thread(target=startRunning)
thread_GRPC.start()
thread_HTTP.start()
# thread_Main.sleep(10)
thread_Main.start()

# thread_GRPC.join()
# thread_HTTP.join()
# threadMain.join()

thread_GRPC.run()
thread_HTTP.run()
thread_Main.run()

   

# print(os.environ[catalog_host_env])


# dotenv.set_key(dotenv_file, "CATALOG_HOST", os.environ["CATALOG_HOST"])

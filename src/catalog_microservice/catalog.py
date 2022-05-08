
from threading import *
from concurrent import futures
import pandas as pd
from datetime import datetime
import grpc
import catalog_pb2
import catalog_pb2_grpc
import order_pb2
import order_pb2_grpc
import frontend_pb2
import frontend_pb2_grpc
import config_pb2
import config_pb2_grpc
import csv
import dotenv
import json
import os
from threading import Timer, Thread, Event
import json

global df
global inventory_lock

inventory_lock = Lock()
global lock
lock = Lock()
 
order_host_var = "ORDER_HOST"
catalog_host_var = "CATALOG_HOST"
frontend_host_var = "FRONTEND_HOST"
leader_id = "LEADER_ID"
leader_ip = "LEADER_IP"
# catalog_data_file = "/data/catalogdata.csv" #code for containerized
catalog_data_file = "data/catalogdata.csv"
df=pd.read_csv(catalog_data_file)#code for noncontainerized
# order_host = os.getenv("ORDER_HOST", "order") #code for containerized
# order_host='localhost'
# frontend_host = os.getenv("FRONTEND_HOST", "order")
# frontend_host='localhost'
# config_host = "192.168.0.21"

class Catalog(catalog_pb2_grpc.CatalogServicer):
	def Query(self, request, context):
		print(context.peer())
		inventory_lock.acquire()
		df = pd.read_csv(catalog_data_file)
		toy=request.toy

		if request.toy not in list(df.columns): # if toy does not exist in the catalog return price as 0 and quantity as -1
			price=0
			quantity=-1
		else:
			#send toy details 
			toyDetails=df[toy]
			price=toyDetails[1]
			quantity=toyDetails[0]
		inventory_lock.release()
		return catalog_pb2.QueryReply(price=price, quantity=int(quantity))

	def Update(self, request, context):

		inventory_lock.acquire()
		num=request.num
		toy=request.toy
		if request.toy not in list(df.columns): #if toy does not exist
			status=-1
		else:
			df[toy][0]=num
			status=1
			df.to_csv(catalog_data_file,index=False)

		inventory_lock.release()
		
		# print("returning reply")
		return catalog_pb2.UpdateReply(status=status)

	#frontend telling catalog about leader ip and port 
	
	def LeaderNotification(self, request,context):
		print("Inside leader notification of CATALOG")
		leaderip=request.leaderadderss
		print(leaderip)
		os.environ["LEADER_IP"] = leaderip
		# os.environ["ORDER_HOST"] = leaderip
		print(leaderip)
		# dotenv.set_key(dotenv_file, "ORDER_HOST", os.environ["ORDER_HOST"])
		dotenv.set_key(dotenv_file, "LEADER_IP", os.environ["LEADER_IP"])
		status = 1
		return catalog_pb2.LeaderNotificationReply(status = status)



class RestockThread(Thread):
	def __init__(self, resetStockEvent):
		Thread.__init__(self)
		self.resetStockEvent = resetStockEvent
	
	def restockCatalogData(self):
		# inventory_lock.acquire()
		restock_flag = False
		inventory_lock.acquire()
		df = pd.read_csv(catalog_data_file)
		# print(df)
		toys_to_update=[]
		i=0
		cache_toys=[]
		for toy in list(df.columns):
			if df[toy][0] == 0:
				df[toy][0] = 100
				toys_to_update.append(i)
				cache_toys.append(toy)
				restock_flag = True
			i+=1
			# toys_to_update=list(df.loc[0])
		if restock_flag:
			# peint("restock flag is true")
			df.to_csv(catalog_data_file,index=False)
			# inventory_lock.release()
			#restock
			# send restock updates to order and invalidate requests to frontend using GRPC
			leader_ip = os.environ["LEADER_IP"]
			frontend_host = os.environ["FRONTEND_HOST"]
			
			if leader_ip == "" or frontend_host == "":
				with grpc.insecure_channel(config_host) as channel: 
					stub = config_pb2_grpc.ConfigStub(channel)
					env_vars_json = stub.GetConfigDetails(config_pb2.getConfigRequest(dummy="")) #For buy requests, response will store the status i.e 1,0 or -1 representing buy request successful, item out of stock and invalid item respectively
					env_vars = json.loads(env_vars_json.configdetails)
					for item, val in env_vars.items():
						os.environ[item] = val
						dotenv.set_key(dotenv_file, item, os.environ[item])
			
			leader_ip=os.environ["LEADER_IP"]
			# order_host = os.environ["ORDER_HOST"]
			frontend_host = os.environ["FRONTEND_HOST"]
			print("LEADERIP:", leader_ip)
			print("FRONTENDIP:",frontend_host)
			try:
				with grpc.insecure_channel(leader_ip) as channel: 
				# print("Here")
					stub = order_pb2_grpc.OrderStub(channel)
					# start = datetime.now()
					print(toys_to_update)
					mydict={'1':toys_to_update}
					toys_to_update=json.dumps(mydict)
					print("Telling leader to Restock order data")
					response = stub.RestockOrderData(order_pb2.RestockRequest(stocklist=toys_to_update))
					print("leader has restocked orderdata")
					# end = datetime.now()
			except:
				print("Leader down")
				# traceback.print_exc()
			#caching push
			try:
				with grpc.insecure_channel(frontend_host) as channel:
					stub = frontend_pb2_grpc.CacheStub(channel)
					# start = datetime.now()
					print("sending invalidate cache request")
					cache_toys_dict={"1":cache_toys}
					cache_toys=json.dumps(cache_toys_dict)
					response = stub.InvalidateCache(frontend_pb2.InvalidateRequest(toylist=cache_toys))
					print("invalidation done")
					# end = datetime.now()
			except:
				print("Frontend down")

			
		# else:
		inventory_lock.release()
		

	def run(self):
		while not self.resetStockEvent.wait(10):
			print("In timer every 10 seconds")
			self.restockCatalogData()

def getEnv():
	with grpc.insecure_channel(config_host) as channel: 
		stub = config_pb2_grpc.ConfigStub(channel)
		response = stub.AddToConf(config_pb2.addToConfRequest(keyName = "CATALOG_HOST", value = "50051", order_host_id = ""))
		
		env_vars_json = stub.GetConfigDetails(config_pb2.getConfigRequest(dummy="")) #For buy requests, response will store the status i.e 1,0 or -1 representing buy request successful, item out of stock and invalid item respectively
		env_vars = json.loads(env_vars_json.configdetails)
		for item, val in env_vars.items():
			os.environ[item] = val
			dotenv.set_key(dotenv_file, item, os.environ[item])

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
	print("catalog server up and waiting for requests")
	startConfig()
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=50))
	catalog_pb2_grpc.add_CatalogServicer_to_server(Catalog(), server)
	server.add_insecure_port('[::]:50051')
	resetStockEvent = Event()
	restockThread = RestockThread(resetStockEvent)
	restockThread.start()
	server.start()
	server.wait_for_termination()

config_host = "192.168.0.21:50055"
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
getEnv()

if __name__=='__main__':
	print(df)
	serve() #serve clients

from __future__ import print_function
from threading import *
import logging
from concurrent import futures
from datetime import datetime
import grpc
import order_pb2
import order_pb2_grpc
import catalog_pb2
import catalog_pb2_grpc
import config_pb2
import config_pb2_grpc
import pandas as pd
import os
import dotenv
import json

global df
global order_df
global inventory_lock
global catalog_host
 
order_host_var = "ORDER_HOST"
catalog_host_var = "CATALOG_HOST"
frontend_host_var = "FRONTEND_HOST"
leader_id_var = "LEADER_ID"
leader_ip_var = "LEADER_IP"
# catalog_host = os.getenv("CATALOG_HOST", "catalog") #code for containerized
# catalog_host='localhost' #code for noncontainerized
inventory_lock = Lock()
# df=pd.read_csv("/data/orderdata.csv") #code for containerized
# order_df=pd.read_csv("/data/orderlog.csv") #code for containerized
df=pd.read_csv("data/orderdata.csv") #code for noncontainerized
order_df=pd.read_csv("data/orderlog.csv")#code for noncontainerized


global order_host_leader
order_host_leader = None
global leader_ip
# leader_ip = "192.168.0.21:50050"
leader_ip = ""
global leader_id
leader_id = ""
global orderhosts
orderhosts = None
global config_host
config_host = "192.168.0.21:50055"
global lock
lock = Lock()

order_host_var = "ORDER_HOST"
catalog_host_var = "CATALOG_HOST"
frontend_host_var = "FRONTEND_HOST"
leader_id_var = "LEADER_ID"
leader_ip_var = "LEADER_IP"

global dotenv_file 
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


class Order(order_pb2_grpc.OrderServicer):
	def IsAlive(self,request,context):
		alive=True
		return order_pb2.IsAliveReply(alive=alive)

	#replics are informed about leader
	def GiveLeaderInfo(self,request, context):
		inventory_lock.acquire()
		# print("REPLICA IS GETTING LEADER INFO")
		leader_id = request.leaderid
		leader_ip = request.leaderip
		os.environ["LEADER_IP"] = leader_ip
		os.environ["LEADER_ID"] = leader_id
		order_host_leader = leader_ip
		dotenv.set_key(dotenv_file, "LEADER_IP", os.environ["LEADER_IP"])
		dotenv.set_key(dotenv_file, "LEADER_ID", os.environ["LEADER_ID"])
		status=1
		inventory_lock.release()
		return order_pb2.GLReply(status=status)
	
	#leader is informed about follower nodes
	def GiveFollowersNodesInfo(self,request, context):# TODO: lock
		# inventory_lock.acquire()
		print("getting follower nodes")
		orderhosts = json.loads(request.nodes)
		os.environ["ORDER_HOST"]=request.nodes
		dotenv.set_key(dotenv_file, "ORDER_HOST", os.environ["ORDER_HOST"])

		print(orderhosts)
		status=1
		print(status)

		return order_pb2.GFNReply(status=int(status))
	
	# #add node to list of followers
	# def AddFollowerNode(self,request, context):
		
	# 	pass

	
	#catalog tells leader to restock when restocking out of stock toys
	def RestockOrderData(self, request, context):
		
		inventory_lock.acquire()
		# print(request.stocklist)
		print("Inside restock order data")
		lis=json.loads(request.stocklist)
		# print(lis)
		lis=lis['1']
		# df.loc[1]=lis
		leader_ip = os.environ[leader_ip_var]
		df.iloc[0,lis]=100
		df.to_csv(r'data/orderdata.csv',index=False)
		status=1
		getEnv()
		followernodes=json.loads(os.environ['ORDER_HOST'])
		# followernodes=[]
		for key,value in followernodes.items():
			print(key, value)
			if value != leader_ip:
				try:
					with grpc.insecure_channel(value) as channel: 
						stub = order_pb2_grpc.OrderStub(channel)
						mydict={'1':lis}
						lis=json.dumps(mydict)
						response = stub.UpdateReplica(order_pb2.UpdateReplicaRequest(stocklist=lis,ordernum=0,name='',quantity=0,restock=True))
				except:
					print("Oops looks like order crashed!")
					#TODO: Call config
					# remove from config
					try:
						with grpc.insecure_channel(config_host) as channel:
							stub = config_pb2_grpc.ConfigStub(channel)
							start = datetime.now()
							response = stub.RemoveOrderHost(config_pb2.removeOrderHostRequest(value = key))
							end = datetime.now()
					except:
						print("Config down")


		#update replica restock=True
		inventory_lock.release()
		return order_pb2.RestockReply(status=status)

	#frontend gets order details (based on order number) from leader to process client get requests
	def GetOrderDetails(self, request, context):
		inventory_lock.acquire()
		ordernumber=request.ordernum
		#lock
		if ordernumber not in list(order_df['Ordernumber']):
			ordernum=-1
			name=''
			quant=-1
		else:
			idx=order_df.loc[order_df['Ordernumber']==ordernumber]
			ordernum=int(idx['Ordernumber'])
			name=list(idx['Toy'])[0]
			quant=int(idx['Quantity'])
		inventory_lock.release()
		return order_pb2.GetOrderDetailsReply(ordernum=ordernum,name=name,quantity=quant)

	#replicas are told to update their order logs as well as data
	def UpdateReplica(self, request, context):
		inventory_lock.acquire()
		print("Inside update replica")
		if request.restock==True:
			print("restock TRUE, updating order logs")
			updated_stock=json.loads(request.stocklist)
			print(type(updated_stock))
			updated_stock=updated_stock['1']
			# df.loc[1]=updated_stock
			df.iloc[0,updated_stock]=100
			df.to_csv(r'data/orderdata.csv',index=False)
			status=1

		if request.restock==False:
			print("restock is set to false, updating order data")
			updated_stock=json.loads(request.stocklist)
			updated_stock=updated_stock['1']
			df.loc[0]=updated_stock
			ordernumber=request.ordernum
			toy=request.name
			quant=request.quantity
			order_df.loc[len(order_df.index)] = [ordernumber,toy,quant]
			df.to_csv(r'data/orderdata.csv',index=False)
			order_df.to_csv(r'data/orderlog.csv',index=False)
			status=1

		inventory_lock.release()
		print("print replica updated, sending response")
		return order_pb2.UpdateReplicaReply(status=status)

	#follower node asks leader for missed order logs after coming back up after crashing
	def GetMissedOrders(self, request, context):
		print("inside get missed orders")
		inventory_lock.acquire()
		update_status=False
		ordernumber=request.ordernum
		print(ordernumber)
		a=order_df[order_df['Ordernumber']==ordernumber].index.values
		idx=a[0]
		missing_logs=order_df.loc[idx+1:,:]
		print(missing_logs)
		if len(missing_logs)==0:
			update_status=True
			missed_logs=''
		else:
			my_dict=missing_logs.to_dict()
			missed_logs=json.dumps(my_dict)
		inventory_lock.release()
		return order_pb2.MissedOrdersReply(missedorders=missed_logs,isUpdated=update_status)

	def Buy(self, request, context):
		print("HERE")
		print(request.num)
		inventory_lock.acquire()
		num=request.num
		toy=request.toy
		if toy not in list(df.columns):
			status=-2
			ordernum=-1
			name=''
			quant=-1
		else:
			toyDetails=df[toy]
			price=toyDetails[1]
			quantity=toyDetails[0]
			
			if int(quantity)==0:
				status=0
				ordernum=-1
				name=''
				quant=-1
			elif quantity>=num:
				print("In elif")
				update_num=df[toy][0]-num
				df[toy][0]=update_num
				print(df.iloc[0,1])
				updated_stock=list(df.loc[0])
				df.to_csv(r'data/orderdata.csv',index=False)
				catalog_host=os.environ["CATALOG_HOST"]
				with grpc.insecure_channel(catalog_host) as channel: 
				# ,options=(('grpc.enable_http_proxy', 0),)
				# with grpc.insecure_channel('localhost:50051') as channel:
					# stub = catalog_pb2_grpc.CatalogStub(channel)
					stub = catalog_pb2_grpc.CatalogStub(channel)
					start = datetime.now()
					print("HERE: updating catalog")
					response = stub.Update(catalog_pb2.UpdateRequest(toy=toy, num=int(update_num))) #For buy requests, response will store the status i.e 1,0 or -1 representing buy request successful, item out of stock and invalid item respectively
					print("HERE: after updating catalog")
					end = datetime.now()
					print("Update catalog done. Status is: ", response.status,"\n1: Update request successful \n 0: Item out of stock, buy unsuccessful \n-1: invalid item, buy unsucessful.")
				
				ordernumber=len(order_df)
				order_df.loc[len(order_df.index)] = [ordernumber,toy,num]

				order_df.to_csv(r'data/orderlog.csv',index=False)
				status=1
				ordernum=ordernumber
				name=toy
				quant=num
				leader_ip = os.environ[leader_ip_var]
				#update replicas or follower nodes
				leader_ip=os.environ[leader_ip_var]
				orderhosts = json.loads(os.environ["ORDER_HOST"])
				print(orderhosts)
				for order_host_id, order_host_ip in orderhosts.items():
					if order_host_ip != leader_ip:
						print("Inside buy: ", order_host_ip, ", leader: ", leader_ip)
						try:
							# send updates to all the replicas
							with grpc.insecure_channel(order_host_ip) as channel:
								stub = order_pb2_grpc.OrderStub(channel)
								mydict={'1':updated_stock}
								updated_stock_json=json.dumps(mydict)
								# updated_stock=
								start = datetime.now()
								print("HERE: Sending update to replica", updated_stock_json)
								response = stub.UpdateReplica(order_pb2.UpdateReplicaRequest(stocklist=updated_stock_json,ordernum=ordernum,name=name,quantity=quant,restock=False)) #For buy requests, response will store the status i.e 1,0 or -1 representing buy request successful, item out of stock and invalid item respectively
								print("HERE: Replica updated ", updated_stock_json)
								end = datetime.now()
						except:
							print("Replica not reachable")
							# remove from config
							try:
								with grpc.insecure_channel(config_host) as channel:
									stub = config_pb2_grpc.ConfigStub(channel)
									start = datetime.now()
									response = stub.RemoveOrderHost(config_pb2.removeOrderHostRequest(value = order_host_id))
									end = datetime.now()
							except:
								print("Config down")


			else:
				status=-1
				ordernum=-1
				name=''
				quant=-1
		inventory_lock.release()
		return order_pb2.BuyReply(status=status,ordernum=ordernum,name=name,quantity=quant)



#code for getting missed logs when a crashed order service is back up
def updateMissedOrders():
	print("Inside update missed order")
	inventory_lock.acquire()
	global order_df
	areOrderlogsUpdated=False
	global order_df
	lastordernum=order_df['Ordernumber'].loc[len(order_df)-1]

	leader_ip = os.environ[leader_ip_var]
	if leader_ip != "":
		try:
			with grpc.insecure_channel(leader_ip) as channel: 
				stub = order_pb2_grpc.OrderStub(channel)
				start = datetime.now()
				response = stub.GetMissedOrders(order_pb2.MissedOrdersRequest(ordernum=lastordernum) )
				end = datetime.now()
				
				if response.isUpdated==False:
					print("updating missed orders")
					missed_logs=json.loads(response.missedorders)

					missed_logs=pd.DataFrame(missed_logs)
					order_df=pd.concat([order_df, missed_logs])
					print(order_df)
					order_df.to_csv(r'data/orderlog.csv',index=False)
				areOrderlogsUpdated=True
		except:
			print("Leader failed to respond!")
	inventory_lock.release()

def getEnv():
	# global config_host
	with grpc.insecure_channel(config_host) as channel: 
		stub = config_pb2_grpc.ConfigStub(channel)
		response = stub.AddToConf(config_pb2.addToConfRequest(keyName = "ORDER_HOST", value = "50048", order_host_id = "0"))
		
		env_vars_json = stub.GetConfigDetails(config_pb2.getConfigRequest(dummy=""))
		env_vars = json.loads(env_vars_json.configdetails)
		# print(env_vars)
		for item, val in env_vars.items():
			os.environ[item] = val
			dotenv.set_key(dotenv_file, item, os.environ[item])
	dotenv.load_dotenv(dotenv_file)

def startConfig():
    lock.acquire()
    dotenv.set_key(dotenv_file, order_host_var, "{}")
    dotenv.set_key(dotenv_file, catalog_host_var, "")
    dotenv.set_key(dotenv_file, frontend_host_var, "")
    dotenv.set_key(dotenv_file, leader_id_var, "")
    dotenv.set_key(dotenv_file, leader_ip_var, "")
    dotenv.load_dotenv(dotenv_file)
    lock.release()
    return

def startConfig():
    lock.acquire()
    dotenv.set_key(dotenv_file, order_host_var, "{}")
    dotenv.set_key(dotenv_file, catalog_host_var, "")
    dotenv.set_key(dotenv_file, frontend_host_var, "")
    dotenv.set_key(dotenv_file, leader_id_var, "")
    dotenv.set_key(dotenv_file, leader_ip_var, "")
    dotenv.load_dotenv(dotenv_file)
    lock.release()
    return


def serve():
	print("Order microservice up and waiting for requests")
	startConfig()
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=50))
	order_pb2_grpc.add_OrderServicer_to_server(Order(), server)
	startConfig()
	getEnv()
	if os.environ[leader_ip_var] != "":
		updateMissedOrders()
	server.add_insecure_port('[::]:50048')
	server.start()
	server.wait_for_termination()


if __name__=='__main__':
	
	# catalog_host = "localhost"
	# dotenv_file = dotenv.find_dotenv()
	# dotenv.load_dotenv(dotenv_file)
	#TODO: call config load env
	# areOrderlogsUpdated=False
	# TODO: call updateMissedOrders()

	logging.basicConfig()
	serve() #serve clients

# map<string, int32> orderdetails=1;





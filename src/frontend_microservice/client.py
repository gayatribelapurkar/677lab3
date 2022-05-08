import logging
import random
import grpc
import order_pb2
import order_pb2_grpc
import catalog_pb2
import catalog_pb2_grpc
from datetime import datetime

def run():
	# querytype = ["Buy"] #for issuing only query requests to the server
	querytype=["Query"]

	toys = ["Tux", "Whale", "Elephant", "Bird"]  
	nums = [1, 2, 3]
	n = 10 # number of requests issued by client
	time_diff = datetime.now()
	time_diff -= time_diff
	with grpc.insecure_channel('192.168.0.16:50051') as channel: 
		for i in range(n):
			toy = random.choice(toys)
			query = random.choice(querytype)
			num = random.choice(nums)

			 #client stub
			if query=='Buy':
				stub = order_pb2_grpc.OrderStub(channel)
				start = datetime.now()
				response = stub.Buy(order_pb2.BuyRequest(toy=toy,num=num)) 
				end = datetime.now()
				time_diff += end - start

				print("Buy client received. Status is: ", response.status,"\n1: Buy request successful \n 0: Item out of stock, buy unsuccessful \n-1: invalid item, buy unsucessful.")
			elif query=='Query':
				stub = catalog_pb2_grpc.CatalogStub(channel)
				start = datetime.now()
				response = stub.Query(catalog_pb2.QueryRequest(toy=toy)) #send request to server and store its response in 'response'. For query requests, response will store the quantity and price of the toy
				end = datetime.now()
				time_diff += end - start
				print("Query client received. For the toy", toy,"the price is: ",response.price," and the available units stock are: ", response.quantity)
			else:
				print("Invalid query, please choose either 'Query' or 'Buy' queries as requests.") #request is not sent to server if it is neither a 'Query' nor 'Buy Request'
		time_diff = time_diff.microseconds #total latency for n requests in microseconds
		time_diff /= n #average latency(in microseconds) per request
		print("The average latency over ", n, " requests was: ", time_diff, " microseconds.")

if __name__ == '__main__':
    logging.basicConfig()
    run()
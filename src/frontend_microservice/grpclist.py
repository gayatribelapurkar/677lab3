import logging
import random
import grpc
import order_pb2
import order_pb2_grpc
import catalog_pb2
import catalog_pb2_grpc
from datetime import datetime

with grpc.insecure_channel('localhost:50050') as channel:
    stub = order_pb2_grpc.OrderStub(channel)
    mylist=[1,2,3,4,5,6,7,8,9,10]
    response = stub.RestockOrderData(order_pb2.RestockRequest(stocklist=mylist)) 
    print(response.status)
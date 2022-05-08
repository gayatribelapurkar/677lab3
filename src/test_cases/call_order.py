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
import pandas as pd

dotenv_file=dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

def run():
    # with grpc.insecure_channel('192.168.0.16:50050') as channel: 
    #     stub = order_pb2_grpc.OrderStub(channel)
    #     stub.GiveLeaderInfo(order_pb2.GiveLeaderInfoRequest(leaderid='3', leaderip='192.168.0.21:50050'))

    with grpc.insecure_channel('192.168.0.21:50050') as channel: 

        #check if alive
        stub = order_pb2_grpc.OrderStub(channel)
        # response = stub.IsAlive(order_pb2.IsAliveRequest(alivereq="Are you alive"))
        # print("Order host alive? ", response.alive)

        # #get order details
        # order_number=32
        # response = stub.GetOrderDetails(order_pb2.GetOrderDetailsRequest(ordernum=order_number))
        # print("Order details are: ", response.ordernum,response.name,response.quantity)

        # #get missed order logs
        # ordernum=1994
        # response = stub.GetMissedOrders(order_pb2.MissedOrdersRequest(ordernum=ordernum))
        # if response.isUpdated==True:
        #     print("logs are up to date")
        # else:
        #     missedlogs=json.loads(response.missedorders)
        #     print(pd.DataFrame(missedlogs))
        
        # # followernodes=json.dumps({})
        # # response = stub.GiveFollowerNodes(order_pb2.FollowerNodesInfoRequest(nodes=followernodes))

        toys_to_update=[0,3]
        mydict={'1':toys_to_update}
        toys_to_update=json.dumps(mydict)
        response = stub.RestockOrderData(order_pb2.RestockRequest(stocklist=toys_to_update))

        # print("buying")
        # response = stub.Buy(order_pb2.BuyRequest(toy='Whale',num=2))
        # response = stub.Buy(order_pb2.BuyRequest(toy = product, num = quantity))


if __name__ == '__main__':
    logging.basicConfig()
    run()
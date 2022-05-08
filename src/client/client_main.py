#!/usr/bin/env python3
import json
import socket
import requests
from requests.structures import CaseInsensitiveDict
import random
from datetime import datetime
import sys

# HOST = "192.168.0.21"
PORT = 8000

def main():

    n_args = len(sys.argv)
    # print(sys.argv)
    if n_args < 3:
        return
    
    HOST = sys.argv[1]
    p = float(sys.argv[2])
    print(HOST)
    print(p)
    # p = float(input("Enter probability of post requests as float: "))
    # p = 0.5 #take as param from client
    headers = CaseInsensitiveDict()
    headers["Connection"] = "keep-alive"
    headers["Keep-Alive"] = "timeout=1, max=2"

    # products = ["Tux", "Whale", "Elephant", "Bird", "Octocat", "Jenga", "Uno", "Twister", "Swing", "Puppet"]
    products = ["Whale"]
    order_information = []
    num_get_requests=0
    num_post_requests=0

    i = 0
    time_diff_get = datetime.now()
    time_diff_get -= time_diff_get #start time before any request is set to 0 in time format to start calculation of total latency
    time_diff_post = datetime.now()
    time_diff_post -= time_diff_post #start time before any request is set to 0 in time format to start calculation of total latency
    time_diff_get_order = datetime.now()
    time_diff_get_order -= time_diff_get_order #start time before any request is set to 0 in time format to start calculation of total latency
    url_base = "http://" + HOST + ":" + str(PORT) + "/"
    while i < 1:
        # print("Hi")

        i += 1
        product = random.choice(products)
        url = url_base + "products/" + product

        start_get = datetime.now()
        r_get = requests.get(url= url, headers = headers)
        end_get = datetime.now() #time just after response is received
        num_get_requests+=1
        time_diff_get += end_get - start_get #add the latency for this particular query request to the total latency
        print(r_get)
        
        # post_response = json.loads(r_post.decode("utf-8"))
        get_response = r_get.json()
        print(get_response)
        print(type(get_response))
        
        #send and process json

        if r_get.status_code == 200:
            quantity = get_response['data']['quantity']
            if quantity > 0:
                print("Done ", quantity)
                num = random.uniform(0,1)
                # num = random.random()
                # sending buy with probability p
                if num < p:
                    #send post request to buy
                    quantity = random.randint(1, 3)
                    # quantity = 42
                    url = url_base + "orders"
                    send_post = {"name": product, "quantity": quantity}
                    json_data = json.dumps(send_post)
                    start_post = datetime.now()
                    r_post = requests.post(url= url, headers=headers, data=json_data)
                    end_post = datetime.now()
                    num_post_requests+=1
                    time_diff_post += end_post - start_post
                    print(r_post)
                    post_response = r_post.json()
                    
                    if r_post.status_code == 200:
                        print(post_response)
                        print(type(post_response))
                        order_number = post_response['data']['order_number']
                        name = post_response['data']['name']
                        quantity = post_response['data']['quantity']
                        print("Done. Order number: ", order_number, ", name: ", name, ", quantity: ", quantity)
                        order_information.append([order_number, name, quantity])
                    else:
                        error = post_response['error']['message']
                        print("Done ", error)

        else:
            error = get_response['error']['message']
            print("Done ", error)

        i+=1
        
    print("Now getting order details to verify")
    print(order_information)
    order_information = [[210, 'Whale', 2]]
    #sending request to get order by order number
    for order_det in order_information:
        print("Sending: ", order_det)
        url_orders = url_base + "orders/" + str(order_det[0])
        print("Sending order number to get details: ", order_det[0])
        print("URL: ", url_orders)
        start_get_order = datetime.now()
        r_get_order = requests.get(url= url_orders, headers = headers)
        end_get_order = datetime.now() #time just after response is received
        num_get_requests+=1
        time_diff_get_order += end_get_order - start_get_order #add the latency for this particular query request to the total latency
        print(r_get_order)
        
        # post_response = json.loads(r_post.decode("utf-8"))
        get_response_order = r_get_order.json()
        print(get_response_order)
        print(type(get_response_order))

        if r_get_order.status_code == 200:
            order_num_recv = get_response_order['data']['order_number']
            name = get_response_order['data']['name']
            quantity = get_response_order['data']['quantity']
            print("The actual details were :- order number received : ", order_det[0], ", name : ", order_det[1], ", quantity : ", order_det[2])
            print("The details received were :- order number received : ", order_num_recv, ", name : ", name, ", quantity : ", quantity)
            if order_num_recv != order_det[0] or name != order_det[1] or quantity != order_det[2]:
                print("There has been a mismatch!!!")
            else:
                print("Order verified")
        else:
            error = get_response_order['error']['message']
            print("Done ", error)



    time_diff_get = time_diff_get.microseconds #total latency for n requests in microseconds
    time_diff_get /= num_get_requests #average latency(in microseconds) per request
    print("The average latency over ", num_get_requests, " get requests was: ", time_diff_get, " microseconds.")

    if num_post_requests != 0:
        time_diff_post = time_diff_post.microseconds #total latency for n requests in microseconds
        time_diff_post /= num_post_requests #average latency(in microseconds) per request
        print("The average latency over ", num_post_requests, " post requests was: ", time_diff_post, " microseconds.")
    else:
        print("There were no post requests sent")

    if len(order_information) > 0:
        time_diff_get_order = time_diff_get_order.microseconds
        time_diff_get_order /= len(order_information)
        print("The average latency over ", len(order_information), " get requests was: ", time_diff_get_order, " microseconds.")


if __name__ == "__main__":
    main()

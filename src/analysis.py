import matplotlib.pyplot as plt 

# Define X and Y variable data
x = [1, 2, 3]
c1 = 1263.75
c2 = (1607.77 + 1545.84) / 2
c3 = (4359.0 + 4536.22 + 5192.92) / 3
y = [c1, c2, c3]
  
plt.plot(x, y)
plt.xlabel("Number of clients")  # add X-axis label
plt.ylabel("Latency in microseconds ")  # add Y-axis label
plt.title("Average latency per request for Get requests with varying number of clients without Containerization")  # add title
plt.show()

x = [1, 2, 3]
c1 = 10157.15
c2 = (10096.83 + 9974.93) / 2
c3 = (10223.89 + 17313.65 + 9941.59) / 3
y = [c1, c2, c3]
  
plt.plot(x, y)
plt.xlabel("Number of clients")  # add X-axis label
plt.ylabel("Latency in microseconds ")  # add Y-axis label
plt.title("Average latency per request for Post requests with varying number of clients without Containerization")  # add title
plt.show()



x = [1, 2, 3, 4,5]
c1 = 1399.59
c2 = (1311.26 +1738.38) / 2
c3 = (4563.93 + 4340.31 + 5796.65 ) / 3
c4 = (3566.43 + 5454.32 + 9066.89 + 6022.28) / 4
c5 = (5934.91 + 6095.46 + 5398.73 + 5411.77 + 6136.62) / 5
y = [c1, c2, c3, c4, c5]
  
plt.plot(x, y)
plt.xlabel("Number of Clients")  # add X-axis label
plt.ylabel("Latency in microseconds")  # add Y-axis label
plt.title("Average latency per request for Get requests with varying number of clients")  # add title
plt.show()



x = [1, 2, 3, 4,5]
c1 = 11060.66
c2 = (17089.69 + 5727.63) / 2
c3 = (18886.6 + 17184.32 + 18719.05) / 3
c4 = (24454.17 + 18245.16 + 17051.67 + 16664.64) / 4
c5 = (29879.6 + 37513.04 + 30063.03 + 25154.51 + 10809.65) / 5
y = [c1, c2, c3, c4, c5]
  
plt.plot(x, y)
plt.xlabel("Number of clients")  # add X-axis label
plt.ylabel("Latency in microseconds ")  # add Y-axis label
plt.title("Average latency per request for Post requests with varying number of clients")  # add title
plt.show()


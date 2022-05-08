To build, go to the root directory and run build.sh or run the command

```
docker-compose build
```

Further, all the services can be started using 
```
docker-compose up
```

and stopped using Ctrl-C and removed by:

```
docker-compose rm
```

Alternatively,
run ```docker-compose up``` in detached mode and stop using ```docker-compose down```.


CLIENT:
To run the client, navigate to the ```/src/client``` folder and run client_main.py giving the IP address of the server followed by the probability of buying as a command line arguments. For example to buy with a probability 0.4 from a server running on the host with IP address 192.168.0.21, run the following:

```
python client_main.py 192.168.0.21 0.4
```

All the Dockerfiles and ```docker-compose.yml``` are placed in the root directory and are named respectively as per catalog, order or frontend.

python -m pip install python-dotenv
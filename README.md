# fever_test
Saul Maldonado: Integratin test to fever APIs

Dependencies:
        - run: pip install -r dependencies.txt

Architecture:

provider_connector:
        - Based on Flask
        - retrieves xml event data from remote endpoint and send it as dictionaries to the server

server:
        - executed with run_server.py
        - websocket service based on Flask running at ws://localhost:1234 for saving events and performing a simple query based on dates for all events
        - events are stored as dictionaries to avoid memory overflow 
        - 3 clases are used only to retrieve events: BaseEvent, Event and Zone
        - When savin events: there's a date validation to avoid store "bad data"
        - It'll get data from provider_connector
        - It'll get requests from microservice client

microservice:
        - executed with run_service.py
        - Based on Flask and it runs on http://localhost:8081/microservice/events_by_date
        - Request data to the server by sending 2 date-time parameters: starts_at and ends_at


Scalation: with some extra coding loadbalancers could be implemented along with a virtualization environment such as AWS
           At the end you can choose how many servers, connectors and microservices must be deployed to scale this solution
           

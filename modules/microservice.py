import sys
sys.path.append('../')

from aiohttp import web
import websockets
import json
from datetime import datetime as dt


CONNECTOR_LOOP_TIMER = 6
SERVER_PORT = 1234
SERVER_URI = "ws://localhost:" + str(SERVER_PORT)
CLIENT = 'CONNECTOR_PROVIDER'

routes = web.RouteTableDef()

@routes.get('/')
async def handle(request):
    response_obj = {'response': 'success', 'creator': 'Saul Maldonado R.'}
    return web.Response(text=json.dumps(response_obj), status=200)


@routes.post('/microservice/events_by_date')
async def events_by_date(request: web.Request) -> web.Response:

    status = 200

    data = await request.json()

    print(f"Microservice. Data received{str(data)}")

    try:
        # Validating expected variables
        starts_at = dt.strptime(data['starts_at'], '%Y-%m-%dT%H:%M:%SZ')
        ends_at = dt.strptime(data['ends_at'], '%Y-%m-%dT%H:%M:%SZ')

    except Exception as e:
        print(e)
        status = 400
        response = {
              "error": {
                "code": "MS001",
                "message": "The request was not correctly formed (missing required parameters, wrong types...)"
              },
              "data": None
            }

    # Sending request to server

    try:
        # NOTE: ping_interval=None is to help with error networking
        async with websockets.connect(SERVER_URI, ping_interval=None) as websocket:

            data_to_send = {}

            data_to_send['client'] = 'MICROSERVICE'
            data_to_send['function'] = 'GET_EVENTS_FROM_DATES'
            data_to_send['starts_at'] = data['starts_at']
            data_to_send['ends_at'] = data['ends_at']

            data_to_send = json.dumps(data_to_send)

            await websocket.send(data_to_send)

            response = await websocket.recv()

            response = json.loads(response)

    except Exception as e:
        print("Can't connect to the server.... ")
        print("Exception: " + str(e))
        status = 500

    if status == 500:
        response = {
            "error": {
                "code": "MS002",
                "message": "Generic Error"
            },
            "data": None
        }

    return web.json_response(response, status=status)


api = web.Application()
api.router.add_routes(routes=routes)
web.run_app(api, port=8081)

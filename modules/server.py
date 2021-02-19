import sys
sys.path.append('../')

from flask import Flask
import websockets
import asyncio
import json
from datetime import datetime as dt

from connectors import provider_connector
from feverup.provider.base_event import BaseEvent

app = Flask(__name__)

SERVER_VERSION = "v1.0"
SERVER_IP = 'localhost'
SERVER_PORT = 1234

EVENT_LIST = []

CONNECTORS = [{'connector_name': 'CONNECTOR_PROVIDER',
                'thread': provider_connector,
                'status': 'OFF',
                'has_market_data': True}]


# Main function to receive all requests
async def get_data(websocket, path):

    data = await websocket.recv()
    data = json.loads(data)
    #print(f"Server.get_data Receiving: {str(data)}")

    # Validating data
    if data['client'] in ['CONNECTOR_PROVIDER']:

        save_data(data=data)

        await websocket.send(f"Data received")

        return

    # Request from API Service
    if data['client'] in ['MICROSERVICE']:
        if data['function'] == 'GET_EVENTS_FROM_DATES':
            starts_at = data['starts_at']
            ends_at = data['ends_at']

            event_list_by_date = get_events_by_date(starts_at, ends_at)

            await websocket.send(json.dumps({"events": event_list_by_date}))

            return


def save_data(data=dict):

    base_event_list = data['eventList']['output']['base_event']

    if len(EVENT_LIST) == 0:

        for base_event in base_event_list:

            # Validate dates before saving the base event
            try:

                dt.strptime(base_event['event']['@event_date'], '%Y-%m-%dT%H:%M:%S')
                dt.strptime(base_event['event']['@sell_from'], '%Y-%m-%dT%H:%M:%S')
                dt.strptime(base_event['event']['@sell_from'], '%Y-%m-%dT%H:%M:%S')

                EVENT_LIST.append(base_event)
            except Exception as e:
                print(f"Saving for the first time. The event '{base_event['@title']}' couldn't be save because of a bad date format")

    else:
        # Compare each incoming base_event with old ones.
        # If it is a new base_event it'll be saved as a dict structure to minimize memory usage
        # If it already exists the old one will be overridden
        for base_event in base_event_list:
            # Validate dates before saving the base event
            try:

                dt.strptime(base_event['event']['@event_date'], '%Y-%m-%dT%H:%M:%S')
                dt.strptime(base_event['event']['@sell_from'], '%Y-%m-%dT%H:%M:%S')
                dt.strptime(base_event['event']['@sell_from'], '%Y-%m-%dT%H:%M:%S')

            except Exception as e:
                print(f"The event '{base_event['@title']}' couldn't be save because of a bad date format")
                continue

            # Getting index of stored base event if any
            stored_event = [(idx, event) for idx, event in enumerate(EVENT_LIST) if
                            event['@base_event_id'] == base_event['@base_event_id']]

            print(f"Buscando base_event['@base_event_id']: {str(base_event['@base_event_id'])}")

            if len(stored_event) == 0:
                EVENT_LIST.append(base_event)
                print("  No encontrado. ")
                print(f"  {str(EVENT_LIST)} ")
            else:
                idx = stored_event[0][0]
                EVENT_LIST[idx] = base_event

    print(f"EVENT_LIST has {str(len(EVENT_LIST))} elements and now is: {str(EVENT_LIST)}")


def get_events_by_date(starts_at, ends_at):
    events_data = []

    print(f"EVENT_LIST: {str(EVENT_LIST)}")

    for be in EVENT_LIST:
        be_object = BaseEvent(base_event_dict=be)

        #TODO: improve this search if hired =)
        data = be_object.get_events_data(from_date=starts_at, to_date=ends_at)
        if data:
            events_data.append(data)

    # Releasing memory
    be_object = None

    return events_data


def start_websocket():

    #print("Starting Fever Server " + SERVER_VERSION)

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    start_server = websockets.serve(get_data, "localhost", SERVER_PORT, ssl=None)

    asyncio.get_event_loop().run_until_complete(start_server)

    # Starting all connectors
    start_connector('CONNECTOR_PROVIDER')

    try:
        asyncio.get_event_loop().run_forever()
    finally:
        asyncio.get_event_loop().run_until_complete(asyncio.get_event_loop().shutdown_asyncgens())
        asyncio.get_event_loop().close()


def run_in_background():
    import threading

    global syncThread_server
    syncThread_server = threading.Thread(target=start_websocket, args=[], name='SYNC_Server')
    syncThread_server.setDaemon(True)
    print("About to start Server in background")
    syncThread_server.start()
    print("Server started in background")


def start_connector(connector_name):

    for c in CONNECTORS:
        if connector_name == c['connector_name'] and c['status'] == 'OFF':
            print(f"  Staring connector {connector_name}")
            c['status'] = 'ON'
            c['thread'].run()

#start_websocket()
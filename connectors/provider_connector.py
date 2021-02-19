import sys
sys.path.append('../')

from utils import xml_parser

from flask import Flask

import urllib.request
import xmltodict
import threading
import time
import json
import websockets
import asyncio


app = Flask(__name__)

global syncThread_provider_connector
global keep_running
keep_running = True

CONNECTOR_LOOP_TIMER = 6
SERVER_PORT = 1234
SERVER_URI = "ws://localhost:" + str(SERVER_PORT)
CLIENT = 'CONNECTOR_PROVIDER'


class Endpoint_Provider:

    def __init__(self):
        self.endpoint_test_list = [{'date': '2021-02-09',
                               'endpoint': 'https://gist.githubusercontent.com/miguelgf/fac9761c528befe700be6f94cdccdaa9/raw/80e552779c5c108bf0d076395bc5421784251bc0/response_2021-02-09.xml'},
                              {'date': '2021-02-10',
                               'endpoint': 'https://gist.githubusercontent.com/miguelgf/38c5a6f6bc7630f9c8fd0a23f4c8327f/raw/203d2d556274369d5f035f079a49a0a45e77b872/response_2021-02-10.xml'},
                              {'date': '2021-02-11',
                               'endpoint': 'https://gist.githubusercontent.com/miguelgf/37f1bea60e0fa262680e6e5031cfb038/raw/5df981e215949ba04a342acc7a36a18ea1c1310a/response_2021-02-11.xml'}
                              ]
        self.current_endpoint = ''
        self.current_date = ''
        self.data_event = None

    def get_endpoint_test_list(self): return self.endpoint_test_list

    def set_current_endpoint(self, ep): self.current_endpoint = ep

    def get_current_endpoint(self): return self.current_endpoint

    def set_current_date(self, d): self.current_date = d

    def get_current_date(self): return self.current_date

    def get_remote_content(self):

        try:
            file = urllib.request.urlopen(self.current_endpoint)
            data = file.read()
            file.close()

            self.data_event = xmltodict.parse(data)

        except Exception as e:
            print(f"Exception reading remote xml file: {str(e)}")

    def get_data_event(self): return self.data_event


def set_keep_running(kp):
    global keep_running
    keep_running = kp


def get_keep_running():
    return keep_running


async def send_data(data):

    if not get_keep_running():
        remote_stop()

    try:
        # NOTE: ping_interval=None is to help with error networking
        async with websockets.connect(SERVER_URI, ping_interval=None) as websocket:

            data['client'] = CLIENT

            data = json.dumps(data)

            await websocket.send(data)

            response = await websocket.recv()

            if response == "STOP_CONNECTOR":
                set_keep_running(False)

    except Exception as e:
        print("Can't connect to the server.... ")
        print("Exception: " + str(e))
        remote_stop()


def loop():

    provider = Endpoint_Provider()

    ep_list = provider.get_endpoint_test_list()

    test_counter = 0

    data = None

    while get_keep_running():

        # TODO: remove this "if statement" after testing if hired
        if test_counter < len(ep_list):
            provider.set_current_date(d=ep_list[test_counter]['date'])
            provider.set_current_endpoint(ep=ep_list[test_counter]['endpoint'])
            print(f"Connector: current endpoint is {provider.get_current_endpoint()}")
            test_counter += 1
        else:
            continue

        provider.get_remote_content()

        # Avoid sending same data to the server
        if data == provider.get_data_event():
            # TODO: remove after testing if hired
            time.sleep(CONNECTOR_LOOP_TIMER)
            continue

        data = provider.get_data_event()

        try:

            response = asyncio.get_event_loop().run_until_complete(send_data(data))

        except Exception as e:
            loop_task = asyncio.new_event_loop()
            asyncio.set_event_loop(loop_task)
            print("PROVIDER_CONNECTOR.LOOP.ERROR No loop detected, creating a new event loop")
            response = asyncio.get_event_loop().run_until_complete(send_data(data))

        # TODO: remove after testing if hired
        time.sleep(CONNECTOR_LOOP_TIMER)


def run():

    print("Starting Provider connector")
    set_keep_running(True)

    global syncThread_provider_connector

    syncThread_provider_connector = threading.Thread(target=loop, args=[], name='PROVIDER_Connector')
    syncThread_provider_connector.setDaemon(True)
    print("About to start PROVIDER Connector in background")
    syncThread_provider_connector.start()
    print("PROVIDER connector started in background")


def remote_stop():
    print("Received a remote Stopping signal. Shutting down PROVIDER connector")

    set_keep_running(False)

    global syncThread_provider_connector

    if syncThread_provider_connector:

        syncThread_provider_connector.join(1)



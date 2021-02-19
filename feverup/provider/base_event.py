import sys
sys.path.append('../../')

from feverup.provider.event import Event
from datetime import datetime as dt

class BaseEvent:

    def __init__(self, base_event_dict=dict):

        self.base_event_id = base_event_dict['@base_event_id']
        self.sell_mode = base_event_dict['@sell_mode']
        self.title = base_event_dict['@title']
        self.event = Event(event_dict=base_event_dict['event'])

    def get_base_event_id(self): return self.base_event_id
    def get_sell_mode(self): return self.sell_mode
    def get_organizer_company_id(self): return self.organizer_company_id
    def get_title(self): return self.title
    def get_event(self): return self.event

    def get_events_data(self, from_date, to_date):

        events_data = {}

        from_date = dt.strptime(from_date, '%Y-%m-%dT%H:%M:%SZ')
        to_date = dt.strptime(to_date, '%Y-%m-%dT%H:%M:%SZ')
        event_sell_from = self.event.get_sell_from()
        event_sell_to = self.event.get_sell_to()

        if event_sell_from >= from_date and event_sell_to <= to_date:

            events_data = {
                "id": self.get_base_event_id(),
                "title": self.get_title(),
                "start_date": self.event.get_sell_from_date(),
                "start_time": self.event.get_sell_from_time(),
                "end_date": self.event.get_sell_to_date(),
                "end_time": self.event.get_sell_to_time(),
                "min_price": self.event.get_expensive_price(),
                "max_price": self.event.get_cheaper_zone()
                }

        return events_data

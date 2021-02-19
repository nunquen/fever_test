import sys
sys.path.append('../../')

from feverup.provider.zone import Zone
from datetime import datetime as dt


class Event:

    def __init__(self, event_dict=dict):

        self.event_date = event_dict['@event_date']
        self.event_id = event_dict['@event_id']
        self.sell_from = dt.strptime(event_dict['@sell_from'], '%Y-%m-%dT%H:%M:%S')
        self.sell_to = dt.strptime(event_dict['@sell_to'], '%Y-%m-%dT%H:%M:%S')
        self.sold_out = True if event_dict['@sold_out'] == 'true' else False
        self.zone_list = []
        if isinstance(event_dict['zone'], list):
            for z in event_dict['zone']:
                self.zone_list.append(Zone(zone_dict=z))

        if isinstance(event_dict['zone'], dict):
            self.zone_list.append(Zone(zone_dict=event_dict['zone']))

    def get_event_date(self): return self.event_date
    def get_event_id(self): return self.event_id
    def get_sell_from(self): return self.sell_from
    def get_sell_from_date(self): return dt.strftime(self.sell_from, "%Y-%m-%d")
    def get_sell_from_time(self): return dt.strftime(self.sell_from, "%H:%M:%S")
    def get_sell_to(self): return self.sell_to
    def get_sell_to_date(self): return dt.strftime(self.sell_to, "%Y-%m-%d")
    def get_sell_to_time(self): return dt.strftime(self.sell_to, "%H:%M:%S")
    def is_sold_out(self): return self.sold_out
    def get_zone_list(self): return self.zone_list

    def get_cheaper_zone(self):
        price = -1.0
        for z in self.zone_list:
            price = float(price)
            if price > -1.0:
                price = min(price, z.get_price())
            else:
                price = z.get_price()

        return price

    def get_expensive_price(self):
        price = -1.0
        for z in self.zone_list:
            price = max(price, z.get_price())

        return price

import sys
sys.path.append('../../')


class Zone:

    def __init__(self, zone_dict=dict):

        self.zone_id = zone_dict['@zone_id']
        self.capacity = int(zone_dict['@capacity'])
        self.price = float(zone_dict['@price'])
        self.name = zone_dict['@name']
        self.numbered = True if zone_dict['@numbered'] == 'true' else False

    def get_zone_id(self): return self.zone_id
    def get_capacity(self): return self.capacity
    def get_price(self): return self.price
    def get_name(self): return self.name
    def is_numbered(self): return self.numbered
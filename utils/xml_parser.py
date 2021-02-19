import sys
sys.path.append('../')

import pandas as pd


def parse_provider_content_from_dict_to_pandas(d:dict):

    data_frame = None

    try:
        base_events = d['eventList']['output']['base_event']
        be_cols = ['base_event_id', 'sell_mode', 'title', 'events']
        be_rows = []

        for be in base_events:

            be_rows.append({'base_event_id': be['@base_event_id'],
                            'sell_mode': be['@sell_mode'],
                            'title': be['@title'],
                            'events': be['event']})

        data_frame = pd.DataFrame(be_rows, columns=be_cols)

    except Exception as e:
        print(f"Exception parsing dict data from provider: {str(e)}")

    return data_frame
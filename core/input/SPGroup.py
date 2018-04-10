'''
Interface for the SPGroup api
- SPGroup api delivers producing data
- delivers production from the past hour
- constructor takes the site_id as parameter
- !!! Access by hardcoded api key !!!
'''


import calendar

import requests
import datetime
from datetime import tzinfo, timedelta

from core.abstract.input import ExternalDataSource, EnergyData, Device

# producing asset
class SPGroupAPI(ExternalDataSource):

    def __init__(self, site_id: str):

        self.site = site_id
        self.api_url = 'https://lighthouse-api-master.apps.vpcf-qa.spdigital.io/v1/'

    def read_state(self) -> EnergyData:
        raw = self._get_daily_data()
        '''
        {
            "sites": [
                {
                    "site_id": "b1",
                    "start_time": "2018-03-26T08:21:20Z",
                    "end_time": "2018-03-26T09:21:20Z",
                    "energy": {
                        "unit": "wh",
                        "data": 875.4090909090909
                    }
                },
                ...
            ]
        }
        '''
        # get the object with the right site_id
        state = {}

        for specific_site in raw["sites"]:
            if specific_site["site_id"] == self.site:
                state = specific_site
                break

        # build the device object
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (0, 0)
        }
        device = Device(**device_meta)

        # get produced energy from filtered object
        # accumulated_power = specific_site['energy']['data']
        accumulated_power = int(("%.2f" % specific_site['energy']['data']).replace('.', ''))

        # instance of mini utc class (tzinfo)
        utc = UTC()

        # build access_timestamp
        now = datetime.datetime.now().astimezone()
        access_timestamp = now.isoformat()

        # build measurement_timestamp
        measurement_timestamp = datetime.datetime.strptime(specific_site['end_time'], '%Y-%m-%dT%H:%M:%SZ')
        measurement_timestamp = measurement_timestamp.replace(tzinfo=utc).isoformat()

        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)

    def _get_daily_data(self) -> dict:
        marginal_query = {
            'limit': 5,
            'start': 'last_hour',
            'end': 'now'
        }
        # sending header until we get usr pwd
        provisional_header = {"Authorization":"Basic ZGdmanNkamoyMzIzMjM5ODc5ZGtma2gzZWhmazM6OTg3OTBpa2pmZGtmM2hrMmpoZGtqaGkza2RzYjM="}
        endpoint = self.api_url + 'produced'

        r = requests.get(endpoint, params=marginal_query, headers=provisional_header, verify=False)
        ans = r.json()
        if len(ans['sites']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


# needs a site_id
class SPGroup_b1(SPGroupAPI):

    def __init__(self, site_id: 'b1'):
        super().__init__(site_id)


ZERO = timedelta(0)

class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


if __name__ == '__main__':
    sp = SPGroup_b1('b1')
    sp.read_state()
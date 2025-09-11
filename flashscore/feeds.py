from utils import Utils
from configs import string, random, requests

class FEEDS:
    def __init__(self):
        self.proxies = Utils.load_proxies()
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.flashscore.com',
            'priority': 'u=1, i',
            'referer': 'https://www.flashscore.com/',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36',
            'x-fsign': 'SW9D1eZo',
            'x-geoip': '1',
        }

        self.sport_alt_ids = {
            'tennis': {
                'id':2,
                'alt_id':'f_2_0_1_en_1',
                'odd_id':'fo_2_0_1_en_1_0'
            }
        }

    @staticmethod
    def generate_fsign(length=8):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))

    def get_sport_events(self,sport, with_odds=False):
        try:
            Utils.write_log(f"Fetching events for {sport}")
            sport_alt_id = None

            if with_odds:
                sport_alt_id = self.sport_alt_ids.get(sport, {}).get('odd_id', None)
                if not sport_alt_id:return False, f"Odd identifier cannot be none for sport: {sport}"
            else:
                sport_alt_id = self.sport_alt_ids.get(sport, {}).get('alt_id', None)
                if not sport_alt_id:return False, f"Alt identifier cannot be none for sport: {sport}"

            response = requests.get(
                f'https://global.flashscore.ninja/2/x/feed/{sport_alt_id}',
                headers=self.headers,
                proxies=random.choice(self.proxies),
                timeout=60
            )

            if not response.ok:raise Exception(response.text)
            return True, response.text
        except Exception as error:
            return False, f'Error getting events {error}'
        

    def get_odds_data(self, event_id, project_id='2', geo_ip_code='NG', geo_ip_subdivision_code='NGLA'):
        try:
            Utils.write_log(f"Fetching events for {event_id}")
            params = {
                '_hash': 'oce',
                'eventId': event_id,
                'projectId': project_id,
                'geoIpCode': geo_ip_code,
                'geoIpSubdivisionCode': geo_ip_subdivision_code,
            }

            response = requests.get(
                'https://global.ds.lsapp.eu/odds/pq_graphql',
                headers=self.headers,
                params=params,
                proxies=random.choice(self.proxies),
                timeout=60
            )

            if not response.ok:raise Exception(response.text)
            return True, response.json()
        except Exception as error:
            return False, f'Error getting odds data {error}'
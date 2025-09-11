# import sys,os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import Utils
from configs import json, re

class PARSER:
    @staticmethod
    def parse_tournament_url(url):
        """
        Extracts sport_name, category, and tournament_name_from_url from a tournament URL.
        Example: '/tennis/atp-singles/us-open/' -> ('tennis', 'atp-singles', 'us-open')
        """
        if not url or not isinstance(url, str):
            return 'tennis', None, None
        pattern = r'^/(\w+)/([\w-]+)/([\w-]+)/?$'
        match = re.match(pattern, url)
        return match.groups() if match else ('tennis', None, None)

    @staticmethod
    def parse_flashscore_tennis(data_string):
        """
        Parses the Flashscore tennis data string dynamically, assigning correct keys and handling matches.
        
        Args:
            data_string (str): The raw data string from odds_data.html.
        
        Returns:
            dict: Structured data with tournaments, matches, featured matches, and metadata.
        """
        try:
            # Remove SA prefix and split records by ¬~
            if data_string.startswith('SA÷'):
                data_string = data_string.split('¬~', 1)[1] if '¬~' in data_string else data_string
            records = data_string.split('¬~')
            
            result = {
                'tournaments': {},
                'featured_matches': [],
                'metadata': {}
            }
            current_tournament = None
            
            for record in records:
                if not record.strip():
                    continue
                # Split fields by ¬
                fields = record.split('¬')
                record_dict = {}
                
                # Process each field
                for field in fields:
                    if not field or '÷' not in field:
                        continue
                    key, value = field.split('÷', 1)
                    # Convert timestamps
                    if key in ['AD', 'ADE', 'AO', 'QC']:
                        value = Utils.convert_timestamp(value.rstrip('|'))
                    # Parse JSON for bookmakers
                    if key == 'AL' and value.startswith('{"2":'):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                    record_dict[key] = value
                
                # Organize into result structure
                if 'ZA' in record_dict:
                    sport_name, category, tournament_name_from_url = PARSER.parse_tournament_url(record_dict.get('ZL'))
                    tournament_id = record_dict.get('ZC', f'tournament_{len(result["tournaments"])}')
                    current_tournament = {
                        'tournament_name': record_dict.get('ZA'),
                        'tournament_id': tournament_id,
                        'sport_id': 2,  # Tennis
                        'sport_name': sport_name,
                        'category': category,
                        'tournament_name_from_url': tournament_name_from_url,
                        'category_id': record_dict.get('ZB'),
                        'surface': record_dict.get('ZD'),
                        'tournament_unique_id': record_dict.get('ZE'),
                        'format': record_dict.get('ZF'),
                        'status': record_dict.get('ZG'),
                        'game_type': record_dict.get('ZI'),
                        'combined_id': record_dict.get('ZO'),
                        'stage': record_dict.get('ZH'),
                        'link': record_dict.get('ZL'),
                        'image': record_dict.get('OAJ'),
                        'zx_field': record_dict.get('ZX'),
                        'season_id': record_dict.get('ZEE'),
                        'tournament_status': record_dict.get('ZHS'),
                        'tss': record_dict.get('ZCC'),
                        'category_name': record_dict.get('ZAF'),
                        'matches': []
                    }
                    result['tournaments'][tournament_id] = current_tournament
                elif 'AA' in record_dict and current_tournament is not None:
                    # Handle doubles matches
                    is_doubles = current_tournament.get('game_type') == '1'
                    home_country = record_dict.get('CC', record_dict.get('FU', ''))
                    away_country = record_dict.get('FV', record_dict.get('FX', ''))
                    home_image = record_dict.get('OA', '')
                    away_image = record_dict.get('OB', '')
                    if is_doubles:
                        if '/' in home_country:
                            home_country = home_country.split('/')[0]
                        if '/' in away_country:
                            away_country = away_country.split('/')[0]
                        if ';' in home_image:
                            home_image = home_image.split(';')[0]
                        if ';' in away_image:
                            away_image = away_image.split(';')[0]
                    
                    match = {
                        'match_id': record_dict.get('AA'),
                        'start_time': record_dict.get('AD'),
                        'start_time_alt': record_dict.get('ADE'),
                        'update_time': record_dict.get('AO'),
                        'sets_played': record_dict.get('AB'),
                        'current_round': record_dict.get('CR'),
                        'game_count': record_dict.get('AC'),
                        'home_player': {
                            'name': record_dict.get('CX'),
                            'full_name': record_dict.get('AE', record_dict.get('CX')),
                            'first_name': record_dict.get('FH', record_dict.get('CX')),
                            'id': record_dict.get('JA'),
                            'slug': record_dict.get('WU'),
                            'country_code': record_dict.get('CA', record_dict.get('CY')),
                            'country': home_country,
                            'image': home_image,
                            'is_winner': record_dict.get('AS') == '1'
                        },
                        'away_player': {
                            'name': record_dict.get('AF', record_dict.get('CX')),
                            'full_name': record_dict.get('AF', record_dict.get('CX')),
                            'first_name': record_dict.get('FK', record_dict.get('CX')),
                            'id': record_dict.get('JB'),
                            'slug': record_dict.get('WV'),
                            'country_code': record_dict.get('CB', record_dict.get('GB')),
                            'country': away_country,
                            'image': away_image,
                            'is_winner': record_dict.get('AW') == '1'
                        },
                        'home_sets_won': record_dict.get('AG') if not is_doubles else None,
                        'away_sets_won': record_dict.get('AH') if not is_doubles else None,
                        'set_scores': {
                            'set1': {
                                'home': record_dict.get('BA') if not is_doubles else None,
                                'away': record_dict.get('BB') if not is_doubles else None
                            },
                            'set2': {
                                'home': record_dict.get('BC') if not is_doubles else None,
                                'away': record_dict.get('BD') if not is_doubles else None
                            },
                            'set3': {
                                'home': record_dict.get('BE') if not is_doubles else None,
                                'away': record_dict.get('BF') if not is_doubles else None
                            },
                            'set4': {
                                'home': record_dict.get('BG') if not is_doubles else None,
                                'away': record_dict.get('BH') if not is_doubles else None
                            }
                        },
                        'home_match_count': record_dict.get('HMC'),
                        'live_status': record_dict.get('AN'),
                        'market_watchers': record_dict.get('MW'),
                        'bookmakers': record_dict.get('AL'),
                        'misc_flags': {
                            'home_rank_weight': record_dict.get('RW'),
                            'away_rank_weight': record_dict.get('BW'),
                            'bx_flag': record_dict.get('BX'),
                            'link_status': record_dict.get('WL'),
                            'home_code': record_dict.get('WM'),
                            'away_code': record_dict.get('WN'),
                            'home_rank_alt': record_dict.get('GRA'),
                            'away_rank_alt': record_dict.get('GRB'),
                            'home_set_flag': record_dict.get('AZ'),
                            'away_set_flag': record_dict.get('AY'),
                            'away_status': record_dict.get('AW')
                        }
                    }
                    current_tournament['matches'].append(match)
                elif 'QB' in record_dict:
                    result['featured_matches'].append({
                        'match_id': record_dict.get('QB'),
                        'timestamp': record_dict.get('QC')
                    })
                elif 'A1' in record_dict:
                    result['metadata']['session_hash'] = record_dict.get('A1')
            
            return True, result
        
        except Exception as error:
            return False, f'Error parsing events data {error}'
    


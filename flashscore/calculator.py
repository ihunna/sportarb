import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import defaultdict
from configs import traceback, time, json, sys
from utils import Utils
from flashscore.feeds import FEEDS
from flashscore.parser import PARSER
from telegram.messanger import MESSANGER

class CALCULATOR:
    def __init__(self, capital=0, min_profit_percentage=0):
        self.feeds = FEEDS()
        self.parser = PARSER
        self.messanger = MESSANGER()
        self.balance = capital
        self.min_profit_percentage = min_profit_percentage

    def fetch_and_parse_tennis_data(self):
        try:
            success, data_or_error = self.feeds.get_sport_events('tennis', with_odds=False)
            if not success:
                return False, data_or_error

            success, parsed_data = self.parser.parse_flashscore_tennis(data_or_error)
            if not success:
                raise Exception(parsed_data)
            return True, parsed_data
        except Exception as error:
            return False, str(error)

    def extract_full_time_odds(self, odds_data):
        """
        Extracts full-time home/away odds from the GraphQL response for each bookmaker, filtering for active odds.
        """
        try:
            event_odds = odds_data.get('data', {}).get('findOddsByEventId', {}).get('odds', [])
            if not event_odds:
                return True, event_odds

            full_time_odds = []
            for item in event_odds:
                if item.get('bettingType') == 'HOME_AWAY' and item.get('bettingScope') == 'FULL_TIME':
                    bookmaker_id = item.get('bookmakerId')
                    odds = item.get('odds', [])
                    if len(odds) == 2 and odds[0].get('active', False) and odds[1].get('active', False):
                        home_odds = float(odds[0]['value']) if 'value' in odds[0] else 0
                        away_odds = float(odds[1]['value']) if 'value' in odds[1] else 0
                        if home_odds > 0 and away_odds > 0:
                            full_time_odds.append({
                                'BI': str(bookmaker_id),
                                'XA': home_odds,
                                'XB': away_odds
                            })
            
            return True, full_time_odds
        except Exception as error:
            return False, f'Error extracting full time odds: {error}'

    def calculate_arbitrage(self, odds_data, capital):
        """
        Calculates arbitrage opportunities for a match's odds.
        Args:
            odds_data: List of dicts with bookmaker odds (e.g., [{'BI': '417', 'XA': 1.8, 'XB': 2.0}, ...]).
            capital: Investment capital for simulation.
        Returns: (has_arb: bool, arb_details: dict or None)
        """
        try:
            if not odds_data or len(odds_data) < 2:
                return False, 'No odds data'
            
            # Find best odds for home (XA) and away (XB)
            best_home_odds = 0
            best_away_odds = 0
            home_bookmaker = None
            away_bookmaker = None
            
            for bookmaker in odds_data:
                home_odds = float(bookmaker.get('XA', 0))
                away_odds = float(bookmaker.get('XB', 0))
                if home_odds > best_home_odds:
                    best_home_odds = home_odds
                    home_bookmaker = bookmaker.get('BI')
                if away_odds > best_away_odds:
                    best_away_odds = away_odds
                    away_bookmaker = bookmaker.get('BI')
            
            if best_home_odds <= 1 or best_away_odds <= 1:
                return False, 'Low best home_away odds'
            
            # Calculate implied probabilities
            implied_prob_home = 1 / best_home_odds if best_home_odds > 0 else 0
            implied_prob_away = 1 / best_away_odds if best_away_odds > 0 else 0
            total_implied_prob = implied_prob_home + implied_prob_away
            
            if total_implied_prob >= 1 or total_implied_prob == 0:
                return False, None
            
            # Calculate stakes for arbitrage
            stake_home = (implied_prob_home / total_implied_prob) * capital
            stake_away = (implied_prob_away / total_implied_prob) * capital
            profit_amount = stake_home * best_home_odds - capital  # Profit if home wins (same for away)
            profit_percentage = (profit_amount / capital) * 100
            
            # Check if profit percentage meets minimum threshold
            if profit_percentage < self.min_profit_percentage:
                return False, f'Profit percentage {profit_percentage:.2f}% below minimum {self.min_profit_percentage}%'
            
            arb_details = {
                'home_odds': best_home_odds,
                'away_odds': best_away_odds,
                'home_bookmaker_id': home_bookmaker,
                'away_bookmaker_id': away_bookmaker,
                'stake_home': round(stake_home, 2),
                'stake_away': round(stake_away, 2),
                'profit_amount': round(profit_amount, 2),
                'profit_percentage': round(profit_percentage, 2),
                'total_implied_prob': round(total_implied_prob, 4)
            }
            return True, arb_details
        except Exception as error:
            return False, f'Error calculating arb: {error}'

    def get_tennis_arbitrage_opportunities(self, country='NG'):
        """
        Fetches tennis events, retrieves odds for each match using multiple geo IPs, merges odds, calculates arbitrage opportunities, and includes bookmaker details.
        Args:
            country (str): Country code for bookmaker details (default: 'NG').
        Returns: dict with tournaments, matches, odds, and arbitrage details.
        """
        try:
            Utils.write_log("------------------------Tennis arb operation started------------------------")
            # Fetch and parse tennis events
            success, data = self.fetch_and_parse_tennis_data()
            if not success:
                return False, data
            
            result = {
                'tournaments': {},
                'metadata': data.get('metadata', {}),
                'arbitrage_opportunities': []
            }
            iteration_profit = 0
            iteration_arbs = 0
            
            # Process each tournament and match
            for tournament_id, tournament in data.get('tournaments', {}).items():
                tournament_data = {
                    'tournament_name': tournament['tournament_name'],
                    'sport_name': tournament['sport_name'],
                    'category': tournament['category'],
                    'tournament_name_from_url': tournament['tournament_name_from_url'],
                    'tournament_id': tournament_id,
                    'matches': []
                }
                
                for match in tournament.get('matches', []):
                    has_arb = False
                    match_id = match['match_id']
                    project_id = '2'  # From params in the code
                    
                    # Fetch odds for the match with multiple geo IPs
                    multi_odd_data = [
                        {'geo_ip': 'NG', 'sub_geo_ip': 'NGLA'},
                        {'geo_ip': '', 'sub_geo_ip': ''}
                    ]
                    merged_odds = []
                    all_bookmakers = []
                    seen_bookmakers = set()
                    
                    for geo in multi_odd_data:
                        success, odds_response = self.feeds.get_odds_data(
                            match_id,
                            geo_ip_code=geo['geo_ip'],
                            geo_ip_subdivision_code=geo['sub_geo_ip']
                        )
                        if not success:
                            Utils.write_log(f"Failed to fetch odds for {match_id} with geo {geo['geo_ip']}/{geo['sub_geo_ip']}: {odds_response}")
                            continue

                        success, parsed_odds = self.extract_full_time_odds(odds_response)
                        if not success:
                            Utils.write_log(f"Error extracting odds for {match_id} with geo {geo['geo_ip']}/{geo['sub_geo_ip']}: {parsed_odds}")
                            continue
                        
                        if not parsed_odds:
                            Utils.write_log(f"No odds data found for {match_id} with geo {geo['geo_ip']}/{geo['sub_geo_ip']}")
                            continue

                        # Merge odds, avoiding duplicates
                        for odds in parsed_odds:
                            bookmaker_id = odds['BI']
                            if bookmaker_id not in seen_bookmakers:
                                merged_odds.append(odds)
                                seen_bookmakers.add(bookmaker_id)
                            else:
                                # If bookmaker exists, keep the higher odds
                                existing = next((o for o in merged_odds if o['BI'] == bookmaker_id), None)
                                if existing and (odds['XA'] > existing['XA'] or odds['XB'] > existing['XB']):
                                    merged_odds.remove(existing)
                                    merged_odds.append(odds)

                        # Collect bookmaker details
                        bookmakers = odds_response.get('data', {}).get('findOddsByEventId', {}).get('settings', {}).get('bookmakers', [])
                        all_bookmakers.extend(bookmakers)

                    if not merged_odds:
                        Utils.write_log(f'No valid odds data for {match_id} from any geo')
                        match_data = {
                            'match_id': match_id,
                            'home_player': match['home_player']['name'],
                            'away_player': match['away_player']['name'],
                            'start_time': match['start_time'],
                            'home_sets_won': match['home_sets_won'],
                            'away_sets_won': match['away_sets_won'],
                            'set_scores': match['set_scores'],
                            'odds_error': 'No valid odds data'
                        }
                        tournament_data['matches'].append(match_data)
                        continue

                    # Create bookie_map from all bookmakers, prioritizing NG/NGLA
                    bookie_map = {}
                    for b in all_bookmakers:
                        bookmaker_id = str(b.get('bookmaker', {}).get('id'))
                        if bookmaker_id not in bookie_map:
                            bookie_map[bookmaker_id] = b

                    # Calculate arbitrage with merged odds
                    has_arb, arb_details = self.calculate_arbitrage(merged_odds, self.balance)

                    match_data = {
                        'match_id': match_id,
                        'home_player': match['home_player']['name'],
                        'away_player': match['away_player']['name'],
                        'start_time': match['start_time'],
                        'home_sets_won': match['home_sets_won'],
                        'away_sets_won': match['away_sets_won'],
                        'set_scores': match['set_scores'],
                        'odds': merged_odds,
                        'has_arbitrage': has_arb
                    }
                    
                    if has_arb:
                        # Add bookmaker details for arbitrage
                        arb_details['home_bookmaker'] = bookie_map.get(arb_details['home_bookmaker_id'], {})
                        arb_details['away_bookmaker'] = bookie_map.get(arb_details['away_bookmaker_id'], {})
                        match_data['arbitrage_details'] = arb_details
                        result['arbitrage_opportunities'].append({
                            'tournament_id': tournament_id,
                            'tournament_name': tournament['tournament_name'],
                            'match_id': match_id,
                            'home_player': match['home_player']['name'],
                            'away_player': match['away_player']['name'],
                            'arbitrage_details': arb_details
                        })
                        # Simulate profit and update iteration counters
                        iteration_profit += arb_details['profit_amount']
                        iteration_arbs += 1

                    tournament_data['matches'].append(match_data)
                    if has_arb:
                        Utils.write_arb(
                            f"""
                                /* --------------------------------------------------------------- */
                                An arb opportunity found on match {match_id}
                                {match_data["match_id"]} -- {match_data["arbitrage_details"]["profit_percentage"]}%
                                Home: {match_data["home_player"]} @ {arb_details["home_odds"]} (Bookmaker: {arb_details["home_bookmaker"].get("bookmaker", {}).get("name", "Unknown")})
                                Away: {match_data["away_player"]} @ {arb_details["away_odds"]} (Bookmaker: {arb_details["away_bookmaker"].get("bookmaker", {}).get("name", "Unknown")})
                                Stakes: Home {arb_details["stake_home"]}, Away {arb_details["stake_away"]}
                                Profit Amount: {arb_details["profit_amount"]}
                                Profit: {arb_details["profit_percentage"]}%
                                /* --------------------------------------------------------------- */
                            """
                        )
                        success,msg = self.messanger.report_arb(match_data,arb_details)
                        if not success:raise Exception(msg)

                    elif isinstance(arb_details, str) and 'below minimum' in arb_details:
                        Utils.write_log(f"Skipped arb for {match_id}: {arb_details}")
                
                result['tournaments'][tournament_id] = tournament_data
            
            # Update balance with iteration profit
            self.balance += iteration_profit
            Utils.write_log(f"Iteration Summary: {iteration_arbs} arbs found, Total Profit: {iteration_profit:.2f}, New Balance: {self.balance:.2f}")
            Utils.write_log("------------------------Tennis arb operation done------------------------")
            return True, result
        
        except Exception as error:
            traceback.print_exception(error)
            return False, str(error)

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python calculator.py <capital> <wait_time> <min_profit_percentage>")
        sys.exit(1)
    
    try:
        capital = float(sys.argv[1])
        wait_time = int(sys.argv[2])
        min_profit_percentage = float(sys.argv[3])
    except ValueError:
        print("Error: Capital, wait time, and minimum profit percentage must be numbers")
        sys.exit(1)

    calc = CALCULATOR(capital=capital, min_profit_percentage=min_profit_percentage)
    while True:
        success, result = calc.get_tennis_arbitrage_opportunities(country='NG')
        Utils.write_log(result)

        Utils.write_log(f'Sleeping for {wait_time} seconds')
        time.sleep(wait_time)
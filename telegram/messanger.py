import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from configs import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID,TELEGRAM_BOT_NAME, requests, datetime, time, pytz
from utils import Utils

class MESSANGER:
    def __init__(self):
        pass

    def send_message(self, message, is_arb=True):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            params = {
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": f"{TELEGRAM_BOT_NAME} \n\n {message}",
                "parse_mode": "HTML"
            }
            for attempt in range(3):
                response = requests.post(url, json=params)
                if response.ok:
                    return True, "Message sent"
                if response.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                return False, response.text
            return False, "Failed after retries: Rate limit exceeded"
        except Exception as error:
            return False, f"Exception in send_message: {str(error)}"

    def report_arb(self,match_data, arb_details):
        """
        Sends arbitrage opportunity details to a Telegram chat.
        Args:
            match_data (dict): Match data containing match_id, home_player, away_player, etc.
            arb_details (dict): Arbitrage details with odds, bookmakers, stakes, and profit.
        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        try:
            if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
                return False, "Telegram bot token or chat ID not configured"
            
            # Escape special HTML characters to prevent parsing errors
            def escape_html(text):
                if not isinstance(text, str):
                    text = str(text)
                return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # Parse start_time (e.g., "2025-09-11 13:00:00 UTC") to human-readable
            try:
                start_time = str(match_data['start_time']).replace(' UTC', '')  # Remove UTC suffix
                if isinstance(match_data['start_time'], (int, float)):
                    dt = datetime.fromtimestamp(match_data['start_time'], tz=pytz.UTC)
                else:
                    dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    dt = pytz.UTC.localize(dt)  # Assign UTC timezone
                # Convert to WAT (UTC+1)
                dt = dt.astimezone(pytz.timezone('Africa/Lagos'))
                formatted_time = dt.strftime("%b %d, %Y %I:%M %p")
            except (ValueError, TypeError) as e:
                formatted_time = escape_html(str(match_data['start_time']))

            # Format the message
            message = (
                f"🎾 <b><u>Arbitrage Opportunity Found</u></b> \n"
                f"<b>Match ID:</b> {escape_html(match_data['match_id'])}\n"
                f"<b>Match:</b> {escape_html(match_data['home_player'])} vs {escape_html(match_data['away_player'])}\n\n"
                f"<b>Odds:</b>\n"
                f"  -Home: {escape_html(arb_details['home_odds'])} ({escape_html(arb_details['home_bookmaker'].get('bookmaker', {}).get('name', 'Unknown'))})\n"
                f"  -Away: {escape_html(arb_details['away_odds'])} ({escape_html(arb_details['away_bookmaker'].get('bookmaker', {}).get('name', 'Unknown'))})\n\n"
                f"<b>Stakes:</b>\n"
                f"  -Home: {arb_details['stake_home']:.2f}\n"
                f"  -Away: {arb_details['stake_away']:.2f}\n\n"
                f"<b>Profit:</b> 💰 <b>{arb_details['profit_percentage']:.2f}% ({arb_details['profit_amount']:.2f})</b> 💰\n"
                f"<b>Time:</b> {formatted_time}"
            )

            success, msg = self.send_message(message)
            if not success:raise Exception(msg)
            return success, f"Successfully sent arb report for {match_data['match_id']} to Telegram"
        
        except Exception as error:
            return False, f"Error sending Telegram message for {match_data.get('match_id')}: {str(error)}"
        


if __name__ == "__main__":
    match_data = {
        'match_id': 'nHr98cHL',
        'home_player': 'Arnaboldi F.',
        'away_player': 'Napolitano S.',
        'start_time': '2025-09-11 13:00:00 UTC'
    }
    arb_details = {
        'home_odds': 3.4,
        'home_bookmaker': {'bookmaker': {'name': 'bet365'}},
        'away_odds': 1.54,
        'away_bookmaker': {'bookmaker': {'name': 'Betway South Africa'}},
        'stake_home': 31174.09,
        'stake_away': 68825.91,
        'profit_percentage': 5.99,
        'profit_amount': 5991.90
    }
    messenger = MESSANGER()
    success, msg = messenger.report_arb(match_data, arb_details)
    print(success, msg)
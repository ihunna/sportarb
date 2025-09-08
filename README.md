# Tennis Arbitrage Bot

## Overview
This Python bot identifies arbitrage opportunities in tennis matches by fetching and analyzing odds from Flashscore. It retrieves match data, collects odds from multiple bookmakers using different geo IPs (Nigeria and global), merges them, and calculates potential arbitrage profits. Results are saved to `arbs.json`, and opportunities are logged for review.

## Features
- **Fetches Tennis Events**: Retrieves upcoming tennis matches using the Flashscore API.
- **Collects Odds**: Gathers full-time home/away odds for each match
- **Merges Odds**: Combines odds from both sources, removing duplicates and prioritizing higher odds.
- **Calculates Arbitrage**: Identifies arbitrage opportunities where the total implied probability is less than 100%, ensuring a guaranteed profit.
- **Logs Results**: Saves arbitrage details to `arbs.json` and logs opportunities with match IDs, players, odds, stakes, and profit percentages.
- **Active Odds Only**: Filters for active odds to ensure actionable opportunities.

## Requirements
- Python 3.x
- Dependencies: `requests`, `json`, `random`, `time`
- Modules: `configs`, `utils`, `flashscore.feeds`, `flashscore.parser` (assumed to be provided)
- Internet connection for API calls to Flashscore

## Usage
1. Ensure dependencies and required modules are installed.
2. Run the script:
   ```bash
   python calculator_updated.py
   ```
3. The bot runs in a loop, fetching data every 30-60 minutes (randomized).
4. Check `arbs.json` for results and logs for arbitrage opportunities.

## Output
- **arbs.json**: Contains tournaments, matches, odds, and arbitrage details.
- **Logs**: Arbitrage opportunities are logged with match details, odds, bookmakers, stakes, and profit percentages.

## Notes
- **Error Handling**: Logs errors for failed API calls or invalid odds.
- **Time-Sensitive**: Odds are fetched close to match times (e.g., `Yi9s9uDD` at 2025-09-07 17:30 UTC). Run frequently to catch live opportunities.

## Example
    /* --------------------------------------------------------------- */
        An arb opportunity found on match pYLxOp7D
        pYLxOp7D -- 1.15%
        Home: Shimizu A. @ 2.75 (Bookmaker: Unibet)
        Away: Okamura K. @ 1.6 (Bookmaker: bwin)
        Stakes: Home 0.3678, Away 0.6322
        Profit: 1.15%
    /* --------------------------------------------------------------- */

    /* --------------------------------------------------------------- */
        An arb opportunity found on match pUeOUBJq
        pUeOUBJq -- 1.5%
        Home: Bentzel C. S. @ 5.4 (Bookmaker: Unibet)
        Away: Duran T. @ 1.25 (Bookmaker: Paripesa)
        Stakes: Home 0.188, Away 0.812
        Profit: 1.5%
    /* --------------------------------------------------------------- */

## Contact me for setup or sport/tournament inclusion.
- **Telegram**: https://t.me/hustleoclok
- **Email**: ihunnaemmanuel@gmail.com
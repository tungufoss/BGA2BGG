import argparse
from script import load_json
import os

def prompt_for_download(player_id, player_name):
    # Construct the URL to open
    url = f"https://boardgamearena.com/gamestats?player={player_id}&opponent_id=0&finished=1#"

    # Instruct the user
    print(f"Please opened {url} as 'latest.gameshistory.html'")

def main(player_name, known):
    # Find player ID by name
    for player_id, player_data in known['players'].items():
        if player_data['BGA'] == player_name:
            # If found, open browser and prompt for download
            prompt_for_download(player_id, player_name)
            return

    # If not found, print an error
    print(f"Player name '{player_name}' not found in known players.")

if __name__ == "__main__":
    # Setting up argparse
    parser = argparse.ArgumentParser(description="Open a player's game stats on Board Game Arena.")
    parser.add_argument('--playername', required=True, help="Player name on Board Game Arena.")
    parser.add_argument('-k', '--known', default='known_data.json', help="Path to the known players and games JSON file.")
    args = parser.parse_args()

    known_data_path = args.known

    # Validate known data file
    assert known_data_path.endswith('.json'), 'Known data file must be a JSON file'
    assert os.path.exists(known_data_path), 'Known data file does not exist'

    # Global data
    known = load_json(known_data_path)
    assert 'players' in known, 'Known data file must contain a "players" key'
    assert 'games' in known, 'Known data file must contain a "games" key'

    main(args.playername, known)

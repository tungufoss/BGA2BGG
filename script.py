import json
import os
import datetime
import argparse


# Open the file containing your JSON data
def load_json(file_path):
    with open(file_path, 'r') as f:
        # Load the JSON data from the file
        return json.load(f)


def extract_game_info(gameplay, creation_time):
    game_info = {
        'players': [],
        'table': None,
        'game': None,
        'time': None,
        'duration_minutes': None,
        'information': None,
    }
    for key, value in gameplay.items():
        if key == 'info':
            game_info['game'] = value[1]['text']
            game_info['table'] = value[1]['href'].split('=')[-1]
        elif key == 'time':
            # Extract duration of game
            duration = value[1]['text']
            if 'mn' in duration:
                minutes = int(duration.split(' ')[0])
            else:
                minutes = None
            game_info['duration_minutes'] = minutes

            # Extract time when game was played
            time_string = value[0]['text']
            # if time since has the format "x hours ago"
            if 'hours' in time_string:
                hours = int(time_string.split(' ')[0])
                time_to_add = datetime.timedelta(hours=hours)
                new_time = creation_time - time_to_add
            elif 'yesterday' in time_string:
                # Extract the time part
                time_part = time_string.split(" at ")[1]

                # Create a datetime object for yesterday's date
                yesterday_date = creation_time - datetime.timedelta(days=1)

                # Combine the date and time parts
                new_time = datetime.datetime.strptime(time_part, '%H:%M').replace(
                    year=yesterday_date.year,
                    month=yesterday_date.month,
                    day=yesterday_date.day)
            else:
                time_part = time_string.split(" at ")[1]
                date_part = time_string.split(" at ")[0]
                date_part = datetime.datetime.strptime(date_part, '%Y-%m-%d')

                new_time = datetime.datetime.strptime(time_part, '%H:%M').replace(
                    year=date_part.year,
                    month=date_part.month,
                    day=date_part.day)

            # new_time -= datetime.timedelta(minutes=minutes)
            game_info['time'] = new_time.strftime('%Y-%m-%d %H:%M')

        elif key == 'players':
            for player_info in value:
                playerid = player_info['children'][1]['children'][0]['href'].split('=')[-1]
                player = {'rank': int(player_info['children'][0]['text'][:-2]),
                          'BGG': known['players'][playerid]['BGG'] if playerid in known['players'] else 'Anonymous',
                          'score': int(player_info['children'][2]['text'])
                          }
                game_info['players'].append(player)
        elif key == 'game_rank':
            value = value[1]['children']
            assert value[2]['children'][1]['class'] == 'gamerank_value'
            gamerank_value = int(value[2]['children'][1]['text'])
            gamerank = value[2]['class'].replace('gamerank gamerank_', '')
            elo_delta = value[1]['text']
            game_info[
                'information'] = f"Played on [url=https://boardgamearena.com/table?table={game_info['table']}]Board Game Arena[/url]\nGame rank: {gamerank}\nELO: {gamerank_value} (delta {elo_delta})"
    return game_info


def print_game(game_info):
    print(f"Game: {game_info['game']}")
    print(f"Time: {game_info['time']}")
    print(f"Duration: {game_info['duration_minutes']} minutes")
    if len(game_info['players']) == 1:
        player = game_info['players'][0]
        print(f'Solo mode: {"won" if player["score"] > 0 else "lost"}')
    else:
        print(f"Players:")
        for player in game_info['players']:
            print(f"\t{player['rank']}. {player['BGG']} ({player['score']})")
    print(f"{game_info['information']}")
    print()


def extract_games_history(data):
    for item in data:
        if 'children' in item and item['children'][0]['text'] == 'Games history':
            games = item['children'][1]['children'][0]['children'][0]['children']
            return [{'info': game['children'],
                     'time': game[1]['children'],
                     'players': game[2]['children'],
                     'game_rank': game[3]['children']} for game in games]
    return []


def extract_games_history(data):
    """Extracts games history from the given data."""
    for item in data:
        # Check if the item has 'children' and the first child's 'text' field is 'Games history'
        if 'children' in item and item['children'][0]['text'] == 'Games history':
            games = item['children'][1]['children'][0]['children'][0]['children'][0]['children']
            games = [game['children'] for game in games]
            return [{'info': game[0]['children'],
                     'time': game[1]['children'],
                     'players': game[2]['children'],
                     'game_rank': game[3]['children']}
                    for game in games]
    return []


def main(file_path, game_filter=None):
    # When was the file created
    creation_time = os.path.getctime(file_path)
    creation_time = datetime.datetime.fromtimestamp(creation_time)

    # Loop through the data
    data = load_json(file_path)
    games_history = extract_games_history(data)
    games_info = [extract_game_info(game, creation_time) for game in games_history]
    games = sorted(set([play['game'] for play in games_info]), key=lambda x: x.lower())
    if game_filter:
        assert game_filter in games, f"Error: '{game_filter}' not found in the list of games: {', '.join(games)}."
        games = [game_filter]

    num_games = 0
    first_game = datetime.datetime.max
    last_game = datetime.datetime.min
    for game in games:
        for play in games_info:
            if play['game'] == game:
                print_game(play)
                num_games += 1
                play_time = datetime.datetime.strptime(play['time'], '%Y-%m-%d %H:%M')
                if play_time < first_game:
                    first_game = play_time
                if play_time > last_game:
                    last_game = play_time

    print(f"=====> {len(games)} unique games played for a total of {num_games} plays"
          f" between {first_game.date()} and {last_game.date()}")

    if game_filter:
        number = known['games'][game_filter]['BGG']
        name = game_filter.replace(' ', '-').lower()
        print(f"Logged plays: https://boardgamegeek.com/boardgame/{number}/{name}/mygames/plays")


if __name__ == "__main__":
    # Setting up argparse
    parser = argparse.ArgumentParser(description="Process a JSON file of games history.")
    parser.add_argument('-f', '--file', default='all.games.history.json', help="Path to the game history JSON file.")
    parser.add_argument('-k', '--known', default='known_data.json',
                        help="Path to the known players and games JSON file.")
    parser.add_argument('-g', '--game', help="Filter by a specific game. If not specified, all games are displayed.")
    args = parser.parse_args()

    file_path = args.file
    known_data_path = args.known

    # Asserts for input validation
    assert file_path.endswith('.json'), 'File must be a JSON file'
    assert os.path.exists(file_path), 'File does not exist'
    assert known_data_path.endswith('.json'), 'Known data file must be a JSON file'
    assert os.path.exists(known_data_path), 'Known data file does not exist'

    # Global data
    known = load_json(known_data_path)
    assert 'players' in known, 'Known data file must contain a "players" key'
    assert 'games' in known, 'Known data file must contain a "games" key'

    main(file_path, args.game)

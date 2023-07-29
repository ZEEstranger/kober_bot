import pandas as pd
import json


def get_custom_players():
    """
    Get players df who play customs
    """
    data = pd.read_csv('files/data/players.csv', index_col=['player_id'])
    df = pd.DataFrame(data)

    return df


def get_json_secrets(file_path):

    with open(file_path) as f:
        json_data = json.load(f)
    
    return json_data


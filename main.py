from importlib import import_module
import riotwatcher as rw
import pandas as pd
import openpyxl as xl

from add_func import get_api, get_custom_players
from updates import rune_update, champs_update, players_update
from utils.structure_query import structure_array


player_name = 'Вареники Буду'
player_region = 'RU'


lol_watcher = rw.LolWatcher(get_api())

actual_version = lol_watcher.data_dragon.versions_all()[0]
#game_id = f'RU_383587693'
player_routing = 'europe'


#match_timeline = lol_watcher.match.timeline_by_match(region=player_routing, match_id=game_id)

#match_data = lol_watcher.match.by_id(region=player_routing, match_id=game_id)['info']['participants']

#custom_file = 'files/customs_big_season_3.xlsx'

#players_df = get_custom_players()
#players_update(players_df, lol_watcher)

#items = lol_watcher.data_dragon.items(actual_version)['data']['1001'].keys()


def get_game_info(lol_watcher : rw.LolWatcher, player_routing : str, game_id : str):
    """
    Get game info about game (game_id)
    """
    match_data_dict = []
    #match_data = lol_watcher.match.by_id(region=player_routing, match_id=game_id)

    match_data = lol_watcher.match.by_id(player_routing, game_id)['info']['participants']

    for j in range(len(match_data)):
        game_data = match_data[j]
        match_data_dict.append([])
        for i in structure_array:
            match_data_dict[j].append(game_data[i])
        if j < len(match_data)/2:
            match_data_dict[j].append('blue')
        else:
            match_data_dict[j].append('red')
    df = pd.DataFrame(match_data_dict, columns=structure_array+['teams'])
    
    pd.read_excel('files/customs_big_season_3.xlsx', sheet_name='Custom_data_players')
    writer =  pd.ExcelWriter('files/customs_big_season_3.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay')
    start_row = writer.sheets['Custom_data_players'].max_row
    if start_row == 0:
        df.to_excel(writer, sheet_name='Custom_data_players', index=False)
    else:
        df.to_excel(writer, sheet_name='Custom_data_players', index=False, header=False, startrow=start_row)

    writer.save()
    df.to_excel('files/customs_big_season_3.xlsx', sheet_name='Custom_data_players')


def get_game_data(lol_watcher : rw.LolWatcher, player_routing : str, game_id : str):
    """
    Get game info about game data
    """

    match_data = lol_watcher.match.by_id(player_routing, game_id)

    print(match_data['info']['gameStartTimestamp'])
    
str = '392885379'
game_id = f'RU_{str}'
get_game_info(lol_watcher, player_routing, game_id)

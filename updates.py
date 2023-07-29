import pandas as pd
import riotwatcher as rw


def rune_update(lol_watcher, actual_version):
    # Update runes
    runes_list = []
    for rune_set in lol_watcher.data_dragon.runes_reforged(actual_version):
        for rune_str in rune_set['slots']:
            for rune in rune_str['runes']:
                runes_list.append([rune['id'], rune['key']])
                
    runes_df = pd.DataFrame(runes_list, columns=['rune_id', 'rune_name'])

    runes_df.to_csv('files/data/runes.csv', index=False)


def champs_update(lol_watcher, actual_version):

    champs_full_dict = lol_watcher.data_dragon.champions(actual_version)['data']
    champ_list = []
    for champ in champs_full_dict:
        champ_list.append([champs_full_dict[champ]['key'], champs_full_dict[champ]['name'], champs_full_dict[champ]['tags']])

    champ_df = pd.DataFrame(champ_list, columns=['champ_id', 'champ_name', 'champ_tags'])

    champ_df.to_csv('files/data/champions.csv', index=False)


def players_update(players_df: pd.DataFrame, lol_watcher : rw.LolWatcher):

    players_df_new = players_df[players_df['player_puuid'].isna()]
    players_df = players_df[players_df['player_puuid'].notna()]

    player_region = 'RU'

    if not players_df_new.empty:
        players_df_new['player_puuid'] = players_df_new['player_name'].apply(lambda x: lol_watcher.summoner.by_name(player_region, x)['puuid'])

        union = pd.concat([players_df, players_df_new])
        union.sort_index(inplace=True)

        union.to_csv('files/data/players.csv')

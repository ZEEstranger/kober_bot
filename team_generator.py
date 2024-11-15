import random
import pandas as pd
import itertools as ite

from add_func import get_custom_players

def read_numbers():
    """
    Функция считывает игроков в кастомы
    """
    while True:
        try:    
            size = int(input("Enter number of players\n"))
            break
        except:
            pass

    players = []    
    df = get_custom_players()
    df = df['player_name']

    print("Players:\n", df.to_string())
    while True:
        try:
            pl_str = input(f"Enter {size} players with spaces\n")

            pl_mas = pl_str.split()

            i = 0
            while i < size:
                flag = False
                for j in players:
                    if pl_mas[i] == j:
                        flag = True
                        break
                if not flag:
                    players.append(int(pl_mas[i]))
                    i += 1
            players = bubble_sort(players)
            break
        except:
            pass

    return players


def setups_check(player_id_list):
    """
    Функция проверяет, есть ли такой сетап уже в записанных
    """
    try:
        df = pd.read_csv('files/team_setups.csv')
    except:
        return False
    player_str = (',').join(map(str, player_id_list))
    teams = list(df.columns)
    for team in teams:
        if team == player_str:
            return True
    return False

def team_gen(players_id_list):
    left_players = []
    left_players_temp = []
    player_str = ','.join(map(str, players_id_list))

    left_players_temp = list(ite.combinations(players_id_list, int(len(players_id_list)/2)))

    for i in left_players_temp:
        str_temp = ''
        for j in i:
            str_temp += str(j) + ','
        str_temp = str_temp[:-1]
        left_players.append(str_temp)

    # дф из одного столбца, где он - новая комбинация игроков
    new_df = pd.DataFrame(left_players, columns=[player_str])

    try:
        df = pd.read_csv('files/team_setups.csv')
        pd.concat([df, new_df], axis=1).to_csv('files/team_setups.csv', index=False)
    except:
        new_df.to_csv('files/team_setups.csv', index=False)

def play_custom(players_id_list, players_dict):

    df = pd.read_csv('files/team_setups.csv')

    player_str = ','.join(map(str, players_id_list))
    a = df[player_str].loc[df[player_str].notnull()].values.tolist()
    df.drop(columns=player_str, inplace=True)

    b = random.randint(0, len(a)-1)

    players_str = a[b].split(',')
    print(players_str)
    players_id = []
    for i in players_str:
        players_id.append(int(i))
    player_str_new = ''
    for i in players_id:
        player_str_new += players_dict.get(i) + ', '
    player_str_new = player_str_new[:-2]

    print('left team = ', player_str_new)
    a.pop(b)
    c = pd.DataFrame(a, columns=[player_str])
    pd.concat([df, c], axis=1).to_csv('files/team_setups.csv', index=False)
    
if __name__ == '__main__':
    players_id = read_numbers()
    
    df = get_custom_players()
    df = df['player_name']
    df = df.to_dict()

    players = []
    for i in players_id:
        players.append(df.get(i))
    setup_flag = setups_check(players_id)
    if not setup_flag:
        team_gen(players_id)
    play_custom(players_id, df)

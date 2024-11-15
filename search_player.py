import psycopg2
import discord
import itertools as ite
import random

def get_all_players(guild_id):
    "Все игроки этого сервера"

    conn = psycopg2.connect(dbname='customs', user='postgres', password='1184', host='localhost')

    with conn.cursor() as cur:
        cur.execute(f'select discord_member_id, player_name from added_players where discord_guild_id = {guild_id} order by player_name')
        data = cur.fetchall()

    return data


def add_new_player(guild_id, disc_id, name):
    "Зарегистрировать игрока в БД"
    conn = psycopg2.connect(dbname='customs', user='postgres', password='1184', host='localhost')
    with conn.cursor() as cur:
        cur.execute(f"insert into added_players values ({guild_id}, {disc_id}, '{name}')")
        conn.commit()
    
    return True


def get_db_data_from_query(sql_query, fetch=False):
    """Выполнение запроса в БД
        sql_query - Запрос
        fetch - нужен ли ответ    
    """
    conn = psycopg2.connect(dbname='customs', user='postgres', password='1184', host='localhost')
    data = None
    with conn.cursor() as cur:
        cur.execute(sql_query)
        if fetch:
            data = cur.fetchall()
        conn.commit()

    conn.close()
    
    return data


def check_db_team_setup(guild_id:int, players_id_list:list):
    "Проверка существования сетапа в БД"


    players_str = ", ".join(map(str, players_id_list))
    sql_query = f"select * from team_setups where all_players @> '{{{players_str}}}' and discord_guild_id = {guild_id}"
    db_data = get_db_data_from_query(sql_query, True)

    if not db_data:
        left_players_list = list(ite.combinations(range(len(players_id_list)), len(players_id_list)//2))
        left_team_players_str = ', '.join(tuple(map(lambda x: f'{{{x[1:-1]}}}', map(str, left_players_list))))
        sql_query = "insert into team_setups values ("
        sql_query += f"""{guild_id}, '{{{players_str}}}', '{{{left_team_players_str}}}')"""
        get_db_data_from_query(sql_query)

    return


def roll_team_setup(guild_id, players_id_list):
    "Ролл игроков"

    # Собираем тим сетапы
    players_str = ", ".join(map(str, players_id_list))
    sql_query = f"select * from team_setups where all_players @> '{{{players_str}}}' and discord_guild_id = {guild_id}"
    db_data = get_db_data_from_query(sql_query, True)

    # Роллим тим сетап и распределяем по командам
    seed = random.randint(1, len(db_data[0][2]))
    choosed_players = list(db_data[0][2][seed-1])
    db_data[0][2].pop(seed-1)
    choosed_players.sort(reverse=True)

    # Наполняем команды
    left_team_list = []
    right_team_list = players_id_list
    for i in choosed_players:
        left_team_list.append(right_team_list[i])
        right_team_list.pop(i)

    # Удаляем использованный сетап из бд
    remaining_setups = str(db_data[0][2]).replace('[', '{').replace(']', '}')
    sql_query = f"""
        update team_setups
        set remaining_setups = '{remaining_setups}'
        where 
            discord_guild_id = {guild_id}
            and all_players @> '{{{players_str}}}'"""
    get_db_data_from_query(sql_query)


    # Готовим сообщение о командах и отправляем его
    left_team_str = "\n".join(f'<@{player}>' for player in left_team_list)
    right_team_str = "\n".join(f'<@{player}>' for player in right_team_list)


    embed = discord.Embed(title='Team Setup',
                          color=discord.Color.blurple()
                          )
    embed.add_field(name="Left Team", value=left_team_str, inline="true")
    embed.add_field(name="Right Team", value=right_team_str, inline="true")

    return embed, left_team_list, right_team_list


def get_custom_channels(guild_id):
    conn = psycopg2.connect(dbname='customs', user='postgres', password='1184', host='localhost')
    with conn.cursor() as cur:
        cur.execute(f"select discord_channel_id from discord_channels_for_customs_id where discord_guild_id = {guild_id}")
        data = cur.fetchall()

        result = []
        for row in data:
            result.append(row[0])

    return result


def check_correct_setup(guild_id, players_id_list: list):
    "Проверка корректности запуска кастома"

    ## Проверка четности количества игроков
    if len(players_id_list) % 2 == 1:
        return False, "Нечетное количество участников"

    ## Проверка наличия игроков в базе
    # Делаем из игроков строку для sql-запроса
    players_str = ", ".join(map(str, players_id_list))

    sql_query = f"""select count(1) from added_players where discord_member_id in ({players_str}) and discord_guild_id = {guild_id}"""

    if get_db_data_from_query(sql_query, True)[0][0] != len(players_id_list):
        return False, "Некоторые участники не зарегистрированы. Воспользуйтесь регистрацией и убедитесь, что все ваши имена призывателя есть в списке игроков"

    return True, "Всё ок"

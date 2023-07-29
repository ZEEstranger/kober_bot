from add_func import get_json_secrets


creds = get_json_secrets('secret.txt')

discord_bot_token = creds['discord_token']
# riot_api_token = creds['riot_api_token']
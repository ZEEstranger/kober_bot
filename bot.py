import discord
import responses
from discord.ext import commands
from search_player import get_all_players, add_new_player, roll_team_setup, check_db_team_setup, get_custom_channels, check_correct_setup
from settings import discord_bot_token
import psycopg2



def run_discord_bot():

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True

    bot = commands.Bot(command_prefix='$', intents=intents)

    bot.reg_msg = None
    bot.current_custom_players = []

    @bot.event
    async def on_ready():
        print(f'{bot} is now running!')
        

    @bot.event
    async def on_reaction_add(reaction, user):
        if reaction.message.id == bot.reg_msg and reaction.emoji == '👍':
            bot.current_custom_players.append(user.id)


    @bot.event
    async def on_reaction_remove(reaction, user):
        if reaction.message.id == bot.reg_msg and reaction.emoji == '👍':
            bot.current_custom_players.remove(user.id)

    
    @bot.command()
    async def players_show(ctx):
        players = get_all_players(ctx.guild.id)

        names_str = "\n".join(player[1] for player in players)
        mentions_str = "\n".join(f'<@{player[0]}>' for player in players)

        embed = discord.Embed(title='Players List',
                              color=discord.Color.blurple()
                              )
        embed.add_field(name="", value=names_str, inline="true")
        embed.add_field(name="", value=mentions_str, inline="true")

        await ctx.send(embed=embed)


    @bot.command()
    async def player_add(ctx, *args):
        
        name = " ".join(args)
        user = ctx.message.author.id

        try:
            add_new_player(ctx.guild.id, user, name)
            await ctx.send(f'Player "{name}" added by <@{str(user)}>')
        except psycopg2.errors.UniqueViolation as error:
            await ctx.send(f'Sorry. Something went wrong')

        
    @bot.command()
    async def button(ctx):
        view = discord.ui.View()
        but = discord.ui.Button("Click me")
        view.add_item(but)
        await ctx.send(view=view)

    @bot.command()
    async def custom_create(ctx):
        bot.current_custom_players.clear()
        msg = await ctx.send("registration message")
        await msg.add_reaction('👍')
        bot.reg_msg = msg.id
        

    @bot.command()
    async def custom_start(ctx):
        "Команда для старта кастома"

        print(bot.current_custom_players)
        ###################
        bot.current_custom_players = [342325519066333204, 277396353389297664, 331401636792762388, 983266083219841044]
        ###################
        bot.current_custom_players.sort()

        # Проверка корректности сетапа из текущих игроков
        custom_correct_flag, expt = check_correct_setup(ctx.guild.id, bot.current_custom_players)
        if not custom_correct_flag:
            print (expt)
            return

        # Проверка существования сетапа в БД и добавление сетапа
        check_db_team_setup(ctx.guild.id, bot.current_custom_players)


        # Роллим команду с текущим сетапом
        team_setup, bot.left_team_players_list, bot.right_team_players_list = roll_team_setup(ctx.guild.id, bot.current_custom_players)
        await ctx.send(embed=team_setup)

        chan = get_custom_channels(ctx.guild.id)

        # Раскидываю игроков по каналам
        for player in bot.left_team_players_list:
            user = ctx.message.guild.get_member(player)
            channel = ctx.message.guild.get_channel(chan[0])
            try:
                await user.move_to(channel)
            except AttributeError as error:
                print(error)
        
        for player in bot.right_team_players_list:
            user = ctx.message.guild.get_member(player)
            channel = ctx.message.guild.get_channel(chan[1])
            try:
                await user.move_to(channel)
            except AttributeError as error:
                print(error)
  
    # Remember to run your bot with your personal TOKEN
    bot.run(discord_bot_token)

if __name__ == '__main__':
    run_discord_bot()
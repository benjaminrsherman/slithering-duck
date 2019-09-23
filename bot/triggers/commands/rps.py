from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger

import discord

reaccs = [
    {"emoji": "\U0001f311", "name": ":new_moon:"},
    {"emoji": "\U0001f4f0", "name": ":newspaper:"},
    {"emoji": "\u2702", "name": ":scissors:"}
]

GLOBAL_GAMES = dict()

class RPSGame:
    def __init__(self, orig_msg, players):
        # initialize answers
        self.msg = orig_msg
        self.players = players
        self.answer_dict = dict()
        for player in players:
            self.answer_dict[player] = ""

    def check_winner(self):
        answers = [self.answer_dict[player] for player in self.players]
        # somebody didn't answer yet >:(
        if answers[0] == "" or answers[1] == "":
            return False

        for i in range(len(answers)):
            if answers[i] == reaccs[0]["emoji"]:
                # rock
                answers[i] = 0
            elif answers[i] == reaccs[1]["emoji"]:
                # paper
                answers[i] = 1
            elif answers[i] == reaccs[2]["emoji"]:
                # scissors
                answers[i] = 2

        result = answers[0] - answers[1]
        # result == 0 iff they are the same
        if result == 0:
            return 0
        elif result == 1 or result == -2:
            return 1
        elif result == -1 or result == 2:
            return 2

        print ("RPS: We shouldn't get here!")
        return False

class RockPaperScissors(Command, ReactionTrigger):
    names = ["rockpaperscissors", "rps"]
    description = "Begins a game of Rock Paper Scissors with a player."
    needsContent = True

    def get_content(self):
        return "You have been challenged to RPS!"

    def get_embed(self, players):
        embed = discord.Embed(
            title="Rock Paper Scissors",
            description="Please react your move!"
        )

        embed.add_field(
            name="Players",
            value=" vs. ".join(
                [
                    player.mention
                    for player in players
                ]
            ),
        )

        embed.set_footer(text="Duck Games not reviewed by @Eli")
        return embed

    # this is called when a message starting with "!commandname" is run
    async def execute_command(self, client, msg, content):
        pieces = [":new_moon:", ":newspaper:", ":scissors:"]

        players = list(set([*msg.mentions, msg.author]))
        if len(players) != 2:
            await utils.delay_send(
                msg.channel,
                "RPS is for TF2 memers only. Valve can't count above 2, so neither can we.",
            )
            return

        # make sure the tagged player is not a bot
        for player in players:
            if player is msg.author:
                continue
            if player.bot:
                await utils.delay_send(
                    msg.channel,
                    "The bot is too busy doing the Kazotsky Kick to play RPS!",
                )
                return

        # collect the players to hash for game management
        player_set = frozenset([player.mention for player in players])

        # verify that the key is in the game dictionary
        if player_set not in GLOBAL_GAMES.keys():
            GLOBAL_GAMES[player_set] = []

        # ensure there is no pre-existing RPS game
        games = GLOBAL_GAMES[player_set]
        for game in games:
            if isinstance(game, RPSGame):
                print("Error: There are multiple RPS Games active between", player_set)
                return

        # initialize the game in the game manager
        games.append(
            RPSGame(msg, [player.id for player in players])
        )

        # send players RPS messages
        for player in players:
            msg = await player.send(content=self.get_content(), embed=self.get_embed(players))
            for spot in reaccs:
                await msg.add_reaction(spot["emoji"])

    async def execute_reaction(self, client, reaction):
        if client.user.id == reaction.user_id:
            return

        channel = await client.fetch_channel(reaction.channel_id)
        msg = await channel.fetch_message(reaction.message_id)

        if len(msg.embeds) == 0 or msg.embeds[0].title != "Rock Paper Scissors":
            return

        options = [spot["emoji"] for spot in reaccs]

        if reaction.emoji.name not in options:
            return

        # grab the players
        players = []
        for field in msg.embeds[0].fields:
            if field.name == "Players":
                players = field.value.split(" vs. ")
                break

        # find the game in the global game dict
        games = GLOBAL_GAMES[frozenset(players)]
        this_game = None

        for game in games:
            if isinstance(game, RPSGame):
                this_game = game
                break
        if this_game is None:
            print("Couldn't find RPS game between", players[0], "and", players[1])
            return

        # store the answer (in Unicode form)
        if (game.answer_dict[reaction.user_id] != ""):
            return
        game.answer_dict[reaction.user_id] = reaction.emoji.name

        # check if there is a winner
        result = game.check_winner()
        if result != False:
            content = "Test"
            player1, player2 = players
            answer1, answer2 = [ans for ans in game.answer_dict.values()]

            embed = discord.Embed(
                title="Rock Paper Scissors",
                description=f"{player1}: {answer1}\n{player2}: {answer2}\n\n"
            )

            embed.set_footer(text="Duck Games not reviewed by @Phi11ipus")

            if result == 0:
                embed.description += f"Draw!"
            elif result == 1:
                embed.description += f"{player1} wins!"
            elif result == 2:
                embed.description += f"{player2} wins!"


            await game.msg.channel.send(content=None, embed=embed)
            # remove the message
            await msg.delete(delay=0.5)
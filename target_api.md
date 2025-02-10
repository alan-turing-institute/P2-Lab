# Target API

This is a document that describes an attempt at a target API for working with
teams, setting up showdown bots that run using a specified configuration, and
running genetic algorithms to optimize teams.

Thank you to github copilot for helping me write this document lmao

```python3
team = generate_team(format="gen8randombattle", seed=1234)

# a team object contains a list of 6 pokemon objects with their moves, items, etc.
# it's also tracking the (normalised) number of wins/losses/ties for this team.
# (would be nice to hard-code an auto-tie at 100 moves or something, but that's not a priority)

# here's an example env file for running a showdown bot:
# BATTLE_BOT=safest
# WEBSOCKET_URI=sim.psim.us:8000
# PS_USERNAME=whimsicaldreams
# PS_PASSWORD=password
# BOT_MODE=CHALLENGE_USER
# POKEMON_MODE=gen3ou
# RUN_COUNT=1
# USER_TO_CHALLENGE=...
# SAVE_REPLAY=False
# TEAM_NAME=gen3/my_teams


# here's an idealised Bot class that uses these same env variables to run a showdown bot, but more cleanly:
bot_1 = Bot(
    team,
    strategy="safest",
    websocket_uri="sim.psim.us:8000",
    user="whimsicaldreams",
    password="password",
    bot_mode="CHALLENGE_USER",
    format="gen3ou",
    num_battles=1,
    save_replay=False,
)

# this will require hacking the bot code to remove dependence from environment variables, but it's doable
# note the absence of the user to challenge -- this is so we can be flexible about which bots are fighting at any given time (needs coding)
# the bot class will also need to be able to run a battle and return the results

# now we can run a battle between two bots:
bot_2 = Bot(
    team,
    strategy="safest",
    websocket_uri="sim.psim.us:8000",
    user="melonchomper",
    password="password",
    bot_mode="CHALLENGE_USER",  # this would need to be ACCEPT_CHALLENGE
    format="gen3ou",
    num_battles=1,
    save_replay=False,
)

# from a little google searching, it looks like we can run these bots in parallel using asyncio:


async def run_battle(bot_1, bot_2):
    # individually run the showdown bots at the same time, and wait for the results
    await asyncio.gather(bot_1.challenge(bot_2), bot_2.accept(bot_1))
    # parse the results
    # update the win/loss/tie counts for each team
    ...


run_battle(bot_1, bot_2)

# within this function, we'll need to:
# - run the bot_1 and bot_2 showdown bots
# - parse the results of the battle
# - update the win/loss/tie counts for each team

# here's a more generic example, where we specify a number of battles for each team, and then run them all:
bots = {
    f"bot{i}": Bot(
        team,
        strategy="safest",
        websocket_uri="sim.psim.us:8000",
        user=f"bot{i}",
        password="password",
        bot_mode="CHALLENGE_USER" if i % 2 == 0 else "ACCEPT_CHALLENGE",
        format="gen3ou",
        num_battles=10,
        save_replay=False,
    )
    for i in range(10)
}

# num_battles = 10 would mean that bot would challenge the same bot 10 times, so we can make every bot fight every other bot 10 times

# now we can run all of these battles in parallel using a while loop that ensures every bot has fought every other bot:

# iterate over every combination of bots, ignoring equivalent combinations (e.g. bot_1 vs bot_2 is the same as bot_2 vs bot_1)
for bot_1, bot_2 in itertools.combinations(bots.values(), 2):
    if bot_1 != bot_2:
        try:
            # make sure bot_1 is the challenger and bot_2 is the acceptor
            bot_1.bot_mode = "CHALLENGE_USER"
            bot_2.bot_mode = "ACCEPT_CHALLENGE"

            # check if either bot is currently in a battle
            if bot_1.in_battle or bot_2.in_battle:
                print(
                    f"Bot {bot_1} or {bot_2} is currently in a battle, waiting for them to finish..."
                )
                while bot_1.in_battle or bot_2.in_battle:
                    await asyncio.sleep(
                        1
                    )  # hopefully this will wait for the battle to finish

            # run the battle
            bot_1.in_battle = True
            bot_2.in_battle = True

            run_battle(bot_1, bot_2)  # this will do 10 battles between bot_1 and bot_2

            bot_1.in_battle = False
            bot_2.in_battle = False

        except Exception as e:
            print(e)
            print(f"Error running battle between {bot_1} and {bot_2}")

# ensure we're only here once every bot has fought every other bot
while any(bot.in_battle for bot in bots.values()):
    await asyncio.sleep(1)

# now we can (hopefully) print out the results of each bot:
for bot in bots:
    print(bot.user, bot.team.wins, bot.team.losses, bot.team.ties)
```

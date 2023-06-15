from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from subprocess import check_output

import numpy as np
from poke_env import PlayerConfiguration
from poke_env.player import RandomPlayer
from poke_env.teambuilder import Teambuilder
from tqdm import tqdm

from p2lab.genetic.fitness import win_percentages
from p2lab.genetic.matching import dense
from p2lab.genetic.operations import build_crossover_fn, locus_swap, mutate
from p2lab.team import Team


class Builder(Teambuilder):
    def yield_team(self):
        pass


def generate_pool(
    num_pokemon, format="gen7anythinggoes", export=False, filename="pool.txt"
):
    teams = []
    print("Generating pokemon in batches of 6 to form pool...")
    # teams are produced in batches of 6, so we need to generate
    # a multiple of 6 teams that's greater than the number of pokemon
    N_seed_teams = num_pokemon // 6 + 1
    for _ in tqdm(range(N_seed_teams), desc="Generating teams!"):
        poss_team = check_output(f"pokemon-showdown generate-team {format}", shell=True)
        try:
            check_output(
                f"pokemon-showdown validate-team {format} ",
                shell=True,
                input=poss_team,
            )
        except Exception as e:
            print("Error validating team... skipping to next")
            print(f"Error: {e}")
            continue
        n_team = Builder().parse_showdown_team(
            check_output(
                "pokemon-showdown export-team ", input=poss_team, shell=True
            ).decode(sys.stdout.encoding)
        )
        if len(n_team) != 6:
            msg = "pokemon showdown generated a team not of length 6"
            raise Exception(msg)
        teams.append(n_team)

    pool = np.array(teams).flatten()

    # trim the pool to the desired number of pokemon
    pool = pool[:num_pokemon]

    if export:
        with Path.open(filename, "w") as f:
            packed = "\n".join([mon.formatted for mon in pool])
            # convert using pokemon-showdown export-team
            human_readable = check_output(
                "pokemon-showdown export-team ",
                input=packed,
                shell=True,
                universal_newlines=True,
            )
            f.write(human_readable)

    return pool


def import_pool(filename):
    with Path.open(filename, "r") as f:
        human_readable = f.read()
    teams = []
    # loop over every 6 lines and parse the team
    for _i in range(0, len(human_readable.splitlines()), 6):
        team = Builder().parse_showdown_team(human_readable)
        teams.append(team)

    return np.array(teams).flatten()


def generate_teams(pool, num_teams, team_size=6):
    return [
        Team(np.random.choice(pool, size=team_size, replace=False))
        for _ in range(num_teams)
    ]


async def run_battles(
    matches,
    teams,
    player_1,
    player_2,
    battles_per_match=1,
    progress_bar=True,
):
    results = []
    for t1, t2 in tqdm(matches, desc="Battling!") if progress_bar else matches:
        player_1.update_team(teams[t1].to_packed_str())
        player_2.update_team(teams[t2].to_packed_str())
        await player_1.battle_against(player_2, n_battles=battles_per_match)
        results.append((player_1.n_won_battles, player_2.n_won_battles))
        player_1.reset_battles()
        player_2.reset_battles()
    return np.array(results)


async def main(
    pool_size=100,
    num_generations=3,
    num_teams=3,
    team_size=3,
    battles_per_match=2,
    battle_format="gen7anythinggoes",
):
    pool = generate_pool(pool_size, export=True)
    # new_pool = import_pool(filename="pool.txt")
    print(f"pool: {pool}")
    print(f"pool shape: {pool.shape}")
    # print(f"new pool: {new_pool}")
    # print(f"new pool shape: {new_pool.shape}")
    teams = generate_teams(pool, num_teams=num_teams, team_size=team_size)
    matches = dense(teams)
    print(f"matches: {matches}")
    print(f"matches shape: {matches.shape}")
    player_1 = RandomPlayer(
        PlayerConfiguration("Player 1", None), battle_format=battle_format
    )
    player_2 = RandomPlayer(
        PlayerConfiguration("Player 2", None), battle_format=battle_format
    )
    results = await run_battles(
        matches, teams, player_1, player_2, battles_per_match=battles_per_match
    )
    print(f"results: {results}")
    fitness = win_percentages(teams, matches, results)
    print(f"fitness: {fitness}")

    crossover_fn = build_crossover_fn(locus_swap)
    for _ in range(num_generations):
        # Crossover based on fitness func
        new_teams = crossover_fn(
            teams=teams,
            fitness=fitness,
            num_teams=num_teams,
            num_pokemon=team_size,
            crossover_prob=0.5,
            allow_all=False,
        )

        # Mutate the new teams
        teams = mutate(
            teams=new_teams,
            num_pokemon=team_size,
            mutate_prob=0.1,
            pokemon_population=pool,
            allow_all=False,
            k=1,
        )

        # Generate matches from list of teams
        matches = dense(teams)

        # Run simulations
        results = await run_battles(
            matches, teams, player_1, player_2, battles_per_match=battles_per_match
        )

        # Compute fitness
        fitness = win_percentages(teams, matches, results)

    # return the best team
    return teams[np.argmax(fitness)].to_packed_str()


# test the pool generation
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

"""
TODO: Write some docs here.
"""
from __future__ import annotations

import asyncio

from tqdm import tqdm

from .evaluator.poke_env import PokeEnv
from .teams.builder import Builder

N_generations = 10  # Number of generations to run
N_teams = 10  # Number of teams to generate per generation
N_battles = 10  # Number of battles to run per team


async def main_loop():
    builder = Builder(N_seed_teams=N_teams)
    builder.build_N_teams_from_poke_pool(N_teams)
    teams = builder.get_teams()

    curr_gen = 0  # Current generation
    evaluator = PokeEnv(n_battles=N_battles)

    # Main expected loop
    print("Starting main loop and running on Generation: ")
    for _ in tqdm(range(N_generations)):
        await evaluator.evaluate_teams(teams)
        builder.generate_new_teams()
        teams = builder.get_teams()
        curr_gen += 1


def main():
    asyncio.get_event_loop().run_until_complete(main_loop())


if __name__ == "__main__":
    main()

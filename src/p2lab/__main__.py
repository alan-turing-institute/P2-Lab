from __future__ import annotations

import argparse
import asyncio

import numpy as np

from p2lab.genetic.genetic import genetic_algorithm
from p2lab.pokemon.premade import gen_1_pokemon
from p2lab.pokemon.teams import generate_teams, import_pool


async def main_loop(num_teams, team_size, num_generations, unique):
    # generate the pool
    pool = import_pool(gen_1_pokemon())
    seed_teams = generate_teams(pool, num_teams, team_size, unique=unique)
    # crossover_fn = build_crossover_fn(locus_swap, locus=0)
    # run the genetic algorithm
    teams, fitnesses = await genetic_algorithm(
        pokemon_pool=pool,
        seed_teams=seed_teams,
        num_teams=num_teams,
        team_size=team_size,
        num_generations=num_generations,
        progress_bars=True,
        mutate_with_fitness=True,
        mutate_k=1,
    )

    print("Best team:")
    best_team = teams[np.argmax(fitnesses)]
    fitness = fitnesses[np.argmax(fitnesses)]
    for mon in best_team.pokemon:
        print(mon.formatted)

    print(f"Fitness: {fitness}")

    print("Worst team:")

    worst_team = teams[np.argmin(fitnesses)]
    fitness = fitnesses[np.argmin(fitnesses)]
    for mon in worst_team.pokemon:
        print(mon.formatted)

    print(f"Fitness: {fitness}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", help="Number of generations", type=int, default=10)
    parser.add_argument("-t", help="Team size", type=int, default=2)
    parser.add_argument("-n", help="Number of teams", type=int, default=30)
    parser.add_argument("-s", help="Random seed", type=int, default=None)
    parser.add_argument("-u", help="Unique teams", default=True)
    return vars(parser.parse_args())


def main():
    args = parse_args()

    if args["s"] is not None:
        np.random.seed(args["s"])

    asyncio.get_event_loop().run_until_complete(
        main_loop(args["n"], args["t"], args["g"], args["u"])
    )


if __name__ == "__main__":
    main()

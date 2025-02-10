from __future__ import annotations

import random

import numpy as np

from p2lab.pokemon.team import Team

# Placeholders:


# Consider seeding this?
def generate_teams(
    pokemon_population: list[str],
    num_pokemon: int,
    num_teams: int,
) -> list[Team]:
    teams = []
    for _i in range(num_teams):
        pokemon = random.sample(population=pokemon_population, k=num_pokemon)
        teams.append(Team(pokemon=pokemon))
    return teams


def generate_matches(teams: list[Team]) -> np.ndarray:
    """

    First column should be team IDs for player 1
    Second column should be team IDs for player 2

    Team IDs can be generated fresh each round, but we'll need to
    track them each round

    Actually, team IDs can just index the current team list?
    """
    return np.zeros(shape=(len(teams), 2))


def crossover(
    teams: list[Team], fitness: list[float], num_teams: int, num_pokemon: int
) -> list[Team]:
    """
    Given a list of teams and a fitness score for each team, generate
    new teams.

    The fitness score determines the likelihood of selection when
    generating 2 teams from 2 old ones.


    """
    print(fitness)  # delete this line - it's here to avoid pre-commit checks
    new_teams: list[Team] = []

    # Assume num_teams is even, sample w/ replacement
    for _i in range(int(num_teams / 2)):
        teams_old = random.sample(teams, k=2)
        team1_old = teams_old[0]
        team2_old = teams_old[1]

        team1_pokemon = team1_old.pokemon
        team2_pokemon = team2_old.pokemon

        # Randomly pick locus
        locus = random.sample(range(num_pokemon), k=1)[0]

        # Check that the sliciing here works but you get the idea
        team1_new_pokemeon = team1_pokemon[0:locus] + team2_pokemon[locus:num_pokemon]
        team2_new_pokemeon = team2_pokemon[0:locus] + team1_pokemon[locus:num_pokemon]

        team1_new = Team(pokemon=team1_new_pokemeon)
        team2_new = Team(pokemon=team2_new_pokemeon)

        new_teams = [*new_teams, team1_new, team2_new]

    return new_teams


def mutate(teams: list[Team], p: float, pokemon_population: list[str]) -> list[Team]:
    for team in teams:
        team.random_mutate(
            p=p, pokemon_population=pokemon_population
        )  # will need to be parameterised with a prob
    return teams

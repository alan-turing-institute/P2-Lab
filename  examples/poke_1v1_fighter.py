# 1v1 fights for the pokemon for stats.
# Author: Edmund Dable-Heath
"""
Setting each of the 150 pokemon to fight each other pokemon until either a cutoff is
reached or the variation of the win ratio over a history of s fights falls below a
threshold.
"""

# Imports include reference to potential scripts
# import pop_gen
# import fight_sim
from __future__ import annotations

import asyncio
import pickle
from itertools import combinations_with_replacement as cwr
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from poke_env import PlayerConfiguration
from poke_env.player import SimpleHeuristicsPlayer

from p2lab.pokemon.battles import run_battles
from p2lab.pokemon.premade import gen_1_pokemon
from p2lab.pokemon.teams import generate_teams, import_pool

if TYPE_CHECKING:
    from p2lab.pokemon.teams import Team

# Actual code ==========================================================================


def gen_pop() -> list[Team]:
    """Generate the population of 151 pokemon objects ready to fight.

    NB: This can be done more explicity here, i.e. implement the rejection sampling
        in this script, but I will simplify away from that for now.
    """
    pool = import_pool(team_string=gen_1_pokemon())
    return generate_teams(pool, num_teams=151, team_size=1, unique=True)


async def duel(poke_1, poke_2, player_1, player_2) -> bool:
    """Simulate a fight between a pair of pokemon, with a result of True if poke_1
        wins.

    Args:
        poke_1 (poke_object): pokemon_1     (IN THE RED CORNER)
        poke_2 (poke_object): pokemon_2     (IN THE BLUE CORNER)

    Returns:
        bool: True if pokemon 1 is victorious.
    """
    return await run_battles([[0, 1]], [poke_1, poke_2], player_1, player_2, 1)


async def duel_to_convergence(
    poke_1,
    poke_2,
    p1,
    p2,
    cutoff: int,
) -> tuple(float, float):
    """DUEL TO THE DEATH! (or at least a converged win ratio.....)

        For two pokemon, duel until the win ration converges or cutoff is reached.
        Return ratios scaled by number of fights.

        TODO: make lookback function of number of fights?

    Args:
        poke_1 (poke_object): pokemon_1      (GLADIATOR, READY!)
        poke_2 (poke_object): pokemon_2      (GLADIATOR, READY!)
        var_threshold (float): threshold for convergence of win ratio variance.
        look_back: how man previous ratio values to consider.
        cutoff: max iters to run this.

    Returns:
        (poke_wins_1, poke_wins_2) tuple(float, float):
            poke_wins_i = (no wins of poke_i) / (no of duels) f
    """
    count = 0
    poke_win_1 = 0
    poke_win_2 = 0
    while count < cutoff:
        count += 1
        res = await duel(poke_1, poke_2, p1, p2)
        if bool(res[0][0]):
            poke_win_1 += 1
        else:
            poke_win_2 += 1
    return poke_win_1 / count, poke_win_2 / count


async def main(**kwargs):
    # Generate a population
    pokemons = gen_pop()
    poke_num = len(pokemons)

    # Read the poke_dict for results
    with Path.open("poke_base_stats.pkl", "rb") as f:
        poke_dict = pickle.load(f)

    conversion_dict = {
        "mr-mime": "mr. mime",
        "farfetchd": "farfetch'd",
        "nidoran-m": "nidoran♂",
        "nidoran-f": "nidoran♀",
    }
    # flip the dict
    conversion_dict = {v: k for k, v in conversion_dict.items()}
    poke_names = []
    for poke in pokemons:
        if poke.first_name.lower() in conversion_dict:
            print("sgewrojoiwjhgnwil")
            poke_names.append(conversion_dict[poke.first_name.lower()])
        else:
            poke_names.append(poke.first_name.lower())

    # print(poke_names)
    # print(poke_dict.keys())
    assert set(poke_names) == set(poke_dict.keys())

    # Instantiate results matrix (we know n = 151)
    res_arr = np.zeros((poke_num, poke_num))

    # Instantiate players
    player_1 = SimpleHeuristicsPlayer(
        PlayerConfiguration("Player 1", None), battle_format="gen7anythinggoes"
    )
    player_2 = SimpleHeuristicsPlayer(
        PlayerConfiguration("Player 2", None), battle_format="gen7anythinggoes"
    )
    # Duel to convergence to get stats
    for dueling_partners_id in cwr(list(range(len(pokemons))), 2):
        i, j = dueling_partners_id
        # print(f"IN THE RED CORNER: {poke_names[i]}")
        # print(f"IN THE BLUE CORNER: {poke_names[j]}")
        poke_ratio_1, poke_ratio_2 = await duel_to_convergence(
            pokemons[i],
            pokemons[j],
            player_1,
            player_2,
            kwargs["cutoff"],
        )
        if i == j:
            res_arr[i, i] += poke_ratio_1
        res_arr[i, j] += poke_ratio_1
        res_arr[j, i] += poke_ratio_2

    # Average over to get stats
    avg_win_ratio = np.mean(res_arr, axis=0)
    for i in range(len(poke_names)):
        poke_dict[poke_names[i]]["average_win_ratio"] = avg_win_ratio[i]

    # Write poke dict to storage
    with Path.open("poke_fight_results.pkl", "wb") as fp:
        pickle.dump(poke_dict, fp)
    return poke_dict


if __name__ == "__main__":
    # Pars hardcoded in for now as should be single run.
    pars = {"cutoff": 10}

    asyncio.get_event_loop().run_until_complete(main(**pars))

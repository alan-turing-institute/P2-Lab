"""
This class is used to generate Pokemon teams using the pokedex provided from
Pokemon Showdown (via poke-env)

This is directly inspired by poke-env's diagostic_tools folder
"""

from __future__ import annotations

import numpy as np
from poke_env.data import GenData as POKEDEX
from poke_env.teambuilder import TeambuilderPokemon


class PokeFactory:
    def __init__(self, gen=1, drop_forms=True):
        self.gen = (
            gen if gen > 4 else 3
        )  # because this seems to be the minimum gen for the pokedex
        self.dex = POKEDEX(self.gen)
        if drop_forms:
            self.dex2mon = {
                int(self.dex.pokedex[m]["num"]): m
                for m in self.dex.pokedex
                if "forme" not in self.dex.pokedex[m].keys()
            }
        else:
            self.dex2mon = {
                int(self.dex.pokedex[m]["num"]): m for m in self.dex.pokedex
            }

    def get_pokemon_by_dexnum(self, dexnum):
        return self.dex.pokedex[self.dex2mon[dexnum]]

    def get_allowed_moves(self, dexnum, level=100):
        pot_moves = self.dex.learnset[self.dex2mon[dexnum]]["learnset"]
        allowed_moves = []
        for move, lims in pot_moves.items():
            gens = [int(lim[0]) for lim in lims]
            # TODO: write logic here to check if level is allowed
            if level != 100:
                msg = "Level checking not implemented yet"
                raise NotImplementedError(msg)
            # lvls = [int(l[1:]) for l in lims if l[1:].isdigit()]
            if self.gen in gens:
                allowed_moves.append(move)
        return allowed_moves

    def get_allowed_abilities(self, dexnum):
        return self.dex.pokedex[self.dex2mon[dexnum]]["abilities"]

    def make_pokemon(self, dexnum=None, generate_moveset=False, **kwargs):
        """
        kwargs are passed to the TeambuilderPokemon constructor and can include:
        - nickname
        - item
        - ability
        - moves
        - nature
        - evs
        - ivs
        - level
        - happiness
        - hiddenpowertype
        - gmax
        """
        if dexnum < 1:
            msg = "Dex number must be greater than 0"
            raise ValueError(msg)
        if dexnum is None:
            dexnum = np.random.choice(list(self.dex2mon.keys()))
        if generate_moveset or "moves" not in kwargs:
            poss_moves = self.get_allowed_moves(dexnum)
            moves = (
                np.random.choice(poss_moves, 4, replace=False)
                if len(poss_moves) > 3
                else poss_moves
            )
            kwargs["moves"] = moves
        if "ivs" not in kwargs:
            ivs = [31] * 6
            kwargs["ivs"] = ivs
        if "evs" not in kwargs:
            # TODO: implement EV generation better
            evs = [510 // 6] * 6
            kwargs["evs"] = evs
        if "level" not in kwargs:
            kwargs["level"] = 100
        if "ability" not in kwargs:
            kwargs["ability"] = np.random.choice(
                list(self.get_allowed_abilities(dexnum).values())
            )

        return TeambuilderPokemon(species=self.dex2mon[dexnum], **kwargs)

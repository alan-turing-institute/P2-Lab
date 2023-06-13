"""
The team builder
"""

from subprocess import check_output
from poke_env.teambuilder import Teambuilder
import numpy as np
import sys

class Builder(Teambuilder):
    """
    The team builder
    """
    def __init__(self, teams=None, format="gen2randombattle"):
        if teams:
            self.teams = [self.join_team(self.parse_showdown_team(team)) for team in teams]
        else:
            self.teams = [self.join_team(self.parse_showdown_team(check_output(f"pokemon-showdown generate-team {format}| pokemon-showdown export-team", shell=True).decode(sys.stdout.encoding)) )]

    def yield_team(self):
        return np.random.choice(self.teams)

    def make_team(self):
        pass

    def make_N_teams(self, N):
        return [self.make_team() for _ in range(N)]
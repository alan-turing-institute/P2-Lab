from __future__ import annotations

import pytest

from p2lab.pokemon import pokefactory, premade, teams


@pytest.fixture
def default_factory():
    return pokefactory.PokeFactory()


@pytest.fixture
def gen_1_pool():
    return teams.import_pool(premade.gen_1_pokemon())

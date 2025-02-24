"""
Copyright (c) 2023 Scientists of the P2 Laboratory. All rights reserved.

p2lab: a package for genetic optimisation of pokemon teams
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

__all__ = ["Literal", "Protocol", "runtime_checkable"]


def __dir__() -> list[str]:
    return __all__

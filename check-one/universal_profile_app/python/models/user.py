"""User data (model layer)."""

from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
    weight: float
    height: float  # centimeters

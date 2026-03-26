"""CLI input helpers (utils layer)."""

from models.user import User


def read_user() -> User:
    name = input("Enter name: ").strip()
    age = int(input("Enter age: ").strip())
    weight = float(input("Enter weight (kg): ").strip())
    height = float(input("Enter height (cm): ").strip())
    return User(name=name, age=age, weight=weight, height=height)

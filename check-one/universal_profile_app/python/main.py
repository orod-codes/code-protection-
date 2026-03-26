#!/usr/bin/env python3
"""Entry — imports model, service, utils (run from python/ so package paths resolve)."""
from models.user import User
from services.bmi_service import calculate
from utils.io_util import read_user


def main() -> None:
    user: User = read_user()
    bmi = calculate(user.weight, user.height)
    print(f"Hello {user.name}, age {user.age}, BMI: {bmi}")


if __name__ == "__main__":
    main()

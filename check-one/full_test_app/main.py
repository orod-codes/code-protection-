#!/usr/bin/env python3
from services.collector import ProfileCollector
from services.reporter import print_profile


def main() -> None:
    try:
        profile = ProfileCollector.collect()
        print_profile(profile)
    except ValueError as err:
        print(f"Input error: {err}")


if __name__ == "__main__":
    main()

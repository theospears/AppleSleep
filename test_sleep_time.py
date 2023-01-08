from typing import List
import yaml

from model import TestCase
from sleep_time import get_total_sleep_minutes


def load_test_cases() -> List[TestCase]:
    with open("testcases.yaml") as f:
        test_cases = yaml.safe_load(f)
    return [TestCase.from_yaml(case) for case in test_cases]


def main():
    test_cases = load_test_cases()
    for case in test_cases:
        print(f"{case.description}: ", end="")
        expected = case.minutes
        actual = get_total_sleep_minutes(case.spans)
        if expected != actual:
            print(f"❌")
            print(f" - Expected {expected} but got {actual} for {case.spans}")
        else:
            print("👍")


if __name__ == "__main__":
    main()

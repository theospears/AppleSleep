from dataclasses import dataclass
import datetime
from enum import Enum


class SleepAnalysis(str, Enum):
    awake = "awake"
    asleepDeep = "asleepDeep"
    asleepCore = "asleepCore"
    asleepREM = "asleepREM"
    asleepUnspecified = "asleep"


def time_from_seconds(seconds):
    return datetime.time(
        hour=seconds // 60 // 60, minute=(seconds // 60) % 60, second=seconds % 60
    )


@dataclass
class Span:
    start: datetime.time
    end: datetime.time
    type: SleepAnalysis

    @staticmethod
    def from_yaml(yaml_dict):
        return Span(
            start=time_from_seconds(yaml_dict["start"]),
            end=time_from_seconds(yaml_dict["end"]),
            type=yaml_dict["type"],
        )


@dataclass
class TestCase:
    description: str
    minutes: int
    spans: [Span]

    @staticmethod
    def from_yaml(yaml_dict):
        return TestCase(
            description=yaml_dict.get("description"),
            minutes=yaml_dict["minutes"],
            spans=[Span.from_yaml(d) for d in yaml_dict["spans"]],
        )

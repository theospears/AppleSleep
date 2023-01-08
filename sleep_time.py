from dataclasses import dataclass
import datetime
from enum import Enum
import itertools
from typing import List

from model import SleepAnalysis, Span


@dataclass
class SpanStart:
    time: datetime.time
    span: Span


@dataclass
class SpanEnd:
    time: datetime.time
    span: Span


def is_asleep(span: Span) -> bool:
    return span.type != SleepAnalysis.awake


def noninclusive_minutes_between(start: datetime.time, end: datetime.time) -> int:
    return end.hour * 60 + end.minute - (start.hour * 60 + start.minute) - 1


def interval_in_seconds(start: datetime.time, end: datetime.time) -> int:
    def total_seconds(t):
        return t.hour * 60 * 60 + t.minute * 60 + t.second

    return total_seconds(end) - total_seconds(start)


def minute(time: datetime.time) -> datetime.time:
    """Truncate a time to the minute it is part of"""
    return datetime.time(hour=time.hour, minute=time.minute)


def add_minute(time: datetime.time) -> datetime.time:
    if time.minute == 59:
        return time.replace(hour=time.hour + 1, minute=0)
    else:
        return time.replace(minute=time.minute + 1)


class SleepResolution(Enum):
    Asleep = 1
    Awake = 2
    Ambiguous = 3


def sleep_resolution_for_minute(spans: List[Span], active_minute: datetime.time) -> SleepResolution:
    """
    Given a set of sleep analysis spans, and a particular minute, calculate whether that minute
    should be considered asleep. This assumes all supplied spans at least partially overlap with the
    supplied minute.

    Note that a minute can have an equal amount of data suggesting it should be awake or asleep. In
    this case the function will return "Ambiguous" and the caller must figure out how to treat it.
    """
    total_awake_seconds = 0
    total_asleep_seconds = 0

    for span in spans:
        start = span.start if minute(span.start) == active_minute else active_minute
        end = (
            span.end if minute(span.end) == active_minute else add_minute(active_minute)
        )
        duration = interval_in_seconds(start, end)
        if is_asleep(span):
            total_asleep_seconds += duration
        else:
            total_awake_seconds += duration
    if total_awake_seconds < total_asleep_seconds:
        return SleepResolution.Asleep
    elif total_awake_seconds == total_asleep_seconds:
        return SleepResolution.Ambiguous
    else:
        return SleepResolution.Awake


def would_first_minute_be_asleep(spans: List[Span]) -> bool:
    """
    Given a set of spans, would we consider the first minute any of cover to be awake, only
    considering the spans supplied.

    Used to tie break whether to consider later periods asleep or awake.
    """
    minutes = [minute(span.start) for span in spans]
    first_minute = min(minutes)
    spans_starting_in_first_minute = [
        span for span in spans if minute(span.start) == first_minute
    ]
    result = sleep_resolution_for_minute(spans_starting_in_first_minute, first_minute)

    # When evaluating first minute, for tie breaks we assume asleep
    if result == SleepResolution.Asleep or result == SleepResolution.Ambiguous:
        return True
    else:
        return False


def get_total_sleep_minutes(spans: List[Span]) -> int:
    """
    Given a set of sleep analysis spans, return the total number of minutes asleep in the same
    way the apple health app would do so.

    Answering this question is complex because:
      - The UI indicates particular minutes as either "awake" or "asleep", while the input spans have
        second level precision
      - There can be overlapping data from multiple input sources. For example from both an Apple Watch
        and an Oura ring.
    """
    # Process events in time order. We process each span twice, once for when it starts,
    # and then again when it ends
    points = []
    for span in spans:
        points.extend(
            [SpanStart(time=span.start, span=span), SpanEnd(time=span.end, span=span)]
        )
    points.sort(key=lambda p: p.time)

    total_sleep_minutes = 0

    last_minute = None
    active_spans = []

    # Consider each minute in which any span starts or ends
    minutes = itertools.groupby(points, key=lambda p: minute(p.time))
    for active_minute, minute_points in minutes:
        ending_spans = []

        # Add all sleep for the period starting after the last minute we considered,
        # up to but not including the current minute. This could be a period of length
        # zero. We know no spans started or stopped in this interval.
        if active_spans:
            sleeping_span_count = len(
                [span for span in active_spans if is_asleep(span)]
            )
            awake_span_count = len(
                [span for span in active_spans if not is_asleep(span)]
            )
            if (awake_span_count < sleeping_span_count) or (
                awake_span_count == sleeping_span_count
                and would_first_minute_be_asleep(active_spans)
            ):
                total_sleep_minutes += noninclusive_minutes_between(
                    last_minute, active_minute
                )

        # Update our span tracking to reflect spans that started or stopped this minute
        for point in minute_points:
            if isinstance(point, SpanStart):
                active_spans.append(point.span)
            elif isinstance(point, SpanEnd):
                active_spans.remove(point.span)
                # Spans which end exactly on the minute aren't considered to last into the minute
                # they end on (half-open). However if they end part way through the minute, consider them
                if point.time != minute(point.time):
                    ending_spans.append(point.span)

        # Determine whether the current minute is asleep, and if so add it to the total
        if active_spans or ending_spans:
            sleep_resolution = sleep_resolution_for_minute(
                active_spans + ending_spans, active_minute
            )
            if (sleep_resolution == SleepResolution.Asleep) or (
                sleep_resolution == SleepResolution.Ambiguous
                and would_first_minute_be_asleep(active_spans + ending_spans)
            ):
                total_sleep_minutes += 1

        last_minute = active_minute

    assert len(active_spans) == 0, f"Ended with active spans: {active_spans}"
    return total_sleep_minutes

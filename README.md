# Apple Sleep Analysis

A reverse-engineering of the algorithm used by iPhone to determine how many minutes
of sleep the user received.

This is a black-box re-implementation. I manually assembled test cases and used the
iPhone simulator to record the number of minutes of sleep reported by Apple Health
for combinations of sleep data. I then developed an algorithm to match this data. It
may or may not be the same as the algorithm used by Apple Health.

This repository includes:
* A python algorithm implementation
* The test cases used to develop it, which can be run against the algorithm

## Summary of Apple Behavior

At a high level, the behavior of Apple Health appears to be:

```
Consider each minute of the night
  Look at all data points which overlap with this minute
  Compare the total number of seconds of sleep during the minute to the total number of seconds of awake
  If there are more total seconds of sleep:
    Treat the minute as asleep
  If there are more total seconds of awake:
    Treat the minute as awake
  If there is a tie:
    Look at the spans and consider the minute in which the first one started
    Considering only the spans for our current minute, calculate total seconds of sleep/awake for that first minute
    If there are more total seconds of sleep:
      Treat this minute as asleep
    If there are more total seconds of awake:
      Treat this minute as awake
    If there is a tie:
      Treat this minute as awake

Return the total number of minutes which are considered asleep.
```

## Testing

```sh
python test_sleep_time.py
```
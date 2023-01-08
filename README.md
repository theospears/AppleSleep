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

## Testing

```sh
python test_sleep_time.py
```
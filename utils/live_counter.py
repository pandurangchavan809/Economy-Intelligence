### world page

from datetime import datetime, timezone

SECONDS_IN_YEAR = 365 * 24 * 60 * 60

def live_nominal_value(base_value, real_growth, inflation, base_year):
    effective_growth = ((real_growth or 0) + (inflation or 0)) / 100

    start = datetime(base_year, 1, 1, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    elapsed = max((now - start).total_seconds(), 0)

    return base_value * (1 + effective_growth * elapsed / SECONDS_IN_YEAR)


def live_population_value(base_population, growth_rate, base_year):
    growth = (growth_rate or 0) / 100

    start = datetime(base_year, 1, 1, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    elapsed = max((now - start).total_seconds(), 0)

    return base_population * (1 + growth * elapsed / SECONDS_IN_YEAR)


## continent

_continent_gdp_state = {}
_continent_population_state = {}


def live_continent_nominal_value(
    continent_code,
    base_value,        # BILLIONS
    real_growth,
    inflation,
    base_year,
):
    effective_growth = ((real_growth or 0) + (inflation or 0)) / 100

    start = datetime(base_year + 1, 1, 1, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    elapsed = max((now - start).total_seconds(), 0)

    value = base_value * (1 + effective_growth * elapsed / SECONDS_IN_YEAR)

    last = _continent_gdp_state.get(continent_code)

    if last is None or value > last:
        _continent_gdp_state[continent_code] = value
    else:
        value = last

    return value / 1000   # convert BILLIONS → TRILLIONS


def live_continent_population_value(
    continent_code,
    base_population,
    growth_rate,
    base_year,
):
    growth = (growth_rate or 0) / 100

    start = datetime(base_year + 1, 1, 1, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    elapsed = max((now - start).total_seconds(), 0)

    value = base_population * (1 + growth * elapsed / SECONDS_IN_YEAR)

    last = _continent_population_state.get(continent_code)

    if last is None or value > last:
        _continent_population_state[continent_code] = value
    else:
        value = last

    return int(value)


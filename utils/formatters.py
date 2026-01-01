def format_trillions(value):
    return f"${value / 1e12:,.2f} T"


def format_trillions_live(value):
    return f"{value / 1e12:.8f} T"


def format_billions(value):
    return f"${value / 1e9:,.2f} B"


def format_number(value):
    return f"{value:,.0f}"


def format_percent(value):
    return f"{value:.2f}%"

def format_currency(value):
    return f"${value:,.2f}"


# GDP & TRADE FORMATTERS

def format_trillions_from_billions(value, decimals=2):
    """
    GDP stored in BILLIONS → display in TRILLIONS
    Example: 40443 → $40.44 T
    """
    if value is None:
        return "—"
    return f"${value / 1000:.{decimals}f} T"


def format_trillions_raw(value, decimals=2):
    """
    Trade values already stored in TRILLIONS → no conversion
    Example: 12.4 → $12.40 T
    """
    if value is None:
        return "—"
    return f"${value:.{decimals}f} T"


def format_trillion_live(value, decimals=8):
    """
    LIVE GDP counter in TRILLIONS with dollar-level precision
    Example: 44.29343789 T
    """
    if value is None:
        return "—"
    return f"${value:,.{decimals}f} T"


# POPULATION & GENERIC NUMBERS

def format_population(value):
    """
    Population with commas
    Example: 4705742000 → 4,705,742,000
    """
    if value is None:
        return "—"
    return f"{int(value):,}"


def format_number(value):
    """
    Generic integer formatter
    """
    if value is None:
        return "—"
    return f"{int(value):,}"


# PERCENTAGES

def format_percent(value, decimals=2):
    """
    Percentage formatter
    Example: 3.64766 → 3.65%
    """
    if value is None:
        return "—"
    return f"{value:.{decimals}f}%"



## country

def format_currency(x):
    try:
        return f"${x:,.2f}"
    except:
        return "N/A"

def format_currency_short_usd(val, decimals=2):
    """
    Generic money formatting for USD in billions or other. Use carefully.
    """
    try:
        return f"${float(val):,.{decimals}f}"
    except Exception:
        return "—"

def format_trillions_detailed(value_usd, decimals=8):
    if value_usd is None:
        return "Not available"
    try:
        t = float(value_usd) / 1e12
        return f"${t:,.{decimals}f} T"
    except Exception:
        return str(value_usd)


def format_live_value(value):
    if value is None:
        return "Not available"
    
    # Scaling logic
    if value >= 1e12:
        return f"${value / 1e12:,.8f} T"  # Trillions
    elif value >= 1e9:
        return f"${value / 1e9:,.6f} B"   # Billions
    elif value >= 1e6:
        return f"${value / 1e6:,.4f} M"   # Millions
    else:
        return f"${value:,.2f}"
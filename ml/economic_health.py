# Starting ML integration in Second phase of project :- for now we use a simple formaula based scores.


def compute_economic_health_score(
    gdp_growth,
    inflation,
    debt_ratio,
    unemployment
):
    score = (
        gdp_growth * 0.3
        - inflation * 0.2
        - debt_ratio * 0.3
        - unemployment * 0.2
    )
    return max(0, min(100, 50 + score))

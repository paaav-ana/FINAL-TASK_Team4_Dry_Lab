
"""
constraints.py
-------------------------
BovEco Health & Sustainability Constraint Checker

This module evaluates whether a proposed algae dose satisfies
literature-based constraints.

Future versions can replace the default values with literature-derived
thresholds or values loaded from a configuration file.
"""

from dataclasses import dataclass


@dataclass
class ConstraintParameters:

    # Dose
    max_safe_dose: float = 25.0

    # Feed
    min_digestibility: float = 0.65
    min_feed_intake: float = 95.0

    # Methanogens
    max_methanogen_reduction: float = 80.0

    # Hydrogen
    min_feed_frequency: float = 2.0
    max_feed_frequency: float = 12.0

    # Expression
    max_expression: float = 20.0

    # Scores
    min_health_score: float = 0.90
    min_sustainability_score: float = 0.80

def calculate_health_score(feed_intake,
                           digestibility,
                           methanogen_reduction):
    """
    Very simple placeholder health score.

    Future versions should replace this with
    literature-based equations.
    """

    feed_score = min(feed_intake / 100.0, 1.0)
    digestibility_score = min(digestibility, 1.0)
    methanogen_score = max(
        0.0,
        1.0 - methanogen_reduction / 100.0
    )

    score = (
        0.4 * feed_score +
        0.4 * digestibility_score +
        0.2 * methanogen_score
    )

    return round(score, 3)


def calculate_sustainability_score(dose,
                                   max_safe_dose):
    """
    Simple sustainability score.

    Lower doses are considered more sustainable.

    Future versions may include:

    - production cost
    - cultivation energy
    - transport
    - CO2 footprint
    """

    score = max(
        0.0,
        1.0 - dose / (2 * max_safe_dose)
    )

    return round(score, 3)


def evaluate_constraints(
        dose,
        methane_reduction,
        digestibility,
        feed_intake,
        feed_frequency,
        expression,
        params=None):
    """
    Evaluate all model constraints.
    """

    if params is None:
        params = ConstraintParameters()

    health = calculate_health_score(
        feed_intake,
        digestibility,
        methane_reduction
    )

    sustainability = calculate_sustainability_score(
        dose,
        params.max_safe_dose
    )

    results = {
        "Dose OK":
            dose <= params.max_safe_dose,

        "Digestibility OK":
            digestibility >= params.min_digestibility,

        "Feed Intake OK":
            feed_intake >= params.min_feed_intake,

        "Methanogen Reduction OK":
            methane_reduction <=
            params.max_methanogen_reduction,

        "Health Score":
            health,

        "Health OK":
            health >= params.min_health_score,

        "Sustainability Score":
            sustainability,

        "Sustainability OK":
            sustainability >=
            params.min_sustainability_score
        "Feed Frequency OK":
            params.min_feed_frequency
            <= feed_frequency
            <= params.max_feed_frequency,

        "Expression OK":
            expression
            <= params.max_expression,
                    
    }

    return results


def print_report(results):

    print("\n==============================")
    print("Constraint Evaluation Report")
    print("==============================")

    for key, value in results.items():

        if isinstance(value, bool):

            status = "PASS" if value else "FAIL"
            print(f"{key:<30}: {status}")

        else:

            print(f"{key:<30}: {value}")

    print("==============================\n")


def main(parameters=None):

    print("==============================")
    print("BovEco Constraint Checker")
    print("==============================")

    if parameters is None:

        dose = float(input("Dose (g/day): "))
        methane = float(input("Methane reduction (%): "))
        digestibility = float(input("Digestibility (0-1): "))
        feed = float(input("Feed intake (% baseline): "))
        feed_frequency = float(input("Feed frequency/day: "))
        expression = float(input("PeiR expression (mg/g): "))

    else:

        dose = parameters["dose"]

        methane = parameters.get(
            "methane_reduction",
            0
        )

        digestibility = parameters.get(
            "digestibility",
            0.75
        )

        feed = parameters.get(
            "feed_intake",
            100
        )

        feed_frequency = parameters["feed_frequency"]

        expression = parameters["expression"]

    results = evaluate_constraints(
        dose,
        methane,
        digestibility,
        feed,
        feed_frequency,
        expression
        )

    print_report(results)
    import pandas as pd

    df = pd.DataFrame([results])
    df.to_csv("constraint_report.csv", index=False)

    print("Constraint report saved to constraint_report.csv")


if __name__ == "__main__":
    main()

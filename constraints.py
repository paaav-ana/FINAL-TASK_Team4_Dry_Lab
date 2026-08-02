"""
constraints.py
------------------------------------
BovEco Model Validation Module

This module validates that the simulation
was run within the assumptions of the
mechanistic model.

It DOES NOT predict biology.

Instead it checks whether all inputs
are physically and mathematically valid.
"""

import pandas as pd


def validate(parameters):

    report = {}

    # --------------------------
    # Dose
    # --------------------------

    dose = parameters["dose"]

    report["Dose > 0"] = dose > 0

    # --------------------------
    # Expression
    # --------------------------

    expression = parameters["expression"]

    report["Expression > 0"] = expression > 0

    # --------------------------
    # Feed frequency
    # --------------------------

    ff = parameters["feed_frequency"]

    report["Feed frequency > 0"] = ff > 0

    report["Feed frequency within calibrated range (1–8/day)"] = (
        1 <= ff <= 8
    )

    # --------------------------
    # Initial methanogens
    # --------------------------

    M0 = parameters["M0"]

    report["Initial methanogens > 0"] = M0 > 0

    # --------------------------
    # First-order rate constants
    # --------------------------

    report["kd > 0"] = parameters["kd"] > 0
    report["kp > 0"] = parameters["kp"] > 0
    report["kl > 0"] = parameters["kl"] > 0

    # --------------------------
    # Monod parameters
    # --------------------------

    report["mu_max > 0"] = parameters["mu_max"] > 0

    report["KH > 0"] = parameters["KH"] > 0

    report["Carrying capacity > 0"] = parameters["K"] > 0

    # --------------------------
    # Efficiencies
    # --------------------------

    report["Release efficiency (0-1)"] = (
        0 <= parameters["eta"] <= 1
    )

    # --------------------------
    # Simulation outputs
    # --------------------------

    if "methane_reduction" in parameters:

        reduction = parameters["methane_reduction"]

        report["Methane reduction calculated"] = True

        report["Methane reduction physically possible"] = (
            0 <= reduction <= 100
        )

    else:

        report["Methane reduction calculated"] = False

    return report


def print_report(report):

    print("\n===================================")
    print("Model Validation Report")
    print("===================================\n")

    passed = 0

    for check, result in report.items():

        if result:

            print(f"[PASS] {check}")
            passed += 1

        else:

            print(f"[FAIL] {check}")

    print("\n-----------------------------------")
    print(f"{passed}/{len(report)} checks passed.")
    print("-----------------------------------")


def main(parameters=None):

    print("===================================")
    print("BovEco Model Validation")
    print("===================================")

    if parameters is None:

        print("\nThis module should normally be")
        print("run from main.py after a simulation.")
        return

    report = validate(parameters)

    print_report(report)

    df = pd.DataFrame(
        list(report.items()),
        columns=["Check", "Pass"]
    )

    df.to_csv(
        "model_validation_report.csv",
        index=False
    )

    print("\nGenerated:")
    print("  model_validation_report.csv")


if __name__ == "__main__":
    main()
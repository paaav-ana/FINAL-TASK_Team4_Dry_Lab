
"""sensitivity.py - BovEco parameter sensitivity analysis"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

DEFAULTS = None

from boveco_simulator import model
from boveco_simulator import hydrogen_concentration

def simulate(parameters):

    p = parameters.copy()

    y0 = [
        p["dose"],
        0.0,
        p["M0"]
    ]

    t = np.linspace(
        0,
        p["days"],
        500
    )

    solution = solve_ivp(
        lambda tt, yy: model(tt, yy, p),
        [0, p["days"]],
        y0,
        t_eval=t
    )

    M = solution.y[2]

    H = np.array([
        hydrogen_concentration(tt, p)
        for tt in t
    ])

    mu = (
        p["mu_max"]
        * H
        / (p["KH"] + H)
    )

    methane = (
        p["yield_coeff"]
        * p["rmax"]
        * mu
        * M
    )

    # Control (no PeiR)

    control = p.copy()
    control["expression"] = 0.0
    control["eta"] = 0.0

    control_solution = solve_ivp(
        lambda tt, yy: model(tt, yy, control),
        [0, p["days"]],
        y0,
        t_eval=t
    )

    control_M = control_solution.y[2]

    control_H = np.array([
        hydrogen_concentration(tt, control)
        for tt in t
    ])

    control_mu = (
        control["mu_max"]
        * control_H
        / (control["KH"] + control_H)
    )

    control_methane = (
        control["yield_coeff"]
        * control["rmax"]
        * control_mu
        * control_M
    )

    reduction = (
        (
            control_methane[-1]
            - methane[-1]
        )
        /
        control_methane[-1]
        * 100
    )

    return reduction

def main(parameters=None):

    if parameters is None:

        print("Run the simulator first.")
        return

    pct = float(
        input("Variation (%) [20]: ") or 20
    )

    base = simulate(parameters)

    rows = []

    parameters_to_test = [

        "kd",
        "eta",
        "kp",
        "kl",
        "mu_max",
        "KH",
        "feed_frequency",
        "expression",
        "yield_coeff"

    ]

    for parameter in parameters_to_test:

        original = parameters[parameter]

        if original == 0:
            continue

        for sign, label in [

            (-1, "Low"),
            (1, "High")

        ]:

            test = parameters.copy()

            test[parameter] = original * (
                1 + sign * pct / 100
            )

            reduction = simulate(test)

            rows.append([
                parameter,
                label,
                test[parameter],
                reduction,
                reduction - base
            ])

    df = pd.DataFrame(

        rows,

        columns=[
            "Parameter",
            "Case",
            "Value",
            "Reduction",
            "Delta"
        ]

    )

    summary = (
        df.groupby("Parameter")["Delta"]
        .apply(lambda x: x.abs().max())
        .sort_values(ascending=False)
    )

    df.to_csv(
        "sensitivity_analysis.csv",
        index=False
    )

    plt.figure(figsize=(8,4))

    plt.bar(
        summary.index,
        summary.values
    )

    plt.xticks(rotation=40)

    plt.ylabel(
        "Maximum change in methane reduction (%)"
    )

    plt.tight_layout()

    plt.savefig(
        "parameter_sensitivity.png"
    )

    plt.close()

    print("\nSensitivity analysis complete.")

    print(f"Baseline reduction: {base:.2f}%")

    print("\nMost influential parameters:")

    print(summary)

    print("\nFiles generated:")

    print(" sensitivity_analysis.csv")

    print(" parameter_sensitivity.png")
    
if __name__=="__main__":
    main()

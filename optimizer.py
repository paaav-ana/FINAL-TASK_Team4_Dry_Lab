"""
optimizer.py
----------------------------------------
BovEco Dose Optimizer
----------------------------------------
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.integrate import solve_ivp

from boveco_simulator import model
from boveco_simulator import hydrogen_concentration
def simulate(parameters, dose):

    p = parameters.copy()

    p["dose"] = dose

    y0 = [
        dose,
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

    control = p.copy()
    control["expression"] = 0
    control["eta"] = 0

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
        (control_methane[-1] - methane[-1])
        / control_methane[-1]
        * 100
    )

    return reduction
def main(parameters=None):

    print("===================================")
    print("      BovEco Dose Optimizer")
    print("===================================\n")

    if parameters is None:
        print("Run the simulator first or provide parameters.")
        return

    target = float(
        input("Target methane reduction (%) [30]: ") or 30
    )

    minimum = float(
        input("Minimum dose (g/day) [1]: ") or 1
    )

    maximum = float(
        input("Maximum dose (g/day) [50]: ") or 50
    )

    step = float(
        input("Dose increment (g/day) [1]: ") or 1
    )

    doses = np.arange(
        minimum,
        maximum + step,
        step
    )

    reductions = []

    best_dose = None
    best_reduction = None

    maximum_reduction = -float("inf")
    maximum_dose = None

    for dose in doses:

        reduction = simulate(parameters, dose)

        reductions.append(reduction)

        # Track the best overall result
        if reduction > maximum_reduction:
            maximum_reduction = reduction
            maximum_dose = dose

        # First dose that reaches the target
        if best_dose is None and reduction >= target:
            best_dose = dose
            best_reduction = reduction

    results = pd.DataFrame({
        "Dose (g/day)": doses,
        "Methane Reduction (%)": reductions
    })

    results.to_csv(
        "dose_optimization.csv",
        index=False
    )

    plt.figure(figsize=(7,4))

    plt.plot(
        doses,
        reductions,
        marker="o"
    )

    plt.axhline(
        target,
        linestyle="--",
        label="Target"
    )

    if best_dose is not None:

        plt.scatter(
            [best_dose],
            [best_reduction],
            s=100,
            label="Recommended Dose"
        )

        print(f"\nRecommended dose: {best_dose:.2f} g/day")
        print(f"Predicted reduction: {best_reduction:.2f}%")

    else:

        print("\nTarget reduction was not reached.")

        print(
            f"Maximum reduction achieved: "
            f"{maximum_reduction:.2f}%"
        )

        print(
            f"Best dose tested: "
            f"{maximum_dose:.2f} g/day"
        )

        print(
            "Consider increasing the maximum dose "
            "or modifying biological parameters."
        )

    plt.xlabel("Dose (g/day)")
    plt.ylabel("Methane Reduction (%)")
    plt.title("Dose Response")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig("dose_response.png")
    plt.close()

    print("\nOptimization complete.")
    print("Generated:")
    print("  dose_optimization.csv")
    print("  dose_response.png")


if __name__ == "__main__":
    main()
"""
=========================================================
BovEco Simulator V3
Mechanistic model for PeiR-mediated methane mitigation
=========================================================

Model structure

Algae --> PeiR --> Methanogens --> Methane

Hydrogen availability controls methanogen growth using
Monod kinetics.

Author: BovEco Dry Lab
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.integrate import solve_ivp


# =========================================================
# Default Parameters
# =========================================================

DEFAULTS = {

    # Experimental Inputs
    "dose": 20.0,                 # g/day
    "expression": 5.0,            # mg PeiR / g algae
    "days": 30.0,
    "feed_frequency": 8.0,        # feedings/day

    # Algae
    "kd": 0.40,

    # PeiR
    "eta": 0.85,
    "kp": 0.08,
    "kl": 0.002,

    # Methanogens
    "mu_max": 0.80,
    "KH": 1.38,
    "K": 1.0,
    "M0": 1.0,

    # Hydrogen
    "H0": 1.38,
    "H_spike": 15.0,
    "spike_duration": 30.0,

    # Methane
    "rmax": 1.0,
    "yield_coeff": 1.0
}


# =========================================================
# Hydrogen Model
# =========================================================

def hydrogen_concentration(t, p):
    """
    Approximate dissolved hydrogen concentration.

    Literature basis:
        Basal H2 ≈ 1.38 µM
        Feeding causes transient spikes of 10–20 µM
        lasting approximately 30 minutes.

    Feed frequency determines how often spikes occur.
    """

    H = p["H0"]

    interval = 24 / p["feed_frequency"]

    duration = p["spike_duration"] / 60.0

    time_since_feed = t % interval

    if time_since_feed <= duration:

        H += p["H_spike"]

    return H
# =========================================================
# Differential Equation Model
# =========================================================

def model(t, y, p):
    """
    State variables

    A = algae
    P = active PeiR
    M = methanogen population
    """

    A, P, M = y

    # -------------------------------------
    # Hydrogen concentration
    # -------------------------------------

    H = hydrogen_concentration(t, p)

    # -------------------------------------
    # Monod growth equation
    # -------------------------------------

    mu = (
        p["mu_max"]
        * H
        / (p["KH"] + H)
    )

    # -------------------------------------
    # Algae degradation
    # -------------------------------------

    dA = -p["kd"] * A

    # -------------------------------------
    # PeiR release
    # -------------------------------------

    dP = (
        p["eta"]
        * p["expression"]
        * p["kd"]
        * A
        -
        p["kp"] * P
    )

    # -------------------------------------
    # Methanogen population
    # -------------------------------------

    growth = (
        mu
        * M
        * (1 - M / p["K"])
    )

    lysis = (
        p["kl"]
        * P
        * M
    )

    dM = growth - lysis

    return [dA, dP, dM]
# =========================================================
# Main Simulation
# =========================================================

def main(parameters=None):

    print("\n===================================")
    print("      BovEco Mechanistic Model")
    print("===================================\n")

    # -----------------------------------------------------
    # Read parameters
    # -----------------------------------------------------

    if parameters is None:

        p = DEFAULTS.copy()

        print("Press Enter to use the default value.\n")

        p["dose"] = float(input(f"Algae dose (g/day) [{p['dose']}]: ") or p["dose"])

        p["expression"] = float(input(
            f"PeiR expression (mg/g algae) [{p['expression']}]: "
        ) or p["expression"])

        p["days"] = float(input(
            f"Simulation length (days) [{p['days']}]: "
        ) or p["days"])

        p["feed_frequency"] = float(input(
            f"Feed frequency (feedings/day) [{p['feed_frequency']}]: "
        ) or p["feed_frequency"])

        print("\n------ Biological Parameters ------\n")

        p["kd"] = float(input(
            f"Algae degradation rate (/day) [{p['kd']}]: "
        ) or p["kd"])

        p["eta"] = float(input(
            f"PeiR release efficiency [{p['eta']}]: "
        ) or p["eta"])

        p["kp"] = float(input(
            f"PeiR degradation rate (/day) [{p['kp']}]: "
        ) or p["kp"])

        p["kl"] = float(input(
            f"PeiR lysis coefficient [{p['kl']}]: "
        ) or p["kl"])

        p["mu_max"] = float(input(
            f"Maximum methanogen growth (/day) [{p['mu_max']}]: "
        ) or p["mu_max"])

        p["KH"] = float(input(
            f"Hydrogen half-saturation KH (µM) [{p['KH']}]: "
        ) or p["KH"])

        p["K"] = float(input(
            f"Carrying capacity [{p['K']}]: "
        ) or p["K"])

        p["M0"] = float(input(
            f"Initial methanogen abundance [{p['M0']}]: "
        ) or p["M0"])

        print("\n------ Hydrogen Parameters ------\n")

        p["H0"] = float(input(
            f"Basal hydrogen (µM) [{p['H0']}]: "
        ) or p["H0"])

        p["H_spike"] = float(input(
            f"Hydrogen spike (µM) [{p['H_spike']}]: "
        ) or p["H_spike"])

        p["spike_duration"] = float(input(
            f"Spike duration (minutes) [{p['spike_duration']}]: "
        ) or p["spike_duration"])

        print("\n------ Methane Parameters ------\n")

        p["rmax"] = float(input(
            f"Maximum methane rate [{p['rmax']}]: "
        ) or p["rmax"])

        p["yield_coeff"] = float(input(
            f"Methane yield coefficient [{p['yield_coeff']}]: "
        ) or p["yield_coeff"])

    else:

        p = parameters.copy()

    # -----------------------------------------------------
    # Initial Conditions
    # -----------------------------------------------------

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

    A = solution.y[0]
    P = solution.y[1]
    M = solution.y[2]
    # =====================================================
    # Hydrogen profile
    # =====================================================

    H = np.array([
        hydrogen_concentration(tt, p)
        for tt in t
    ])

    # =====================================================
    # Methanogen growth rate
    # =====================================================

    mu = (
        p["mu_max"]
        * H
        / (p["KH"] + H)
    )

    # =====================================================
    # Methane production
    # =====================================================

    methane = (
        p["yield_coeff"]
        * p["rmax"]
        * mu
        * M
    )

    # -----------------------------------------------------
    # Control simulation (no PeiR)
    # -----------------------------------------------------

    control_parameters = p.copy()

    control_parameters["expression"] = 0.0
    control_parameters["eta"] = 0.0

    control = solve_ivp(
        lambda tt, yy: model(tt, yy, control_parameters),
        [0, p["days"]],
        y0,
        t_eval=t
    )

    control_M = control.y[2]

    control_H = np.array([
        hydrogen_concentration(tt, control_parameters)
        for tt in t
    ])

    control_mu = (
        control_parameters["mu_max"]
        * control_H
        / (
            control_parameters["KH"]
            + control_H
        )
    )

    control_methane = (
        control_parameters["yield_coeff"]
        * control_parameters["rmax"]
        * control_mu
        * control_M
    )

    # =====================================================
    # Methane reduction
    # =====================================================

    reduction = (
        (
            control_methane[-1]
            - methane[-1]
        )
        /
        control_methane[-1]
        * 100
    )

    # =====================================================
    # Save Results
    # =====================================================

    results = pd.DataFrame({

        "Day": t,

        "Algae": A,

        "PeiR": P,

        "Methanogens": M,

        "Hydrogen": H,

        "Methane": methane,

        "Control_Methane": control_methane

    })

    results.to_csv(
        "simulation_results.csv",
        index=False
    )

    # =====================================================
    # Plots
    # =====================================================

    figures = [

        (A, "Algae", "algae.png"),

        (P, "Active PeiR", "active_peir.png"),

        (M, "Methanogens", "methanogens.png"),

        (methane, "Methane", "methane.png"),

        (H, "Hydrogen", "hydrogen.png")

    ]

    for data, title, filename in figures:

        plt.figure(figsize=(7,4))

        plt.plot(
            t,
            data,
            linewidth=2
        )

        plt.xlabel("Time (days)")
        plt.ylabel(title)
        plt.title(title)

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(filename)

        plt.close()

    # =====================================================
    # Final Summary
    # =====================================================

    print("\n===================================")
    print("Simulation Complete")
    print("===================================")

    print(f"Final algae:        {A[-1]:.4f}")
    print(f"Final PeiR:         {P[-1]:.4f}")
    print(f"Final methanogens:  {M[-1]:.4f}")
    print(f"Final methane:      {methane[-1]:.4f}")
    print(f"Methane reduction:  {reduction:.2f}%")

    print("\nFiles generated:")

    print("  simulation_results.csv")

    print("  algae.png")
    print("  active_peir.png")
    print("  methanogens.png")
    print("  methane.png")
    print("  hydrogen.png")

    return {
    "methane_reduction": reduction,
    "final_methanogens": M[-1],
    "final_peir": P[-1],
    "hydrogen": H,
}


if __name__ == "__main__":
    main()
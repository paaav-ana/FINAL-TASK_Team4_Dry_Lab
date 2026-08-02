"""
main.py
=========================================
BovEco Dry Lab Suite v1.0
=========================================
"""

import os

from boveco_simulator import main as run_simulator
from optimizer import main as run_optimizer
from constraints import main as run_constraints
from sensitivity import main as run_sensitivity

# ----------------------------------
# Shared parameters
# ----------------------------------

shared_parameters = {}

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue...")

def setup():

    print("\nEnter Simulation Parameters")
    print("(Press Enter to use the default shown)\n")

    shared_parameters["dose"] = float(
        input("Initial algae dose (g/day) [20]: ") or 20
    )

    shared_parameters["expression"] = float(
        input("PeiR expression (mg/g algae) [5]: ") or 5
    )

    shared_parameters["days"] = float(
        input("Simulation length (days) [30]: ") or 30
    )

    shared_parameters["feed_frequency"] = float(
        input("Feed frequency (feedings/day) [8]: ") or 8
    )

    shared_parameters["M0"] = float(
        input("Initial methanogen abundance [1]: ") or 1
    )

    print("\n--- Biological Parameters ---")

    shared_parameters["kd"] = float(
        input("Algae degradation rate (/day) [0.4]: ") or 0.4
    )

    shared_parameters["eta"] = float(
        input("PeiR release efficiency [0.85]: ") or 0.85
    )

    shared_parameters["kp"] = float(
        input("PeiR degradation rate (/day) [0.08]: ") or 0.08
    )

    shared_parameters["kl"] = float(
        input("PeiR lysis coefficient [0.002]: ") or 0.002
    )

    shared_parameters["mu_max"] = float(
        input("Maximum methanogen growth rate (/day) [0.8]: ") or 0.8
    )

    shared_parameters["KH"] = float(
        input("Hydrogen half-saturation KH (uM) [1.38]: ") or 1.38
    )

    shared_parameters["K"] = float(
        input("Methanogen carrying capacity [1]: ") or 1
    )

    print("\n--- Hydrogen Parameters ---")

    shared_parameters["H0"] = float(
        input("Basal hydrogen (uM) [1.38]: ") or 1.38
    )

    shared_parameters["H_spike"] = float(
        input("Hydrogen spike (uM) [15]: ") or 15
    )

    shared_parameters["spike_duration"] = float(
        input("Spike duration (minutes) [30]: ") or 30
    )

    print("\n--- Methane Parameters ---")

    shared_parameters["rmax"] = float(
        input("Maximum methane rate [1]: ") or 1
    )

    shared_parameters["yield_coeff"] = float(
        input("Methane yield coefficient [1]: ") or 1
    )

def menu():

    while True:

        clear()

        print("=" * 50)
        print("         BovEco Dry Lab Suite")
        print("=" * 50)

        print("\n1. Run Mechanistic Simulation")
        print("2. Optimize Algae Dose")
        print("3. Validate Model")
        print("4. Sensitivity Analysis")
        print("5. Exit")

        choice = input("\nSelect an option: ")

        clear()

        if choice == "1":

            results = run_simulator(shared_parameters)

            if results is not None:
                shared_parameters.update(results)
            pause()

        elif choice == "2":

            run_optimizer(shared_parameters)
            pause()

        elif choice == "3":

            run_constraints(shared_parameters)
            pause()

        elif choice == "4":

            run_sensitivity(shared_parameters)
            pause()

        elif choice == "5":

            print("\nThank you for using BovEco.\n")
            break

        else:

            print("Invalid option.")
            pause()


if __name__ == "__main__":
    setup()
    menu()

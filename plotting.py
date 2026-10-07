import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import pandas as pd
import numpy as np

def subplots():
    _, axs = plt.subplots(2, 2)
    axs[0,0].tick_params(
        top=True, labeltop=True,
        bottom=False, labelbottom=False
        )
    axs[0,0].xaxis.set_label_position("top")
    
    axs[0,1].tick_params(
        top=True, labeltop=True,
        bottom=False, labelbottom=False,
        right=True, labelright=True,
        left=False, labelleft=False,
        )
    axs[0,1].xaxis.set_label_position("top")
    axs[0,1].yaxis.set_label_position("right")

    axs[1,1].tick_params(
        right=True, labelright=True,
        left=False, labelleft=False,
        )
    axs[1,1].yaxis.set_label_position("right")
    return axs

def plot_results(results:pd.DataFrame):
    axs = subplots()

    # Temperature
    Tfig:Axes = axs[0,0]
    Tfig.plot(results["time"],results["temperature"])
    Tfig.set_xlabel("Time [s]")
    Tfig.set_ylabel("Chamber Temperature [K]")

    # Pressure
    Pfig:Axes = axs[0,1]

    Pfig.plot(results["time"], results["pressure"]/1e6)

    Pfig.set_xlabel("Time [s]")
    Pfig.set_ylabel("Chamber Pressure [MPa]")

    # Mass flow
    dmfig:Axes = axs[1,0]

    dmfig.plot(results["time"], results["fuel_mdot"]+results["oxidizer_mdot"], label="In")

    dmfig.plot(results["time"], results["exhaust_mdot"], label="Out")

    dmfig.set_xlabel("Time [s]")
    dmfig.set_ylabel("Mass Flow Rate [kg/s]")

    dmfig.legend()

    mfig:Axes = axs[1,1]
    m_CV = np.cumsum(results["fuel_mdot"]+results["oxidizer_mdot"]) - np.cumsum(results["exhaust_mdot"])
    mfig.plot(results["time"],m_CV)

    mfig.set_xlabel("Time [s]")
    mfig.set_ylabel("Mass [kg]")

    plt.show()

if __name__ == "__main__":
    df = pd.read_csv("Telemetry.csv")
    plot_results(df)
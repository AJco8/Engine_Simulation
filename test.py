from Simulation import *

import matplotlib.pyplot as plt

def plotting(results):
    plt.figure()

    # Temperature
    plt.subplot(2,2,1)
    plt.plot(results["time"],results["temperature"])
    plt.xlabel("Time [s]")
    plt.ylabel("Chamber Temperature [K]")

    # Pressure
    plt.subplot(2,2,2)

    plt.plot(results["time"], results["pressure"]/1e6)

    plt.xlabel("Time [s]")
    plt.ylabel("Chamber Pressure [MPa]")

    # Mass flow
    plt.subplot(2,2,3)

    plt.plot(results["time"], results["fuel_mdot"]+results["oxidizer_mdot"], label="In")

    plt.plot(results["time"], results["exhaust_mdot"], label="Out")

    plt.xlabel("Time [s]")
    plt.ylabel("Mass Flow Rate [kg/s]")

    plt.legend()

    plt.subplot(2,2,4)
    m_CV = np.cumsum(results["fuel_mdot"]+results["oxidizer_mdot"]) - np.cumsum(results["exhaust_mdot"])
    plt.plot(results["time"],m_CV)

    plt.xlabel("Time [s]")
    plt.ylabel("Mass [kg]")

    plt.show()

def main():

    # Simulation parameters

    chamber_volume = 1.0        # m^3
    throat_area = 1e-3
    MR = 5

    fuel_mdot = 0.002              # kg/s
    oxidizer_mdot = 0.0342         # kg/s
    mdot = fuel_mdot+oxidizer_mdot

    valve_coefficient = 5.0e-7     # kg / (s Pa)

    simulation_time = 1.0          # s
    output_timestep = 1.0e-4       # s

    fuel = "CH4:1"
    oxidizer = "O2:1, N2:3.76"

    # Create system
    fuel_gas = ct.Solution("gri30.yaml")
    fuel_gas.TPX = 300, 10e3, fuel
    oxi_gas = ct.Solution("gri30.yaml")
    oxi_gas.TPX = 300, 10e3, oxidizer

    sim = Sim(mdot,MR,chamber_volume,throat_area,fuel_gas,oxi_gas)
    results = sim.run(progress=True,DataFrame=True)
    #results.to_csv("Telemetry.csv")

    # Final results
    return results

if __name__ == "__main__":
    from pandas import DataFrame
    df = main()
    df.to_csv("Simulation.csv")
    print(df.tail(1))
    plotting(df)
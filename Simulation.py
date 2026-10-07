"""Combustion Chamber Simulation"""
from math import sqrt
import cantera as ct
import numpy as np
import pandas as pd

#%% Chemistry Calculations

def Flow(P:float,T:float,gamma:float,throat_A:float,mass:float)->float:
    R = ct.gas_constant/mass
    return throat_A*P/sqrt(T)*sqrt(gamma/R)*((gamma+1)/2)**-((gamma+1)/(gamma-1)*1/2)

def Ideal_Pressure(V,m,M,T):
    R = ct.gas_constant/m
    n = m/M

    return n*R*T/V

def gas_cd(gas:ct.Solution):
    """
    Characteristic velocity for a calorically perfect gas
    c* = sqrt(R*T/gamma)*((gamma+1)/2)^((gamma+1)/(2*(gamma-1)))

    This is an approximation because gamma and composition vary with temperature.
    Use NASA CEA for higher-fidelity equilibrium/frozen c*.
    """
    
    gamma = gas.cp_mass / gas.cv_mass
    R = ct.gas_constant / gas.mean_molecular_weight

    return sqrt(R * gas.T / gamma)*((gamma + 1.0) / 2.0)**(gamma + 1)/(2*(gamma - 1))

#%% Simulation    
#TODO add heat transfer coefficient of material
class Sim:
    def __init__(self, dm, MR, volume, throat_area, fuel, oxidizer, atm=None, T_0=1, clone=False, mech="gri30.yaml"):

        # Build Objects
        fuel_tank = ct.Reservoir(fuel, name="fuel_tank", clone=clone)
        oxidizer_tank = ct.Reservoir(oxidizer, name="oxidizer_tank", clone=clone)

        dm_fuel = dm/(1 + MR)
        dm_ox = dm - dm_fuel

        #Partial Pressures
        P_ox = Ideal_Pressure(volume,dm_ox*T_0,oxidizer.mean_molecular_weight,oxidizer.T)
        P_fuel = Ideal_Pressure(volume,dm_fuel*T_0,fuel.mean_molecular_weight,fuel.T)
        P_0 = P_ox + P_fuel

        # Create a hot combustion chamber.
        # The chamber is initialized with equilibrium combustion products so that incoming reactants enter already ignited environment
        mix = ct.Solution(mech)
        mix.TPX = 300, P_0, fuel.X + oxidizer.X
        mix.equilibrate("HP") # Adiabatic combustion calculation

        chamber = ct.IdealGasReactor(mix, energy="on", name="combustion_chamber",clone=True)
        
        chamber.volume = volume
        
        #create_exhaust_reservoir()
        if atm == None:
            atm = ct.Solution("gri30.yaml")
            atm.TPX = 1e-3,1e-6,"H2:1"
        exhaust = ct.Reservoir(atm, name="exhaust", clone=True)
    
        # connect_inlets
        fuel_controller = ct.MassFlowController(fuel_tank, chamber, mdot=dm_fuel, name="fuel_inlet")
        oxidizer_controller = ct.MassFlowController(oxidizer_tank, chamber, mdot=dm_ox, name="oxidizer_inlet")
        exhaust_controller = ct.MassFlowController(chamber, exhaust, mdot=0, name="Throat")

        # Save to Object
        self.time = 0
        self.throat_area = throat_area
        self.results = {
            "time": [],
            "temperature": [],
            "pressure": [],
            "chamber_mass": [],
            "fuel_mdot": [],
            "oxidizer_mdot": [],
            "exhaust_mdot": [],
        }

        self.fuel_tank = fuel_tank
        self.oxidizer_tank = oxidizer_tank
        self.chamber = chamber
        self.exhaust = exhaust

        self.fuel_valve = fuel_controller
        self.oxidizer_valve = oxidizer_controller
        self.throat = exhaust_controller

        self.net = ct.ReactorNet([chamber])        
        
    def add_tank(self, gas, clone=False):
        tank = ct.Reservoir(gas, name="Tank", clone=clone)
    
    def step(self, timestep:float=1e-3):
        #for tank in tanks:
        #    valve = tank.valve
        self.time += timestep
        self.net.advance(self.time)

        #gamma
        y = self.chamber.phase.cp_mass / self.chamber.phase.cv_mass

        dm_out = Flow(
            P=self.chamber.phase.P,
            T=self.chamber.T,
            gamma = y,
            throat_A = self.throat_area,
            mass = self.chamber.phase.mean_molecular_weight)
        
        self.throat.mass_flow_rate = dm_out

        self.results["time"].append(self.time)
        self.results["temperature"].append(self.chamber.T)
        self.results["pressure"].append(self.chamber.phase.P)
        self.results["chamber_mass"].append(self.chamber.mass)
        self.results["fuel_mdot"].append(self.fuel_valve.mass_flow_rate)
        self.results["oxidizer_mdot"].append(self.oxidizer_valve.mass_flow_rate)
        self.results["exhaust_mdot"].append(dm_out)  

    def run(self, duration:float=10, timestep:float=1e-3, DataFrame=False, progress=False)->pd.DataFrame|dict:
        times = np.arange(0,duration,timestep)
        if progress:
            from tqdm import tqdm
            times = tqdm(times)

        for t in times:
            self.step(timestep)
        
        if DataFrame: 
            return pd.DataFrame(self.results)
        else: return self.results

    def diagram(self):
        try:
            diagram = self.net.draw(print_state=True, species="X")
        except ImportError as err:
            print(f"Unable to show network structure:\n{err}")
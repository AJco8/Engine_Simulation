# Combustion Chamber Simulation

## Usage 

### Requirements
- cantera

### Inputs

* volume (float): Internal volume of combustion chamber.
* A_throat (float): Area of the throat.
* MR (float): Mix Ratio, mass of oxidizer per mass of fuel.
* fuel (string): Chemical symbol of fuel, defaults to "H2:1"
* oxidizer (string): Chemical symbol of oxidizer, defaults to "O2:1"
* duration (float): Duration of time being simulated, defaults to 10.
* timestep (float): Length of time between simulation steps, defaults to 1e-4 (1*10^-4).

### Outputs
Simulation outputs a dictionary object with string keys indicating a corresponding array
* Time
* Fuel Mass Flow Rate
* Oxidizer Mass Flow Rate
* Exhaust Mass Flow Rate
* Temperature
* Pressure

This format can easily be converted into a Pandas DataFrame object simply by inputting the dictionary into the DataFrame object constructor (`py pandas.DataFrame(output:dict)`).

## Example 


## Verification
Currently having difficulty finding publicly available rocket engine test telemetry data. Will add comparisons when I find test cases to.


## Future Improvements
* 
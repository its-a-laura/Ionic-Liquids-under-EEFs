# -*- coding: utf-8 -*-
"""

This code produces a potenital energy scan (PES) plot from a Gaussian16 calculation.
If you have split your PES into multiple calculations, list all your data  files 
to get a figure for your entire surface.

The potenital energy surface will be plotted directly from the .log files. Energies
are relative to the energy minima in kJ/mol. To cutomise the plot, the user parameters can
be editted.

To run the script:
    python PES_plotter.py starting_coordinate input_file_name_1 input_file_name_2 
        
and list as many file names as you need (please omit extensions!)


"""

# import required modules and libraries
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

### USER DEFINED PARAMETERS ###
x_label = "Dihedral Angle (Degrees)"
plot_title = "Potenital Energy Scan over Rotation of Imidazolium Ethyl Group"
plot_colour = "black"
centre_on_zero = True # if true, will plot angle scans from -180 to 180 degrees
save_fig = False
fig_filename = "test_save.png"



def center_angles(angle):
    # Adjust scan angles to be between -180 and 180 degrees
    centered = ((angle + 180) % 360) - 180
    return centered

# process the input from the user
dir = os.getcwd()

if len(sys.argv) < 3:
    # checks to see that the user has supplied enough arguments when calling the script
    print("To run the script please type: python PES_plotter.py starting_coordinate input_file_name_1 input_file_name_2", 
         " \( and so on for as many .log files as you have)")
    sys.exit()
    
data_files = []
for i in range(len(sys.argv)-2):
    data_files.append(str(sys.argv[i+2])+'.log')


# setting up 
PES_data = pd.DataFrame(columns=['Coordinates','Energy'])
starting_coord = float(sys.argv[1])
supported_scans = {'B':'bond_length', 'A':'bond_angle', 'D':'dihedral_angle'}
angle_scans = ["A", "D"]
input_nextline = False


# defining search strings
input_str = "The following ModRedundant input section has been read:"
step_no_str = "Step number"
energy_str = "SCF Done:"


for data_file in data_files:
    print("Gathering data from", data_file)
    file = open(data_file,'r')
    line = file.readline()
    energys = np.array([])
    iterations = np.array([], dtype=int)
    step_numbers = np.array([], dtype=int)
    
    # Steps through each line in the file, checking if any search strings appear
    while line:
        if input_nextline:
            # Gathers baseline information about the PES
             temp = line.rstrip().split()
             scan_type = temp[0]
             no_steps = int(float(temp[-2]))
             no_structures = no_steps + 1
             step_size = float(temp[-1])
             input_nextline = False
             
        
             if scan_type not in supported_scans:
                 print("WARNING: This scan type may not be supported, please double check results.",
                       " Supported scan types are:", *supported_scans, sep="\n")
        
        if input_str in line:
             input_nextline = True
             
        if step_no_str in line:
            # Identifies which scan and optimisation step we are up to
            temp = line.rstrip().split()
            iterations = np.append(iterations,int(float(temp[2])))
            step_numbers = np.append(step_numbers,int(float(temp[-4])))
            
        if energy_str in line:
            # Records the energy of current step
            temp = line.rstrip().split()
            energys = np.append(energys,float(temp[4]))
        
        # Moves to the next line
        line = file.readline()
    
    print(no_structures, "structures identified, recording optimised structure energies")
    
    # Selects the final structure for each scan step and records its energy and x-coordinate
    for i in range(no_structures):
        coord = starting_coord - i * step_size
        mask = step_numbers != i + 1
        step_iterations = iterations.copy()
        step_iterations[mask] = 0
        energy_index = list(step_iterations).index(np.max(step_iterations))
        eng = energys[energy_index]
        df = pd.DataFrame([[coord, eng]], columns=['Coordinates','Energy'])
        PES_data = pd.concat([PES_data, df], ignore_index=True)
    print("Structure energies identified")
        
        
# If True, adjusts the scan angles to be centered about 0    
if centre_on_zero and scan_type in angle_scans: 
    print("Adjusting angles to range between -180 degrees and 180 degrees")
    PES_data["Coordinates"] = PES_data["Coordinates"].apply(center_angles)
    

# Sorts the data by scanning variable
sorted_PES_data = PES_data.sort_values(by="Coordinates")

# Converts Energy from a.u. to kJ/mol and zeroes the energy to the minimum
print("Converting energy from a.u. to ΔkJ/mol")
energies_kj = sorted_PES_data["Energy"] * 2625
zeroed_energies_kj = energies_kj - np.min(energies_kj)
print("Energy of lowest energy structure: "+np,min(energies_kj)+" kJ/mol")


# Plots the potential energy surface
print("Plotting PES...")
ax = plt.axes()    
ax.plot(sorted_PES_data["Coordinates"], zeroed_energies_kj, c=plot_colour, marker="o", linewidth=0.75)
ax.set_xlabel(x_label)
ax.set_ylabel("Energy (kJ/mol)")
ax.set_title(plot_title)

# Saves the PES as an image if user has specified, otherwise plots the figure.
if save_fig:
    plt.savefig(fig_filename)
    print("Plotted PES saved as", fig_filename)
else: plt.show()


sys.exit()


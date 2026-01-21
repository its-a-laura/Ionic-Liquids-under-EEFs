# -*- coding: utf-8 -*-
"""
This code calculates the difference in charges from .pdb files produced from charges_pdb.py,
and writes the charge differences to a new .pdb file. 

To run this script:
    python charge_differences.py main_file file_to_subtract output_file
    
Please note no file extensions
"""

import numpy as np
import pandas as pd
import sys
import os
import subprocess

def subtract_charges(main_file, minus_file, output_file):
    with open(main_file) as f1, open(minus_file) as f2, open(output_file, "w") as output:
        for main_line, minus_line in zip(f1, f2):

            # Edit atom lines
            if main_line.startswith("ATOM"):
                main_row = main_line.split()
                minus_row = minus_line.split()

                # Calculate charge difference
                value1 = float(main_row[-1])
                value2 = float(minus_row[-1])
                diff = value1 - value2

                # Replace original charge with charge difference
                main_row[-1] = f"{diff:6.2f}"

                # Rebuild atom line
                new_line = '{0:4}  {1:>5d}  {2:>3s}             {3:7.3f} {4:7.3f} {5:7.3f} {6:6.2f} \n'.\
                format("ATOM",int(main_row[1]),main_row[2],float(main_row[3]),float(main_row[4]),float(main_row[5]),float(main_row[6]))
                
                # Write new atom line to new output file
                output.write(new_line)
            else:
                # Copy all other lines to new output file
                output.write(main_line)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python charge_differences.py file_1 file_2 output_file")
        sys.exit(1)

filenames = [sys.argv[1], sys.argv[2], sys.argv[3]]

for i in range(len(filenames)):
    if not filenames[i].lower().endswith(".pdb"):
        filenames[i] += ".pdb"
        
subtract_charges(filenames[0], filenames[1], filenames[2])


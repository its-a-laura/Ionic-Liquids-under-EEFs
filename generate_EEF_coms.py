# -*- coding: utf-8 -*-
"""

This code generates a collection of Gaussian input .com files with fields of varying strengths
and directions based on a provided .com file. 

The user can specify the fields that use the keyword format Field=M±N where M describes 
a multipole (e.g x, y, z, xx, xy, xyz, etc) and N describes the magnitude of the field where 
N*0.0001 is the field strength in atomic units (au). 

To use, first create a .com file for the molecule you want to apply fields to. 
To run this script:
    python generate_EEF_coms.py template_com_file
    
Please note no file extensions

"""

import os
import sys
import re

# User-editable parameters
FIELD_DIRECTIONS = ["x","y","z"]
FIELD_STRENGTHS = [5,20,50,100,200,250]
FIELD_SIGNS = [1, -1]


def update_chk_line(lines, suffix):
    """
    Modify %chk= line to have the updated file name.

    Parameters
    ----------
    lines : list
        list of every string in the file
    suffix : string
        string containing the suffix to be appended to the template file name

    Returns
    -------
    new_lines : list
        list of every string in the file with the updated .chk file name.

    """
    
    new_lines = []
    chk_updated = False
    
    # Goes through line by line looking for a %chk line, and updates with
    # the new file name if found.
    for line in lines:
        if line.strip().lower().startswith("%chk="):
            chk_base = line.strip().split("=")[1]
            base_name, ext = os.path.splitext(chk_base)
            new_chk = f"%chk={base_name}_{suffix}.chk\n"
            new_lines.append(new_chk)
            chk_updated = True
        else:
            new_lines.append(line)

    # If no %chk line found, add one at top
    if not chk_updated:
        new_lines.insert(0, f"%chk=job_{suffix}.chk\n")

    return new_lines


def update_field_line(lines, field_spec):
    """
    Adds the Field= keyword to the .com file if not present, or replaces it
    with the updated field if present. 

    Parameters
    ----------
    lines : list
        list of every string in the file.
    field_spec : str
        argument for the field keyword e.g 'x+50'.

    Returns
    -------
    new_lines : list
        list of every string in the file with the updated/added field keyword. 

    """

    new_lines = []
    field_inserted = False

    for line in lines:
            # If Field= already present, replace it
        if "field=" in line:
            line = re.sub(r"field=[^\s]+", f"field={field_spec}", line)
            field_inserted = True
            new_lines.append(line)
        elif not field_inserted and line.strip() == "":
            # If Field= isn't present in the methodd, insert Field= right before
            # first blank after method section
            if any("#" in l for l in new_lines):
                new_lines.append(f"# field={field_spec}\n")
                field_inserted = True
            new_lines.append(line)
        else:
            new_lines.append(line)

    if not field_inserted:
        print("Warning: Keyword 'Field="+field_spec+"' failed to be added to corrosponding file.",
              "Please check .com files are correctly formatted")
        
    return new_lines


def generate_field_files(filename):
    """
    Generates a new .com file for each combination of field strength and direction. 
    The resulting files have the following naming format:
        templatefilename_directionstrength.com
        
        e.g if the template filename is "emim_opt.com", then the files for field=x±50 are
            emim_opt_x50.com
            emim_opt_x-50.com


    Parameters
    ----------
    filename : str
        Name of template .com file excluding extension.

    """
    filename_ext = filename + ".com"
    
    if not os.path.exists(filename_ext):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    with open(filename_ext, "r") as f:
        lines = f.readlines()

    base_name, ext = os.path.splitext(filename)

    for direction in FIELD_DIRECTIONS:
        for strength in FIELD_STRENGTHS:
            for sign in FIELD_SIGNS:
                field_value = sign * strength
                if sign >= 0:
                    field_spec = f"{direction}+{strength}"
                else:
                    field_spec = f"{direction}-{strength}"

                suffix = f"{direction}{field_value}"

                new_lines = update_chk_line(lines, suffix)
                new_lines = update_field_line(new_lines, field_spec)

                new_filename = f"{base_name}_{suffix}{ext}"
                with open(new_filename, "w") as f:
                    f.writelines(new_lines)

                print(f"Created: {new_filename}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_EEF_coms.py template_com_file")
        sys.exit(1)

    generate_field_files(sys.argv[1])

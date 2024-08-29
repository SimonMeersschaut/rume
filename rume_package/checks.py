"""
This file is used to check user input etc.
(no functionality)
"""


def check_sim_input(data: dict):
    if not "outputOptions" in data:
        raise RuntimeError("The simulation input file did not contain the keyword 'outputOptions'. This usually happens when opening a Ruthelde7 file.")
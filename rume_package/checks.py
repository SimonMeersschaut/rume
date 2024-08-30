"""
This file is used to check user input etc.
(no functionality)
"""
import os

def check_sim_input(data: dict):
    if not "outputOptions" in data:
        print("[WARNING] You are probably running a Ruthelde7 file. This file might not contain all keywords.")

def check_task_filename(filename: str):
    if not '.rume.json' in filename:
        raise ValueError(f'Your task file {filename} does not have the extension ".rume.json". Check the task file and rename it manually.')

def check_for_data_folder():
    if not os.path.exists('data') or not os.path.isdir('data'):
        os.mkdir('data')
        raise ValueError('Make sure to put your .imec files in the new "data" folder.')

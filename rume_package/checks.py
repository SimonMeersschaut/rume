"""
This file is used to check user input etc.
(no functionality)
"""
import os
import json

def check_sim_input(data: dict, json_file: str):
    if not "outputOptions" in data:
        print("[WARNING] You are probably running a Ruthelde7 file.")
        data.update({"outputOptions": {}})
        with open(json_file, 'w') as f_copy:
            json.dump(data, f_copy)
    return data

def check_task_filename(filename: str):
    if not '.rume.json' in filename:
        raise ValueError(f'Your task file {filename} does not have the extension ".rume.json". Check the task file and rename it manually.')

def check_for_data_folder():
    if not os.path.exists('data') or not os.path.isdir('data'):
        os.mkdir('data')
        raise ValueError('Make sure to put your .imec files in the new "data" folder.')

import rume_package
import json
import sys
import os

# The script needs a task-input file
if len(sys.argv) == 1:
  input('[ERROR] please provide a task file.')
  exit()

# Make sure to work from where the .bat was executed
WORK_DIR = os.path.dirname(sys.argv[1])
os.chdir(WORK_DIR)

# read task file
with open(sys.argv[1], 'r') as f:
  task_data = json.load(f)

if type(task_data) is list:
  pass
elif type(task_data) is dict:
  # Since the data is one single dictionary, convert it to a list with
  # one single item so that the program can continue as if it was 
  task_data = [task_data]

# Prepare an excel file to write the simulations to
csv_logger = rume_package.CSVLogger()
csv_logger.clear_file()

for task in task_data:
  # execute the tasks
  for txt_filename in task['txt_files']:
    # Combine .json and .imec into .dat for Ruthelde
    json_file = rume_package.combine(task['json_file'], 'data/'+txt_filename)

    # Initialize a simulation
    simulation = rume_package.RutheldeSimulation(normalization_interval=task['normalization_interval'])

    # Run the Ruthelde Simulation
    print(f'Simulating {json_file}')
    simulation.run(input_file=json_file)

    # Save two plots as png (cartesian & logaritmic)
    rume_package.plot(simulation, "rume.work.png", show_graph=False, save_image=True, y_log=False)
    rume_package.plot(simulation, "rume-log.work.png", show_graph=False, save_image=True, y_log=True)

    # write the output in a csv file and csv backup file
    csv_logger.log_simulation(simulation, task, txt_filename)

  csv_logger.write()
"""
This is the main script of rume. Run it with a
batch script and provide a task file as an argument.

The program will start a local Ruthelde8 server and communicate
with it using sockets.
"""

import rume_package
import json
import sys
import os
import subprocess

# The script needs a task-input file
if len(sys.argv) == 1:
  raise ValueError('Please provide a task file and drag it to the special batch file.')

dir_path = os.path.dirname(os.path.realpath(__file__))

# Start Ruthelde Server
os.chdir(f'{dir_path}/rume_package/')
print('Starting the Java Ruthelde Server.')
java_server_process = subprocess.Popen(['java', '-jar', 'Ruthelde_Server.jar'], 
    stdout=subprocess.DEVNULL, 
    stderr=subprocess.STDOUT)
os.chdir('..')

# store the path
WORK_DIR = os.path.dirname(sys.argv[1])
os.chdir(WORK_DIR)

# check if there is a data folder
rume_package.checks.check_for_data_folder()

# read task file
rume_package.checks.check_task_filename(sys.argv[1])
with open(sys.argv[1], 'r') as f:
  task_data = json.load(f)

if type(task_data) is list:
  # data is already strucuted correctly (a list of task)
  pass
elif type(task_data) is dict:
  # As the program expects a list of tasks,
  # create a list with one item
  task_data = [task_data]

# Prepare an excel file to write the simulations to
csv_logger = rume_package.CSVLogger()
csv_logger.clear_file()

plot_index = 1

# loop over the tasks
for task in task_data:
  try:
    # execute each task individually
    for txt_filename in task['txt_files']:
      # create a folder to put all the files in
      folder = txt_filename.split('.imec')[0]
      try:
        os.mkdir(folder)
      except FileExistsError:
        pass
      # copy the model to the folder
      with open(task['json_file'], 'r') as f:
        data = json.load(f)
        data = rume_package.checks.check_sim_input(data)
        with open(folder+'/'+task['json_file'], 'w') as f_copy:
          json.dump(data, f_copy)

      # Combine .json and .imec into .dat for Ruthelde
      work_json_data = rume_package.combine(task['json_file'], 'data/'+txt_filename)

      # Initialize a simulation
      simulation = rume_package.RutheldeSimulation(normalization_interval=task['normalization_interval'])

      # Run the Ruthelde Simulation
      simulation.run(input_data=work_json_data, working_dir=WORK_DIR)

      # Now change the template file to get better plots
      # Change aerial density
      simulation.update_aerial_density(task=task, template_file=task['json_file'])

      # Change chargea
      simulation.update_charge(charge=simulation.q*(10**6), template_file=task['json_file'])

      # write the output in a csv file and csv backup file
      csv_logger.log_simulation(simulation, task, txt_filename)

      # Combine .json and .imec into .dat for Ruthelde
      work_json_data = rume_package.combine(task['json_file'], 'data/'+txt_filename)

      # Run a new simulation
      simulation = rume_package.RutheldeSimulation(normalization_interval=task['normalization_interval'])
      simulation.run(input_data=work_json_data, working_dir=WORK_DIR)

      with open(folder+'/output.work.json', 'w+') as f:
        json.dump(simulation.json_data, f)

      # Save two plots as png (cartesian & logaritmic)
      rume_package.plot(simulation, folder+"/rume-plot-cart.work.png", show_graph=False, save_image=True, y_log=False)
      rume_package.plot(simulation, folder+"/rume-plot-log.work.png", show_graph=False, save_image=True, y_log=True)
      plot_index +=1

      print(f'Done analysing {txt_filename}')

    # Write the registered content to the csv file
    csv_logger.write()

  except Exception as e:
    # Write the registered content to the csv file
    csv_logger.write()
    raise e

# Kill Ruthelde Server
print('Stopping the Ruthelde Server.')
if java_server_process.poll() is None:  # Check if process is still running
    java_server_process.terminate()  # Gracefully terminate the process
    java_server_process.wait()  # Wait for the process to terminate
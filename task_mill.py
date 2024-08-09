import rume_package
import json
import sys
import os
import subprocess
import time

# The script needs a task-input file
if len(sys.argv) == 1:
  input('[ERROR] please provide a task file.')
  exit()


dir_path = os.path.dirname(os.path.realpath(__file__))
# Start Ruthelde Server
os.chdir(f'{dir_path}/rume_package/')
print('Starting the Java Ruthelde Server.')
java_server_process = subprocess.Popen(['java', '-jar', 'Ruthelde_Server.jar'], 
    stdout=subprocess.DEVNULL, 
    stderr=subprocess.STDOUT)
# time.sleep(2)
os.chdir('..')

# Make sure to work from where the .bat was executed
WORK_DIR = os.path.dirname(sys.argv[1])
os.chdir(WORK_DIR)

# A basic check
if not os.path.exists('data') or not os.path.isdir('data'):
  os.mkdir('data')
  input('[ERROR] Make sure to put your .imec files in the new "data" folder.')
  exit()


# read task file
with open(sys.argv[1], 'r') as f:
  task_data = json.load(f)

if type(task_data) is list:
  pass
elif type(task_data) is dict:
  # As the program expects a list of tasks,
  # create a list with one item
  task_data = [task_data]

# Prepare an excel file to write the simulations to
csv_logger = rume_package.CSVLogger()
csv_logger.clear_file()

plot_index = 1

for task in task_data:
  # execute the tasks
  for txt_filename in task['txt_files']:
    # create a folder to put all the files in
    folder = txt_filename.split('.imec')[0]
    os.mkdir(folder)
    # copy the model to the folder
    with open(task['json_file'], 'r') as f:
      with open(folder+'/'+task['json_file'], 'w') as f_copy:
        f_copy.write(f.read())

    # Combine .json and .imec into .dat for Ruthelde
    work_json_data = rume_package.combine(task['json_file'], 'data/'+txt_filename)

    # Initialize a simulation
    simulation = rume_package.RutheldeSimulation(normalization_interval=task['normalization_interval'])

    # Run the Ruthelde Simulation
    simulation.run(input_data=work_json_data, working_dir=WORK_DIR)
    # simulation.run(input_file=task['json_file'], working_dir=WORK_DIR)


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

  # Write the registered content to the csv file
  csv_logger.write()

# Kill Ruthelde Server
print('Stopping the Ruthelde Server.')
if java_server_process.poll() is None:  # Check if process is still running
    java_server_process.terminate()  # Gracefully terminate the process
    java_server_process.wait()  # Wait for the process to terminate
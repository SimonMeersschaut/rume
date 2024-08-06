import rume_package
import json
import sys
import os
import glob

# The script needs a task-input file
if len(sys.argv) == 1:
  input('[ERROR] please provide a task file.')
  exit()

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
    # Combine .json and .imec into .dat for Ruthelde
    json_file = rume_package.combine(task['json_file'], 'data/'+txt_filename)

    # Initialize a simulation
    simulation = rume_package.RutheldeSimulation(normalization_interval=task['normalization_interval'])

    # Run the Ruthelde Simulation
    simulation.run(input_file=json_file, working_dir=WORK_DIR)

    # write the output in a csv file and csv backup file
    csv_logger.log_simulation(simulation, task, txt_filename)

    # Now change the template file to get better plots
    # Change aerial density
    simulation.update_aerial_density(task=task, template_file=task['json_file'])
    # Change charge
    simulation.update_charge(charge=simulation.q*(10**6), template_file=task['json_file'])

    # Run a new simulation
    simulation = rume_package.RutheldeSimulation(normalization_interval=task['normalization_interval'])
    simulation.run(input_file=task['json_file'], working_dir=WORK_DIR)

    # Save two plots as png (cartesian & logaritmic)
    rume_package.plot(simulation, f"rume-plot-cart.work.png", show_graph=False, save_image=True, y_log=False)
    rume_package.plot(simulation, f"rume-plot-log.work.png", show_graph=False, save_image=True, y_log=True)
    plot_index +=1

  # Write the registered content to the csv file
  csv_logger.write()
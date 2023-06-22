import rume_package
import json
import sys
import math

if len(sys.argv) == 1:
  input('[ERROR] please provide a task file.')

with open(sys.argv[1], 'r') as f:
  TASK = json.load(f)
DELIMITER = ','
ISOTOPE = '4He'
CSV_FILE = 'rume_results.csv'


with open(CSV_FILE, 'a+') as f:
    f.write('\n')


for txt_filename in TASK['txt_files']:
  json_file = rume_package.combine(TASK['json_file'], TASK['txt_path']+'/'+txt_filename)
  print('analyzing '+str(json_file))
  simulation = rume_package.RutheldeSimulation(json_file, normalization_interval=TASK['normalization_interval'])
  rume_package.plot(simulation)
  with open(CSV_FILE, 'a+') as f:
    f.write(f'{txt_filename}{DELIMITER}{simulation.sample_id}{DELIMITER}{simulation.q:e}')
  for subject in TASK['subjects']:
    print('subject :: '+subject['element'])
    sigma = simulation.calc_dsigma(rume_package.table.isotope(ISOTOPE), subject['element'])
    roi_sum = simulation.interval_sum(subject['channel_interval'])
    Nt = roi_sum / (sigma * simulation.omega_particles) * 1.E+24 / 1.E+15
    if roi_sum == 0:
      droi_sum = 1
    else:
      droi_sum = math.sqrt(roi_sum) / roi_sum
    DNt = Nt * droi_sum

    with open(CSV_FILE, 'a+') as f:
      f.write(f'{DELIMITER}{subject["element"]}{DELIMITER}{Nt:e}{DELIMITER}{DNt:e}')

    
  with open(CSV_FILE, 'a+') as f:
    f.write('\n')
"""
The csv logger will register each simulation one by one.
For each simulation 'log_simulation' is called to register this line.
For each simulation, the program will go over all subjects of that simulation.
It will store all the registered information in self.samples, in which each item corresponds to one line in the csv file.
"""

from .surf import table
import math

DELIMITER = ','
ISOTOPE = '4He'
CSV_FILE = 'rume_results.csv'

class CSVLogger:
    def __init__(self):
        """Initialize the CSV logger."""
    def log_simulation(self, simulation, task, txt_filename):
        """Save a RutheldeSimulation object in a csv file and a csv-backup file."""
        # Each sample is translated to one line in the csv file
        sample = [
            ("filename", txt_filename.split('.imec')[0]),
            ("ID", simulation.json_data['SampleId']),
            ("Charge (μC)", simulation.q),
        ]
        
        for subject in task['subjects']:
            # print('subject :: '+subject['element'])
            sigma = simulation.calc_dsigma(table.isotope(ISOTOPE), subject['element'])
            roi_sum = simulation.interval_sum(subject['channel_interval'])
            Nt = roi_sum / (sigma * simulation.omega_particles) * 1.E+24 / 1.E+15
            if roi_sum == 0:
                droi_sum = 1
            else:
                droi_sum = math.sqrt(roi_sum) / roi_sum
                DNt = Nt * droi_sum


            sample.append((subject['element'], Nt))
            sample.append((f'error {subject['element']}', DNt))

            # with open(CSV_FILE, 'a+') as f:
            #     f.write(f'{DELIMITER}{subject["element"]}{DELIMITER}{Nt:e}{DELIMITER}{DNt:e}')

    def write(self):
        """Write the registered data to the csv file."""
        print(self.samples)


    def close(self):
        """Save and close the excel document."""
        ...

# with open(CSV_FILE, 'a+') as f:
#     f.write(f"\n{txt_filename.split('.imec')[0]}{DELIMITER}{simulation.json_data['SampleId']}{DELIMITER}{simulation.q:e}")



    
# with open(CSV_FILE, 'a+') as f:
#     f.write('\n')
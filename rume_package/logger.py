"""
The csv logger will register each simulation one by one.
For each simulation 'log_simulation' is called to register this line.
For each simulation, the program will go over all subjects of that simulation.
It will store all the registered information in self.samples, in which each item corresponds to one line in the csv file.
"""

from .surf import table
import math
from datetime import datetime

DELIMITER = ','
ISOTOPE = '4He'
CSV_FILE = 'rume_results.csv'
BCKP_CSV_FILE = 'bckp_rume_results.csv'

class CSVLogger:
    def __init__(self):
        """Initialize the CSV logger."""
        self.samples = []
    
    def clear_file(self):
        try:
            with open(CSV_FILE, 'w+') as f:
                f.write('')
        except PermissionError:
            raise PermissionError('Could not open the csv file. Mayble you opened it?')
    
    def log_simulation(self, simulation, task, txt_filename):
        """Save a RutheldeSimulation object in a csv file and a csv-backup file."""
        # 'sample' is a temporary variable that holds the data for the current line
        if not('SampleId' in simulation.json_data):
            simulation.json_data['SampleId'] = 'Not Found!'
        sample = [
            ("filename", txt_filename.split('.imec')[0]),
            ("ID", simulation.json_data['SampleId']),
            ("Charge (uC)", simulation.q * (10**6)),
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
            sample.append((f"stat uncertainty {subject['element']}", DNt))
            abs_error = math.sqrt(min(0.2, Nt/4)**2 + (Nt*0.02)**2)
            sample.append((f"Abs error {subject['element']}", abs_error))
            total_uncertainty = min(DNt+abs_error, Nt)
            sample.append((f"Total Uncertainty {subject['element']}", total_uncertainty))
        
        self.samples.append(sample)
    
    def write(self):
        """Prepare and write the registered data to the csv file."""
        # STEP 1: prepare content
        content = ''
        # prepare the heading
        # store ALL heading-items
        headings = []
        for sample in self.samples:
            headings += [heading for (heading, _) in sample]
        
        # remove any duplicates from the list
        headings = list(dict.fromkeys(headings))

        # write headings to content variable
        content += DELIMITER.join(headings)
        content += '\n'

        # prepare body
        for sample in self.samples:
            for heading in headings:
                # search the value corresponding with the current heading
                try:
                    value = [value for head_, value in sample if head_ == heading][0]
                except IndexError:
                    value = '/'
                content += str(value) + DELIMITER
            content += '\n'

        # STEP 2: write content
        try:
            # write to the output file
            with open(CSV_FILE, 'a+', encoding='utf-8') as f:
                f.write(content)
                f.write('\n')
            
            # also write to a backup file
            with open(BCKP_CSV_FILE, 'a+', encoding='utf-8') as f:
                # include an empty line
                f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n')
                f.write(content)
                f.write('\n')
        except PermissionError:
            raise PermissionError('Could not open the file. Perhaps you already opened the file?')
        
        # now clear the samples list so that the next tasks
        # won't have the same headings and body as this one does
        # in other words: we don't want samples to apear twice
        self.samples = []
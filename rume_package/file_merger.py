import json
import os

def combine(json_file:str, data_file:str) -> dict:
  '''
  returns the name of the outputfile (.dat)
  '''
  # read data file
  with open(data_file, 'r') as f:
    content = f.read()
  y_values = [int(line.split(', ')[1]) for line in content.split('End comments')[-1].split('\n') if len(line.split(', ')) > 1]

  # load json file
  with open(json_file, 'r') as f:
    data = json.load(f)
  data['experimentalSpectrum'] = y_values
  data['SampleId'] = content.split(' * Sample ID             := ')[1].split('\n')[0]

  # dir_path = os.path.dirname(os.path.realpath(__file__))
  filename = json_file.split('/')[-1].split('\\')[-1].split('.')[0] + '.work.json'
  with open(filename, 'w+') as f:
    json.dump(data, f)
  return filename
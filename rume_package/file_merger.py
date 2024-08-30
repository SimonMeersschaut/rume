import json
import os

def combine(json_file:str, data_file:str) -> dict:
  '''
  Combines a json file and a datafile (.imec).
  returns the data
  '''
  # read data file
  with open(data_file, 'r') as f:
    content = f.read()
  y_values = [int(line.split(', ')[1]) for line in content.split('End comments')[-1].split('\n') if len(line.split(', ')) > 1]
  if len(y_values) > 1024:
    print('[WARNING] The length of your txt file was more than 1024, automatically cropped the data.')

  # load json file
  with open(json_file, 'r') as f:
    data = json.load(f)
  data['experimentalSpectrum'] = y_values
  data['SampleId'] = content.split(' * Sample ID             := ')[1].split('\n')[0]
  data['Title'] = content.split(' % Title                 := ')[1].split('\n')[0]
  

  return data
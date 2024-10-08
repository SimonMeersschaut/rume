"""
A RutheldeSimulation will start a simulation by 
using the python client (written by Tobi) and 
send a command to the server running locally.
"""

import json
from .surf import Q_COULOMB, table
from . import surf
import socket
import math
from .surf import table

ISOTOPE = '4He'

class RutheldeSimulation:
  """This object will interact with the Ruthelde8 server and start a simulation."""
  def __init__(self, normalization_interval):
    """
    input_file: .json
    """
    self.normalization_begin = normalization_interval[0]
    self.normalization_end = normalization_interval[1]

    self.simulated_y = []
  
  def run(self, input_data:dict, working_dir) -> None:
    self.json_data = input_data

    # Run the Ruthelde Simulation
    self.simulation_output = ruthelde_simulate(input_data)

    # simulation is done
    # set attributes
    self.experimental_y = self.json_data['experimentalSpectrum']
    self.channel = list(range(len(self.experimental_y)))
    self.simulated_y = self.simulation_output['spectra'][0]['data']
  
  def update_aerial_density(self, task, template_file):
    """Update the aerial density from the working file to the template file."""
    # load in the template file
    with open(template_file, 'r') as f:
      template_data = json.load(f)

    # calculate the aerial densities of the subjects
    for subject in task['subjects']:
      # print('subject :: '+subject['element'])
      sigma = self.calc_dsigma(table.isotope(ISOTOPE), subject['element'])
      roi_sum = self.interval_sum(subject['channel_interval'])
      Nt = roi_sum / (sigma * self.omega_particles) * 1.E+24 / 1.E+15
      if roi_sum == 0:
          droi_sum = 1
      else:
          droi_sum = math.sqrt(roi_sum) / roi_sum
          DNt = Nt * droi_sum

      z = table.atomic_number(subject['element'])
      # search the element by atomic number
      for i, element in enumerate(template_data['target']['layerList'][0]['elementList']):
        if element['atomicNumber'] == z:
          element['arealDensity'] = Nt
          break
    
    with open(template_file, 'w') as f:
      json.dump(template_data, f)
    
  def update_charge(self, charge: int, template_file: str):
    """Update the charge of the template file to the newly calculated value."""
    # load in the template file
    with open(template_file, 'r') as f:
      template_data = json.load(f)
    
    template_data['experimentalSetup']['charge'] = charge

    with open(template_file, 'w') as f:
      json.dump(template_data, f)

      
  def to_channel(self, x):
    return (x-self.offset)/self.step

  @property
  def exp_sum(self):
    '''integrated experimental amplitude substrate (in counts)'''
    sum_ =  sum(self.experimental_y[self.normalization_begin:self.normalization_end])
    if sum_ == 0:
      raise ZeroDivisionError("Sum of normalization interval is 0.")
    return sum_

  @property
  def sim_sum(self):
    '''integrated simulated amplitude substrate (in counts)'''
    sum_ = sum(self.simulated_y[self.normalization_begin:self.normalization_end])
    if sum_ == 0:
      raise ZeroDivisionError("Sum of normalization interval is 0.")
    return sum_
  
  @property
  def q(self):
    '''actual scaled charge (in Coulomb)'''
    return (self.exp_sum/self.sim_sum)*self.json_data['experimentalSetup']['charge']*1.E-6
    
  @property
  def solid_angle(self):
    '''in steradian'''
    return self.json_data['detectorSetup']['solidAngle'] *1.E-3
  
  @property
  def particles(self):
    return self.q / Q_COULOMB
  
  @property
  def omega_particles(self):
    '''in Coulomb'''
    return self.solid_angle*self.particles

  def interval_sum(self, interval) -> int:
    '''
    x_min and x_max in channels
    '''
    x_min, x_max = interval
    total = 0
    for x, y in zip(self.channel, self.experimental_y):
      if x_min <= x-1 <= x_max:
        total += y
    return total
  
  @property
  def E_prim(self):
    return self.json_data['experimentalSetup']['E0']/1000
  
  @property
  def theta(self):
    return self.json_data['experimentalSetup']['theta']
  
  @property
  def alpha(self):
    return self.json_data['experimentalSetup']['alpha']
    
  def calc_Fscreening(self, isotope1, element2):
    return 1 - (0.049*isotope1[1]*(table.atomic_number(element2)**(4/3))) / (self.E_prim*1000)

  def calc_dsigma(self, isotope1, element2):
    return surf.calc_dsigma(self.E_prim, self.theta, self.alpha, isotope1, element2) * self.calc_Fscreening(isotope1, element2)

def ruthelde_simulate(input_data):
  '''
  Function input: request_type (str), data (str)
  - request_type: 'OPTIMIZE_' or 'SIMULATE_'
  - data: json file in a string, this should contain all the necessary information for the request
  Function purpose: Connects to the server, sends the request and waits for the answer
  Function returns: The response of the server as SIM-RESULT_{output}
  '''
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      # Connect to the server
      s.connect(("localhost", 9090))

      # Send the message
      message = 'SIMULATE_' + json.dumps(input_data) + "\n"
      s.sendall(message.encode('utf-8'))

      end_of_transmission = "End_Of_Transmission\n"
      s.sendall(end_of_transmission.encode('utf-8'))

      # Wait for response
      response = b""
      # The respons of the server will generally be too large, so in order to be able to receive the full respons we make use of a buffer
      # The idea is that you keep reading parts of the response where each part is 4096 bytes in size.
      # It's like splitting the response into different parts of a certain size and then adding all these parts together to be able to reconstruct the full response
      # At some point the part you are reading will contain the end of the response so the size of the part will be less than 4096 bytes, then stop.
      
      s.settimeout(2.0)
      while True:
        try:
          part = s.recv(4096)
          response += part
        except socket.timeout:
          # If we hit a timeout, assume no more data is coming
          # print("Timeout reached, assuming end of message")
          break
      
      response = response.decode('utf-8')
      start_index = response.find("SIM-RESULT_") + len("SIM-RESULT_")
      end_index = response.find("End_Of_Transmission")
      Simulation_output_json = response[start_index:end_index].strip()
      return json.loads(Simulation_output_json)
      

  except Exception as ex:
    print("Error sending request to server.")
    print(ex)
    print(response)
    raise ValueError('Error in Ruthelde8 (client or server.)')
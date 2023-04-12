import os
import json
import glob 
from .surf import Q_COULOMB, table
from . import surf

class RutheldeSimulation:

  def __init__(self, input_file:str, normalization_interval):
    """
    input_file: .json
    """
    self.normalization_begin = normalization_interval[0]
    self.normalization_end = normalization_interval[1]

    self.generate_output(input_file)
    
    with open(input_file, 'r') as f:
      self.json_data = json.load(f)
  
  def generate_output(self, input_file:str) -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    output_filename = input_file.split('/')[-1].split('\\')[-1].split('.')[0] + '.work.dat'
    ruthelde_exec = glob.glob(dir_path+'/ruthelde-*.jar')[0]
    
    os.system(f'java -jar {ruthelde_exec} simulate {input_file} {output_filename}')
    
    # simulation is done, read output
    self.load_dat_file(output_filename)
  
  def load_dat_file(self, dat_file:str) -> None:
    with open(dat_file, 'r') as f:
      self.content = f.read().replace(',', '.')
    self.initialize_convertion()
  
  def initialize_convertion(self) -> None:
    self.step = (self.simulated_x[-1] - self.simulated_x[0])/(self.channel[-1] - self.channel[0])
    self.offset = self.simulated_x[0]
  
  def to_channel(self, x):
    # print(x)
    return (x-self.offset)/self.step
  
  @property
  def sample_id(self):
    return self.json_data['SampleId']

  @property
  def header(self):
    return self.content.split('</Header>')[0].split('<Header>')[-1]
  
  @property
  def spectrum_name(self):
    return self.header.split('Spectra - ')[1].split('\n')[0]
  
  @property
  def body(self):
    return self.content.split('</Header>')[-1]
  
  @property
  def data(self):
    return [[float(datapoint) for datapoint in line.split()] for line in self.body.split('\n') if len(line.split()) > 0]
  
  @property
  def charge(self):
    '''charge in json-file (in micro Coulomb)'''
    return self.json_data['experimentalSetup']['charge']
  
  @property
  def channel(self):
    return [line[0] for line in self.data]
  
  @property
  def simulated_x(self):
    '''energy (in keV)'''
    return [line[1] for line in self.data]
  
  @property
  def simulated_y(self):
    '''simulated spectrum (in counts)'''
    return [line[2] for line in self.data]
  
  @property
  def experimental_x(self):
    '''energy (in keV)'''
    return [line[3] for line in self.data]
  
  @property
  def experimental_y(self):
    '''experimental spectrum (in counts)'''
    return [line[4] for line in self.data]

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
    return (self.exp_sum/self.sim_sum)*self.charge*1.E-6
    
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

  # def surface_approximation(self, element2, x_min, x_max):
  #   isotope1 = table.get_isotope_by_mass(
  #     mass=self.json_data['experimentalSetup']['projectile']['M'],
  #     z=self.json_data['experimentalSetup']['projectile']['Z']
  #     )
  #   dsigma = calc_dsigma(
  #     E_prim=self.E_prim,
  #     theta=self.theta,
  #     alpha=self.alpha,
  #     isotope1=isotope1,
  #     elem2=element2
  #   )
  #   # print(dsigma)
  #   return self.interval_sum(x_min, x_max) / (dsigma*self.omega_particles)
  
  def calc_dsigma(self, isotope1, element2):
    return surf.calc_dsigma(self.E_prim, self.theta, self.alpha, isotope1, element2) * self.calc_Fscreening(isotope1, element2)
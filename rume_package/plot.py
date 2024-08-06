from .ruthelde import RutheldeSimulation
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass


class PlotOptions:
  y_label = 'Yield (counts)'

  first_x_label:str = 'Channel'
  first_color:str = '#FF0000'

  second_x_label:str = 'Energy (MeV)'
  second_color:str = '#000000'
  second_marker_size = 10

def plot(simulation:RutheldeSimulation, filename: str, y_log: bool, show_graph: bool, save_image: bool) -> None:
  simulation = simulation
    
  matplotlib.rcParams.update({'font.size': 14})
  matplotlib.rc('xtick', labelsize=10) 
  matplotlib.rc('ytick', labelsize=10) 

  fig = plt.figure()
  ax1 = fig.add_subplot(111)
  plt.title(simulation.spectrum_name, fontdict={'fontsize':10}, loc='left')
  ax1.set_xlabel(PlotOptions.first_x_label)
  ax1.set_ylabel(PlotOptions.y_label)

  y_values = [y*simulation.exp_sum/simulation.sim_sum for y in simulation.simulated_y]
  ax1.plot(simulation.channel, y_values, c=PlotOptions.first_color)
  ax1.scatter(simulation.channel, simulation.experimental_y, facecolors='none', edgecolors=PlotOptions.second_color, s=PlotOptions.second_marker_size)

  ax2 = ax1.twiny()
  
  ax2.set_xlabel(PlotOptions.second_x_label)
  ax2.plot([i/1000 for i in simulation.simulated_x], np.ones(len(simulation.simulated_x)), linestyle='None')
  ax2.set_title('', fontdict={'fontsize':10}, loc='right')

  if y_log:
    plt.yscale("log") 

  plt.tight_layout()

  if save_image:
    plt.savefig(filename)
  if show_graph:
    plt.show()
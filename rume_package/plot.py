from .ruthelde import RutheldeSimulation
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass

@dataclass
class PlotOptions:
  y_label = 'Yield (counts)'

  first_x_label:str = 'Channel'
  first_color:str = '#FF0000'

  second_x_label:str = 'Energy (MeV)'
  second_color:str = '#000000'
  second_marker_size = 10

def plot(simulation:RutheldeSimulation) -> None:
  plt = Plot(simulation)
  plt.show()

class Plot:
  def __init__(self, simulation:RutheldeSimulation, plot_options=None):
    self.simulation = simulation
    
    if plot_options == None:
      self.plot_options = PlotOptions()
    else:
      self.plot_options = plot_options
  
  def handle_click(self, event):
    x, y = self.simulation.to_channel(event.xdata*1000), event.ydata
    
    # print (f'x = {x}, y = {y}')
    self.ax2.set_title(f'({round(x, 1)}, {round(y, 1)})', fontdict={'fontsize':10}, loc='right')
    plt.draw() #redraw

  def show(self):
    matplotlib.rcParams.update({'font.size': 14})
    matplotlib.rc('xtick', labelsize=10) 
    matplotlib.rc('ytick', labelsize=10) 

    self.fig = plt.figure()
    self.ax1 = self.fig.add_subplot(111)
    plt.title(self.simulation.spectrum_name, fontdict={'fontsize':10}, loc='left')
    self.ax1.set_xlabel(self.plot_options.first_x_label)
    self.ax1.set_ylabel(self.plot_options.y_label)

    y_values = [y*self.simulation.exp_sum/self.simulation.sim_sum for y in self.simulation.simulated_y]
    self.ax1.plot(self.simulation.channel, y_values, c=self.plot_options.first_color)
    self.ax1.scatter(self.simulation.channel, self.simulation.experimental_y, facecolors='none', edgecolors=self.plot_options.second_color, s=self.plot_options.second_marker_size)

    self.ax2 = self.ax1.twiny()
    
    self.ax2.set_xlabel(self.plot_options.second_x_label)
    self.ax2.plot([i/1000 for i in self.simulation.simulated_x], np.ones(len(self.simulation.simulated_x)), linestyle='None')
    self.ax2.set_title('', fontdict={'fontsize':10}, loc='right')

    cid = self.fig.canvas.mpl_connect('button_press_event', self.handle_click)

    plt.tight_layout()
    plt.savefig('rume.work.png')
    # plt.show()

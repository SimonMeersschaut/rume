"""
This file does the calculations for RutheldeSimulation.
It contains very litle to no functionality.
"""

import os
import json
from math import pi, sin, radians, sqrt, cos

Q_COULOMB = 1.60206E-19
EPSILON0 = 8.85434E-12
TMP0 = (Q_COULOMB)**2 / (4*pi*EPSILON0)
BARN = 1E+28

class Table:
    FILENAME = 'Chu_Table_Ib.json'
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path+'/'+Table.FILENAME, 'r') as f:
            self.data = json.load(f)
    
    def isotope(self, isotope):
        isotope_number = int(''.join([letter for letter in isotope if letter in '0123456789']))
        isotope_name = isotope.split(str(isotope_number))[-1]
        isotopes = [isotope for isotope in self.isotopes(isotope_name)]
        sorted_isotopes = sorted(isotopes, key=lambda iso:abs(int(isotope_number)-iso[2]))
        # print(sorted_isotopes)
        return sorted_isotopes[0]
    
    def get_isotope_by_mass(self, mass, z):
        filtered_isotopes = [isotope for isotope in self.data if int(isotope[1]) == z]
        sorted_isotopes = sorted(filtered_isotopes, key=lambda iso:abs(int(mass)-iso[2]))
        return sorted_isotopes[0]

    def isotopes(self, isotope):
        """get all isotopes of an element"""
        for isotope_ in self.data:
            if isotope_[0] == isotope:
                yield isotope_
        return
    
    def atomic_number(self, element):
        return int(list(self.isotopes(element))[0][1])
    

def calc_dsigma(E_prim, theta, alpha, isotope1, elem2) -> float:
    z1 = isotope1[1]
    z2 = table.atomic_number(elem2)

    tmp2 = 4/(sin(radians(theta)))**4

#L'Ecuyer screening
    Fscreening = 1.0-(0.049*z1*pow(z2,(4./3.)))/(E_prim*1000.0)

    dsigma = 0
    for j in table.isotopes(elem2):
        m1 = isotope1[2]
        m2 = j[2]

        energy = E_prim*1.E+06*Q_COULOMB

        tmp1 = ((z1*z2*TMP0)/(4*energy))**2
        tmp4 = sqrt(1 - (m1/m2 * sin(radians(theta)))**2)
        tmp3 = (tmp4 + cos(radians(theta)) )**2

        dsigma += j[3]/cos(radians(alpha)) * tmp1 * tmp2 * tmp3 / tmp4 * BARN

    dsigma = dsigma*Fscreening
    return dsigma

        

table = Table()
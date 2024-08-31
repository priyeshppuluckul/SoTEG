## @package SoTEGModel
#  This package implements the model of a custom Soil-Air Thermolectric Generator (SoTEG) described in https://doi.org/10.1109/ACCESS.2024.3414652.
#  SoTEG converts the temperature difference between soil and air into energy which can be used to power outdoor batteryless devices. The model
#  uses a one-dimensional heat conduction approximation of the harvester which considers heat transfer through radiation, convection and conduction.
#  Refer ./COPYING.txt for terms and conditions
#

import sympy as sp
from math import sqrt
import sys
import csv
import sys
import math


class SoTEGModel:
    ## The initialization constructor.
    # All non-time varying variables are initialized here.
    # Units of measurements, unless otherwise specified:
    # Temperature - °C
    # Thermal  resistance = °C/W
    # Electrical resistance- Ohm
    # Area = m^2
    # Seebeck coefficient  = mV/°C
    # Irradiance - W/m^2
    # wind speed- m/s
    # Electrial Power - mW

    def __init__(self):

        ## @var h_air
        # natural convection coefficient.
        self.h_air = 0
        ## @var
        # Stefan-Boltzmann constant
        self.sigma = 5.670374419e-8
        ## @var
        # emissivity of the radiator as measured in the lab
        self.emissivity = 0.92
        ## @var
        # absorptivitiy of the radiator as measured in the lab
        self.absorptivity = 0.92
        ## @var
        # Seebeck coefficient of the TEG experimentally measured
        self.sCoefficient = 41.7
        ## @var
        # Electrical resistance of the TEG, obtained from the datasheet
        self.tegElectricalR = 3.8
        ## @var
        # Thermal resistance of the TEG, can be obtained from the datasheet
        self.R_teg = 1.56
        ## @var
        # Thermal resistance of the copper rods in parallel (10 cm in length and 6.35 mm in diameter)
        # Can be calculated as R  = length/(conductivity*area)
        self.R_rod = 0.87
        ## @var
        # Thermal resistance of the adhesive used: You may assume this is zero for ideal calculations.
        self.R_adhesive = 0.5
        ## @var
        # Thermal resistance of the copper plate used between the copper rods and the TEG
        self.R_plate = 0.0008
        ## @var
        # Thermal resistance of the radiator (10 cm diameter and 0.5 mm thickness)
        self.R_radiator = 0.0001445
        ## @var
        # Area of the radiator (use the equation for the area of a disk)
        self.A_radiator = 0.00865

        ## @var
        # Total thermal resistance of the entire system. All the thermal resistances are in parallel
        self.R_total = self.R_rod + self.R_plate + self.R_teg + self.R_radiator + self.R_adhesive

        # uses the radiation model of the STEG to calculate the
        # air side temperature

    ## Calculates radiator temperature
    # @param t_air The temperature of the air in °C
    # @param t_soil Temperature of the ambient air
    # @param I_solar Irradiance
    # @param wind_speed wind speed
    # @param theta angle of incidence of solar radiation
    # @return Calculated temperature difference
    def getRadiatorTemperature(self, t_air, t_soil, I_solar, wind_speed, theta, t_sky):
        ## converts temperatures from  °C to K
        t_air += 273.15
        t_soil += 273.15
        t_sky = t_sky + 273.15

        ## @var s_lambda decides the amount of solar radiation falling on the radiator.
        # The value of s_lambda is calculated using the incidence angle.
        # 1- implies the radiator faces the sun and the entire irradiance falls on it.
        # 0- no radiation falls on the radiator.
        s_lambda = 1.0

        # Estimate convection coefficient from wind speed.
        # Refer to the publication for more details
        self.h_air = 6.5 + 2.8 * wind_speed

        ## Calculate the irradiance factor s_lambda.
        # The value is calculated only for a valid value of solar radiation, else 1 is used
        if I_solar > 0.0:
            s_lambda = math.cos(math.radians(theta))

        ## @var m first variable of the quartic equation
        m = ((1 / (self.sigma * self.emissivity)) * (self.h_air + (1 / (self.A_radiator * self.R_total))))

        ##@var c second variable of the quartic equation
        c = (t_sky ** 4 + \
             ((self.h_air * t_air) / (self.sigma * self.emissivity)) + \
             ((self.absorptivity * s_lambda * I_solar) / (self.sigma * self.emissivity)) + \
             (t_soil / (self.sigma * self.emissivity * self.A_radiator * self.R_total)))

        ## Calculate the temperature of the radiator.
        # This equation is obtained by solving the quartic equation using MATLAB and choosing only
        # valid root
        temp_radiator = (3 ** (1 / 2) * (4 * 3 ** (1 / 2) * c * (
                    3 * ((3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (1 / 2)) / 18 + m ** 2 / 2) ** (
                        2 / 3) - 4 * c) ** (1 / 2) - 3 * 3 ** (1 / 2) * (3 * (
                    (3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (1 / 2)) / 18 + m ** 2 / 2) ** (2 / 3) - 4 * c) ** (
                                                     1 / 2) * ((3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (
                    1 / 2)) / 18 + m ** 2 / 2) ** (2 / 3) + 3 ** (1 / 2) * 6 ** (1 / 2) * m * (
                                                     3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (
                                                         1 / 2) + 9 * m ** 2) ** (1 / 2)) ** (1 / 2)) / (6 * (
                    9 * ((3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (1 / 2)) / 18 + m ** 2 / 2) ** (
                        2 / 3) - 12 * c) ** (1 / 4) * ((3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (
                    1 / 2)) / 18 + m ** 2 / 2) ** (1 / 6)) - (3 ** (1 / 2) * (
                    3 * ((3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (1 / 2)) / 18 + m ** 2 / 2) ** (
                        2 / 3) - 4 * c) ** (1 / 2)) / (6 * (
                    (3 ** (1 / 2) * (256 * c ** 3 + 27 * m ** 4) ** (1 / 2)) / 18 + m ** 2 / 2) ** (1 / 6))

        ## Sanity check.
        # This should never happen. However, by chance this condition is hit, the simulation is
        # terminated
        if isinstance(temp_radiator, complex):
            sys.exit()

        ## Convert temperature back to back to Celsius
        return (temp_radiator - 273.15)

    ## Calculates the temperature of a generator with a heatsink used at the ambient side
    # @warning This is not a verified method!
    # @param t_air Temperature of the air
    # @param t_soil Temperature of the soil
    # @param h Natural convection coefficient
    # @param hs_area Area of the heatsink
    # @return Calculated temperature difference
    def getHeatSinkTemperature(self, t_air, t_soil, h, hs_area):
        t_hs = (t_air * h + t_soil / (self.R_total)) / ((1 / self.R_total) + h)
        return t_hs

    ## Calculates temperature difference across teg
    # @param t_radiator Temperature of the radiator
    # @param t_soil Temperature of the soil
    # @return Calculated temperature difference
    def getDeltaT(self, t_radiator, t_soil):
        dT = (t_radiator - t_soil) * self.R_teg / (self.R_total)
        return (dT)

    ## Estimates the matched load power of the TEG
    # @param dt temperature difference across the TEG
    # @return Estimated power in mW
    def getTEGMatchedLoadPower(self, dt):
        power = self.sCoefficient * self.sCoefficient * (dt * dt) / (4 * self.tegElectricalR * 1000)
        return round(power, 3)


# Example Run
if __name__ == '__main__':
    soteg = SoTEGModel()
    t_soil = 20
    t_air = 25
    I_solar =  200
    wind_speed = 2
    theta = 0
    t_sky = 0

    t_rad = soteg.getRadiatorTemperature(t_air, t_soil, I_solar, wind_speed, theta, t_sky)
    t_delta = soteg.getDeltaT(t_rad, t_soil)
    power = soteg.getTEGMatchedLoadPower(t_delta)
    # print: radiator temperature, delta temperature across the TEG and the generated power
    print(t_rad, t_delta, power)

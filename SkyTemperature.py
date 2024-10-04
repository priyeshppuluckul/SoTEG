## @package SkyTemperature
# This package calculates the sky temperature.
# the Clark-Allen model is used to calculate the  clear sky emissivity.
# Simulations tools like EnergyPlus uses this model to calculate sky emissivity and temperature.
# The Clear sky model is then converted for cloudy sky using a cloud correlation factor.
# There are two methods given: one uses the generic relation between sky emissivity and the ambient temperature
# and the other uses the energy plus calculation model.

import numpy as np

class SkyTemperature:
    def __init__(self):
        # Stefan-Boltzmann constant
        self.sigma = 5.670374419e-8

    # Calculates sky emissivity using Clark-Allen model
    def emissivity(self, N,  t_dp):
        t_dp += 273.15
        # Calculate sky emissivity
        sky_emissivity = ( 0.787 + 0.767 * np.log(t_dp / 273) ) + ( (0.0224 * N) - (0.0035 * N ** 2) + (0.00028 * N ** 3))

        return (sky_emissivity)

    ## Calculates sky temperature using the relation between emissivity and ambient temp
    # @param N Opaque sky cover in   tenths (0 - no cover, 10 - completely covered)
    # @param t_air air temperature in degree Celsius
    # @param t_dp dew point temperature in degree Celsius
    # @return  sky temperature in degree Celsius
    def get_temperature1(self, N,  t_air, t_dp):
        # Get sky emissivity
        sky_emissivity = self.emissivity(N, t_dp)
        # Calculate sky temperature
        t_sky = (sky_emissivity ** 0.25) * t_air
        # return sky temperature in Celsius
        return (t_sky)

    ## Calculates sky temperature using EnergyPlus method
    # @param N Opaque sky cover in   tenths (0- no cover, 10- completely covered)
    # @param t_air air temperature in degree Celsius
    # @param t_dp dew point temperature in degree Celsius (-25°C + 25°C)
    # @return  sky temperature in degree Celsius
    def get_temperature2(self, N,  t_air, t_dp):
        t_air += 273.15

        # get sky emissivity
        sky_emissivity = self.emissivity(N, t_dp)

        # Calculate horizontal IR  radiation in W/m^2
        horizontal_IR = sky_emissivity*self.sigma*(t_air**4)

        # Calculate sky temperature and convert it into Celsius
        sky_temperature = ((horizontal_IR/self.sigma)**0.25)-273.15
        # return sky temperature
        return sky_temperature

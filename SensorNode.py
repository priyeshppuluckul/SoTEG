

## @package SensorNode
# This package simulates the working of LoRaWAN Sensor Node transmitting 6 bytes at DR 5 data rate.
# Emprical values of energy consumption, lekage current are used. In addition, the operation of the
# Power Management Unit (PMU) is approximated using a model derived from the empirical measurements.
# Refer ./COPYING.txt for terms and conditions.
#

from datetime import datetime
from DBManager import DataBaseMgmt
import pandas as pd

class SensorNode:
    ## Entry point of the package
    # Units of measurements, unless otherwise specified:
    # Capacitance- mF
    # Current - mA
    # Voltage- V
    # Resistance- Ohm
    # Power- mW
    # Energy - mJ
    # Temperature - °C

    def __init__(self):
        ## @var  baseEnergy
        # Base energy required in the capacitor, ie., the energy stored when charged upto VL
        self.baseEnergy = 27.54
        ## @var accEnergy
        # Total accumulated energy in the capacitor
        self.accEnergy = 0.0
        ## @var 
        # Total generated energy overtime
        self.totalGeneratedEnergy = 0
        ## @var accEnergyPerSample
        # Energy accumulated between two data samples
        self.accEnergyPerSample = 0.0
        ## @var nodeConsumption
        # Energy consumption of the node, ecmperically estimated
        self.nodeConsumption = 66.29
        ## @var lastSamplingTime
        # Sampling point of the last data point, required to calculate the energy generaated between samples
        self.lastSamplingTime = datetime.strptime('2016-04-06 21:26:27', '%Y-%m-%d %H:%M:%S')
        ## @var txPackets
        # Total number of packets transmitted
        self.txPackets = 0

        ## @var Cstore
        # Capacitance of the energy storage buffer
        self.Cstore = 17
        ## @var Ileakage
        # Leakage current of the supercapacitor
        self. Ileakage = 0.002
        ## @var GardenIDFile
        # path to the file containing all the garden IDs (optional)
        self.GardenIDFile = ""
    
    ## Resets and brings the system to the initial state
    def resetSystem(self):
        self.txPackets = 0
        self.accEnergy = 0.0
        self.accEnergyPerSample = 0.0
        self.totalGeneratedEnergy = 0.0

    
    ## Model of the PMU based on empirical measurements
    # @param dT Temperature difference across TEG
    # return average charging power estimated
    def pmuModel(self, dT):
        pAvg = 0.0
        if dT >= 0.625:
            pAvg = abs(0.0366*(dT**1.8830))

        return pAvg

    
    ## Updated energy values of the system
    def updateEnergy(self, energy):
        self.accEnergy += energy
        self.totalGeneratedEnergy += energy
        self.accEnergyPerSample += energy

 
    ## Update energy lost through leakge of supercap
    # @warning Updates happen only after each sample in the datafile is read,
    # not instantaneosuly
    #
    # @param timeDelta Time detla between two  samples, used ti calculate energy
    def updateLeakageEnergy(self, timeDelta):
        # deduct, leakage energy in mJ but make sure it is not less than 0 mJ
        eLeakage = ((self.Ileakage*timeDelta)**2)/(2*self.Cstore)
        self.accEnergy -= eLeakage
        if self.accEnergy <= 0.0:
            self.accEnergy = 0.0


    ## Voltage monitoring circuit
    # Periodically monitor the energy thresholds and decide
    # if a packet can be transmitted. Again, this is not instantaneous,
    # but happens only after a sample is read
    def checkThresholds (self):
        if (self.accEnergy-self.baseEnergy-self.nodeConsumption) >= 0.0:
            return True

        return False

    ## Transmit a packet when enough energy is available in Cstore
    # Energy of a single packet transmission is reduced from the total stored energy   
    def transmitPacket(self):
        while(self.checkThresholds()):
            self.txPackets += 1
            self.accEnergy -= self.nodeConsumption

    ## Process the data samples and simulates the execution of the node
    # @param tableData The data samples for which the node performance has to be simulated.
    #       row [0]- sampling time in the specified formt
    #       tableData [1]- temperature difference across the TEG
    # @return total number of packtes transmitted for the given sample run
    def processData(self, tableData):
        for row in tableData:
            try:
                timeDelta = row[1] - self.lastSamplingTime
                timeDeltaSeconds = int(round(timeDelta.total_seconds()))
                self.lastSamplingTime = row[0]

                if (timeDeltaSeconds >= 86400):
                    self.accEnergy = 0.0

                self.txPackets = 0
                self.accEnergyPerSample = 0.0
                self.updateEnergy(self.pmuModel(row[1])*float(timeDeltaSeconds))
                self.updateLeakageEnergy(timeDeltaSeconds)
                self.transmitPacket()

            except Exception as e:
                print("Error!! + {}".format(e))

        return self.txPackets

'''
if __name__ == '__main__':
    sn = SensorNode()
    # call sn.processData() with your data as input
'''

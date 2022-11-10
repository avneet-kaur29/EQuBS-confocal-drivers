# @Author: Eric Rosenthal
# @Date:   2022-02-22T16:41:43-08:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T15:41:34-07:00



"""
Fake signal generator driver for demonstration purposes.

Author: Jacob Feder
Date: 12/27/2021
"""
import logging
logger = logging.getLogger(__name__)

class SigGen:
    def __init__(self):
        self.output_en = False
        self._amplitude = 0.0
        self._frequency = 100e3

    def frequency(self):
        return self._frequency

    def set_frequency(self, value):
        """Change the frequency (Hz)"""
        if value < 100e3 or value > 10e9:
            raise ValueError('Frequency must be in range [100kHz, 10GHz].')
        self._frequency = value
        logger.info(f'Set frequency to {self._frequency} Hz')

    def amplitude(self):
        return self._amplitude

    def set_amplitude(self, value):
        """Change the amplitude (dBm)"""
        if value < -30 or value > 10:
            raise ValueError('Amplitude must be in range [-30dBm, 10dBm].')
        self._amplitude = value
        logger.info(f'Set amplitude to {self._amplitude} dBm')

    def calibrate(self):
        logger.info('Sig-gen calibration succeeded.')

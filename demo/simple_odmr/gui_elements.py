"""
Example GUI elements for an ODMR application.

Copyright (c) 2021, Jacob Feder
All rights reserved.

This work is licensed under the terms of the 3-Clause BSD license.
For a copy, see <https://opensource.org/licenses/BSD-3-Clause>.
"""
from functools import partial
from importlib import reload

import numpy as np
import spin_measurements
from nspyre import DataSink
from nspyre import LinePlotWidget
from nspyre import FlexLinePlotWidget
from nspyre import ExperimentWidget
from nspyre import ParamsWidget
from nspyre import ProcessRunner
from nspyre import SaveWidget
from pyqtgraph import SpinBox
from pyqtgraph.Qt import QtWidgets


class ODMRWidget(ExperimentWidget):
    def __init__(self):
        params_config = {
            'start_freq': {
                'display_text': 'Start Frequency',
                'widget': SpinBox(
                    value=3e9,
                    suffix='Hz',
                    siPrefix=True,
                    bounds=(100e3, 10e9),
                    dec=True,
                ),
            },
            'stop_freq': {
                'display_text': 'Stop Frequency',
                'widget': SpinBox(
                    value=4e9,
                    suffix='Hz',
                    siPrefix=True,
                    bounds=(100e3, 10e9),
                    dec=True,
                ),
            },
            'num_points': {
                'display_text': 'Number of Scan Points',
                'widget': SpinBox(value=100, int=True, bounds=(1, None), dec=True),
            },
            'iterations': {
                'display_text': 'Number of Experiment Repeats',
                'widget': SpinBox(value=5, int=True, bounds=(1, None), dec=True),
            },
            'dataset': {
                'display_text': 'Data Set',
                'widget': QtWidgets.QLineEdit('odmr'),
            },
        }

        super().__init__(params_config, 
                        spin_measurements,
                        'SpinMeasurements',
                        'odmr_sweep',
                        title='ODMR')

# all that's really needed in this file is the "ODMRWidget" class
# below is provided just for demonstration purposes

class FlexLinePlotWidgetWithSomeDefaults(FlexLinePlotWidget):
    """This is meant to give the user some hints as to how to use the FlexSinkLinePlotWidget.
    Generally there should be no need to subclass it in this way."""
    def __init__(self):
        super().__init__()
        self.add_plot('avg', 'mydata', '', '', 'Average')
        self.add_plot('latest', 'mydata', '-1', '', 'Average')
        self.add_plot('first', 'mydata', '0', '1', 'Average')
        self.add_plot('latest_10', 'mydata', '-10', '', 'Average')
        self.hide_plot('first')
        self.hide_plot('latest_10')
        self.datasource_lineedit.setText('odmr')


class CustomODMRWidget(QtWidgets.QWidget):
    """Qt widget subclass that generates an interface for running ODMR scans.
    It contains a set of boxes for the user to enter the experimental parameters,
    and a button to start the scan.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle('ODMR')

        # stacked layout of spinboxes that allow the user to enter experimental parameters
        self.params_widget = ParamsWidget(
            {
                'start_freq': {
                    'display_text': 'Start Frequency',
                    'widget': SpinBox(
                        value=3e9,
                        suffix='Hz',
                        siPrefix=True,
                        bounds=(100e3, 10e9),
                        dec=True,
                    ),
                },
                'stop_freq': {
                    'display_text': 'Stop Frequency',
                    'widget': SpinBox(
                        value=4e9,
                        suffix='Hz',
                        siPrefix=True,
                        bounds=(100e3, 10e9),
                        dec=True,
                    ),
                },
                'num_points': {
                    'display_text': 'Number of Scan Points',
                    'widget': SpinBox(value=100, int=True, bounds=(1, None), dec=True),
                },
                'iterations': {
                    'display_text': 'Number of Experiment Repeats',
                    'widget': SpinBox(value=20, int=True, bounds=(1, None), dec=True),
                },
                'dataset': {
                    'display_text': 'Data Set',
                    'widget': QtWidgets.QLineEdit('odmr'),
                },
            }
        )

        # Qt button widget that takes an ODMR scan when clicked
        sweep_button = QtWidgets.QPushButton('Sweep')
        # the process running the sweep function
        self.sweep_proc = ProcessRunner()
        # start run sweep_clicked on button press
        sweep_button.clicked.connect(self.sweep_clicked)

        # Qt button widget that takes an ODMR scan when clicked
        stop_button = QtWidgets.QPushButton('Stop')
        # start run sweep_clicked on button press
        stop_button.clicked.connect(self.stop)
        # stop the process if the widget is destroyed
        self.destroyed.connect(partial(self.stop))

        # Qt layout that arranges the params and button vertically
        params_layout = QtWidgets.QVBoxLayout()
        params_layout.addWidget(self.params_widget)
        params_layout.addStretch()
        params_layout.addWidget(stop_button)
        params_layout.addWidget(sweep_button)

        self.setLayout(params_layout)

    def sweep_clicked(self):
        """Runs when the 'sweep' button is pressed."""

        # reload the spin measurements module at runtime in case any changes were made to the code
        reload(spin_measurements)

        # create an instance of the ODMR class that implements the experimental logic.
        spin_meas = spin_measurements.SpinMeasurements()

        # run the sweep function in a new thread.
        self.sweep_proc.run(
            spin_meas.odmr_sweep,
            self.params_widget.dataset,
            self.params_widget.start_freq,
            self.params_widget.stop_freq,
            self.params_widget.num_points,
            self.params_widget.iterations
        )

    def stop(self):
        """Stop the sweep process."""
        self.sweep_proc.kill()

class CustomODMRPlotWidget(LinePlotWidget):
    def __init__(self):
        super().__init__(
            title='ODMR @ B = 15mT', xlabel='Frequency (GHz)', ylabel='PL (counts)'
        )

    def setup(self):
        self.add_plot('odmr')
        self.plot_widget.setYRange(-100, 5100)
        self.sink = DataSink('odmr')
        self.sink.start()

    def teardown(self):
        self.sink.stop()

    def update(self):
        if self.sink.pop():
            # update the plot
            avg_data = np.average(np.stack(self.sink.datasets['mydata']), axis=0)
            freqs = avg_data[0]
            counts = avg_data[1]
            self.set_data('odmr', freqs, counts)

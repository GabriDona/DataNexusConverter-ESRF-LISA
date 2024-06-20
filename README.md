DataNexusConverter 
================================

Overview
--------
Welcome to the Data Nexus Converter application! This tool is designed to simplify and streamline the process of converting `.dat` files into Nexus (`.nx5`) format. It provides a user-friendly interface for loading configuration files, selecting data files, and performing conversions efficiently. This program works in conjunction with ROIMaster (repository path [a link](https://github.com/GabriDona/ROIMaster-ESRF-LISA)) With the help of the Data Nexus Converter, it is possible to create files compatible with the ROIMaster application. ROIMaster allows for very efficient retrospective analysis.

Features
--------
- Load Configuration Files: Easily import and view energy configuration files.
- Select Data Files: Choose `.dat` files for conversion.
- Convert Files: Convert selected `.dat` files into Nexus (`.nx5`) format with a single click.
- Clear Selections: Clear the list of selected files to start fresh.
- User Feedback: Get real-time feedback on the process and file paths.

Requirements
------------
- Python 3.x
- Required Libraries:
  - tkinter
  - numpy
  - pyglet
  - PIL (Pillow)
  - customtkinter
  - readingfunct2 (custom module)
  - h5py

Installation
------------
1. Clone the repository or download the source code.

2. Install the required libraries:

 - pip install tk
 - pip install numpy
 - pip install --upgrade --user pyglet
 - pip install pillow
 - pip3 install customtkinter
 - pip install h5py

 
The Data Nexus Converter is an application that allows converting 
data files into the Nexus format, offering an intuitive user interface 
and advanced features to enhance workflow. In particular given a '.dat'
file and '.edf' files the program builds a '.nx5' file with the following 
groups:
1. Entry: This is the main group within the Nexus file. It contains all the information related to the dataset. 

2. Instrument: Contains information about the instruments used to collect the data, such as detectors and monochromators.

3. NXDetector Groups (I0_Eh1, I0_Eh2, IR_Eh2, IX_Eh2, I1_Eh2, Fluorescence): These are specific groups for the various detectors used in the experiment.

4. NXMonochromator (Monochromator): This group contains information about the monochromator used, such as the type of crystal.

5. NXData Groups (I0 EH1, I1 EH2, I0 EH2, Reference, Electrons, Fluo_XX): These are groups that contain the actual data, divided by detector type or measurement operation. For example, reference data is stored in the 'Reference' group, while fluorescence data is divided into separate groups named 'Fluo_XX', where 'XX' represents the index of the fluorescence data.

The Nexus file created will also contain metadata and attributes associated with each group and dataset, which may include information such as measurement units, time axis, and other details about the experiment and collected data.



Usage
------------
1. Start the application by running the `DataNexusConverter.py` file.

2. Click on "Load Config" to import an energy configuration, If the energy 
   configuration file is read successfully, the configuration details 
   will appear on the screen. The configuration file must contain in the
   following order: atomic number (Z), the edge and the Bragg expression.

3. Click on "Open file" to select the `.dat` files to convert.
   Pay attention, only '.dat' files will be correctly read.
   Also, please ensure that the '.dat' file is located in the
   same folder as the corresponding Xia '.edf' files.



4. Click on "Convert" to start the conversion.

5. Use the "Clear" button to clear selected files.
6. Use the "QUIT" button to exit the application.


Contact
-------
For any inquiries or issues, please contact the project maintainer at gabriele.donati11@studio.unibo.it.
## Author

- Gabriele Donati


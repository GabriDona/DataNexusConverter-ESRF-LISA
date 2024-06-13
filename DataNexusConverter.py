import os
from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import importlib.machinery
import customtkinter
import readingfunct2 as rdf2
import numpy as np
from numpy import radians, sin

# Initialize the main window
root = Tk()
root.geometry("330x380")
root.config(bg='white')
root.resizable(False, False)
root.title("Data Nexus Converter")

# Define frames
titleframe = Frame(root, background="white", height=100)
tableframe = Frame(root, background="white", height=200)
buttonframe = Frame(root, background="white", height=100)
exitframe = Frame(root, background="white", height=100)

titleframe.pack(side='top', fill='x')
tableframe.pack(side='top', fill='x')
buttonframe.pack(side='top', fill='x')
exitframe.pack(side='top', fill='x')

# Load and display the title image
image = Image.open("programXas/convertertitle.png")
tk_image = ImageTk.PhotoImage(image)
label = Label(titleframe, image=tk_image)
label.pack()

# Constants and Variables
a0 = 5.4185 * 1.00202  # Constant
factorDict = {'111': 20560.4204, '311': 10737.3294, '333': 31122.9881}

# String Variables
calibElText = StringVar(value='n.a.')
calibShellText = StringVar(value='n.a.')
eBraggText = StringVar(value='n.a.')
configPathText = StringVar(value='n.a.')
feedbacktext = StringVar(value=('***************************************************\n'
                                '*  Welcome to LISA 4 NeXus\n'
                                '*\n'
                                '*  Initializing...\n'
                                '*  Fast and efficient file conversion\n'
                                '*  to Nexus format.\n'
                                '*  Ready to streamline your workflow.\n'
                                '*\n'
                                '*  © 2024 Gabriele Donati\n'
                                '***************************************************\n'
                                '\n -> Please, Click on button "Load Config" to input the energy configuration file'))

# Scrollable Frame Class
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self, *args, **kwargs, bg='white', border=0)
        scrollbar = customtkinter.CTkScrollbar(self, command=canvas.yview)
        self.scrollable_frame = Frame(canvas, bg='white')

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

lbl7Frame = ScrollableFrame(tableframe, width=310, height=50)
lbl7Frame.pack()
customtkinter.CTkLabel(lbl7Frame.scrollable_frame, textvariable=feedbacktext, anchor='w', wraplength=310, justify='left').pack()

# Functions
def loadConfig():
    global CalibEl, CalibEdge, eBraggExp, openConfig
    configFile = filedialog.askopenfilename(title='Choose a configuration file')
    myvars = importlib.machinery.SourceFileLoader('myvars', configFile).load_module()
    CalibEl = myvars.CalibElZ
    CalibEdge = myvars.CalibEdge
    eBraggExp = myvars.eBraggExp
    calibElText.set(str(CalibEl))
    calibShellText.set(CalibEdge)
    eBraggText.set(str(eBraggExp))
    configPathText.set(configFile)
    openConfig = True
    feedbacktext.set(f'->The configuration file you have imported is the following:\n{configFile}\n'
                     f'-> Your parameters are:\n Z = {CalibEl}\n Edge = {CalibEdge}\n BraggExp = {eBraggExp}\n'
                     '-> Please, Click on button "Open File" to insert the .dat files you want to convert to Nexus')

def selected_file():
    file_paths = filedialog.askopenfilenames(filetypes=[("DAT files", "*.dat")])
    pathstr = '->Importing:\n'
    for file_path in file_paths:
        pathstr += f'{os.path.basename(file_path)}\n'
        selected_files.append(file_path)
    feedbacktext.set(pathstr)

def clear_file():
    selected_files.clear()
    feedbacktext.set(('***************************************************\n'
                      '*  Welcome to LISA 4 NeXus\n'
                      '*\n'
                      '*  Initializing...\n'
                      '*  Fast and efficient file conversion to Nexus format.\n'
                      '*  Ready to streamline your workflow.\n'
                      '*\n'
                      '*  © 2024 Gabriele Donati\n'
                      '***************************************************\n'
                      '\n -> Please, Click on button "Load Config" to input the energy configuration file'))

def convert_file():
    pathstr = '->Importing:\n'
    exporting = ''
    for file_path in selected_files:
        datfile, metadata = rdf2.read_dat(file_path)
        edf_data = rdf2.read_Xias2(metadata)
        icr, ocr = rdf2.icr_ocr(metadata)
        exporting += f'{os.path.basename(file_path).rstrip(".dat")}.nx5\n'
        pathstr += f'{os.path.basename(file_path)}\n'
        nexus_file = os.path.splitext(os.path.basename(file_path))[0] + ".nx5"
        with rdf2.h5py.File(nexus_file, "w") as f:
            factor = factorDict[metadata['crystal']]
            eBraggTheo = rdf2.calcEBragg(CalibEl, CalibEdge, metadata['crystal'], a0)
            th0 = eBraggTheo - eBraggExp
            EBraggEnergy = factor / a0 / sin(radians((datfile['ebragg'] + th0) / 800000.0))

            nxentry = rdf2.makeGroup(f, 'Entry', 'NXentry', time=metadata['data'].isoformat())
            nxinstrument = rdf2.makeGroup(nxentry, 'Instrument', 'NXInstrument')

            nxI0EH1 = rdf2.makeGroup(nxinstrument, 'I0_Eh1', 'NXDetector')
            nxI0EH2 = rdf2.makeGroup(nxinstrument, 'I0_Eh2', 'NXDetector')
            nxIREH2 = rdf2.makeGroup(nxinstrument, 'IR_Eh2', 'NXDetector')
            nxIXEH2 = rdf2.makeGroup(nxinstrument, 'IX_Eh2', 'NXDetector')
            nxI1EH2 = rdf2.makeGroup(nxinstrument, 'I1_Eh2', 'NXDetector')
            nxFLUO = rdf2.makeGroup(nxinstrument, 'Fluorescence', 'NXDetector')
            nxmonochromator = rdf2.makeGroup(nxinstrument, 'Monochromator', 'NXMonochromator', miller=metadata['crystal'])

            I0EH1Data = rdf2.makeDataset(nxI0EH1, 'counts', datfile.loc[:, 'I0_eh1'], units='counts', signal=1, axes=['energy'])
            I1EH2Data = rdf2.makeDataset(nxI1EH2, 'counts', datfile.loc[:, 'I1_eh2'], units='counts', signal=1, axes=['energy'])
            I0EH2Data = rdf2.makeDataset(nxI0EH2, 'counts', datfile.loc[:, 'I0_eh2'], units='counts', signal=1, axes=['energy'])
            IREHRData = rdf2.makeDataset(nxIREH2, 'elettroni', datfile.loc[:, 'IR_eh2'], units='counts', signal=1, axes=['energy'])
            IXEH2Data = rdf2.makeDataset(nxIXEH2, 'riferimento', datfile.loc[:, 'IX_eh2'], units='counts', signal=1, axes=['energy'])
            sourceEnergy = rdf2.makeDataset(nxmonochromator, 'energy_corretta', EBraggEnergy, units='keV')
            eBragg = rdf2.makeDataset(nxmonochromator, 'eBragg', datfile.loc[:, 'ebragg'].values, units='motor steps')
            channel = rdf2.makeDataset(nxFLUO, 'channels', np.arange(0, len(edf_data[1].columns)))

            nxdataI0_EH1 = rdf2.makeGroup(nxentry, 'I0 EH1', 'NXdata')
            rdf2.makeLink(nxI0EH1, I0EH1Data, nxdataI0_EH1.name + '/counts')
            nxdataI1_EH2 = rdf2.makeGroup(nxentry, 'I1 EH2', 'NXdata')
            rdf2.makeLink(nxI1EH2, I1EH2Data, nxdataI1_EH2.name + '/counts')
            nxdataI0_EH2 = rdf2.makeGroup(nxentry, 'I0 EH2', 'NXdata')
            rdf2.makeLink(nxI0EH2, I0EH2Data, nxdataI0_EH2.name + '/counts')
            nxdata_Ref = rdf2.makeGroup(nxentry, 'Reference', 'NXdata')
            rdf2.makeLink(nxIXEH2, IXEH2Data, nxdata_Ref.name + '/counts')
            nxdataElectrons = rdf2.makeGroup(nxentry, 'Electrons', 'NXdata')
            rdf2.makeLink(nxIREH2, IREHRData, nxdataElectrons.name + '/counts')

            for i in edf_data.keys():
                if edf_data[i].values.sum() > 100:
                    text_i = f'0{i}' if i < 10 else str(i)
                    nxFLUO_i = rdf2.makeGroup(nxFLUO, f'Fluo_{text_i}', 'NXDetector')
                    fluodata = rdf2.makeDataset(nxFLUO_i, 'counts', edf_data[i].values, units='counts', signal=1, axes=['energy', 'channels'])
                    icr_dat = rdf2.makeDataset(nxFLUO_i, 'icr', icr.loc[:, i], units='counts', axes=['energy'])
                    ocr_dat = rdf2.makeDataset(nxFLUO_i, 'ocr', ocr.loc[:, i], units='counts', axes=['energy'])
                    nxdatafluo = rdf2.makeGroup(nxentry, f'Fluo_{text_i}', 'NXdata')
                    rdf2.makeLink(nxFLUO_i, fluodata, nxdatafluo.name + '/counts')

    pathstr += '->Exporting:\n'
    feedbacktext.set(pathstr + exporting)

# Selected files list
selected_files = []

# Buttons
btn1 = Button(buttonframe, text='Load Config', width=10, command=loadConfig)
btn1.grid(column=0, row=0, padx=15, pady=5)

btn2 = Button(buttonframe, text='Open file', width=10, command=selected_file)
btn2.grid(column=1, row=0, padx=15, pady=5)

btn3 = Button(buttonframe, text='Convert', width=10, command=convert_file)
btn3.grid(column=2, row=0, padx=15, pady=5)

btn4 = Button(exitframe, text='QUIT', width=15, borderwidth=3, command=quit)
btn4.grid(column=0, row=1, columnspan=2, padx=40, pady=10)

btn5 = Button(exitframe, text='Clear', width=15, borderwidth=3, command=clear_file)
btn5.grid(column=2, row=1, columnspan=2, padx=10, pady=10)

root.mainloop()

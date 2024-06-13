import pandas as pd
import h5py
import numpy as np
import os
import re
import EdfFile as EF
from datetime import datetime
import matplotlib.pyplot as plt
import math
from xraylib import K_SHELL, L3_SHELL, L2_SHELL, L1_SHELL, EdgeEnergy
 

class DatFile:
    def __init__(self, Command, Date, Directory, Energy, Root, Xtal):
        self.Command = Command
        self.Data = None
        self.Date = Date
        self.Directory = Directory
        self.Energy = np.round(Energy, 3)
        self.EdfPaths = None
        self.Index = None
        self.NChannels = 0
        self.NPoint = 0
        self.Shape = 0
        self.Range = None
        self.Root = Root

        if Xtal < 0:
            self.Xtal = [1, 1, 1]
        else:
            self.Xtal = [3, 1, 1]

    def AddData(self, Data):
        self.Data = Data
        if self.Command == 'mesh':
            self.Index = list(Data.columns[0: 2])
            self.Range = [Data.iloc[:, 0].max()-Data.iloc[:, 0].min(), Data.iloc[:, 1].max()-Data.iloc[:, 1].min()]
        else:
            self.Index = list(Data.columns[0])
            self.Range = [Data.iloc[:, 0].max()-Data.iloc[:, 0].min()]

        self.NPoint = Data.shape[0]
        self.Shape = [len(np.unique(Data.iloc[:, 0])), len(np.unique(Data.iloc[:, 1]))]
        self.Data.set_index(self.Index, inplace = True)

    def FindEdf(self, path = None):
        if path is None:
            path = self.Directory
            
        files = os.listdir(path)
        filepaths = []
        for f in files:
            if (self.Root in f) and (f.endswith('edf')):
                filep = os.path.join(path, f)
                filepaths += [filep]

        filepaths.sort()
                
        self.EdfPaths = filepaths

    def AddEdfPath(self, path):
        if type(path) ==  str:
            self.EdfPaths += [path]
        
        elif type(path) == list:
            self.EdfPaths += path
            
                  

def read_Xias2(meta):
    
    
    XiaSpectra = {}
	
    # Leggi i dati dai file .edf e costruisci il dizionario XiaSpectra
    for path in meta['edf_file']:
        if 'xiast' not in path:
            Xia = int(re.findall(r'\d{2}', re.findall(r'xia\d{2}', path)[0])[0])
            EdfFile = EF.EdfFile(path)
            NumImages = EdfFile.GetNumImages()
            if NumImages > 0:
                Spectrum = EdfFile.GetData(0)
                Spectrum = pd.DataFrame(Spectrum)
                XiaSpectra[Xia] = Spectrum
                
    return XiaSpectra

            


def read_Xiast(meta):
    """Read XiaSt edf file, the data contains detector statistics: [#Xia, Tot_events, ICR, OCR, LiveT, DeadT% ...]
    Args:
        meta: dat file metadata imported with read_dat
    Returns:
        XiaSt: dataframe with XiaSt statistics
    """
   
    path_xiast = [percorso for percorso in meta['edf_file'] if "xiast" in percorso][0]
    EdfFile_xia = EF.EdfFile(path_xiast)
    NumImages = EdfFile_xia.GetNumImages()

    if NumImages > 0:
        XiaSt = EdfFile_xia.GetData(0)
        XiaSt = pd.DataFrame(XiaSt)
        
    return XiaSt      



def read_dat(path: str):
    if path.endswith('dat'):
        head_pos = None
        time_info = None
        crystall_info = None
        data_info = None
        filename = os.path.basename(path)
        filename = filename.split(".")[0]
        fluofolder = os.path.dirname(path) + '\\fluo'       

        with open(path, 'r') as f:
            for index, line in enumerate(f):
                if head_pos is None and '#L' in line:
                    head_pos = index
                elif '#D' in line:
                    data_info= datetime.strptime(line[3:-1], "%a %b %d %H:%M:%S %Y")
                elif '#T' in line:
                    time_info = line.split()
                elif '#P4' in line:
                    crystall_info = line.split()

                if head_pos is not None and time_info is not None and crystall_info is not None:
                    break

        if head_pos is None:
            raise ValueError("Error problem n_1.")

        dat_file = pd.read_csv(path, header=head_pos-1, sep='\s+', engine='python')
        dat_file.columns = dat_file.columns[1:].tolist() + ['None']
        dat_file = dat_file.dropna(axis=1)
        dat_file.set_index('energy', inplace=True)
        if float(crystall_info[4]) < 0:
            cri=111 #prima era [1,1,1]
        else:
            cri=311
            
        edf_name_tot = os.listdir(fluofolder)
        selected_files = [file for file in edf_name_tot if os.path.basename(file).startswith(filename)]
        edf_path = [f"{fluofolder}\\{file}" for file in selected_files]
  
        
        
        
        metadates = {
            'time': float(time_info[1]) if time_info else None,
            'data' : data_info,
            'crystal': str(cri) if crystall_info else None,
            'directory': os.path.dirname(path),
            'edf_file': edf_path
        }
        
    read_Xiast(metadates)
    return dat_file, metadates


def lista_percorsi_file(percorso_cartella):
    percorsi_file = []
    for nome_file in os.listdir(percorso_cartella):
        percorso_file = os.path.join(percorso_cartella, nome_file)
        os.path.isfile(percorso_file)
        percorsi_file.append(percorso_file)
        nomi_file = [os.path.basename(percorso) for percorso in percorsi_file]
    return nomi_file


def calcEBragg(El, Edge, Xtal, a0):
    Shells = {'K': K_SHELL,
              'L3': L3_SHELL,
              'L2': L2_SHELL,
              'L1': L1_SHELL             
             }
    EdgeE = EdgeEnergy(El, Shells[Edge])*1000
    ene1ang = 12398.42014541
    stepEnc = 0.0000000218166156499

    XtalD = {'111': math.sqrt(3),
             '311': math.sqrt(11)}
    
    d =  a0/XtalD[Xtal]
    conv = ene1ang/(2*d)
    mono = math.asin(conv/EdgeE)
    ebragg = int(round(mono/stepEnc))
    return ebragg

factorDict = {'311': 20560.4204,
              '111': 10737.3294,
              '333': 31122.9881}

a0 = 5.4185*1.00202
global openConfig
openConfig = False



def makeFile(filename, **attr):
    """
    create and open an empty NeXus HDF5 file using h5py
    
    Any named parameters in the call to this method will be saved as
    attributes of the root of the file.
    Note that **attr is a dictionary of named parameters.

    :param str filename: valid file name
    :param attr: optional keywords of attributes
    :return: h5py file object
    """
    obj = h5py.File(filename, "w")
    addAttributes(obj, attr)
    return obj

def makeGroup(parent, name, nxclass, **attr):
    """
    create a NeXus group
    
    Any named parameters in the call to this method 
    will be saved as attributes of the group.
    Note that **attr is a dictionary of named parameters.

    :param obj parent: parent group
    :param str name: valid NeXus group name
    :param str nxclass: valid NeXus class name
    :param attr: optional keywords of attributes
    :return: h5py group object
    """
    obj = parent.create_group(name)
    obj.attrs["NX_class"] = nxclass
    addAttributes(obj, attr)
    return obj

def makeDataset(parent, name, data = None, **attr):
    '''
    create and write data to a dataset in the HDF5 file hierarchy
    
    Any named parameters in the call to this method 
    will be saved as attributes of the dataset.

    :param obj parent: parent group
    :param str name: valid NeXus dataset name
    :param obj data: the data to be saved
    :param attr: optional keywords of attributes
    :return: h5py dataset object
    '''
    if data.all() == None:
        obj = parent.create_dataset(name)
    else:
        obj = parent.create_dataset(name, data=data)
    addAttributes(obj, attr)
    return obj

def makeLink(parent, sourceObject, targetName):
    """
    create an internal NeXus (hard) link in an HDF5 file

    :param obj parent: parent group of source
    :param obj sourceObject: existing HDF5 object
    :param str targetName: HDF5 node path to be created, 
                            such as ``/entry/data/data``
    """
    if not 'target' in sourceObject.attrs:
        # NeXus link, NOT an HDF5 link!
        sourceObject.attrs["target"] = str(sourceObject.name)
    parent._id.link(sourceObject.name.encode('utf-8'), targetName.encode('utf-8'), h5py.h5g.LINK_HARD)

def makeExternalLink(hdf5FileObject, sourceFile, sourcePath, targetPath):
    """
    create an external link from sourceFile, sourcePath to targetPath in hdf5FileObject

    :param obj hdf5FileObject: open HDF5 file object
    :param str sourceFile: file containing existing HDF5 object at sourcePath
    :param str sourcePath: path to existing HDF5 object in sourceFile
    :param str targetPath: full node path to be created in current open HDF5 file, 
                            such as ``/entry/data/data``
                            
    .. note::
       Since the object retrieved is in a different file, 
       its ".file" and ".parent" properties will refer to 
       objects in that file, not the file in which the link resides.

    .. see:: http://www.h5py.org/docs-1.3/guide/group.html#external-links
    
    This routine is provided as a reminder how to do this simple operation.
    """
    hdf5FileObject[targetPath] = h5py.ExternalLink(sourceFile, sourcePath)

def addAttributes(parent, attr):
    """
    add attributes to an h5py data item

    :param obj parent: h5py parent object
    :param dict attr: dictionary of attributes
    """
    if attr and type(attr) == type({}):
        # attr is a dictionary of attributes
        for k, v in attr.items():
            parent.attrs[k] = v
            
            
def icr_ocr(meta):
    st = read_Xiast(meta)
    print(st)
    icr = {}
    ocr = {}
    for i in range(0, st.shape[1], 6):
        xian = st.iloc[0, i]
        icr[xian] = st.iloc[:,i+2]
        ocr[xian] = st.iloc[:,i+3]
        
    return pd.DataFrame(icr), pd.DataFrame(ocr)
        
    
    

def get_groups_XIA(file):
    entry_group = file.get('Entry', {})
    pattern = re.compile(r'Fluo_(?:[0-9]|[1-9][0-9])$')
    return [name for name in entry_group.keys() if pattern.match(name)]

def integral(path:str, x:int = 0, y:int = 4096, DTCorr = False):
    try:
        with h5py.File(path, 'r') as file:
            groups = get_groups_XIA(file)
            integral_dict = {}
            I0_EH2 = file['Entry/I0 EH2/counts'][:]    
            energy = file['Entry/Instrument/Monochromator/energy'][:]
            corr = 1
            for group_n in groups:
                dati = file['Entry/'+ group_n + '/counts']
                ocr = file['Entry/Instrument/Fluorescence/'+ group_n +'/ocr'][:]
                icr = file[f'Entry/Instrument/Fluorescence/{group_n}/icr'][:]
                if DTCorr == True:
                    corr = icr/ocr
                integral_array = np.sum(dati[:, x:y], axis=1)/I0_EH2*corr
                #dividi per per I0_EH2
                integral_dict[int(re.findall('\d+', group_n)[0])] = integral_array.tolist()
                integral_data = pd.DataFrame(integral_dict).sort_index(axis = 1)
                integral_data.loc[:, 'energy'] = energy
                integral_data.set_index('energy', inplace= True)
            return integral_data
    except FileNotFoundError:
        print(f"Il file {path} non è stato trovato.")
    except Exception as e:
        print(f"Si è verificato un errore durante l'apertura del file: {e}")
    return pd.DataFrame()




def correction(data_,icr_,ocr_):
    row = data_.index
    icr_.index = row
    ocr_.index = row
       
    
    return data_*(icr_/ocr_)

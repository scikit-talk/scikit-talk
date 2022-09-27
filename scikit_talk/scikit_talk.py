import os
import csv
import regex as re
import numpy as np
import pandas as pd
import pylangacq
from speach import elan
import datetime

# ----------------------------------------------------------------------
# Preprocessor module for parsing Preprocessor module for parsing Preprocessor module for parsing
# ----------------------------------------------------------------------


def cha_to_dataframe(path_in, *path_out):
    """This method will be used to add two numbersss
        :param str path_in: The first number
        :param str path_out: The second number
        :returns: The sum of two numbers
        :rtype: str
    """

    data_cha = pd.DataFrame()
    for filename in os.listdir(path_in):
      if filename.endswith(".cha"):
          chatfile = pylangacq.read_chat(filename)
          chat_utterances=chatfile.utterances(by_files=False)
          for row in chat_utterances:
            data_cha = data_cha.append(pd.DataFrame({'speaker':row.participant, 'time':str(row.time_marks), 'utterance':str(row.tiers), 'source': path_in+filename}, index=[0]), ignore_index=True)
      else:
          continue

    data_cha[['begin','end']] = data_cha.time.str.split(r', ', 1, expand=True)
    data_cha = data_cha[['begin', 'end', 'speaker', 'utterance', 'source']]
    data_cha['begin'] = [re.sub(r'\(', "", str(x)) for x in data_cha['begin']]
    data_cha['end'] = [re.sub(r'\)', "", str(x)) for x in data_cha['end']]
    data_cha['utterance'] = [re.sub(r'^([^:]+):', "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r'^\s+', "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r'\s+$', "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r'\}$', "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r'^\"', "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r'\"$', "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r"^\'", "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r"\'$", "", str(x)) for x in data_cha['utterance']]
    data_cha['utterance'] = [re.sub(r'\\x15\d+_\d+\\x15', "", str(x)) for x in data_cha['utterance']]
    data_cha.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    data_cha.replace(r'None', np.nan, regex=True, inplace=True)
    data_cha.fillna(value=np.nan, inplace=True)
    data_cha['begin'] = pd.to_numeric(data_cha['begin'])
    data_cha['begin'] = pd.to_datetime(data_cha['begin'], unit='ms', errors='ignore')
    data_cha['begin'] = pd.to_datetime(data_cha['begin']).dt.strftime("%H:%M:%S.%f")#[:-3]
    data_cha['end'] = pd.to_numeric(data_cha['end'])
    data_cha['end'] = pd.to_datetime(data_cha['end'], unit='ms', errors='ignore')
    data_cha['end'] = pd.to_datetime(data_cha['end']).dt.strftime("%H:%M:%S.%f")#[:-3]

    if path_out:
        os.mkdir(''.join(path_out))
        data_cha.to_csv(''.join(path_out)+'data_cha.csv')
    return data_cha



def eaf_to_dataframe(path_in, *path_out):
    """
    This function reads .eaf files, transcriptions of speech that were produced in the ELAN format.
    The function takes the files, reads and appends them one by one, line by line, and returns one dataframe.
    The function takes two arguments: an input path (e.g. path_in) and an output path (e.g. path_out), where the latter is optional.
    If you only give the input path (path_in), the function returns a pandas dataframe object.
    If you give the optional output path (*path_out) as well, the function writes the dataframe into that, as a .csv file.
    path_in should be a string, pointing to a folder where .cha files are located. Example: path_in = '/folder/'
    *path_out should be a string, pointing to a folder where you want your dataset written. Example: path_out = '/folder/output/'
    You have to make this output directory yourself before calling the function.
    Overall, calling the function should look like the following:
    preprocessor.eaf_to_dataframe(path_in)
    OR
    preprocessor.eaf_to_dataframe(path_in, path_out)
    """
    data_eaf = pd.DataFrame([])
    for filename in os.listdir(path_in):
        if filename.endswith(".eaf"):
            eaf = elan.read_eaf(filename)
            for tier in eaf:
              for ann in tier:
                   data_eaf = data_eaf.append(pd.DataFrame({'begin': ann.from_ts, 'end' : ann.to_ts, 'speaker' : tier.ID, 'utterance' : ann.text, 'source': path_in+filename}, index=[0]), ignore_index=True)
        else:
            continue
    if path_out:
      data_eaf.to_csv(''.join(path_out)+'data_eaf.csv')
    return data_eaf



def ldc_to_dataframe(path_in, *path_out):
    """
    This function reads .txt files, transcriptions of speech that were produced in the LDC format.
    The function takes the files, reads and appends them one by one, line by line, and returns one dataframe.
    The function takes two arguments: an input path (e.g. path_in) and an output path (e.g. path_out), where the latter is optional.
    If you only give the input path (path_in), the function returns a pandas dataframe object.
    If you give the optional output path (*path_out) as well, the function writes the dataframe into that, as a .csv file.
    path_in should be a string, pointing to a folder where .cha files are located. Example: path_in = '/folder/'
    *path_out should be a string, pointing to a folder where you want your dataset written. Example: path_out = '/folder/output/'
    You have to make this output directory yourself before calling the function.
    Overall, calling the function should look like the following:
    preprocessor.ldc_to_dataframe(path_in)
    OR
    preprocessor.ldc_to_dataframe(path_in, path_out)
    """
    data_ldc = pd.DataFrame()
    for filename in os.listdir(path_in):
        if filename.endswith(".txt"):
          textfile = pd.DataFrame()
          textfile[['time_speaker', 'utterance']] = pd.read_table(filename, sep=':', header=None)
          textfile['source'] = path_in+filename
          data_ldc = data_ldc.append(textfile)
        else:
          continue
    meta_pattern = '^\#'
    filter = data_ldc['time_speaker'].str.contains(meta_pattern)
    data_ldc = data_ldc[~filter]
    data_ldc.reset_index(inplace=True, drop=True)
    data_ldc[['time','speaker']] = data_ldc.time_speaker.str.split(r'\s(?!.*\s)', 1, expand=True)
    data_ldc[['begin','end']] = data_ldc.time.str.split(r' ', 1, expand=True)
    data_ldc.drop(columns=['time_speaker', 'time'], inplace=True)
    data_ldc = data_ldc[['begin',  'end', 'speaker', 'utterance', 'source']]
    data_ldc['begin'] = pd.to_numeric(data_ldc['begin'])
    data_ldc['begin'] = pd.to_datetime(data_ldc['begin'], unit='s', errors='ignore')
    data_ldc['begin'] = pd.to_datetime(data_ldc['begin']).dt.strftime("%H:%M:%S.%f")#[:-3]
    data_ldc['end'] = pd.to_numeric(data_ldc['end'])
    data_ldc['end'] = pd.to_datetime(data_ldc['end'], unit='s', errors='ignore')
    data_ldc['end'] = pd.to_datetime(data_ldc['end']).dt.strftime("%H:%M:%S.%f")#[:-3]

    if path_out:
      data_ldc.to_csv(''.join(path_out)+'data_ldc.csv')
    return data_ldc

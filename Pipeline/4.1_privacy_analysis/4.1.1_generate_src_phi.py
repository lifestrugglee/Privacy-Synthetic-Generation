#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Based on the src_phi.pickle, collect the phi information from the synthetic text
to generate the ICD9 collect dict pickle file.
    
The function further check and convert the first name and last name into the final full name, 
which following HIPAA standard.

After the execution, please run the 4.1.3

Author: Patrick C.
Date: 2024-09-11
Version: 1.0

"""

import re, os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
import pandas as pd
import numpy as np
import json
from pathlib import Path
from glob import glob
from tqdm import tqdm
import pickle
import time

def writePickle(file_path, sth):
    # store list in binary file so 'wb' mode
    with open(file_path, 'wb') as fp:
        pickle.dump(sth, fp)

def loadPickle(file_path):
    # for reading also binary mode is important
    with open(file_path, 'rb') as fp:
        return pickle.load(fp)

import sys
sys.path.append("../privacy/")
import icd9_obj 
icd9obj = icd9_obj.ICD9_obj()
from HIPPA import HIPAA
hipaa = HIPAA()

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device, torch.cuda.device_count())

import spacy
# !python -m spacy download en_core_web_trf
spacy.prefer_gpu()
nlp = spacy.load('en_core_web_trf')


if __name__ == "__main__":
    newDir = os.path.join("./re_id_history/MIMIC_reid_val_record_20230704")
    contain_dict = {}
    # load all the mapping phi pickle files
    icd9_pickle_ls = [fn for fn in os.listdir(newDir) if '.pickle' in fn]

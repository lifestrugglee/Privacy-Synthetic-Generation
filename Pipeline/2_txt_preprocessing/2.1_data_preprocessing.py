#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script performs data preprocessing for the MIMIC III dataset.

Author: Patrick C
Date: 2024-09-11
Version: 1.0
"""


import os
import glob
import csv
from pathlib import Path
import random
import pandas as pd
from nltk.tokenize import sent_tokenize, RegexpTokenizer
from transformers import GPT2TokenizerFast
import re
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import shutil
import copy
import itertools

import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from utils import icd9_obj 
icd9obj = icd9_obj.ICD9_obj()


def extract_number_from_filename(filename):
    match = re.search(r'\d+', filename)
    if match:
        return int(match.group())
    else:
        return None
    
def remove_first_line(text):
    # Split the text into lines and exclude the first line
    lines = text.split('\n', 1)
    if len(lines) > 1:
        return lines[1]
    else:
        return ''

def contains_alphabetic(token):
    for c in token:
        if c.isalpha():
            return True
    return False

def normalise_text(text):
    output = []
    length = 0
    tokenizer = RegexpTokenizer(r'\w+')
    for sent in sent_tokenize(text):
        tokens = [token.lower() for token in tokenizer.tokenize(sent) if contains_alphabetic(token)]
        sent = " ".join(tokens)
        if len(sent) > 0:
            output.append(sent)

    return "\n".join(output)

def create_split_csv(folder_prefix, output_folder, icd9_dir_ls, isSource=False, isNormal=True, isCut=True, seed=42):
    csv_col_ls = ['Admission_Id', 'Three_Character_Labels', 'Full_Labels', 'Text']
    output_csv = os.path.join(output_folder, 'all.csv')
    
#     if os.path.exists(output_csv) is False:
    all_file_paths = []
    for icd9_abbr in icd9_dir_ls:
        all_file_paths += glob.glob(os.path.join(folder_prefix, icd9_abbr, '*.txt'))
    random.Random(seed).shuffle(all_file_paths)
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(csv_col_ls)

        for file_path in tqdm(all_file_paths):
            folder_name = os.path.basename(os.path.dirname(file_path))
            file_number = extract_number_from_filename(os.path.basename(file_path))
            with open(file_path, 'r', encoding='utf-8') as fr:
                if isSource: 
                    fr.readline()
                text = fr.read()


            if isNormal: text = normalise_text(text)
            input_id = tokenizer.encode(text.strip())#['input_ids']
            if isCut:
                if(len(input_id) > 4000): #1500
                    input_id=input_id[:4000] #1500
                    text = tokenizer.decode(input_id).strip()

            if(len(input_id)==0) or text.strip() == 'N/A':continue

            csv_writer.writerow([file_number, folder_name, folder_name, text])
    
    df = pd.read_csv(output_csv)
    idx_ls = df.index.to_list()
    
    train_idx, val_idx = train_test_split(idx_ls, test_size=0.3, random_state=seed)
    val_idx, test_idx = train_test_split(val_idx, test_size=0.5, random_state=seed)
    
    print("Total contains: ", len(idx_ls), " rows")
    print("Train contains: ", len(train_idx), " rows")
    print("Valid contains: ", len(val_idx), " rows")
    print("Test contains: ", len(test_idx), " rows")
    
    for csv_type, idx_ls in zip(['train', 'valid', 'test'], [train_idx, val_idx, test_idx]):
        output_csv = os.path.join(output_folder, f'{csv_type}.csv')

        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_col_ls)

            for idx in idx_ls:
                csv_writer.writerow(df.loc[idx].to_list())

def main(folder_prefix, isNormal = True, isCut = True, isSource=False):
    ls = []
    if isCut: ls.append('4k')
    if isNormal: ls.append('n')
    else: ls.append('un')
    appendix = '_' + '_'.join(ls)

    random_seed = 39
    # Create output folder if it doesn't exist
    output_folder = os.path.join(folder_prefix, f'output_csv{appendix}')
    os.makedirs(output_folder, exist_ok=True)
    create_split_csv(folder_prefix, output_folder, icd9obj.ICD9_ABBR_LS, isSource=isSource, isNormal=isNormal, seed=random_seed)

    print(f"CSV files have been created in the '{output_folder}' folder.")



NORMAL_4k = 'output_csv_4k_n'

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
if "[PAD]" not in tokenizer.get_vocab():
    tokenizer.add_tokens(["[PAD]"])
tokenizer.pad_token = "[PAD]"

if __name__ == "__main__":
    # Benchmark
    data_type_dict = {'deid': r'./data/MIMICIII_ori_nosp/',
                      'reid': r'./data/MIMIC_reid_val_record_20230704/', 
                    }

    for data_type, folder_prefix in data_type_dict.items():
        main(folder_prefix, isNormal=False, isSource=True)
        main(folder_prefix, isSource=True)

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

NORMAL_4k = 'output_csv_4k_n'

def getLeftone_out(ls):
    collect_ls = []
    for i in range(len(ls)-1):
        test = ls[i+1]
        valid = ls[i]
        tmp_ls = copy.deepcopy(ls)
        tmp_ls.pop(i)
        tmp_ls.pop(i)
        train = list(itertools.chain.from_iterable(tmp_ls))
        collect_ls.append((train, valid, test))

    test = ls[-1]
    valid = ls[0]
    tmp_ls = copy.deepcopy(ls)
    tmp_ls.pop(-1)
    tmp_ls.pop(0)
    train = list(itertools.chain.from_iterable(tmp_ls))
    collect_ls.append((train, valid, test))
    return collect_ls

def divide_into_ten_parts(data):
    n = len(data)
    # Compute the size of each piece
    piece_size = n // 10
    # Calculate the number of elements left over after dividing evenly
    remainder = n % 10
    
    pieces = []
    current_start = 0
    
    for i in range(10):
        # Add an extra element to some of the first 'remainder' pieces
        current_end = current_start + piece_size + (1 if i < remainder else 0)
        # Append the current piece to the result list
        pieces.append(data[current_start:current_end])
        # Move the start pointer
        current_start = current_end
    
    return pieces

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

def create_split_csv10(folder_prefix, output_folder, icd9_dir_ls, isSource=False, isNormal=True, isCut=True, seed=42):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    if "[PAD]" not in tokenizer.get_vocab():
        tokenizer.add_tokens(["[PAD]"])
    # Set the pad_token
    tokenizer.pad_token = "[PAD]"
    
    all_csv_file = os.path.join(folder_prefix, NORMAL_4k, 'all.csv')
    if os.path.exists(all_csv_file) is False:
        print('generating from source')
        all_file_paths = []
        for icd9_abbr in icd9_dir_ls:
            all_file_paths += glob.glob(os.path.join(folder_prefix, icd9_abbr, '*.txt'))

        random.Random(seed).shuffle(all_file_paths)

        col_ls = ['Admission_Id', 'Three_Character_Labels', 'Full_Labels', 'Text']
        all_ls = []

        for file_path in tqdm(all_file_paths):
            folder_name = os.path.basename(os.path.dirname(file_path))
            file_number = extract_number_from_filename(os.path.basename(file_path))
            with open(file_path, 'r', encoding='utf-8') as text_file:
                text = text_file.read()

            if isSource: text = remove_first_line(text) 
            if isNormal: text = normalise_text(text)

            input_id = tokenizer.encode(text.strip())#['input_ids']
            if isCut:
                if(len(input_id) > 4000): #1500
                    input_id=input_id[:4000] #1500
                    text = tokenizer.decode(input_id).strip()

            if(len(input_id)==0) or text.strip() == 'N/A':
                continue

            all_ls.append([file_number, folder_name, folder_name, text])
        df = pd.DataFrame(all_ls, columns=col_ls)
        df.to_csv(all_csv_file, index=False)
    else:
        df = pd.read_csv(all_csv_file)
        all_ls = [df.loc[idx].to_list() for idx in range(df.shape[0])]
    
    result = divide_into_ten_parts(all_ls)
    collect_ls = getLeftone_out(result)
    
    for i in tqdm(range(len(collect_ls))):
        sub_output_folder = os.path.join(output_folder, str(i+1))
        Path(sub_output_folder).mkdir(parents=True, exist_ok=True)
        training, valid, testing = collect_ls[i]
        for csv_type, val_ls in zip(['train', 'valid', 'test'], [training, valid, testing]):
            output_csv = os.path.join(sub_output_folder, f'{csv_type}.csv')
            with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Admission_Id', 'Three_Character_Labels', 'Full_Labels', 'Text'])
                for ls in val_ls:
                    csv_writer.writerow(ls)
        
#     return output_folder

def main(folder_prefix, isNormal = True, isCut = True, isSource=False):
    
    ls = []
    if isCut: ls.append('4k')
    if isNormal: ls.append('n')
    else: ls.append('un')
    appendix = '_' + '_'.join(ls)

    random_seed = 39
    # Create output folder if it doesn't exist
    output_folder = os.path.join(folder_prefix, f'output_csv{appendix}_10fold')
    if os.path.isdir(output_folder): os.system(f'rm -rf {output_folder}')
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    create_split_csv10(folder_prefix, output_folder, icd9obj.ICD9_ABBR_LS, isSource, isNormal, isCut, seed=random_seed)

    print(f"CSV files have been created in the '{output_folder}' folder.")
    return output_folder




tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
if "[PAD]" not in tokenizer.get_vocab():
    tokenizer.add_tokens(["[PAD]"])

tokenizer.pad_token = "[PAD]"

if __name__ == "__main__":
    root = r'./data/MIMIC3'

    data_type_ls = ['reid', 'deid']
    model_ls = [ 'gpt-4-0613', 'Mistral7b', 'gpt-35-turbo-a0301']
    gener_type_ls = ['one_shot_src', 'one_shot', 'keyword']

    for data_type in data_type_ls:
        for gener_type in gener_type_ls:
            for model in model_ls:
                print(f'{data_type} {gener_type} {model}')
                folder_prefix = os.path.join(root, f'src_{data_type}', 'output_csv_4k_n', gener_type, model )            
                main(folder_prefix)
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
sys.path.append("/home/privacy/")
import icd9_obj 
icd9obj = icd9_obj.ICD9_obj()

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "3"
import spacy
spacy.prefer_gpu()
nlp = spacy.load('en_core_web_trf')

# functions
def write2Log(msg):
    with open('collect_dict_os_src.log', 'a') as fw:
        try:
            fw.write(f"{str(msg)}\n")
        except:
            fw.write(f"{msg.encode('utf-8').strip()}\n")

def getFullName_ls(f_name_ls, l_name_ls, corpus, threshold = 3, isDebug=0):
    global isRecord
    # print((f_name_ls, l_name_ls, corpus, threshold , isDebug))
    f_name_lc_ls = [(corpus.find(name), len(name)) for name in f_name_ls]
    l_name_lc_ls = [(corpus.find(name), len(name)) for name in l_name_ls]
    
    isGotcha = 0
    full_name_ls = []
    for lc_f, len_f in f_name_lc_ls:
        for lc_l, len_l in l_name_lc_ls:
            inRange = abs(lc_f+len_f - lc_l) <= threshold or abs(lc_l + len_l - lc_f) <= threshold
#             print(inRange, abs(lc_f+len_f - lc_l), abs(lc_l + len_l - lc_f))
            if inRange:
                if lc_f < lc_l:
                    full_name = corpus[lc_f: lc_l+len_l]
                else:
                    full_name = corpus[lc_l: lc_f+len_f]
                
                full_name = full_name.strip()
                if ',' in full_name:
                    f_l_ls = full_name.split(',')
                    if len(f_l_ls) != 2: continue
                    tmp_l, tmp_f = f_l_ls
                    full_name = f'{tmp_l.strip()}, {tmp_f.strip()}'
                    
                    
                elif ' ' in full_name:
                    f_l_ls = full_name.strip().split(' ')
                    if len(f_l_ls) != 2: continue
                    tmp_f, tmp_l = f_l_ls
                    full_name = f'{tmp_l}, {tmp_f}'

                
                filter_result = [f for f in re.findall(r'((?!\w).)', full_name) \
                                 if f not in [',', ' ', '-', ';', ':', '(', ']']]
                
                if len(filter_result) > 0:
                    # add to log
                    isRecord = True
                    ls = ['-'*5, isRecord, 'filter_result', 'full_name = ', full_name, 'first_name_ls = ', f_name_ls, 'last_name_ls = ', l_name_ls, 'corpus = ', corpus]
                    for i in ls:
                        # print(i)
                        write2Log(i)
                        
                else:
                    re_result = re.findall(r'(\w+)', '(Peyton, Pittman')
                    if len(re_result) == 2:
                        full_name = ', '.join(re_result)
                        full_name_ls.append(full_name.strip())
                        isGotcha = 1

    return full_name_ls

# getFullName_ls(['Velma'], ['Walmsley'], "The patient was intubated endotracheally, had a central line placement in his RIJ, and was living in a facility named Velma's Walmsley Living Center in Panama City Beach, Florida.", 3, 0)
def getCollectLs(one_src_phi_dict, syn_sent_tokenls):
    collected_ls = []
    for phi_type, phi_val_ls in one_src_phi_dict.items():
    
        if phi_type == 'full_name':
            phi_ls = one_src_phi_dict['full_name']
            for full_name in phi_ls:
                l_n, f_n  = full_name.split(', ')
                for syn_token_ls, sent in syn_sent_tokenls: # checking
                    if l_n in syn_token_ls and f_n in syn_token_ls:
                        extracted_full_name = getFullName_byTokens([f_n], [l_n], [[syn_token_ls, sent],] )
                        if len(extracted_full_name) == 1 and full_name == extracted_full_name[0]:
                            collected_ls.append( (phi_type, full_name) )
                        elif len(extracted_full_name) > 1: raise ValueError(extracted_full_name)
        elif phi_type == 'first_name' or phi_type == 'last_name': continue
        else:
            for phi in phi_val_ls:
                
                for syn_token_ls,_ in syn_sent_tokenls:
                    if phi in syn_token_ls:
                        collected_ls.append( (phi_type, phi) )
                        break
    return collected_ls

# collect_ls = getCollectLs(src_phi_dict[icd9_abbr][src_fn], syn_sent_token_ls)

def getFullName_byTokens(first_name_ls, last_name_ls, sent_tokenls, isDebug=0):
    ls = []
    for tokenls, sent in sent_tokenls:
        got_f_name_ls = isIn(first_name_ls, sent)
        got_l_name_ls = isIn(last_name_ls, sent)
        if len(got_f_name_ls) > 0 and len(got_l_name_ls) > 0:
            # token level: double check the words is contained
            if any( '-' in n for n in got_f_name_ls) or any( '-' in n for n in got_l_name_ls):
                pass
            else:
                got_f_name_ls = isIn(got_f_name_ls, tokenls) 
                got_l_name_ls = isIn(got_l_name_ls, tokenls)
            if isDebug:
                print('getFullName_byTokens')
                print(tokenls)
                print(repr(sent))
                print(got_f_name_ls, got_l_name_ls)
                print('-'*5)
            tmp_full_name_ls = getFullName_ls(got_f_name_ls, got_l_name_ls,
                                              sent.replace('\n', ' ').replace('  ', ' '))
            if isDebug: print(f'FULL NAME -->', tmp_full_name_ls)
            if len(tmp_full_name_ls) > 0: ls += tmp_full_name_ls

    ls.sort()
    return ls

def check_date(dateLs):
    tmp_phi_ls = dateLs[:]
    for idx in range(len(tmp_phi_ls)-1, -1, -1)  :
        result = re.findall(r'\d{1,2}[/-]\d{1,2}', tmp_phi_ls[idx])
        if len(result) == 0:
            dateLs.pop(idx)
    return dateLs
    
# filter name in the src list and check the structure
def filter_gpt_name_ls(gpt_name_ls, src_f_name_ls, src_l_name_ls):
    tmp_ls = []
    for gpt_name in gpt_name_ls:
        result = re.findall(r'([A-Za-z-]*), +([A-Za-z-]*)', gpt_name)
        if len(result) > 0 and len(result[0]) == 2:
            l_n, f_n = result[0]
            if f_n in src_f_name_ls and l_n in src_l_name_ls:
                tmp_ls.append('{}, {}'.format(l_n, f_n))
    return tmp_ls

def getTokenLsBySent(corpus):
    corpus_ls = corpus.split('\n\n')
    sent_token_ls = []
    for paragraph in corpus_ls:
        doc = nlp(paragraph.strip())
        for sent in doc.sents:
            sent_token_ls.append(([token.text for token in sent], sent.text) )
    return sent_token_ls

def getSrc_corpus(icd9abbr, fn):
    with open(os.path.join(src_MIMIC_dir, ICD9_ABBR2FULL[icd9abbr], fn), 'r') as fr:
        content = fr.read()
    return content

def isIn(name_ls, one_sentence):# token_ls):
    capture_ls = []
    for name in name_ls:
        if name in one_sentence:
            capture_ls.append(name)
    return capture_ls
#### End of functions


src_phi_dict = loadPickle(os.path.join('./re_id_history', 'src_phi.pickle'))

'''
#### Structure
- contain_dict
    - ICD9_Abbr (eg. ARF, UTI)
        - Src text
            - Re-id type
                - List of reid elements

contain_dict = {
    'ARF': {
        '98573.txt': {
            'date': ['January', '11/25', '11/03', '11/19',          
'''

if __name__ == "__main__":


    root = r'./data/MIMIC3'

    data_type_ls = ['reid', 'deid']
    data_type = data_type_ls[0]

    prompt_dir = os.path.join( root, f'src_{data_type}', 'output_csv_4k_n')

    generation_ls = ['one_shot_src', 'keyword', 'one_shot']

    TOT_NUM = 9817

    model_ls = [ 'Mistral7b','gpt-35-turbo-a0301','gpt-4-0613', ]

    isRecord = False
    for data_type in data_type_ls:
        prompt_dir = os.path.join( root, f'src_{data_type}', 'output_csv_4k_n')
        for generation_type in generation_ls:
            for model_type in model_ls:
                task_name = f'{data_type} {generation_type} {model_type}'
                for icd9_idx in range(len(icd9obj.ICD9_ABBR_LS)):
                    icd9_abbr = icd9obj.ICD9_ABBR_LS[icd9_idx]

                    output_dir = os.path.join(prompt_dir, generation_type, model_type, icd9_abbr)
                    if os.path.isdir(output_dir): 
                        fls = glob(os.path.join(output_dir, '*.txt'))
                        collect_dict = {}
                        collected_pickle_fp = os.path.join(prompt_dir, generation_type, model_type, f'{icd9_abbr}_collect_dict.pickle')
                        if os.path.exists(collected_pickle_fp): collect_dict = loadPickle(collected_pickle_fp)
                        for fidx in tqdm(range(len(fls))):
                            fp = fls[fidx]
                            fn = os.path.basename(fp)
                            if fn in collect_dict.keys(): continue
                            src_fn = fn.replace('syn_', '')
                            with open(fp, 'r', encoding='utf-8') as fr:
                                syn_content = fr.read()
                            syn_sent_token_ls = getTokenLsBySent(syn_content)
                            collect_ls = getCollectLs(src_phi_dict[icd9_abbr][src_fn], syn_sent_token_ls)
                            if isRecord:
                                write2Log(f'Current Task --> {task_name} --------------------------------')
                                write2Log(f'Error in --> {icd9_abbr} {fn} {fidx}')
                                write2Log('='*20)
                                isRecord = False

                            collect_dict[fn] = collect_ls
                            if fidx%30 == 0: writePickle(collected_pickle_fp, collect_dict)
                            
                        writePickle(collected_pickle_fp, collect_dict)

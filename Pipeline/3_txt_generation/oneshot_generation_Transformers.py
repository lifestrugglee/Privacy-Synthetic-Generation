#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script performs text generation for one-shot and normalized one-shot generation.
Please update the following variables:

# Tokenizer settings
- model_dir
- MAX_LEN

# Data settings
- data_type: 'deid' or 'reid'
- generation_type: 'one_shot' or 'one_shot_src'
- data_dir: the directory of the data
- root: the root directory of the data
- src_data_dir: the directory of the source data

Author: Patrick C
Date: 2024-09-11
Version: 1.0
"""

import os
from pathlib import Path
import time
from datetime import timedelta
import shutil
import pickle
import torch

def save2pickle(file_name, obj):
    with open(file_name, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)

def loadPickle(file_name):
    with open(file_name, 'rb') as handle:
        return pickle.load(handle)

from openai import AzureOpenAI
import openai

import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from utils import icd9_obj 
icd9obj = icd9_obj.ICD9_obj()
#------------------------------------------------------------
# Fucntions
def getTxtGeneration(model, tokenizer, device, prompt, max_length, do_sample):
    prompt = f'[INST] {prompt} [/INST]'
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    input_len =  inputs.input_ids.shape[1]
    tot_len = input_len + max_length
    # Generate
    if do_sample:
        generate_ids = model.generate(
                        inputs.input_ids,
                        do_sample=True,
                        temperature=0.7,
                        max_length=tot_len,
                        pad_token_id=tokenizer.eos_token_id
                       )
    else:
        generate_ids = model.generate(inputs.input_ids, pad_token_id=tokenizer.eos_token_id, max_length=tot_len)
    output = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    simple_output = output.replace(prompt, '')

    output_len = tokenizer(output, return_tensors="pt").input_ids.shape[1]
    # print(f'output_len - {output_len}, input_len - {input_len}, generate - {output_len - input_len}')
    
    return simple_output

def getCorrectLen_prompt(prompt, multiCut, max_len):
    ls = prompt.split('\n')
    if getSeqLen('\n'.join(ls[:multiCut]), tokenizer) > (8192-2250):
        return getCorrectLen_prompt(prompt, multiCut-10, max_len)
    else:
        return '\n'.join(ls[:multiCut])

def getSeqLen(txt, tokenizer):
    inputs = tokenizer(txt, return_tensors="pt").to(device)
    size = inputs.input_ids.shape[1]
    return size

def getOutput(model, tokenizer, device, prompt, cut, max_length, err_count):
    # global title
    # try:
    prompt = getCorrectLen_prompt(prompt, cut, max_length)
    output = getTxtGeneration(model, tokenizer, device, prompt, max_length, True)
    # except:
        # err_count += 1
        # if err_count == 5:
        #     return None
        #     prompt = getCorrectLen_prompt(prompt, cut, max_length)
        #     output = getOutput(model, tokenizer, device, prompt, max_length, True)
    return output


# ==============================================================
# Following are for using the Mistral 7B model from Transformers
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

model_type = 'Mistral-7B-Instruct-v0.2'
model_dir = os.path.join(r'./lang_model/', model_type)

MAX_LEN = 8192
tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            model_max_length=MAX_LEN,
            padding_side="left",
            add_eos_token=False)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_dir, device_map='auto',)
model_type = 'Mistral7b'

def getTxtGeneration(model, tokenizer, device, prompt, max_length, do_sample):
    prompt = f'[INST] {prompt} [/INST]'
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    input_len =  inputs.input_ids.shape[1]
    tot_len = input_len + max_length
    # Generate
    if do_sample:
        generate_ids = model.generate(
                        inputs.input_ids,
                        do_sample=True,
                        temperature=0.7,
                        max_length=tot_len,
                        pad_token_id=tokenizer.eos_token_id
                       )
    else:
        generate_ids = model.generate(inputs.input_ids, pad_token_id=tokenizer.eos_token_id, max_length=tot_len)
    output = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    simple_output = output.replace(prompt, '')

    output_len = tokenizer(output, return_tensors="pt").input_ids.shape[1]
    # print(f'output_len - {output_len}, input_len - {input_len}, generate - {output_len - input_len}')
    
    return simple_output
# End of the settings for local transformers model
# ==============================================================



if __name__ == "__main__":
    
    data_type = 'deid' # 'reid'
    generation_type = 'one_shot' # 'one_shot_src'

    root = r'./data/MIMIC3'
    src_data_dir = os.path.join( r'./data/MIMICIII_ori_nosp')
    prompt_dir = os.path.join( root, f'src_{data_type}', 'output_csv_4k_n')

    avg_onef_time = 0
    OUTPUT_LEN = 2250
    tot_sec = 0
    icd9_ls = icd9obj.ICD9_ABBR_LS

    pre_prompt = 'As a physician, please write a clinical note using the following template.\n'
    for i in range(len(icd9_ls)):
        icd9_abbr = icd9_ls[i]
        output_dir = os.path.join(prompt_dir, f'{generation_type}_src', model_type, icd9_abbr)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        src_icd9_dir = os.path.join(src_data_dir, icd9_abbr)
        src_fls = os.listdir(src_icd9_dir)
        for src_fn in src_fls:
            output_fp = os.path.join(output_dir, f"syn_{src_fn}")
            if os.path.exists(output_fp): continue
            start_time = time.monotonic()
            with open(os.path.join(src_icd9_dir, src_fn), 'r') as fr:
                fr.readline()
                src_note = fr.read()
            prompt = pre_prompt + src_note.strip()
            output = getOutput(model, tokenizer, device, prompt, -1, GEN_MAX_LEN, 0)

            if output is None: continue
            with open(output_fp, 'w') as fw:
                fw.write(output)
            exec_sec = time.monotonic()- start_time
            
            tot_sec += exec_sec
            avg_onef_time += round(timedelta(seconds=exec_sec).total_seconds())
            avg_onef_time = round(avg_onef_time/2)
        if avg_onef_time == 0: continue

    tot_exec_time = timedelta(seconds=tot_sec)



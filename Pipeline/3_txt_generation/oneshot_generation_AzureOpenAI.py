#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script performs text generation for one-shot and normalized one-shot generation.
Please update the following variables:

# Azure openAI API settings
- endpoint
- key
- version
- model
- model_type

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
def getSynthetic_ChatGPT(model, prompt, max_tokens, temperature_val=0.7):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=max_tokens,
            temperature=temperature_val,
            stop="\n###"
        )
        return response
    except Exception as error:
        print("An exception occurred:", error) 

def getSeqLen(txt):
    inputs = tokenizer(txt, return_tensors="pt").to(device)
    size = inputs.input_ids.shape[1]
    return size
    
def getCorrectLen_prompt(ls, multiCut, max_len):
    if getSeqLen('\n'.join(ls[:multiCut])) > max_len:
        return getCorrectLen_prompt(ls, multiCut-10, max_len)
    else:
        return '\n'.join(ls[:multiCut])


def getOutput(model, prompt, cut, output_length, err_count):
    response = None
    try:
        original_limit = 8192-output_length
        new_limit = int(getSeqLen(prompt)*0.7)
        if new_limit > original_limit:
            prompt = getCorrectLen_prompt(prompt.split('\n'), -1, int(original_limit*0.7))
        else:
            prompt = getCorrectLen_prompt(prompt.split('\n'), -1, new_limit)
                
        response = getSynthetic_ChatGPT(model, prompt, output_length, temperature_val=0.7)
    except openai.APIError as e:
        if err_count == 0:
            new_limit = int(getSeqLen(prompt)*0.7)
            if new_limit > original_limit:
                prompt = getCorrectLen_prompt(prompt.split('\n'), -1, int(original_limit*0.7))
            else:
                prompt = getCorrectLen_prompt(prompt.split('\n'), -1, int(new_limit*0.7))
        
            response = getOutput(model, prompt, -1, OUTPUT_LEN, 1)
            
    return response

# response = getOutput(model, prompt, -1, OUTPUT_LEN, 0)


# ==============================================================
# Following are for using the Azure OpenAI API
# For trimming the input text to the correct length by using the tokenization
from transformers import AutoTokenizer
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "5"
device = "cuda" if torch.cuda.is_available() else "CPU"
print(device)

# Load the tokenizer from transformers
model_dir = os.path.join(r'./lang_model/',  'M7B-v0.2')

MAX_LEN = 8192
tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            model_max_length=MAX_LEN,
            padding_side="left",
            add_eos_token=False)
tokenizer.pad_token = tokenizer.eos_token


# Azure OpenAI API settings
endpoint = "YOUR_ENDPOINT"
key = "YOUR_API_KEY"
version="2024-02-01"
model = "YOUR_DEPLOYED_MODEL"
model_type = 'YOUR_MODEL_ABBREVIATION' # e.g. 'gpt-4-0613', 'Mistral7b', 'gpt-35-turbo-a0301'
os.environ["AZURE_OPENAI_API_KEY"] = key
os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    api_version=version,
    azure_endpoint=endpoint,
)

# End of the settings for Azure OpenAI API settings
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
            response = getOutput(model, prompt, -1, OUTPUT_LEN, 0)
            try:
                output = response.dict()['choices'][0]['message']['content']
                with open(output_fp, 'w') as fw:
                    fw.write(output)
            except:
                continue
            exec_sec = time.monotonic()- start_time

            tot_sec += exec_sec
            avg_onef_time += round(timedelta(seconds=exec_sec).total_seconds())
            avg_onef_time = round(avg_onef_time/2)

    tot_exec_time = timedelta(seconds=tot_sec)


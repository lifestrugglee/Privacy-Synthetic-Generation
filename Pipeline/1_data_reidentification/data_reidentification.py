#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script performs data reidentification for MIMIC III dataset.

Author: Patrick C
Date: 2024-09-11
Version: 1.0
"""


import re
import os
import random, string
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import json
from random_address import real_random_address

import pickle
def writePickle(file_path, sth):
    # store list in binary file so 'wb' mode
    with open(file_path, 'wb') as fp:
        pickle.dump(sth, fp)

def loadPickle(file_path):
    # for reading also binary mode is important
    with open(file_path, 'rb') as fp:
        return pickle.load(fp)

import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

from utils import icd9_obj 
icd9obj = icd9_obj.ICD9_obj()

# folder containing mock data
reid_dir = 're-id_sources'

# date range for admission and discharge based on the MIMIC III dataset
MAX_YEAR = 2012
MIN_YEAR = 2001


def random_pick(ls):
    return random.choice(ls)

num_dict = {}
def get_num(startpt, endpt, prefix=None):
    # math: [startpt, endpt]
    num = random.randint(startpt, endpt)
    if prefix:
        if prefix not in num_dict.keys():
            num_dict[prefix] = [num]
        elif num in num_dict[prefix]:
            num = get_num(startpt, endpt, prefix)
        else:
            num_dict[prefix].append(num)
    return num
    
def read_name_file(root):
    with open(os.path.join(root, 'full_name_list.txt'), 'r') as f:
        namels = [i.strip() for i in f.readlines()]
    firstn_ls = []
    lastn_ls = []
    for i in namels:
        f, l = i.split(' ')
        firstn_ls.append(f)
        lastn_ls.append(l)
    return (firstn_ls, lastn_ls)

firstname_ls, lastname_ls = read_name_file(reid_dir)

def read_state_name(root):
    with open(os.path.join(root, 'states_list.txt'), 'r') as f:
        contentls = [i.strip() for i in f.readlines()]
    return contentls

def read_country_name(root):
    with open(os.path.join(root, 'country_list.txt'), 'r') as f:
        contentls = [i.strip() for i in f.readlines()]
    return contentls
    
state_ls = read_state_name(reid_dir)
country_ls = read_country_name(reid_dir)

def get_phone_num():
    return '{}-{}-{}'.format(get_num(100, 999), get_num(100, 999), get_num(1000, 9999))

def get_md_number():
    pre_part = ''.join(random.choices(string.ascii_letters + string.ascii_letters, k=2)).upper()
    return 'MD_{}-{}'.format(pre_part, get_num(1000, 9999))

def get_ssn():
    return '{}-{}-{}'.format(get_num(100, 999), get_num(10, 99), get_num(1000, 9999))

def get_age():
    # The median age of adult patients is 65.8 years (Q1–Q3: 52.8–77.8)
    return get_num(52, 99)


def get_year():
    if MIN_YEAR == MAX_YEAR:
        return MAX_YEAR
    else: 
        return get_num(MIN_YEAR, MAX_YEAR)

def get_month():
    return get_num(1, 12)

def get_month_name():
    return datetime.strptime(str(get_month()), "%m").strftime("%B")

def get_date():
    return random.choice(list(range(1, 31)) )# 31 days

def get_formate_date(isyear, isDate):
    if isyear:
        if isDate:
            fmt = '%Y/%m/%d'#['%Y/%m/%d', '%Y-%m-%d']
        else:
            fmt = '%Y/%m'#['%Y/%m', '%Y-%m']
    else:
        fmt = '%m/%d'#['%m/%d', '%m-%d']
        
    return random_date(admis_date, disch_date).strftime(fmt)
    # return random_date(admis_date, disch_date).strftime(random.choice(fmt))


def get_date_range():
    fmt = ['{}~{}', '{}-{}']
    isYear = random.choice([True, False])
    isDate = random.choice([True, False])
    return random.choice(fmt).format(get_formate_date(isYear,isDate), get_formate_date(isYear,isDate))
    
def get_address():
    # Generate a dictionary with valid random address information
    tmp = real_random_address()
    address = ''
    for _,v in list(tmp.items())[:-1]:
        address += ' ' + v
    return address

def get_location():
    city = ''
    # some of the address not include city attr.
    while city == '':
        tmp = real_random_address()
        if 'city' in tmp.keys():
            city = tmp['city']
    return city

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)

def ymd(dateObj):
    return dateObj.strftime('%Y/%m/%d')

def getDateObj_byYear(year_val, isStart):
    if isStart:
        return datetime.strptime(f'1/1/{year_val} 12:00 AM', '%m/%d/%Y %I:%M %p')
    else:
        return datetime.strptime(f'1/1/{year_val} 11:59 PM', '%m/%d/%Y %I:%M %p')
d1 = getDateObj_byYear(MIN_YEAR, 1)
d2 = getDateObj_byYear(MAX_YEAR, 0)

def get_ImportantDate():
    # function of generating ADMIS and DISCH Date
    admis_date = random_date(d1, d2)
    disch_date = random_date(admis_date, d2)

    # function for generating DOB
    age = get_age()
    dob_year = yearsago(age, admis_date).strftime('%Y')

    dob = random_date(getDateObj_byYear(dob_year, 1), d2)
#     return age, ymd(dob), ymd(admis_date), ymd(disch_date)
    return age, dob, admis_date, disch_date

def isAdm_check(sent, star_date):
    star_date = star_date.replace('[**', '\[\*\*').replace('**]', '\*\*\]')
    
    regex = f'Admission Date:[ ]+{star_date}[ ]+Discharge Date:'
    result = re.findall(regex, sent)

    if len(result) > 0 :
        return True
    else:
        return False

def add2file_dict(keyType, val_pair_ls):
    if keyType not in f_record_dict.keys():
        f_record_dict[keyType] = []
    
    f_record_dict[keyType].append(val_pair_ls)


def get_reid_string(mask, fileNum):
    mask = mask.lower()
    isNum = False
    reid_str = ''
    reid_type = 'date'
    if 'age_over_90_' in mask:
        reid_str = get_age(); reid_type = 'age'
    elif 'name' in mask:
        if 'initial' in mask:
            reid_str = '{}.{}.'.format(random_pick(firstname_ls)[0], random_pick(lastname_ls)[0]); reid_type = 'name_inital'
        elif 'hospital_ward' in mask:
            reid_str = f'Hospital Ward{fileNum}'; reid_type = 'hospital_ward'
        elif 'last_name' in mask:
            reid_str = random_pick(lastname_ls); reid_type = 'last_name'
        elif 'first_name' in mask or 'name' in mask:
            reid_str = random_pick(firstname_ls); reid_type = 'first_name'
    elif 'dictator_info' in mask or 'attending_info' in mask:
        reid_str = f'{random_pick(firstname_ls)} {random_pick(lastname_ls)}'; reid_type = 'full_name'
    elif 'hospital' in mask:
        reid_str = f'Hospital{fileNum}'; reid_type = 'hospital'
    elif 'company' in mask:
        reid_str = f'Company{fileNum}'; reid_type = 'company'
    elif 'phone' in mask or 'provider_number' in mask:
        reid_str = get_phone_num(); reid_type = 'phone_num'
    elif 'location' in mask:
        reid_str = get_location(); reid_type = 'location'
    elif 'md_number' in mask:
        # XX-0000
        reid_str = get_md_number(); reid_type = 'md_number'
    elif 'address' in mask:
        reid_str = get_address(); reid_type = 'address'
        
    elif 'unit_number' in mask:
        reid_str = f"un_{get_num(1000,9999, 'un')}"; reid_type = 'unit_number'
    elif 'pager_number' in mask:
        reid_str = f"pg_{get_num(10,999, 'pg')}"; reid_type = 'pager_number'
    elif 'job_number' in mask:
        reid_str = f"jb_{get_num(10000,99999, 'jb')}"; reid_type = 'job_number'
    elif 'numeric_identifier' in mask:
        reid_str = f"ni_{get_num(100000, 999999, 'ni')}";reid_type = 'numeric_identifier'
    elif 'clip_number' in mask:
        reid_str = f"clip_{get_num(1000,9999, 'clip')}";reid_type = 'clip_number'
    elif 'medical_record_number' in mask:
        reid_str = f"mrn_{get_num(100000, 999999, 'mrn')}";reid_type = 'medical_record_number'
    elif 'serial_number' in mask:
        reid_str = f"sn_{get_num(1000000, 9999999, 'sn')}";reid_type = 'serial_number'
        
    elif 'country' in mask:
        reid_str = random_pick(country_ls); reid_type = 'country'
    elif '[**state' in mask:
        reid_str = random_pick(state_ls); reid_type = 'state'
    elif 'cc_contact_info' in mask:
        # First name + last name + phone number 
        reid_str = f'{random_pick(firstname_ls)} {random_pick(lastname_ls)} {get_phone_num()}'
        reid_type = 'full_name_phone'
    elif 'holiday_' in mask:
        reid_str = f'the Holiday{fileNum}'; reid_type = 'holiday'
    elif 'university/college' in mask:
        reid_str = f'University{fileNum}'; reid_type = 'university'
    elif 'social_security_number' in mask:
        # 000-00-0000
        reid_str = get_ssn(); reid_type = 'ssn'
    elif 'date_range' in mask:
        reid_str = get_date_range()
    elif 'month' in mask:
        reid_str = get_month_name()
    else:
        
        # date
        result = re.match("(?:\[\*\*)(?P<year>\d{3,4})?-?(?P<date>\d{1,2}-\d{1,2})?", mask)
        if result.group('year') and result.group('date'):
            reid_str = get_formate_date(1, 1)
        elif result.group('date'):
            reid_str = get_formate_date(0, 1)
        elif result.group('year'):
            reid_str = get_year()

        if reid_str == '':
            result = re.match("(?:\[\*\*)-?(?P<month>\d{1,2})-?/(?P<year>\d{4})", mask)
            if result and (result.group('month') or result.group('year')):
                reid_str = get_formate_date(1, 0)
            
        
        if reid_str == '':
            result = re.match("(?:.*)_(?P<year>\d{4})(?:\*\*\])", mask)
            if result and result.group('year') or 'year' in mask:
                reid_str = get_year()
        # deal with num
        # simply number == 00
        result = re.match("(?:\[\*\*)(?P<num>\d{1,2})(?:\*\*\])", mask)
        if result and result.group('num'):
            reid_str = get_num(100, 999); reid_type = 'num'; isNum=True
        # "url_", "[**_**]", "[**po_box_">>> skip
    reid_str = str(reid_str)
    return reid_type, reid_str, isNum


if __name__ == '__main__':
    sourceDir = os.path.join("..", "data","MIMICIII_ori_nosp")

    # Output dir
    mimic_data_dir = '../data/MIMIC_reid_val_record_20240620'

    num_idx_dict = {} # for def getNum()
    num_ls = []

    for oneicd9_abbr in icd9obj.ICD9_ABBR_LS:
        print(oneicd9_abbr)

        new_icd9dir = os.path.join(mimic_data_dir, oneicd9_abbr)
        Path(new_icd9dir).mkdir(parents=True, exist_ok=True)
        fileLs = os.listdir(os.path.join(sourceDir, oneicd9_abbr))
        
        record_dict = {}
        oneicd9_num_dict = {}
        for fidx in range(len(fileLs)):
        # for fidx in range():
            fn = fileLs[fidx]
        
            f_record_dict = {}
            MAX_YEAR = 2012
            MIN_YEAR = 2001
            age, dob_date, admis_date, disch_date = get_ImportantDate()
            MAX_YEAR = int(disch_date.strftime('%Y'))
            MIN_YEAR = int(admis_date.strftime('%Y'))
            
            fn_noext = fn.replace('.txt', '')
            f_p = os.path.join(sourceDir, oneicd9_abbr, fn)
            with open(f_p, 'r') as f:
                contentls = f.readlines()
                
            num_content_idx_ls = set()
            for lineidx in range(len(contentls)):
                f_key = ''
                sent = contentls[lineidx]
                
                regex = r'(\[\*\*.*?\*\*\])'
                result = re.findall(regex, sent) 
                if len(result) > 0:
                    if 'Admission Date' in sent and 'Discharge Date' in sent:
                        if len(result) == 2:
                            # print('ADM be-', repr(sent) )
                            sent = sent.replace(result[0], ymd(admis_date) )
                            add2file_dict('date', (ymd(admis_date), sent) )
                            sent = sent.replace(result[1], ymd(disch_date) )
                            add2file_dict('date', (ymd(disch_date), sent) )
                            # print('ADM af-', repr(sent) )
                        else:
                            if isAdm_check(sent, result[0]):
                                sent = sent.replace(result[0], ymd(admis_date) )
                                f_key = ymd(admis_date)
                            else:
                                sent = sent.replace(result[0], ymd(disch_date) )
                                f_key = ymd(disch_date)
                            add2file_dict('date', (f_key, sent) )
                    elif 'Date of Birth' in sent:
                        # print('DOB be-', repr(sent) )
                        sent = sent.replace(result[0], ymd(dob_date) )
                        f_key = ymd(dob_date) 
                        # print('DOB af-', repr(sent) )
                        add2file_dict('date', (f_key, sent) )
                    else:
                        # print('ori be-', repr(sent) )
                        for ridx in range(len(result)):
                            oristr = result[ridx]
                            newstr_type, newstr, isNum = get_reid_string(oristr, fn_noext)
                            if isNum:
                                num_content_idx_ls.add(lineidx)
                            if newstr_type in ['unit_number', 'pager_number', 'job_number', 'numeric_identifier', 'clip_number', 'medical_record_number', 'serial_number', ]:
                                # print(f_p); print(oristr)
                                num_ls.append((newstr, oristr ))#, f'{oneicd9}_{fn_noext}'))

                            extra_space = ''
                            if f'{oristr} ' not in sent:
                                extra_space = ' '
                                
                            sent = sent.replace(oristr,f'{newstr}{extra_space}')
                            add2file_dict(newstr_type, (newstr, sent) )
                        # print('ori af-', repr(sent) )
                    contentls[lineidx] = sent
            if len(num_content_idx_ls):
                oneicd9_num_dict[fn] = num_content_idx_ls
            
            with open(os.path.join(new_icd9dir, fileLs[fidx]), 'w') as f:
                f.write(''.join(contentls))
            
            record_dict[fileLs[fidx]] = f_record_dict
        num_idx_dict[oneicd9_abbr] = oneicd9_num_dict
        writePickle(os.path.join(mimic_data_dir, f'{oneicd9_abbr}.pickle'), record_dict)
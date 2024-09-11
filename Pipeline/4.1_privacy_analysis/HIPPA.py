class HIPAA:
    def __init__(self):
        self.name = 'Names'
        self.geo = 'All_geo'
        self.date = 'All_date'
        self.tel = 'Telephone'
        self.vehicle_lic = 'Vehicle_serial_license'
        self.fax = 'Fax_num'
        self.device_id = 'Device_identifiers'
        self.email = 'Email'
        self.url = 'Web_URLs'
        self.ssn = 'SSN'
        self.ip = 'IP_address'
        self.medical_num = 'Medical_record_numbers'
        self.bio_id = 'Biometric_identifiers'
        self.health_ben_num = 'Health_plan_beneficiary_numbers'
        self.images = 'Images'
        self.acc_num = 'Account_numbers'
        self.unique_id_num = 'Unique_identifying_number'
        self.certificate_lic = 'Certificate_license_num'
        
        self.desc_dict = {
            self.name : 'given names, middle names, surnames, or name initials',
            self.geo : 'geographic or locations',
            self.date : 'date or age number',
            self.tel : 'telephones number',
            self.vehicle_lic : 'vehicle serial numbers',
            self.fax : 'fax number',
            self.device_id : 'device identifiers or numbers',
            self.email : 'Emails',
            self.url : 'web URLs',
            self.ssn : 'social security number',
            self.ip : 'IP address',
            self.medical_num : 'medical record numbers',
            self.bio_id : 'biometric identifiers',
            self.health_ben_num : 'health plan beneficiary numbers or insurance numbers',
            self.images : 'images',
            self.acc_num : 'account numbers',
            self.unique_id_num : 'unique identifying numbers',
            self.certificate_lic : 'certificate license numbers',
        }

        self.MIMIC3_MAP_2_HIPAA = {
            'address': self.geo, 'age': self.date, 'clip_number': self.unique_id_num,
            'company': self.geo, 'country': self.geo, 'date': self.date, 
            'first_name': self.name, 'full_name': self.name, 'holiday': self.date, 'last_name': self.name, 
            'holiday': self.date, 'hospital': self.geo, 'hospital_ward': self.geo, 
            'job_number': self.unique_id_num, 'location': self.geo, 'md_number': self.unique_id_num, 
            'medical_record_number': self.medical_num, 'name_inital': self.name, 'num': self.unique_id_num, 
            'numeric_identifier': self.unique_id_num, 'pager_number': self.tel, 'phone_num': self.tel, 
            'serial_number': self.device_id, 'ssn': self.ssn, 'state': self.geo, 'unit_number': self.unique_id_num, 
            'university': self.geo, 'po_box': self.geo, 'url': self.url,  
        }

    def get_phi_ls(self):
        return list(self.desc_dict.keys())

    def get_PHI_descriptive(self, phi_type):
        return self.desc_dict[phi_type]

    def get_HIPPA_by_MIMIC3_tag(self, mimic_tag):
        return self.MIMIC3_MAP_2_HIPAA[mimic_tag]
    
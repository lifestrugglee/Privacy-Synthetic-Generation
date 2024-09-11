class ICD9_obj():
	def __init__(self):
		self._ARF_ABBR = 'ARF' ; self._ARF_FULL = 'acute respiratory failure'; self._ARF_num = 1067
		self._CHF_ABBR = 'CHF' ; self._CHF_FULL = 'congestive heart failure' ; self._CHF_num = 1002
		self._AKF_ABBR = 'AKF' ; self._AKF_FULL = 'acute kidney failure'     ; self._AKF_num = 1083
		self._HPN_ABBR = 'HPN' ; self._HPN_FULL = 'hypertension'             ; self._HPN_num = 3452
		self._CAS_ABBR = 'CAS' ; self._CAS_FULL = 'coronary atherosclerosis' ; self._CAS_num =  993
		self._DM2_ABBR = 'DM2' ; self._DM2_FULL = 'diabetes mellitus type 2' ; self._DM2_num =  410
		self._AF_ABBR  = 'AF'  ; self._AF_FULL  = 'atrial fibrillation'      ; self._AF_num  = 1010
		self._UTI_ABBR = 'UTI' ; self._UTI_FULL = 'urinary tract infection'  ; self._UTI_num =  800
		self.TOT_NUM = 9817

		self.ICD9_ABBR_LS = ( self._ARF_ABBR, self._CHF_ABBR, self._AKF_ABBR, self._HPN_ABBR, 
							  self._CAS_ABBR, self._DM2_ABBR, self._AF_ABBR , self._UTI_ABBR, )
		self.ICD9_FULL_LS = ( self._ARF_FULL, self._CHF_FULL, self._AKF_FULL, self._HPN_FULL,
							  self._CAS_FULL, self._DM2_FULL, self._AF_FULL , self._UTI_FULL,  )

		self.ICD9_ABBR2FULL= {self._ARF_ABBR : self._ARF_FULL, self._CHF_ABBR : self._CHF_FULL, self._AKF_ABBR : self._AKF_FULL,
							  self._HPN_ABBR : self._HPN_FULL, self._CAS_ABBR : self._CAS_FULL, self._DM2_ABBR : self._DM2_FULL,
							  self._AF_ABBR  : self._AF_FULL , self._UTI_ABBR : self._UTI_FULL,}

		self.ICD9_FULL2ABBR = {v:k for k , v in self.ICD9_ABBR2FULL.items()}

		self.ICD9_NUM_DICT = {
								self._ARF_ABBR : self._ARF_num, self._CHF_ABBR : self._CHF_num, self._AKF_ABBR : self._AKF_num,
								self._HPN_ABBR : self._HPN_num, self._CAS_ABBR : self._CAS_num, self._DM2_ABBR : self._DM2_num,
								self._AF_ABBR  : self._AF_num , self._UTI_ABBR : self._UTI_num, 
							}

	def getFull(self, abbr):
		return self.ICD9_ABBR2FULL[abbr]

	def getAbbr(self, full):
		return self.ICD9_FULL2ABBR[full]

	def getICD9_NUM(self, icd9_abbr):
		return self.ICD9_NUM_DICT[icd9_abbr]




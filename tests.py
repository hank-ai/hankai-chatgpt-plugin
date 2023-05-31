#%%
import json, requests, re, os
import openai
import pandas as pd
from enum import Enum
from samples import SampleDocuments, SampleGPTResponses

class MalformedOpenaiJSON(Exception):
    pass

class Specialty(Enum):
    ANESTHESIA = "anesthesia"
    SURGERY = "surgical"
    RADIOLOGY = "radiology"
    EMERGENCYMEDICINE = "emergencymedicine"
    EANDM = "eandm"

class GPTModel(Enum):
    GPT4 = "gpt-4"
    GPT3_5 = "gpt-3.5-turbo"

class SimpleAutocoder:
    def __init__(self, specialty=Specialty.ANESTHESIA, year=2023, gptmodel=GPTModel.GPT3_5, claimcleaner_token="", quiet=True):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        print(f"Using openai api_key={openai.api_key}")
        self.gptmodel = gptmodel
        self.quiet = quiet
        #load csv datafiles for asa crosswalk, icds, cpts, and modifiers
        self.asacwdf = pd.read_csv("CROSSWALKs-ALL.csv", dtype={'CPT Procedure Code':str, 'CPT Anesthesia Code':str})
        #self.asacwdf columns: CPT Procedure Code, CPT Procedure Descriptor, CPT Anesthesia Code, CPT Anesthesia Descriptor, Base Unit Value, Time, Alternates, Changed This Year, New, Alternate Changed, Comment Instruction Added or Changed, Comment	Instruction Text, CMS Base Units Differ, Year, Instructi/Text, Base Unit Value - ASA
        self.icddf = pd.read_csv("ICDs-ALL.csv", dtype={'ICD Code':str, 'Description':str})
        #self.icddf columns: ICD Code, Description, Year
        self.cptdf = pd.read_csv("CPTs-ALL.csv", dtype={'CPT Code':str, 'Description':str})
        #self.cptdf columns: CPT Code, Relative ID, Description Type, Description, Year
        self.moddf = pd.read_csv("modifier.csv", dtype={'Modifier':str, 'Description':str})
        #self.moddf columns: Modifier, Description

        self.year = year
        self.specialty = specialty
        self.CC_URL = f"https://claimcleaner.api.hank.ai/clean/1.0.1/{claimcleaner_token}"
        self.cc_body = { #template of json body for calls to claim cleaner
            "cleaners": ["all"], #list of cleaners. i.e. ['frc','acc','nlcd']. from short abbreviation in parenthesis above
            "claims": [
                {
                    "dos": "2022-02-07", #date of service. yyyy-mm-dd expected
                    "category": "Practitioner Services", #choice of Practitioner Services, DME Services, or Hospital Outpatient Services
                    "frequency_cutoff": "0.02", # the % frequency to be considered abnormal coding for the frequency checker. range 0.0 to 1.0
                    "zipcode": "29201", #zip code. 5 digits. if given, will supercede county+state if those are given as well. used for NCD and LCD edits
                    "county": "", #county. used for NCD and LCD edits #optional
                    "state": "", #state. 2 char version. used for NCD and LCD edits #optional
                    "line_items":[ #list of line items for the claim
                        # {
                        #     "cpt": "23472", #cpt code. 5 digits
                        #     "anescpt": "00400", #anesthesia cpt code (optional). 5 digits
                        #     "mods": [""], #list of modifier codes (i.e. LT, RT, 59, 26, etc)
                        #     "icds": ["k22.22"] #list of icd10 codes, with decimal
                        # },
                    ]
                }
            ]
        }
        self.pre_prompts = {
            "anesthesia": """given this operative report, return 1 minimized json object containing 2 unlabeled tries 
                of only your best unique predictions for surgical cpts (s), anesthesia cpts (a), icds (i), and modifiers (m). no extra words.
                """, 
            "anesthesia": "given the following medical note, predict " + \
                "lists of the best procedure cpts (s), anesthesia cpts (a), icd codes (i), and the billing modifiers (m) as json. only return the json object. use json keys s, a, i, m.",
            "anesthesia_procedure": "given the following anesthesia procedure note, predict " + \
                "lists of the best procedure cpts (s), icd codes (i), and the billing modifiers (m) as json. only return the json object. use json keys s, i, m.",
            # 'anesthesia': "given the following surgical operative report, return a single json object with no headers/footers, or extra spaces that contains 3 seperate prediction attempts as seperate items in the parent json list " + \
            #     "for the combination of surgical cpt, anesthesia cpt, list of icds, any applicable modifiers, and prediction confidence. use keys surgcpt, anescpt, icds, mods, conf. Please apply the ASA crosswalk rules and the NCCI edits.",
                # "return 3 different attempts to do the predictions as a list of seperate prediction groups in the json. make sure everything is in one json object.",
            'radiology': "given the following radiology report, return a single json object with no headers/footers that contains 3 seperate prediction attempts as seperate items in the parent json list " + \
                "for the combination of radiology procoedure cpt, list of icds, any applicable modifiers, and a numerical prediction confidence. use keys cpt, icds, mods, conf.",
                # "return 3 different attempts to do the predictions as a list of seperate prediction groups in the json. make sure everything is in one json object.",
            'surgical': "given this surgical note, return 1 json list with no extra spaces or newlines containing two independent attempts to predicted all the surgical cpts (s), anesthesia cpts (a), icds (i), and modifiers (m) as lists. include a confidence (c) 0.0 to 1.0 for each attempt. no extra words.",
            # "here is a surgical operative report. return exactly 1 json object with no extra spaces. predict the unique surgical cpts, icds, and modifiers. " + \
            #     "return 2 different prediction attempts as a list of 1 grouped list in the json. use keys surgcpt, anescpt, icds, mods. no descriptions.",
        }

    #returns the asa codes mapped to given cptcode in the ASA Crosswalk datafile
    #always returns a list
    #if alternates is set, will return the alternate codes as well (first code in list will be primary, then alternates)
    def getCrosswalkedASAs(self, cptcode, alternates=False, quiet=True, year=2022):
        rval=[]
        if len(self.asacwdf)>0:
            cptcode = str(cptcode).replace('.', '')  
            cptcode = cptcode.zfill(5).strip()
            rdf = self.asacwdf[(self.asacwdf['Year']==year) & (self.asacwdf['CPT Procedure Code'].str.match(cptcode))]
            if not quiet: print('Finding cpt {} in ASA crosswalk'.format(cptcode))
            if len(rdf)>0:
                rval = [str(int(x)).zfill(5) for x in list(rdf['CPT Anesthesia Code'].dropna()) if (~pd.isnull(x) and x != '')]
                if alternates:
                    for alt in str(rdf.iloc[0]['Alternates']).split(','):
                        if alt != '': rval.append(alt)
            rval = [str(x).zfill(5) for x in rval if float(x)>0] #don't include the -0004 codes
            if not quiet: print("rdf: ", rdf)
        return rval

    #checks a row in a dataframe to see if the anescpt (a) in that row is in the crosswalk for the given surgcpt (s).
    #returns anescpt value if it is in the crosswalk for that surgcpt. if not, will return the first anesthesia cpt code listed in the crosswalk
    def checkASACW(self, row, year=2023, dropUncrosswalked=True):
        cwasas = self.getCrosswalkedASAs(row['s'], alternates=True, year=year, quiet=1)
        if len(cwasas)>0:
            if row['a'] not in cwasas:
                print(f"swapping {row['a']} for {cwasas[0]} from crosswalk")
                return cwasas[0]
        elif dropUncrosswalked:
            return ""
        return row['a']
        #lookup anesthesia base units. asa = an asa cpt code as a string

    #returns -1 if asa code not found
    #looks up the base units for an asa cpt code in a given year
    def buLookup(self, asa:str, year:int=None, useASAValues:bool=0):
        if year is None: year = self.year
        if not self.quiet: print('Looking up {} in buLookup'.format(asa))
        asa = str(asa).zfill(5)
        if all(c == '0' for c in asa): return -1
        try:
            if useASAValues:
                qdf = self.asacwdf[(self.asacwdf['CPT Anesthesia Code']==asa) & (self.asacwdf['Year']==year)]['Base Unit Value - ASA']
            else:
                qdf = self.asacwdf[(self.asacwdf['CPT Anesthesia Code']==asa) & (self.asacwdf['Year']==year)]['Base Unit Value']
            if len(qdf)>0:
                return int(qdf.iloc[0])
        except Exception as e:
            print(f"ERROR in buLookup: {e}")
        return -1


    #this function runs BEFORE sending line items to claim cleaner
    #returns a list of independent attempts containining lists of the cleaned up predicted line items
    def _processLineItemSpecialty_BEFORE_claimcleaner(self, openai_json, specialty:Specialty=None, dropUncrosswalkedASAs=True):
        if specialty is None: specialty=self.specialty
        # Create empty list to contain the prediction lists for the claim line items
        preds = []
        for idx, d in enumerate(openai_json): #iterating over independent prediction responses
            thisclaim = []
            # For each surgical CPT
            for s in d['s']:
                td = d.copy() #need to make copy or doesn't update dict properly
                td['s'] = s
                if 'a' not in td.keys(): td['a']="" #most processing in later functions expects an anescpt key (even if empty). so put an empty one.
                if specialty == Specialty.ANESTHESIA: 
                    #gpt may return an asa list. pick just the first one
                    if isinstance(td['a'], list): 
                        if len(td['a']) > 0: td['a'] = td['a'][0]
                        else: td['a']=""
                    #check asa crosswalk. remove asa code if doesn't match to cpt code
                    td['a'] = self.checkASACW(td, year=self.year, dropUncrosswalked=1) #[x for x in d['a'] if x in validasas and not len(validasas)==0]               
                else:
                    td['a'] = ""
                # Add row to dataframe with other fields repeated
                thisclaim.append({
                    's': s,
                    'a': td['a'],
                    'i': td['i'],
                    'm': [re.sub(r'[^\w\s]', '', s) for s in td['m']], #remove punctuation
                    #'c': td['c']
                })
            preds.append(thisclaim)
        return preds
    
    #this function runs AFTER sending line items to claim cleaner
    #returns a list of independent attempts containining lists of the cleaned up predicted line items
    def _processLineItemSpecialty_AFTER_claimcleaner(self, line_items, specialty:Specialty=None):
        if specialty is None: specialty=self.specialty
        # Create empty list to contain the prediction lists for the claim line items
        preds = []
        if specialty==Specialty.ANESTHESIA: #do anesthesia stuff like keeping only line item that has asa code with highest base units
            #[{'cpt':'27447', 'anescpt':'00400'}, {'cpt':'27447', 'anescpt':'00731'}, {'cpt':'64450', 'anescpt':''}]
            licopy = line_items.copy()
            highest_baseunits = -1
            highest_baseunits_lineitem = {}
            for li in licopy:
                if li['anescpt']!= "":
                    baseunits = self.buLookup(li['anescpt'])
                    print(li['anescpt'], baseunits)
                    if baseunits > highest_baseunits:
                        highest_baseunits = baseunits
                        highest_baseunits_lineitem = li

            line_items = [li for li in line_items if li['anescpt']=='' or (li['cpt']==highest_baseunits_lineitem['cpt'] and li['anescpt']==highest_baseunits_lineitem['anescpt'])]

        if specialty==Specialty.SURGERY: #drop non surgical line items (i.e. anesthesia procedures, etc)
            line_items = line_items
        return line_items
    

    #takes line_items as a dict list in the openai short format (keys = s, a, i, m, c) and converts them to claim cleaner keys
    #make line items for the claim cleaner api from the prompted gpt json response
    #returns: list of claim line items as expected by claim cleaner api spec
    def convertForCC(line_items):
        out = []
        for li in line_items:
            out.append({
                'cpt': li['s'],
                'anescpt': li['a'],
                'icds': li['i'],
                'mods': li['m']
            })
        return out


    def fix_json(json_string):
        # Remove trailing commas
        fixed = re.sub(",\s*}", "}", json_string)
        fixed = re.sub(",\s*\]", "]", fixed)
        # Add double quotes around alphanumeric values not already enclosed in quotes
        fixed = re.sub(r'([a-zA-Z0-9.]+)', r'"\1"', fixed)
        # find the JSON part using regex
        match = re.search(r'{.*}|\[.*\]', json_string, re.DOTALL)
        if match:
            fixed = match.group()
        try: 
            json.loads(fixed)
        except json.JSONDecodeError:
            raise MalformedOpenaiJSON(f"The JSON from openai seems to be malformed.\n{repr(json_string)}")
        return fixed
    
    def _reducePredictions(self, openai_json):
        #in the future should calculate some averages across the independent prediction group responses instead of just taking the first one
        return openai_json[0] 

    def handleCands(self, openai_json:list, year:int=2023, specialty:Specialty=None):
        if specialty is None: specialty=self.specialty
        res = []
        if isinstance(openai_json, dict): openai_json = [openai_json] #to be compatible with prompts that return multiple candidate responses in the json as a list
        print(openai_json)
        openai_json = self._processLineItemSpecialty_BEFORE_claimcleaner(openai_json, specialty=specialty, dropUncrosswalkedASAs=1)
        openai_json = self._reducePredictions(openai_json)
        print(openai_json)
        df = pd.DataFrame(openai_json)
        #if self.specialty=='anesthesia': df['a'] = df.apply(lambda row: self.checkASACW(row, year=year), axis=1) 
        res = df.to_json(orient="records", indent=2)
        return openai_json

    #submits this_prompt string to gpt for predictions. 
    #depending upon specialty, will use a different openai prompt
    #gptmodel can be 3.5turbo or 4 currently
    def query_openai(self, this_prompt:str, specialty:Specialty=None, document_type:str=None):
        if specialty==None: specialty=self.specialty
        print(f"Sending request to openai {self.gptmodel.value} ...\nSPECIALTY={specialty.value}\nDOCUMENT_TYPE={document_type}\nPROMPT={self.pre_prompts.get(specialty.value)}\nCONTENT={this_prompt}")
        prompt = self.pre_prompts.get(specialty.value)
        #if we are predicting anesthesia claim and processing a anesthesia procedure note, use a different prompt
        if specialty==Specialty.ANESTHESIA and document_type=='anesthesia_procedure':
            prompt = self.pre_prompts.get(document_type)

        #response = openai.Completion.create(model="text-davinci-003", prompt="write me a short poem about a bird", temperature=0, max_tokens=7)
        #### text-davinci-003 ####
        # response = openai.Completion.create(
        #     model="text-davinci-003", 
        #     prompt=f"{pre_prompt}\n{this_prompt}", 
        #     temperature=0, max_tokens=50)

        #### gpt-3.5-turbo or gpt-4
        response = openai.ChatCompletion.create(
            model=self.gptmodel.value, #"gpt-4", #"gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": this_prompt}
            ],
            #temperature=0, max_tokens=50
            )
        print(f"**RAW RESPONSE:**\n{response}")
        choices = response.get('choices')
        firstchoice = choices[0]
        json_response = SimpleAutocoder.fix_json(firstchoice.get('message', {}).get('content'))
        #print(f"**JSON RESPONSE:**\n{json_response}")
        
        try:
            cands = json.loads(json_response)
        except: 
            print("ERROR loading the message as a json object. Probably malformed.")
            cands = {}
        return cands
    
    #takes the response from claimcleaner and formulates it into a list containing lists of cure dicts with indexes matching line items passed to claim cleaner
    #will contain things like +00400 for anescpt, -59, +51, etc for mods
    #+00400 anescpt would mean to use that for the anescpt for the claim
    #-59 mods would mean remove modifier 59 from the claim. +51 mods would mean add the 59 modifier to the claim
    #return format: [{"surgcpt": ["+27641"], "anescpt":["-00400", "+00300"], "icds":[], "mods":[]}, {"surgcpt": [], "anescpt":[], "icds":[], "mods":[]} ...]
    def buildCureList(self, claimcleaner_response):
        li_cures = []
        for li in claimcleaner_response.get("line_items"):
            cures = {"surgcpt": [], "anescpt":[], "icds":[], "mods":[]}
            liidx = li.get('line_item_index')
            print(li)
            for k, v in li.items():
                if isinstance(v, dict):
                    issues = v.get("issues")
                    for issue in issues:
                        for issue_type, issue_cure in issue.get("issue_cure").items():
                            if not isinstance(issue_cure, list): issue_cure = [issue_cure.split(',')[0]]
                            if issue_type=='surgcpt': issue_type='cpt'
                            if issue_type=='anescpts': issue_type='anescpt'
                            if '+59' in issue_cure and "+XU" in issue_cure: issue_cure = [x for x in issue_cure if not x == '+XU']
                            cures[issue_type] += (issue_cure)
                            print(liidx, issue_type, issue_cure)
            li_cures.append(cures)
            print(f"liidx={liidx}. cures={cures}")
        return li_cures
    
    #takes a list of a claim's line items as line_items and a list of corresponding line_item_cures from the claim cleaner api response
    # and returns a list of line items that have been modified based upon the claim cleaner cure recommendations
    #inputs: 
    # list of line items from convertForCC()
    # list of line item cures from buildCureList()
    def cureClaim(self, line_items, line_item_cures):
        for liidx, lic in enumerate(line_item_cures):
            for issue_type, cure_list in lic.items():
                for cure in cure_list:
                    liitem = line_items[liidx][issue_type] 
                    print(liidx, issue_type, cure)
                    if cure[1:].strip()=="": continue
                    if cure[0]=='+': #add a thing
                        if isinstance(liitem, list) and cure[1:] not in liitem: #add to front of list
                            liitem.insert(0, cure[1:])
                        elif isinstance(liitem, str): #replace string
                            liitem = cure[1:]
                    elif cure[0]=="-": #remove a thing
                        if isinstance(liitem, list): #remove from list
                            print(" -> removing")
                            liitem = [x for x in liitem if not cure[1:] == x]
                        elif isinstance(liitem, str): #replace string
                            if liitem == cure[1:]: liitem=""
                    line_items[liidx][issue_type] = liitem
        return line_items
    
    def checkAndCureWithClaimCleaner(self, openai_json, quiet=True):
        line_items = SimpleAutocoder.convertForCC(openai_json)
        if not quiet: print("claim:", json.dumps(line_items))
        cc_response = self.postToClaimCleaner(line_items)
        
        if not quiet: print("cc_response:",json.dumps(cc_response, indent=2))
        cure_list = self.buildCureList(cc_response)
        if not quiet: print("li_cures: ", cure_list)
        cured_claim = self.cureClaim(line_items, cure_list)
        return cured_claim
    
    
    def postToClaimCleaner(self, line_items):    
        #update the claimcleaner json body to hold the predicted line items
        cc_body = self.cc_body
        cc_body['claims'][0]['line_items'] = line_items
        print("Posting to claim cleaner api ...")
        response = requests.post(self.CC_URL, json=json.dumps(cc_body))
        if response.status_code == 200:
            res = response.json()
            results = res.get('RESULTS')
            errs = res.get('ERRORS')
            md = res.get('METADATA')
        elif response.status_code == 500: 
            print("Request to claim cleaner api failed with status code 500. Unauthorized access. Did you pass a valid token in the contructor to SimpleAutocoder()?")
        else:
            print("Request to claim cleaner api failed with status code", response.status_code)
            print(cc_body)

        # print(json.dumps(cc_body, indent=2))
        # print(json.dumps(results, indent=2))
        claimcleaner_response = results.get('claims')[0]
        return claimcleaner_response

    #documents: dict of lists. dict keys should match to available prompts in this class
    def autocode(self, documents_dictionary, specialty:Specialty=None, preds_raw_json=None):
        if specialty==None: specialty=self.specialty
        if preds_raw_json is None: #just allows you to pass in some preds you already got from openai during testing
            preds = []
            for doctype, documents in documents_dictionary.items():
                if not isinstance(documents, list): documents = [documents]
                for i, doc in enumerate(documents):
                    this_prompt = ' '.join(doc.split()) #strip all extra spaces and newlines
                    cands = self.query_openai(this_prompt, specialty=specialty, document_type=doctype)
                    res = self.handleCands(cands, specialty=specialty)
                    res = [{**d, 'doc_type':doctype, 'doc_idx':i} for d in res] #add the document type and index to each prediction for later use
                    preds += res
            print(f"***AUTOCODE RESULTS:\n{json.dumps(preds, indent=2)}")
        else:
            preds = json.loads(preds_raw_json)
        all_line_items = preds
        # for i, line_items in preds:
        #     all_line_items += line_items
        #print(all_line_items)
        cleaned_line_items = self.checkAndCureWithClaimCleaner(all_line_items)
        print(f"***AFTER CLEANING RESULTS:\n{json.dumps(cleaned_line_items, indent=2)}")
        filtered_line_items = self._processLineItemSpecialty_AFTER_claimcleaner(cleaned_line_items, specialty=specialty)
        print(f"***AFTER FILTERING FOR SPECIALTY RESULTS:\n{json.dumps(cleaned_line_items, indent=2)}")
        return filtered_line_items

docs_dict = { 'anesthesia':SampleDocuments.anesthesia[0], 
             'anesthesia_procedure':SampleDocuments.anesthesia_procedure[6]
}
ac = SimpleAutocoder(gptmodel=GPTModel.GPT4, claimcleaner_token="hankcc2023")

#keep an openai json response in the preds variable and can pass it to the autocode funciton directly if you want to test things that happen after openai without sending it to openai again
# pass the preds variable in to the preds_raw_json var in the autocode function to use it
preds = SampleGPTResponses.sample_gpt_response_list[0]
#res = ac.autocode(docs, specialty=Specialty.ANESTHESIA, preds_raw_json=preds)
res = ac.autocode(docs_dict, specialty=Specialty.ANESTHESIA)


print("FINAL RESULTS:")
print(json.dumps(res, indent=2))

sys.exit()
#%%


#%%


#%%
# Create a dataframe
df = pd.json_normalize(data, 's', ['a', 'i', 'm', 'prediction_id'], record_prefix='s_')


# %%
df

# %%

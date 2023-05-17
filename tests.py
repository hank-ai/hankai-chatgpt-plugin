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
    def __init__(self, specialty=Specialty.ANESTHESIA, year=2023, claimcleaner_token=""):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        print(f"Using openai api_key={openai.api_key}")
        self.asacwdf = pd.read_csv("CROSSWALKs-ALL.csv", dtype={'CPT Procedure Code':str, 'CPT Anesthesia Code':str})
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
            "anesthesia": "given the following medical note, predict " + \
                "lists of the surgical cpts (s), anesthesia cpts (a), icd codes (i), and the billing modifiers (m) and confidence (c) from 0.0 to 1.0 as json. only return the json object. use json keys s, a, i, m, c. ",
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
    

    #returns a list of the cleaned up claim predictions
    def _processLineItemSpecialty(self, openai_json, specialty:Specialty=None, dropUncrosswalkedASAs=True):
        if specialty is None: specialty=self.specialty
        # Create empty list to contain the prediction lists for the claim line items
        preds = []
        for idx, d in enumerate(openai_json): #iterating over independent prediction responses
            thisclaim = []
            # For each surgical CPT
            for s in d['s']:
                td = d.copy() #need to make copy or doesn't update dict properly
                td['s'] = s
                if specialty == Specialty.ANESTHESIA: 
                    #occasionally gpt returns an asa list. pick just the first one
                    if isinstance(td['a'], list): td['a'] = td['a'][0]
                    #check asa crosswalk. remove asa code if doesn't match to cpt code
                    td['a'] = self.checkASACW(td, year=self.year, dropUncrosswalked=1) #[x for x in d['a'] if x in validasas and not len(validasas)==0]               
                else:
                    td['a'] = ""
                # Add row to dataframe with other fields repeated
                thisclaim.append({
                    's': s,
                    'a': td['a'],
                    'i': td['i'],
                    'm': td['m'],
                    'c': td['c']
                })
            preds.append(thisclaim)
        return preds
    
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
        # find the JSON part using regex
        match = re.search(r'{.*}|\[.*\]', json_string, re.DOTALL)
        if match:
            fixed = match.group()
        try: 
            json.loads(fixed)
        except json.JSONDecodeError:
            raise MalformedOpenaiJSON(f"The JSON from openai seems to be malformed.\n{repr(json_string)}")
        return fixed
    
    def handleCands(self, openai_json:list, year:int=2023, specialty:Specialty=None):
        if specialty is None: specialty=self.specialty
        res = []
        if isinstance(openai_json, dict): openai_json = [openai_json]
        print(openai_json)
        openai_json = self._processLineItemSpecialty(openai_json, specialty=specialty, dropUncrosswalkedASAs=1)
        print(openai_json)
        df = pd.DataFrame(openai_json)
        #if self.specialty=='anesthesia': df['a'] = df.apply(lambda row: self.checkASACW(row, year=year), axis=1) 
        res = df.to_json(orient="records", indent=2)
        return openai_json

    #submits this_prompt string to gpt for predictions. 
    #depending upon specialty, will use a different openai prompt
    #gptmodel can be 3.5turbo or 4 currently
    def query_openai(self, this_prompt:str, specialty:Specialty=None, gptmodel:GPTModel=GPTModel.GPT3_5):
        if specialty==None: specialty=self.specialty
        print(f"Sending request to openai ...\nSPECIALTY={specialty.value}\nPROMPT={self.pre_prompts.get(specialty.value)}\n CONTENT={this_prompt}")
        #response = openai.Completion.create(model="text-davinci-003", prompt="write me a short poem about a bird", temperature=0, max_tokens=7)
        #### text-davinci-003 ####
        # response = openai.Completion.create(
        #     model="text-davinci-003", 
        #     prompt=f"{pre_prompt}\n{this_prompt}", 
        #     temperature=0, max_tokens=50)

        #### gpt-3.5-turbo or gpt-4
        response = openai.ChatCompletion.create(
            model=gptmodel.value, #"gpt-4", #"gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.pre_prompts.get(specialty.value)},
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
    def cureClaim(self, line_items, line_item_cures):
        for liidx, lic in enumerate(line_item_cures):
            for issue_type, cure_list in lic.items():
                for cure in cure_list:
                    liitem = line_items[liidx][issue_type] 
                    print(liidx, issue_type, cure)
                    if cure[1:].strip()=="": continue
                    if cure[0]=='+': #add a thing
                        if isinstance(liitem, list) and cure[1:] not in liitem: #add to list
                            liitem.append(cure[1:])
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
    
    def checkAndCureWithClaimCleaner(self, openai_json):
        claim = SimpleAutocoder.convertForCC(openai_json)
        print("claim:", json.dumps(claim))
        cc_response = self.postToClaimCleaner(claim)
        
        print("cc_response:",json.dumps(cc_response, indent=2))
        cure_list = self.buildCureList(cc_response)
        print("li_cures: ", cure_list)
        cured_claim = self.cureClaim(claim, cure_list)
        return cured_claim
    
    
    def postToClaimCleaner(self, claim):    
        #update the claimcleaner json body to hold the predicted line items
        cc_body = self.cc_body
        cc_body['claims'][0]['line_items'] = claim
        response = requests.post(self.CC_URL, json=json.dumps(cc_body))
        if response.status_code == 200:
            res = response.json()
            results = res.get('RESULTS')
            errs = res.get('ERRORS')
            md = res.get('METADATA')
        else:
            print("Request failed with status code", response.status_code)

        # print(json.dumps(cc_body, indent=2))
        # print(json.dumps(results, indent=2))
        claimcleaner_response = results.get('claims')[0]
        return claimcleaner_response

    def autocode(self, documents, specialty:Specialty=None):
        if specialty==None: specialty=self.specialty
        preds = {}
        for i, doc in enumerate(documents):
            this_prompt = ' '.join(doc.split()) #strip all extra spaces and newlines
            cands = self.query_openai(this_prompt, specialty=specialty)
            res = self.handleCands(cands, specialty=specialty)
            preds[i] = res
        print(f"***AUTOCODE RESULTS:\n{json.dumps(preds, indent=2)}")
        all_line_items = []
        for i, line_items in preds.items():
            all_line_items += line_items
        cleaned_line_items = self.checkAndCureWithClaimCleaner(all_line_items)
        print(f"***AFTER CLEANING RESULTS:\n{json.dumps(cleaned_line_items, indent=2)}")
        return preds

docs = [SampleDocuments.anesthesia[0]] #, SampleDocuments.anesthesia_nerveblock[0]]
ac = SimpleAutocoder()
res = ac.autocode(docs, specialty=Specialty.ANESTHESIA)

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

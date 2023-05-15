#%%
import json, requests
import pandas as pd
CC_URL = "https://claimcleaner.api.hank.ai/clean/1.0.1/hankcc2023"
cc_body = {
    "cleaners": ["all"], #list of cleaners. i.e. ['frc','acc','nlcd']. from short abbreviation in parenthesis above
    "claims": [
        {
            "dos": "2022-02-07", #date of service. yyyy-mm-dd expected
            "category": "Practitioner Services", #choice of Practitioner Services, DME Services, or Hospital Outpatient Services
            "frequency_cutoff": "0.02", # the % frequency to be considered abnormal coding for the frequency checker. range 0.0 to 1.0
            "zipcode": "29477", #zip code. 5 digits. if given, will supercede county+state if those are given as well. used for NCD and LCD edits
            "county": "", #county. used for NCD and LCD edits #optional
            "state": "", #state. 2 char version. used for NCD and LCD edits #optional
            "line_items":[ #list of line items for the claim
                # {
                #     "cpt": "23472", #cpt code. 5 digits
                #     "anescpt": "00400", #anesthesia cpt code (optional). 5 digits
                #     "mods": [""], #list of modifier codes (i.e. LT, RT, 59, 26, etc)
                #     "icds": ["k22.22"] #list of icd10 codes, with decimal
                # },
                # {"cpt": "93312", "mods": ["59"], "icds": []}, #tee
                # {"cpt": "64415", "mods": [], "icds": []},
                # {"cpt": "45378", "mods": ["53"], "icds": []},
                # {"cpt": "45378", "mods": [], "icds": ["K92.1"]},
                # {"cpt": "453711", "mods": ["59"], "icds": ["K9.1"]},
            ]
        }
    ]
}
t = "[\n  {\n    \"s\": [\"27447\", \"26952\"],\n    \"a\": [\"01402\"],\n    \"i\": [\"M17.11\", \"M19.041\", \"E08.621\", \"I48.91\", \"N18\"],\n    \"m\": [\"RT\"]\n  },\n  {\n    \"s\": [\"27447\", \"26952\"],\n    \"a\": [\"01402\"],\n    \"i\": [\"M17.11\", \"M19.041\", \"E08.621\", \"I48.91\", \"N18.9\"],\n    \"m\": [\"RT\"]\n  }\n]"
data = json.loads(t)

def makeCCLineItems(openai_json):
    # Create empty list to contain the prediction lists for the claim line items
    preds = []
    # Iterate over data
    for idx, d in enumerate(data):
        thisclaim = []
        # For each surgical CPT
        for s in d['s']:
            # Add row to dataframe with other fields repeated
            thisclaim.append({
                'cpt': s,
                'anescpt': d['a'][0] if len(d['a'])>0 else None,
                'icds': d['i'],
                'mods': d['m']
            })
        preds.append(thisclaim)
    return preds

claims = makeCCLineItems(data)
print(json.dumps(claims, indent=2))

#%%
cc_body['claims'][0]['line_items'] = claims[0]
response = requests.post(CC_URL, json=json.dumps(cc_body))
if response.status_code == 200:
    res = response.json() #json.loads(response.data.decode('utf-8'))
    results = res.get('RESULTS')
    errs = res.get('ERRORS')
    md = res.get('METADATA')
else:
    print("Request failed with status code", response.status_code)
print(json.dumps(cc_body, indent=2))
print(json.dumps(results, indent=2))
claimcleaner_response = results.get('claims')[0]

#%%
li_cures = []
claim = claims[0].copy()
for li in claimcleaner_response.get("line_items"):
    cures = {"surgcpt": [], "anescpt":[], "icds":[], "mods":[]}
    liidx = li.get('line_item_index')
    for k, v in li.items():
        if isinstance(v, dict):
            issues = v.get("issues")
            for issue in issues:
                for issue_type, issue_cure in issue.get("issue_cure").items():
                    if issue_type=='surgcpt': issue_type='cpt'
                    if issue_type=='anescpts': issue_type='anescpt'
                    cures[issue_type] += (issue_cure)
    li_cures.append(cures)
    print(f"liidx={liidx}. cures={cures}")
print('original claim: ', claim)
print("li_cures: ", li_cures)
#takes a list of a claim's line items as line_items and a list of corresponding line_item_cures from the claim cleaner api response
# and returns a list of line items that have been modified based upon the claim cleaner cure recommendations
def cureClaim(line_items, line_item_cures):
    for liidx, lic in enumerate(line_item_cures):
        for issue_type, cure_list in lic.items():
            for cure in cure_list:
                liitem = line_items[liidx][issue_type] 
                print(issue_type, cure)
                if cure[0]=='+': #add a thing
                    if isinstance(liitem, list): #add to list
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
print(cureClaim(claim, li_cures))
#%%
# Create a dataframe
df = pd.json_normalize(data, 's', ['a', 'i', 'm', 'prediction_id'], record_prefix='s_')


# %%
df

# %%

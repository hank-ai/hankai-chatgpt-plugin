import json, os, requests, re
import openai
import pandas as pd
import quart
import quart_cors
import urllib.parse
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")
HOST_URL = "https://example.com"
CC_URL = "https://claimcleaner.api.hank.ai/clean/1.0.1/hankcc2023"

# Keep track of todo's. Does not persist if Python session is restarted.
_PARAMS = {}
#     "dos": "2021-07-07",
#     "category": "Practitioner Services",
#     "frequency_cutoff": "0.04",
#     "zipcode": "29477",
#     "line_items":[
#         {"cpt": "00560", "mods": [], "icds": []}, #tavr
#         {"cpt": "64415", "mods": [], "icds": []},
#         {"cpt": "76942", "mods": ["53"], "icds": []},
#     ]
# },
# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")
print(f"Using openai api_key={openai.api_key}")

pre_prompt = "you are a medical coder. " + \
    "respond with a list of surgical cpt codes, anesthesia cpt codes, icd10 codes, " + \
    "and billing modifiers. always include a code. you do not include notes, headers, or any other text." + \
    "respond ONLY with a json object with keys surgcpt, anescpt, icd, mod. don't use cpt code 00740 or 00810"
pre_prompts = {
    "anesthesia": "given this surgical note, return 1 json list with no extra spaces or newlines containing two independent attempts to predicted all the surgical cpts (s), anesthesia cpts (a), icds (i), and modifiers (m) as lists. include a confidence (c) 0.0 to 1.0 for each attempt. no extra words.",
    # 'anesthesia': "given the following surgical operative report, return a single json object with no headers/footers, or extra spaces that contains 3 seperate prediction attempts as seperate items in the parent json list " + \
    #     "for the combination of surgical cpt, anesthesia cpt, list of icds, any applicable modifiers, and prediction confidence. use keys surgcpt, anescpt, icds, mods, conf. Please apply the ASA crosswalk rules and the NCCI edits.",
        # "return 3 different attempts to do the predictions as a list of seperate prediction groups in the json. make sure everything is in one json object.",
    'radiology': "given the following radiology report, return a single json object with no headers/footers that contains 3 seperate prediction attempts as seperate items in the parent json list " + \
        "for the combination of radiology procoedure cpt, list of icds, any applicable modifiers, and a numerical prediction confidence. use keys cpt, icds, mods, conf.",
        # "return 3 different attempts to do the predictions as a list of seperate prediction groups in the json. make sure everything is in one json object.",
    'surgical': "here is a surgical operative report. return exactly 1 json object with no extra spaces. predict the unique surgical cpts, icds, and modifiers. " + \
        "return 2 different prediction attempts as a list of 1 grouped list in the json. use keys surgcpt, anescpt, icds, mods. no descriptions.",
}

asacwdf = pd.read_csv("CROSSWALKs-ALL.csv", dtype={'CPT Procedure Code':str, 'CPT Anesthesia Code':str})
print(asacwdf.sample(5))
#returns the asa codes mapped to given cptcode in the ASA Crosswalk datafile
#always returns a list
#if alternates is set, will return the alternate codes as well (first code in list will be primary, then alternates)
def getCrosswalkedASAs(cptcode, alternates=False, quiet=True, year=2022):
    rval=[]
    if len(asacwdf)>0:
        cptcode = str(cptcode).replace('.', '')  
        cptcode = cptcode.zfill(5).strip()
        rdf = asacwdf[(asacwdf['Year']==year) & (asacwdf['CPT Procedure Code'].str.match(cptcode))]
        if not quiet: print('Finding cpt {} in ASA crosswalk'.format(cptcode))
        if len(rdf)>0:
            rval = [str(int(x)).zfill(5) for x in list(rdf['CPT Anesthesia Code'].dropna()) if (~pd.isnull(x) and x != '')]
            if alternates:
                for alt in str(rdf.iloc[0]['Alternates']).split(','):
                    if alt != '': rval.append(alt)
        rval = [str(x).zfill(5) for x in rval if float(x)>0] #don't include the -0004 codes
        if not quiet: print("rdf: ", rdf)
    return rval

def fix_json(json_string):
    # Remove trailing commas
    fixed = re.sub(",\s*}", "}", json_string)
    fixed = re.sub(",\s*\]", "]", fixed)
    return fixed

def query_openai(specialty, this_prompt):
    print(f"Sending request to openai ...\nSPECIALTY={specialty}, CONTENT={this_prompt}")
    #response = openai.Completion.create(model="text-davinci-003", prompt="write me a short poem about a bird", temperature=0, max_tokens=7)
    #### text-davinci-003 ####
    # response = openai.Completion.create(
    #     model="text-davinci-003", 
    #     prompt=f"{pre_prompt}\n{this_prompt}", 
    #     temperature=0, max_tokens=50)

    #### gpt-3.5-turbo or gpt-4
    response = openai.ChatCompletion.create(
        model="gpt-4", #"gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": pre_prompts.get(specialty)},
            {"role": "user", "content": this_prompt}
        ],
        #temperature=0, max_tokens=50
        )
    print(f"**RAW RESPONSE:**\n{response}")
    choices = response.get('choices')
    firstchoice = choices[0]
    json_response = fix_json(firstchoice.get('message', {}).get('content'))
    #print(f"**JSON RESPONSE:**\n{json_response}")
    
    try:
        cands = json.loads(json_response)
    except: 
        print("ERROR loading the message as a json object. Probably malformed.")
        cands = {}
    return cands

#checks a row in a dataframe to see if the anescpt (a) in that row is in the crosswalk for the given surgcpt (s).
#returns anescpt value if it is in the crosswalk for that surgcpt. if not, will return the first anesthesia cpt code listed in the crosswalk
def checkASACW(row, year=2023, dropUncrosswalked=True):
    cwasas = getCrosswalkedASAs(row['s'], alternates=True, year=year, quiet=1)
    if len(cwasas)>0:
        if row['a'] not in cwasas:
            print(f"swapping {row['a']} for {cwasas[0]} from crosswalk")
            return cwasas[0]
    elif dropUncrosswalked:
        return ""
    return row['a']

@app.post("/autocode/<string:username>")
async def autocode(username):
    if username not in _PARAMS:
        _PARAMS[username] = {"dos": "2023-01-01", "specialty":"anesthesia", "category": "Practitioner Services", "frequency_cutoff": "0.04", "zipcode": "29201", "patient_age": None}
    
    request = await quart.request.get_json(force=True)
    actext = request['autocodetext']
    if 'dos' in request.keys():
        _PARAMS[username]['dos'] = request["dos"]
    if 'zipcode' in request.keys():
        _PARAMS[username]['zipcode'] = request["zipcode"]
    if 'patient_age' in request.keys():
        _PARAMS[username]['patient_age'] = request["patient_age"]
    if 'specialty' in request.keys(): 
        _PARAMS[username]['specialty'] = request["specialty"]

    print(_PARAMS)
    print(actext)
    #this_prompt = f"Procedure: {sd['Description']}\nDiagnosis: {sd['Diagnoses']}\nAge: {sd['Age']}.\nYear performed: {sd['Year']}"
    ud = _PARAMS[username]
    this_prompt = f"Patient age: {ud['patient_age']}\nMedical Document: {actext}"
    cands = query_openai(ud['specialty'], this_prompt)
    res = handleCands(cands)
    print("RETURNING: ")
    print(res)
    return quart.Response(response=json.dumps(res), status=200)

    # query = request.args.get("query")
    # res = requests.get(
    #     f"{HOST_URL}/api/v1/players?search={query}&page=0&per_page=100")
    # body = res.json()
    # return quart.Response(response=json.dumps(body), status=200)

def groupAnes(df):
    return 0

def handleCands(cands:dict, year:int=2023, specialty='anesthesia'):
    res = []
    df = pd.DataFrame(cands)
    # Add prediction_id based on index
    # for i, d in enumerate(cands):
    #     d['prediction_id'] = i+1
    # df = pd.json_normalize(cands, 's', ['a', 'i', 'm', 'prediction_id'], record_prefix='s_')

    
    if specialty=='anesthesia': df['a'] = df.apply(lambda row: checkASACW(row, year=year), axis=1) 
    res = df.to_json(orient="records", indent=2)
    return res

def startup_test():
    actexts = {"anesthesia_long": """
        Patient: Smith, Jimithy X\nDate of Birth: 01/01/55\nDate of Procedure: 08/06/20\nSurgeon: Wamer Commodore Baker, MD\nAnesthesiologist: Michael Daman Smithson, MD\nProcedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
Diagnosis: RIGHT KNEE OSTEOARTHRITIS\n
ANESTHESIA: General, with peripheral nerve block administered by Dr. Michael Daman Smithson, MD. Fentanyl and ropivacaine were administered for pain management.\n
FINDINGS: Severe degenerative changes of the right knee consistent with osteoarthritis.\n
PROCEDURE DETAILS: The patient was brought to the operating room and placed supine on the operating table. After successful induction of anesthesia, the right leg was prepped and draped in the usual sterile fashion. 
A tourniquet was applied to the right upper thigh. A standard midline incision was made over the knee, and arthrotomy was performed.\n\nSevere osteoarthritic changes were noted. The degenerated portions of the knee joint were resected. 
Measurements were made, and the appropriate sized prosthetic components were selected. The prosthetic knee joint was then placed without complication.\n\nThe wound was thoroughly irrigated, and the joint was checked for appropriate alignment and range of motion. Hemostasis was achieved, and the joint capsule and skin were closed in layers. 
We also removed the right 4th finger just proximal to the distal interphalangeal joint via a guillatine method due to unhealing chronic wound. 
The tourniquet was released, and the patient was awakened from anesthesia.
        PMH: atrial fibrillation, diabetes mellitus on insulin, ckd
        """,
        "anesthesia": """
        Procedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
Diagnosis: RIGHT KNEE OSTEOARTHRITIS\n
ANESTHESIA: General, with peripheral nerve block administered by Dr. Michael Daman Smithson, MD.\n
FINDINGS: Severe degenerative changes of the right knee consistent with osteoarthritis.\n
PROCEDURE DETAILS: The patient was brought to the operating room and placed supine on the operating table. After successful induction of anesthesia, the right leg was prepped and draped in the usual sterile fashion. 
A tourniquet was applied to the right upper thigh. A standard midline incision was made over the knee, and arthrotomy was performed.\n\nSevere osteoarthritic changes were noted. The degenerated portions of the knee joint were resected. 
Measurements were made, and the appropriate sized prosthetic components were selected. The prosthetic knee joint was then placed without complication.\n\nThe wound was thoroughly irrigated, and the joint was checked for appropriate alignment and range of motion. Hemostasis was achieved, and the joint capsule and skin were closed in layers. 
We also removed the right 4th finger just proximal to the distal interphalangeal joint via a guillatine method due to unhealing chronic wound. 
The tourniquet was released, and the patient was awakened from anesthesia.
        PMH: atrial fibrillation, diabetes mellitus on insulin, ckd
        """,
        "surgical":
        """
        Patient: Smith, Jimithy X\nDate of Birth: 01/01/55\nDate of Procedure: 08/06/20\nSurgeon: Wamer Commodore Baker, MD\nAnesthesiologist: Michael Daman Smithson, MD\nProcedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
Diagnosis: RIGHT KNEE OSTEOARTHRITIS\n\nPREOPERATIVE DIAGNOSIS: Right knee osteoarthritis\nPOSTOPERATIVE DIAGNOSIS: Right knee osteoarthritis\nPROCEDURE PERFORMED: Right total knee arthroplasty\n\n
ANESTHESIA: General, with peripheral nerve block administered by Dr. Michael Daman Smithson, MD. Fentanyl and ropivacaine were administered for pain management.\n\n
FINDINGS: Severe degenerative changes of the right knee consistent with osteoarthritis.\n\n
PROCEDURE DETAILS: The patient was brought to the operating room and placed supine on the operating table. After successful induction of anesthesia, the right leg was prepped and draped in the usual sterile fashion. 
A tourniquet was applied to the right upper thigh. A standard midline incision was made over the knee, and arthrotomy was performed.\n\nSevere osteoarthritic changes were noted. The degenerated portions of the knee joint were resected. 
Measurements were made, and the appropriate sized prosthetic components were selected. The prosthetic knee joint was then placed without complication.\n\nThe wound was thoroughly irrigated, and the joint was checked for appropriate alignment and range of motion. Hemostasis was achieved, and the joint capsule and skin were closed in layers. 
We also removed the right 4th finger just proximal to the distal interphalangeal joint via a guillatine method due to unhealing chronic wound of the distal finger. 
The tourniquet was released, and the patient was awakened from anesthesia.
        PMH: atrial fibrillation, diabetes mellitus on insulin, ckd
        """,
        "radiology": """
    History: Abdominal aortic aneurysm.
Technique: Oral contrast was administered orally to the patient. The patient was fully informed of the
nature and risks of intravenous contrast. Written informed consent was granted. Non-ionic contrast
was administered intravenously without complication. A helical CT was acquired from the lung bases
through the symphysis pubis. Maximum intensity pixel images were reconstructed and reviewed as
well. Images were reviewed in lung windows, bone windows, and abdominal windows. Delayed
images were also acquired.
Findings: Abdomen: The lung bases are clear, and the heart is not enlarged. There is no aneurysmal
dilatation of the aorta despite extensive vascular calcification. Bony structures reflect the patient's
age and the muscular structures are all intact.
The liver, spleen, adrenal glands, pancreas, and gallbladder are all morphologically normal with
normal enhancement. A 3.1 cm exophytic hypodense mass is seen laterally of the left kidney; this
lesion appears solid and hypervascular, suspicious for renal cell carcinoma. There is no free air, free
fluid, or inflammatory change. The stomach and visualized portions of the small bowel and large
bowel are normal. There is no portal, retroperitoneal, or mesenteric adenopathy. There is no omental
caking.
Pelvis: The ureters are normal in course and caliber. The bladder has a normal configuration. The
uterus is unremarkable but neither ovary is visualized.
Bony muscular and vascular structures reflect the patient's age without aneurysmal dilatation of
arterial structures. There is no free air, free fluid, or inflammatory change. The visualized portions of
the small bowel are normal. Diverticulosis is present in the sigmoid colon without radiographic
evidence for diverticulitis. There is no pelvic or inguinal adenopathy.
Impression: Abdomen:
1. 3.1 cm hypodense but solid exophytic lesion of the left kidney suspicious for renal cell carcinoma.
2. Vascular calcification but no evidence for aneurysmal dilatation of the aorta.
Pelvis: Diverticulosis without radiographic evidence for diverticulitis
"""
    }

    specialty = "anesthesia" #radiology anesthesia surgical
    this_prompt = f"Patient age: 58\nMedical Document: {actexts.get(specialty)}"
    

    cands = query_openai(specialty, this_prompt)


    res = handleCands(cands, specialty=specialty)
    print("RETURNING: ")
    print(res)

# async def get_games():
#     query_params = [("page", "0")]
#     limit = request.args.get("limit")
#     query_params.append(("per_page", limit or "100"))
#     start_date = request.args.get("start_date")
#     if start_date:
#         query_params.append(("start_date", start_date))
#     end_date = request.args.get("end_date")

#     if end_date:
#         query_params.append(("end_date", end_date))
#     seasons = request.args.getlist("seasons")

#     for season in seasons:
#         query_params.append(("seasons[]", str(season)))
#     team_ids = request.args.getlist("team_ids")

#     for team_id in team_ids:
#         query_params.append(("team_ids[]", str(team_id)))

#     res = requests.get(
#         f"{HOST_URL}/api/v1/games?{urllib.parse.urlencode(query_params)}")
#     body = res.json()
#     return quart.Response(response=json.dumps(body), status=200)


# @app.get("/stats")
# async def get_stats():
#     query_params = [("page", "0")]
#     limit = request.args.get("limit")
#     query_params.append(("per_page", limit or "100"))
#     start_date = request.args.get("start_date")
#     if start_date:
#         query_params.append(("start_date", start_date))
#     end_date = request.args.get("end_date")

#     if end_date:
#         query_params.append(("end_date", end_date))
#     player_ids = request.args.getlist("player_ids")

#     for player_id in player_ids:
#         query_params.append(("player_ids[]", str(player_id)))
#     game_ids = request.args.getlist("game_ids")

#     for game_id in game_ids:
#         query_params.append(("game_ids[]", str(game_id)))
#     res = requests.get(
#         f"{HOST_URL}/api/v1/stats?{urllib.parse.urlencode(query_params)}")
#     body = res.json()
#     return quart.Response(response=json.dumps(body), status=200)


# @app.get("/season_averages")
# async def get_season_averages():
#     query_params = []
#     season = request.args.get("season")
#     if season:
#         query_params.append(("season", str(season)))
#     player_ids = request.args.getlist("player_ids")

#     for player_id in player_ids:
#         query_params.append(("player_ids[]", str(player_id)))
#     res = requests.get(
#         f"{HOST_URL}/api/v1/season_averages?{urllib.parse.urlencode(query_params)}")
#     body = res.json()
#     return quart.Response(response=json.dumps(body), status=200)


@app.get("/hank_logo.png")
async def plugin_logo():
    filename = 'hank_logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    print("Running startup test ...")
    startup_test()
    print("DONE with startup tests.")
    main()

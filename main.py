#%%
import json, os, requests, re
import openai
import pandas as pd
import quart
import quart_cors
import urllib.parse
from quart import request, send_from_directory
import SimpleAutocoder 
import flask
import flask_cors


app = quart_cors.cors(quart.Quart(__name__), allow_origin="*") #, allow_origin="https://chat.openai.com")
#app = flask_cors.CORS()

HOST_URL = "https://hank.ai"
CC_URL = "https://claimcleaner.api.hank.ai/clean/1.0.1/hankcc2023"

ac = SimpleAutocoder.SimpleAutocoder()

# Keep track of user's parameters. Does not persist if Python session is restarted.
_PARAMS = {}
@app.post("/autocode/<string:username>/<string:token>")
async def autocode(username, token):
    if username not in _PARAMS:
        _PARAMS[username] = {"dos": "2023-01-01", "specialty":"anesthesia", "category": "Practitioner Services", "frequency_cutoff": "0.04", "zipcode": "29201", "patient_age": None}
    
    request = await quart.request.get_json(force=True)
    print("request received. details:")
    print(json.dumps(request, indent=2))
    actext = request['autocodetext']
    note_type = request.get("doc_type", "")
    if 'dos' in request.keys():
        _PARAMS[username]['dos'] = request["dos"]
    if 'zipcode' in request.keys():
        _PARAMS[username]['zipcode'] = request["zipcode"]
    if 'patient_age' in request.keys():
        _PARAMS[username]['patient_age'] = request["patient_age"]
    if 'specialty' in request.keys(): 
        _PARAMS[username]['specialty'] = request["specialty"]

    docs_dict = {SimpleAutocoder.DocType(note_type):[actext]}
    coding_specialty = SimpleAutocoder.Specialty(request.get('specialty'))
    if token!="hankcc2023":
        return quart.Response("Unauthorized access. Please enter your token and send request again. Contact support@hank.ai for access.", status=500)

    print(f"token: {token}")
    print(f"docs_dict: {docs_dict}")
    print(f"coding_specialty: {coding_specialty}")
    res = ac.autocode(documents_dictionary=docs_dict, coding_specialty=coding_specialty, 
                zipcode=request.get("zipcode", ""))
    
    #this_prompt = f"Procedure: {sd['Description']}\nDiagnosis: {sd['Diagnoses']}\nAge: {sd['Age']}.\nYear performed: {sd['Year']}"
    ud = _PARAMS[username]
    print("RETURNING: ")
    print(res)
    return quart.Response(response=json.dumps(res), status=200)

    # query = request.args.get("query")
    # res = requests.get(
    #     f"{HOST_URL}/api/v1/players?search={query}&page=0&per_page=100")
    # body = res.json()
    # return quart.Response(response=json.dumps(body), status=200)

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

# @app.get("/hank_logo.png")
# async def plugin_logo():
#     filename = 'hank_logo.png'
#     return await quart.send_file(filename, mimetype='image/png')

# @app.get("/.well-known/ai-plugin.json")
# async def plugin_manifest():
#     host = request.headers['Host']
#     with open("./.well-known/ai-plugin.json") as f:
#         text = f.read()
#         return quart.Response(text, mimetype="text/json")
    
# @app.route('/')
# def hello_world():
#     return '<a href="https://hank.ai">HANK.ai</a> ChatGPT Medical Autocoding Plugin. Contact <a href="support@hank.ai">support@hank.ai</a> to obtain access.'

# @app.get("/openapi.yaml")
# async def openapi_spec():
#     host = request.headers['Host']
#     with open("openapi.yaml") as f:
#         text = f.read()
#         return quart.Response(text, mimetype="text/yaml")
@app.route('/')
async def root():
    return await send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
async def static_files(filename):
    return await send_from_directory('static', filename)

def main():
    #run localhost
    #app.run(debug=True, host="0.0.0.0", port=5003)
    
    #run for prod
    app.run(debug=True, host="0.0.0.0", port=443, certfile="fullchain.pem", keyfile="privkey.pem")

if __name__ == "__main__":
    print("Running startup test ...")
    #ac.test()
    print("DONE with startup tests.")
    main()

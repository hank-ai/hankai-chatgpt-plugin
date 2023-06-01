# HANK.ai ChatGPT Medical Coding plugin quickstart

Get the HANK.ai Medical Autocoding plugin up and running in under 5 minutes using Python. If you do not already have plugin developer access, please [join the waitlist](https://openai.com/waitlist/plugins).

## Setup

To install the required packages for this plugin, run the following command:

```bash
conda create --name hank-mc-llm python=3.9
conda activate hank-mc-llm
pip install -r requirements.txt
```

<br><br>

# To run locally (via the 'Develop your own plugin' button on the plugin store): 
Modify main.py, near the bottom, and do the following:

Uncomment:
```python
#app.run(debug=True, host="0.0.0.0", port=5003)
```
And comment out: (by adding a # in front of the line)
```python
app.run(debug=True, host="0.0.0.0", port=443, certfile="fullchain.pem", keyfile="privkey.pem")

```

Then run:
```bash
conda activate hank-mc-llm
python main.py
```

or run
```
run.bat
```


Once the local server is running:

1. Navigate to https://chat.openai.com. 
2. Select GPT4. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5003` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start sending medical documents. DO NOT send any PHI.
You can use the token hankcc2023 if needed.

<br><br>
# To run in cloud for production (via the 'Install unverivied plugin' button on the plugin store): 
Modify main.py, near the bottom, and do the following:

Comment out the following line: (by adding a # in front of the line)
```python
app.run(debug=True, host="0.0.0.0", port=5003)
```
Uncomment the following line: (this assumes you're serving via the url https://chatgpt.api.hank.ai) since that is the url the certfile and keyfiles are for
```python
app.run(debug=True, host="0.0.0.0", port=443, certfile="fullchain.pem", keyfile="privkey.pem")

```

Then run:
```bash
conda activate hank-mc-llm
python main.py
```

or run
```
run.bat
```


Once the local server is running:

1. Navigate to https://chat.openai.com. 
2. Select GPT4. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Install unverified plugin"
5. Enter in `chatgpt.api.hank.ai`. Select "Find manifest file".

The plugin should now be installed and enabled! You can start sending medical documents. DO NOT send any PHI.
You can use the token hankcc2023 if needed.



## Getting help

If you run into issues or have questions building a plugin, contact jack.neil@hank.ai 

from fastapi import FastAPI, Request
from vi_lang.code_bart.inference import inference
from vi_lang.code_bart.inference import prepare_inference
import json
import os
import torch

app = FastAPI()

#==============================================================================
# global variables
#==============================================================================
BASE_PATH = os.getcwd()
CONFIG_PATH = f"{BASE_PATH}/vi_lang/bart_models/model_5/config/config_0000045210.json"
MODEL_PATH = f"{BASE_PATH}/vi_lang/bart_models/model_5/model"
TOKENIZER_PATH = f"{BASE_PATH}/vi_lang/dataset/tokenizer.json"
#==============================================================================

#==============================================================================
# functions
def set_config(config):
    config["model_folder_name"] = MODEL_PATH
    config["tokenizer_tgt_path"] = TOKENIZER_PATH
    config["tokenizer_src_path"] = TOKENIZER_PATH
    config["device"] = "cuda" if torch.cuda.is_available() else "cpu"
    return config
#==============================================================================

#==============================================================================
# read config
with open(CONFIG_PATH) as f:
    config = json.load(f)
    config = set_config(config)

# clean data
def clean_data(text):
    text = " ".join(text.split())
    text = text.replace("  ", " ")
    text = text.strip()
    text = text.lower()
    return text

# get prepare_inference
prepare_inference_model = prepare_inference(config)
#================================================================

@app.get("/")
async def root(request: Request):
    return {"message": "Welcome to the ViLang API", "config": config}

@app.post("/vi_lang")
async def vi_lang(request: Request):
    data = await request.json()
    
    src = data.get("src", "")
    src = clean_data(src)
    print(f"{src=}")
    
    if not src:
        return {"error": "No source text provided."}
    
    result = inference(src, config['beams'][0], prepare_inference_model)
    
    return {"result": result}

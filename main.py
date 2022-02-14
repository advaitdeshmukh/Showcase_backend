import json
import openai
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sql_gpt import sql_GPT
import re
# server_url = "http://127.0.0.1:8000"

# with open('config.json') as f:
#     data = json.load(f)
# openai.api_key = data['API_KEY']

# with open('schema.json') as f:
#     schema = json.load(f)
    
import os

openai.api_key = os.getenv("API_KEY", "optional-default")

app = FastAPI(title="GPT-3 Applications",
    description="API Docs",
    version="1.0.0",)

class SQL_Testing(BaseModel):
    prompt: str
    schemajson: str

   
@app.post("/ask_sql_gpt")
def user_endpoint1(item:SQL_Testing):
    prefix="### Postgres SQL tables, with their properties:\n#"
    schema = json.loads(item.schemajson)
    for element in schema['tables']:
        prefix=prefix+'\n#'+element['name']+'('+','.join(element['rows'])+')'

    prefix=prefix+"\n#\n### "


    gpt_sql = sql_GPT(engine="davinci-codex",
            input_prefix=prefix,
            input_suffix="\nSELECT",
            temperature=0,
            max_tokens=300,
            stop=["#", ";"])

    result = gpt_sql.get_top_reply(item.prompt)
    return result

def window(text_list, window_size):
    final_list = []
    for i in range(len(text_list)-window_size+1):
        try:
            interim = text_list[i:i+window_size]
            final_list.append(interim)
        except:
            pass
    print(final_list) 
    return final_list


def get_response_MOM(new_prompt):
    response = openai.Completion.create(
    engine="davinci-instruct-beta",
    prompt=new_prompt,
    temperature=0.25,
    max_tokens=100,
    top_p=1)
    return response

def isBlank (myString):
    if myString and myString.strip():
        #myString is not None AND myString is not empty or blank
        return False
    #myString is None OR myString is empty or blank
    return True

class MOM_Testing(BaseModel):
    windowSize: int
    l_text: list

@app.post("/ask_mom_gpt")
def user_endpoint2(item:MOM_Testing):
        print(item.l_text)
       
        text = list(filter(('\n').__ne__, item.l_text))
        text = list(filter(('  \n').__ne__, text))
        text = text[1:]
        print("text:")
        print(text)
        next_text = []
        for string in text:
            next_text.append(string.replace('\n',''))
        print("next text:")
        print(next_text)

        next_text_1=[]
        for string in next_text:
            if not isBlank(string):
                next_text_1.append(string)

        final_text_2 = []
        for i in range(len(next_text_1)):
            try:
                final_text_2.append(next_text_1[i] + " " + next_text_1[i+1])       
            except:
                pass
        final_text_2
        result = final_text_2[0::2]
        print("result:")
        print(result)

        preprocess = []
        for q in result:
            preprocess.append(re.split(' pm - | am - ',q)[1])
	    
        prompt_list = window(preprocess,item.windowSize)
        prompt_list.pop()
        con_list = []
        for prompt in prompt_list:
            new_prompt = '. '.join([str(sentence) for sentence in prompt])
            new_prompt = new_prompt + " \n\nSummarise the conversation"
            con_list.append(new_prompt)
	    
        response_list = []
        for prompt in con_list: 
            response_list.append(get_response_MOM(prompt))
	
        response = ""
        # print(response_list)
        for n, i in enumerate(response_list):
            response+='\n\nSummary of Window #'+str(n+1)+' '+i.choices[0].text
        
        # print(response)
        return response

class Tweet_Testing(BaseModel):
    prompt: str


@app.post("/ask_tweet_gpt")
def user_endpoint3(item:Tweet_Testing):
        # tweet = item.prompt
        prefix = "This is a tweet sentiment classifier\n\n\nTweet: \"I loved the new Batman movie!\"\nSentiment: Positive\n###\nTweet: \"I hate it when my phone battery dies.\"\nSentiment: Negative\n###\nTweet: \"My day has been 👍\"\nSentiment: Positive\n###\nTweet: \"This is the link to the article\"\nSentiment: Neutral\n###\nTweet: \""
        # prompt = prompt+tweet+"\"\nSentiment:"
        # sentiment=get_response_tweet(prompt)
        gpt_sql = sql_GPT(engine="davinci-codex",
            input_prefix=prefix,
            input_suffix="\"\nSentiment:",
            temperature=0.3,
            max_tokens=2,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["###"]
            )
        
        # print(response)
        result = gpt_sql.get_top_reply(item.prompt)
        return result

class Python_Code(BaseModel):
    code: str

@app.post("/fix_python_code")
def user_endpoint4(item:Python_Code):
        prefix="##### Fix bugs in the below function\n \n### Buggy Python\n"
        suffix="\n### Fixed Python"
        gpt_sql = sql_GPT(engine="davinci-codex",
            input_prefix=prefix,
            input_suffix=suffix,
            temperature=0,
            max_tokens=210,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["###"]
            )
        result = gpt_sql.get_top_reply(item.code)
        return result

@app.post("/explain_python_code")
def user_endpoint4(item:Python_Code):
        prefix=""
        suffix="\n\n\"\"\"\nHere's what the above class is doing:\n1."
        gpt_sql = sql_GPT(engine="davinci-codex",
            input_prefix=prefix,
            input_suffix=suffix,
            temperature=0,
            max_tokens=70,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\"\"\""]
            )
        result = gpt_sql.get_top_reply(item.code)
        return result

class Completion_prompt(BaseModel):
    prompt: str
    engine:str
    temperature:float
    response_length:int
    top_p:float
    frequency_penalty:float
    presence_penalty:float

@app.post("/gpt_complete")
def user_endpoint4(item:Completion_prompt):
        prefix=""
        suffix=""
        gpt_sql = sql_GPT(engine=item.engine,
            input_prefix=prefix,
            input_suffix=suffix,
            temperature=item.temperature,
            max_tokens=item.response_length,
            top_p=item.top_p,
            frequency_penalty=item.frequency_penalty,
            presence_penalty=item.presence_penalty,
            stop=["#","###"]
            )
        result = gpt_sql.get_top_reply(item.prompt)
        return result
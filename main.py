import json
import openai
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sql_gpt import sql_GPT
import re
# server_url = "http://127.0.0.1:8000"

with open('config.json') as f:
    data = json.load(f)
openai.api_key = data['API_KEY']

# with open('schema.json') as f:
#     schema = json.load(f)
    
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
            max_tokens=150,
            stop=["#", ";"])

    result = gpt_sql.get_top_reply(item.prompt)
    return result

def window(text_list, window_size):
    final_list = []
    for i in range(len(text_list)):
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

class MOM_Testing(BaseModel):
    windowSize: int
    l_text: list

@app.post("/ask_mom_gpt")
def user_endpoint2(item:MOM_Testing):
        text = list(filter(('\n').__ne__, item.l_text))
        text = list(filter(('  \n').__ne__, text))
        text = text[1:]
        next_text = []
        for string in text:
            next_text.append(string.replace('\n',''))
        # final_text_2 = []
        # for i in range(len(next_text)):
        #     try:
        #         final_text_2.append(next_text[i] + " " + next_text[i+1])       
        #     except:
        #         pass
        # final_text_2
        result = next_text
	
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

def get_response_tweet(new_prompt):
    response = openai.Completion.create(
    engine="davinci-codex",
    prompt=new_prompt,
    temperature=0.3,
    max_tokens=2,
    top_p=1.0,
    frequency_penalty=0.5,
    presence_penalty=0.0,
    stop=["###"]
    )
    return response

    #"This is a tweet sentiment classifier\n\n\nTweet: \"I loved the new Batman movie!\"\nSentiment: Positive\n###\nTweet: \"I hate it when my phone battery dies.\"\nSentiment: Negative\n###\nTweet: \"My day has been 👍\"\nSentiment: Positive\n###\nTweet: \"This is the link to the article\"\nSentiment: Neutral\n###\nTweet: \"This new music video blew my mind\"\nSentiment:"

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
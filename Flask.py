from flask import Flask
from flask import request, send_file,send_from_directory, render_template
import subprocess
import requests
import json
import time
import torch
from TTS.api import TTS
from datetime import datetime
import re
from flask_cors import CORS


ModelList = [
    "tts_models/multilingual/multi-dataset/xtts_v2",
    "tts_models/en/ek1/tacotron2", #Good
    "tts_models/en/ljspeech/tacotron2-DDC",
    "tts_models/en/ljspeech/tacotron2-DDC_ph", #Really Good
    "tts_models/en/ljspeech/glow-tts",
    "tts_models/en/ljspeech/speedy-speech",
    "tts_models/en/ljspeech/tacotron2-DCA",#Really Good
    "tts_models/en/ljspeech/vits",
    "tts_models/en/ljspeech/vits--neon", #Good
    "tts_models/en/ljspeech/fast_pitch",
    "tts_models/en/ljspeech/overflow",
    "tts_models/en/ljspeech/neural_hmm",
    "tts_models/en/sam/tacotron-DDC", #Good
    "tts_models/en/blizzard2013/capacitron-t2-c150_v2", #Good
    "tts_models/en/jenny/jenny", #Good
]


app = Flask(__name__)
cors = CORS(app,
            allow_origins=['*'],  # Allow all origins
            allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
            allow_headers=['Content-Type', 'Authorization'])

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
tts2 = TTS("tts_models/en/ljspeech/tacotron2-DDC_ph").to(device)

FormattedTime = datetime.today().strftime('%Y.%m.%d_%H.%M.%S')
OutputPath = ".\AudioFiles\\"+FormattedTime+"_"+"00"+".wav"


@app.route('/audio')
def audio():
    FileName = request.args.get('FileName')
    return send_from_directory('AudioFiles', FileName, as_attachment=False)

def CallCoqui(Message, iteration):
    FormattedTime = datetime.today().strftime('%Y.%m.%d_%H.%M.%S')
    OutputPath = ".\AudioFiles\\"+FormattedTime+"_"+"00"+".wav"
    #PowerShellFilePath = '"C:\Program Files\Decisions\PowershellScripts\CreateTTSFiles.ps1"'
    #print(subprocess.call("C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe echo "+Message, shell=True))
    #call_powershell_script(Message,iteration)
    InputFile = ".\Dutchman_Longer.wav"
    #InputFile = ".\dabc.mp3"
    #InputFile = ".\Dutchman.wav"
    
    tts.tts_to_file(text=Message, 
                            speaker_wav=InputFile, 
                            language="en", 
                            #speaker= "Damien Black",
                            #speaker= "Craig Gutsy",
                            speaker="Baldur Sanjin",
                            #speaker="Rosemary Okafor",
                            split_sentences=True, 
                            file_path=OutputPath)
    
   # return send_file(
        # OutputPath, 
         #mimetype="audio/wav", 
         #as_attachment=True, 
         #attachment_filename="test.wav"
        #)
    return {'FileLocation':OutputPath, 'Message':Message}

def CallCoquiLong(Message, iteration):
    FormattedTime = datetime.today().strftime('%Y.%m.%d_%H.%M.%S')
    OutputPath = ".\AudioFiles\\"+FormattedTime+"_"+"00"+".wav"
    #PowerShellFilePath = '"C:\Program Files\Decisions\PowershellScripts\CreateTTSFiles.ps1"'
    #print(subprocess.call("C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe echo "+Message, shell=True))
    #call_powershell_script(Message,iteration)
    InputFile = ".\Dutchman_Longer.wav"
    #InputFile = ".\dabc.mp3"
    #InputFile = ".\Dutchman.wav"
    OutputPath = ".\AudioFiles\\"+FormattedTime+"_"+iteration+".wav"
    tts2.tts_to_file(text=Message, 
                            speaker_wav=InputFile,
                            split_sentences=True, 
                            file_path=OutputPath)
    #return send_file(
     #    OutputPath, 
     #    mimetype="audio/wav", 
         #as_attachment=True, 
         #attachment_filename="test.wav"
     #    )
    return {'FileLocation':OutputPath, 'Message':Message}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('frontend/static', path)

@app.route('/TTS', methods=['GET'])
def TTS():
    start_time = time.time()
    TTS_prompt = request.args.get('Prompt')
    try:
        RQMethodVar = request.headers['Request Method']
        print(RQMethodVar)
    except KeyError:
        RQMethodVar = "blank"
    if ( RQMethodVar != "OPTIONS" ):
        #TTS_prompt = any(prompt_request)
        #TTS_prompt = any(request.args.get('Prompt'))
        # Do something with the user ID (e.g., retrieve a user from a database)
        #Ollama_requestobj = StreamObject(model="Squawker", prompt=TTS_prompt, stream="false")
        Ollama_requestobj = {'model':'Squawker', "prompt":TTS_prompt, "stream":False}
        Ollama_url = 'http://127.0.0.1:11434/api/generate'
        Ollama_POSTdata = json.dumps(Ollama_requestobj)
        Ollama_response = requests.post(Ollama_url, data=Ollama_POSTdata)
        OllamaResponseJSON = Ollama_response.json()

        
        FormattedString = str(OllamaResponseJSON['response']).replace('"', "")
        FormattedString = FormattedString.replace('\\', "")
        #FormattedString = FormattedString.replace('*', "...")
        #FormattedString = FormattedString.replace('\'', "")
        #FormattedString = FormattedString.replace('\\n', "")
        #FormattedString = FormattedString.replace('!', ".")
        FormattedString = FormattedString.replace('?', ".")
        FormattedString = re.sub(r'\*.*?\*', '', FormattedString)



        
        Out_file = CallCoqui(FormattedString,"00")
        #FormattedStringList = FormattedString.rsplit('.')
        #n = 0
        #my_list = []
        #timecheck = time.time() - start_time
        #my_list.append({'iteration':n,'timeSinceStart':timecheck})
        #for i in FormattedStringList:
        #    if len(i) >= 2:
        #        n=n+1
        #        CallCoqui(i,str(n))
        #        timecheck = time.time() - start_time
        #        my_list.append({'iteration':n,'timeSinceStart':timecheck, 'prompt':i})
        #    else:
        #        FormattedStringList.remove(i)
        end_time = time.time()
        elapsed_time = end_time - start_time
        #return {'status':200,"List_prompts":FormattedStringList,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url, "outputAudios": my_list}
        #return {'File':Out_file,'status':200,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url}
        return Out_file
    else:
        return Out_file
        return send_file(
         OutputPath, 
         mimetype="audio/wav", 
         #as_attachment=True, 
         #attachment_filename="test.wav"
         )

@app.route('/LongTTS', methods=['GET'])
def LongTTS():
    start_time = time.time()
    TTS_prompt = request.args.get('Prompt')
    try:
        RQMethodVar = request.headers['Request Method']
        print(RQMethodVar)
    except KeyError:
        RQMethodVar = "blank"
    if ( RQMethodVar != "OPTIONS" ):
        #TTS_prompt = any(prompt_request)
        #TTS_prompt = any(request.args.get('Prompt'))
        # Do something with the user ID (e.g., retrieve a user from a database)
        #Ollama_requestobj = StreamObject(model="Squawker", prompt=TTS_prompt, stream="false")
        Ollama_requestobj = {'model':'llama3.2', "prompt":TTS_prompt, "stream":False}
        Ollama_url = 'http://127.0.0.1:11434/api/generate'
        Ollama_POSTdata = json.dumps(Ollama_requestobj)
        Ollama_response = requests.post(Ollama_url, data=Ollama_POSTdata)
        OllamaResponseJSON = Ollama_response.json()

        
        FormattedString = str(OllamaResponseJSON['response']).replace('"', "")
        FormattedString = FormattedString.replace('\\', "")
        #FormattedString = FormattedString.replace('*', "...")
        #FormattedString = FormattedString.replace('\'', "")
        #FormattedString = FormattedString.replace('\\n', "")
        #FormattedString = FormattedString.replace('!', ".")
        FormattedString = FormattedString.replace('?', ".")
        FormattedString = re.sub(r'\*.*?\*', '', FormattedString)



        
        Out_file = CallCoquiLong(FormattedString,"00")
        #FormattedStringList = FormattedString.rsplit('.')
        #n = 0
        #my_list = []
        #timecheck = time.time() - start_time
        #my_list.append({'iteration':n,'timeSinceStart':timecheck})
        #for i in FormattedStringList:
        #    if len(i) >= 2:
        #        n=n+1
        #        CallCoqui(i,str(n))
        #        timecheck = time.time() - start_time
        #        my_list.append({'iteration':n,'timeSinceStart':timecheck, 'prompt':i})
        #    else:
        #        FormattedStringList.remove(i)
        end_time = time.time()
        elapsed_time = end_time - start_time
        #return {'status':200,"List_prompts":FormattedStringList,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url, "outputAudios": my_list}
        #return {'File':Out_file,'status':200,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url}
        return Out_file
    else:
        return send_file(
         OutputPath, 
         mimetype="audio/wav", 
         #as_attachment=True, 
         #attachment_filename="test.wav"
         )

@app.route('/DirectTTS', methods=['GET'])
def DirectTTS():
    start_time = time.time()
    TTS_prompt = request.args.get('Prompt')
    #print(TTS_prompt)
    #try:
    #    HeaderVar = request.headers['Referer']
    #except KeyError:
    #    HeaderVar = "blank"
    try:
        RQMethodVar = request.headers['Request Method']
        print(RQMethodVar)
    except KeyError:
        RQMethodVar = "blank"
    if ( RQMethodVar != "OPTIONS" ):
        #TTS_prompt = any(prompt_request)
        #TTS_prompt = any(request.args.get('Prompt'))
        # Do something with the user ID (e.g., retrieve a user from a database)
        #Ollama_requestobj = StreamObject(model="Squawker", prompt=TTS_prompt, stream="false")
        #Ollama_requestobj = {'model':'llama3.2', "prompt":TTS_prompt, "stream":False}
        #Ollama_url = 'http://127.0.0.1:11434/api/generate'
        #Ollama_POSTdata = json.dumps(Ollama_requestobj)
        #Ollama_response = requests.post(Ollama_url, data=Ollama_POSTdata)
        #OllamaResponseJSON = TTS_prompt

        
        FormattedString = TTS_prompt
        FormattedString = FormattedString.replace('\\', "")
        #FormattedString = FormattedString.replace('*', "...")
        #FormattedString = FormattedString.replace('\'', "")
        #FormattedString = FormattedString.replace('\\n', "")
        #FormattedString = FormattedString.replace('!', ".")
        FormattedString = FormattedString.replace('?', ".")
        FormattedString = re.sub(r'\*.*?\*', '', FormattedString)



        
        Out_file = CallCoquiLong(FormattedString,"00")
        #FormattedStringList = FormattedString.rsplit('.')
        #n = 0
        #my_list = []
        #timecheck = time.time() - start_time
        #my_list.append({'iteration':n,'timeSinceStart':timecheck})
        #for i in FormattedStringList:
        #    if len(i) >= 2:
        #        n=n+1
        #        CallCoqui(i,str(n))
        #        timecheck = time.time() - start_time
        #        my_list.append({'iteration':n,'timeSinceStart':timecheck, 'prompt':i})
        #    else:
        #        FormattedStringList.remove(i)
        end_time = time.time()
        elapsed_time = end_time - start_time
        #return {'status':200,"List_prompts":FormattedStringList,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url, "outputAudios": my_list}
        #return {'File':Out_file,'status':200,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url}
        return Out_file
    else:
        ##return send_file(
         ##OutputPath, 
        ## mimetype="audio/wav", 
         #as_attachment=True, 
         #attachment_filename="test.wav"
        ## )
        return {'FileLocation':OutputPath}


@app.route('/DVTTS', methods=['GET'])
def DVTTS():
    start_time = time.time()
    TTS_prompt = request.args.get('Prompt')
    try:
        RQMethodVar = request.headers['Request Method']
        print(RQMethodVar)
    except KeyError:
        RQMethodVar = "blank"
    if ( RQMethodVar != "OPTIONS" ):
        #TTS_prompt = any(prompt_request)
        #TTS_prompt = any(request.args.get('Prompt'))
        # Do something with the user ID (e.g., retrieve a user from a database)
        #Ollama_requestobj = StreamObject(model="Squawker", prompt=TTS_prompt, stream="false")
        Ollama_requestobj = {'model':'DiabolicalVillain', "prompt":TTS_prompt, "stream":False}
        Ollama_url = 'http://127.0.0.1:11434/api/generate'
        Ollama_POSTdata = json.dumps(Ollama_requestobj)
        Ollama_response = requests.post(Ollama_url, data=Ollama_POSTdata)
        OllamaResponseJSON = Ollama_response.json()

        
        FormattedString = str(OllamaResponseJSON['response']).replace('"', "")
        FormattedString = FormattedString.replace('\\', "")
        #FormattedString = FormattedString.replace('*', "...")
        #FormattedString = FormattedString.replace('\'', "")
        #FormattedString = FormattedString.replace('\\n', "")
        #FormattedString = FormattedString.replace('!', ".")
        FormattedString = FormattedString.replace('?', ".")
        FormattedString = re.sub(r'\*.*?\*', '', FormattedString)



        
        Out_file = CallCoqui(FormattedString,"00")
        #FormattedStringList = FormattedString.rsplit('.')
        #n = 0
        #my_list = []
        #timecheck = time.time() - start_time
        #my_list.append({'iteration':n,'timeSinceStart':timecheck})
        #for i in FormattedStringList:
        #    if len(i) >= 2:
        #        n=n+1
        #        CallCoqui(i,str(n))
        #        timecheck = time.time() - start_time
        #        my_list.append({'iteration':n,'timeSinceStart':timecheck, 'prompt':i})
        #    else:
        #        FormattedStringList.remove(i)
        end_time = time.time()
        elapsed_time = end_time - start_time
        #return {'status':200,"List_prompts":FormattedStringList,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url, "outputAudios": my_list}
        #return {'File':Out_file,'status':200,"PythonTimeSpan":elapsed_time,"Ollama_duration":OllamaResponseJSON['total_duration'], "Body":Ollama_requestobj, "Ollama_url":Ollama_url}
        return Out_file
    else:
        return Out_file
        return send_file(
         OutputPath, 
         mimetype="audio/wav", 
         #as_attachment=True, 
         #attachment_filename="test.wav"
         )

@app.route('/Prompt', methods=['GET'])
def Prompt():
    start_time = time.time()
    TTS_prompt = request.args.get('Prompt')
    Out_file = {}
    try:
        RQMethodVar = request.headers['Request Method']
        print(RQMethodVar)
    except KeyError:
        RQMethodVar = "blank"
    if ( RQMethodVar != "OPTIONS" ):

        Ollama_requestobj = {'model':'llama3.2', "prompt":TTS_prompt, "stream":False}
        Ollama_url = 'http://127.0.0.1:11434/api/generate'
        Ollama_POSTdata = json.dumps(Ollama_requestobj)
        Ollama_response = requests.post(Ollama_url, data=Ollama_POSTdata)
        OllamaResponseJSON = Ollama_response.json()

        
        FormattedString = str(OllamaResponseJSON['response']).replace('"', "")
        FormattedString = FormattedString.replace('\\', "")
        Out_file = {'FileLocation':"empty", 'Message':FormattedString}
        end_time = time.time()
        elapsed_time = end_time - start_time
    return Out_file

if __name__ == '__main__':
    app.run(host="0.0.0.0")
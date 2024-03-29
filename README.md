# chatGPT

python Web OpenAI ChatGPT with STT (Speech to Text)

[github] https://github.com/YfNk1d5up/chatGPT


## Software

 - Running on Gradio Interface
 - Powered Open AI Chat GPT, Dall-e and Whisper API


## Features

- **STT** : In app live Speech 2 Text
- **Chat Bot** : ChatGPT Powered chat bot
- **Image Gen** : Dall-e image generation with keyword "image" in prompt
- **Code execution** : Python script generated by bot can be executed with keyword "execute code" in prompt
- **Securised** : SSL on HTTPS python web server
- **Environment** : Dotenv with encrypted Open AI Token

## Screenshots

![Gradio App v0.1](pictures/gradioAppv0.1.png)


## Installation

### OpenAI

Navigate to OpenAI api-keys webpage to get your token :
[api-keys](https://platform.openai.com/account/api-keys)

Insert it into the **.env** file :

```
openai_API_KEY="<my_api_key>"
```

### Linux

```bash
git clone https://github.com/YfNk1d5up/chatGPT
cd chatGPT
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
cp ChatGPT.template ChatGPT & rm ChatGPT.template
```

Change directory on ChatGPT file with your working directory :

```shell
#!/bin/bash

cd <Project_Directory_Parent>/chatGPT/
source venv/bin/activate
python3 main.py
```

Add ChatGPT to your path or to /usr/bin

```shell
ln -s ChatGPT ChatGPT.s
sudo cp ChatGPT.s /usr/bin/ChatGPT
rm ChatGPT.s
sudo chmod +x /usr/bin/ChatGPT
```

You can now launch ChatGPT from your terminal
```shell
ChatGPT
```
### Windows


## Web App

Open your fav Browser and navigate to :

[chatGPT local url](https://localhost:7860)

## Ressources

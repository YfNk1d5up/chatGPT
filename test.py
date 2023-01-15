# -------------------------------------------------#
# -------------------- MODULES --------------------#
# -------------------------------------------------#

import os
import sys
import jsoncfg
import openai
import whisper
import gradio as gr
import shutil
from dotenv import load_dotenv
import urllib.request
from log.trace import trace as logger

import log.registre as registre

# ---------------------------------------------------------------- #
# ------------------------  CONSTANTES  -------------------------- #
# ---------------------------------------------------------------- #

globalConfig = None
exe_dir = ""
model_engine = "text-davinci-003"
raz_next_inp = False


# ---------------------------------------------------------------- #
# ------------------------  FONCTIONS  --------------------------- #
# ---------------------------------------------------------------- #

def dir_folder():
    """
    Permet de controler le repertoire de python.
    Ceci est utile lorsque nous construisons un exe
    :return: le repertoire ou se situe le fichier source
    """
    if getattr(sys, 'frozen', False):
        # we are running in a bundle'
        bundle_dir = sys._MEIPASS
    else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    return bundle_dir


# ---------------------------------------------------------------- #
def checkfolder(directory):
    """
     Verifie si un repertoire est present et le cree si besoin
     :param directory: le nom du repertoire a creer si absent
    """
    logger.debug("Verification du dossier '" + getname(directory) + "' ")
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        logger.exception(
            r'/!\ Pb lors de la verification du dossier: ' + directory + " ")


# ---------------------------------------------------------------- #
def concat_file(folder, filer):
    """
     Verifie si un repertoire est present et le cree si besoin
     :param folder: le chemin du repertoire
     :param filer: le nom du repertoire a ajouter avec chemin
    """
    return os.path.join(folder, filer)


# ---------------------------------------------------------------- #
def getname(filename, extension=0):
    """
    Renvoie le nom d'un fichier sans son path et son extension
    :return: le nom du fichier sans path ni extension
    """
    return os.path.splitext(os.path.basename(filename))[extension]


# ---------------------------------------------------------------- #
def remove_file(filename):
    """
    Supprime les pdf dans le répertoire passé en paramètre
    :param filename: Nom du répertoire
    """
    logger.debug("Suppression du répertoire '" + getname(filename) + "'")
    try:
        if os.path.exists(filename):
            shutil.rmtree(filename, ignore_errors=True)
    except OSError:
        logger.exception(
            r"/!\ Pb lors de la suppresion du dossier: '" + getname(filename) + "'")
        return False


"""
def promptManager(mode, prompt, last_resp):
    logger.info("[You]> ")
    question = recordSound()
    logger.info("[You]> " + question)
    if mode == "image":
        if question == "end image":
            return True
        try:
            url = chatGPTImage(question)
            logger.info("[ChatGPT]> " + url)
        except Exception as e:
            logger.error(e)
            return False
        return True
    elif mode == "chat":
        if "end chat" in question.lower():
            return True
        elif "execute code" in question.lower():
            try:
                exec(last_resp)
            except Exception as e:
                logger.error(e)
                return False
            return True
        elif prompt == "":
            try:
                resp = chatGPTresponse(question)
                logger.info("[ChatGPT]> " + resp[2:])
                prompt = '-' + question + '\n' + '-' + resp[2:] + '\n' + '-'
                promptManager("chat", prompt, resp)
            except Exception as e:
                logger.error(e)
                return False
        else:
            try:
                question = prompt + question + '\n' + '-'
                resp = chatGPTresponse(question)
                logger.info("[ChatGPT]> " + resp)
                prompt = question + resp + '\n' + '-'
                promptManager("chat", prompt, resp)
            except Exception as e:
                logger.error(e)
                return False
    return True
"""


def chatGPTresponse(prompt):
    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return completion.choices[0].text


def chatGPTImage(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    url = response['data'][0]['url']
    try:
        urllib.request.urlretrieve(url, os.path.join(globalConfig.folder.output(), prompt.replace(' ', '_') + '.png'))
    except Exception as e:
        logger.error(e)
    return url


def openai_create(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    logger.info("[ChatGPT]> " + response.choices[0].text)
    return response.choices[0].text


def transcribe(audio):
    # time.sleep(3)
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(whisper_model.device)

    # detect the spoken language
    _, probs = whisper_model.detect_language(mel)
    logger.info(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(whisper_model, mel, options)
    logger.info("[You]> " + result.text)
    return result.text


def chatgpt_clone(input, record, history):
    text_recognised = ""
    if input == "":
        try:
            text_recognised = transcribe(record)
        except Exception as e:
            logger.error(e)
    else:
        text_recognised = input
    history = history or []
    s = list(sum(history, ()))
    s.append(text_recognised)
    if "image" in text_recognised.lower():
        try:
            url = chatGPTImage(text_recognised)
            logger.info("[ChatGPT]> " + url)
            output = "L'image a bien été générée"

        except Exception as e:
            logger.error(e)
            output = "Erreur pendant la génération de l'image"
    elif "execute code" in text_recognised.lower():
        try:
            print(history)
            #exec(history)
            output = "Le code s'est bien executé"
        except Exception as e:
            logger.error(e)
            output = "Erreur lors de l'éxécution du code"
    else:
        if raz_next_inp:
            inp = text_recognised
        else:
            inp = ' '.join(s)
        logger.info("[input]> " + inp)
        output = openai_create(inp)
    history.append((text_recognised, output))
    return history, history


def start():
    # Recuperation de la configuration avec json
    global exe_dir
    exe_dir = dir_folder()
    global raz_next_inp
    raz_next_inp = False
    fichierconf = registre.confModule(exe_dir)
    global globalConfig
    globalConfig = jsoncfg.load_config(fichierconf)
    for i in globalConfig.folder():
        folder_to_check = concat_file(exe_dir, globalConfig.folder[i]())
        checkfolder(folder_to_check)

    global model_engine
    # Set up the OpenAI API client
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    openai.api_key = os.environ.get("openai_API_KEY")

    global whisper_model
    whisper_model = whisper.load_model("small")

    block = gr.Blocks()

    with block:
        gr.Markdown("""<h1><center>Better than Alexa</center></h1>
        """)
        chatbot = gr.Chatbot()
        message = gr.Textbox(placeholder="Ecrire à chatGPT")
        record = gr.inputs.Audio(source="microphone", type="filepath")
        state = gr.State()
        submit = gr.Button("SEND")
        submit.click(chatgpt_clone, inputs=[message, record, state], outputs=[chatbot, state])

    block.launch(debug=False, server_name="192.168.1.10")

    """
    gr.Interface(
        title='OpenAI Whisper ASR Gradio Web UI',
        fn=transcribe,
        inputs=[
            gr.inputs.Audio(source="microphone", type="filepath")
        ],
        outputs=[
            "textbox"
        ],
        live=True).launch()
    """
    """
    while True:
        logger.info("New chat")
        logger.info("Choose mode (Chat - Image)")
        mode = str(input())
        if mode.lower() == "end":
            break
        if promptManager(mode.lower(), "", ""):
            logger.info(mode.lower() + " went well")
        else:
            logger.info(mode.lower() + " went wrong")
    """


# ---------------------------------------------------------------- #
# ------------------------  MAIN  -------------------------------- #
# ---------------------------------------------------------------- #


if __name__ == "__main__":
    start()

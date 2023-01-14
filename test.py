# -------------------------------------------------#
# -------------------- MODULES --------------------#
# -------------------------------------------------#

import os
import sys
import jsoncfg
import openai
import shutil
from dotenv import load_dotenv
import urllib.request
from log.trace import trace as logger

import log.registre as registre

# ---------------------------------------------------------------- #
# ------------------------  CONSTANTES  -------------------------- #
# ---------------------------------------------------------------- #

globalConfig = None
model_engine = "text-davinci-003"


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


def promptManager(mode, prompt, last_resp):
    logger.info("[You]> ")
    question = input()
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
        if question == "end chat":
            return True
        elif question == "execute code":
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

def start():
    # Recuperation de la configuration avec json
    exe_dir = dir_folder()
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

# ---------------------------------------------------------------- #
# ------------------------  MAIN  -------------------------------- #
# ---------------------------------------------------------------- #


if __name__ == "__main__":
    start()

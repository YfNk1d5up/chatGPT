# -*- coding: utf-8 -*-

"""
Module Python de trace/log

Ce module vise à configurer le système Python existant de log, logging
(voir https://docs.python.org/3.6/library/logging.html).

Il suffit d'importer ce module et de l'utiliser comme n'importe quel "Logger" :

    from PMR.trace import trace

    trace.info('trace d'information')
    trace.warning('trace soulevant un warning')
    trace.error('erreur...'')

Par défaut, toutes les traces sont stockées sous forme de fichier dans le dossier ~/data/trace.
Chaque fichier est conservé suivant un système de mois glissant.
"""

import logging
import logging.handlers

import os
from logging.config import dictConfig
from pathlib import Path


import __main__

# Définition des paramètres
DEFAULT_PATH = 'log/trace'   # MODIF DU CODE POUR ALLER DANS LE DOSSIER COURANT (AVANT DEFAULT_PATH = expanduser("~") + '/data/trace/' )
DEFAULT_FILE_EXT = '.log'
except_librairies = ['urllib', 'web3', 'requests', 'urllib3']
APPLICATION_DFT = 'trace'

# BALISE_COMMENTAIRE = "#"

# BALISE_CHEMIN_FICHIER_TRACE     = "CHEMIN_FICHIER_TRACE"
# BALISE_MIN_LVL_RELEASE_DEFAUT   = "MIN_LVL_RELEASE_DEFAUT"
# BALISE_HEURE                    = "heure"
# BALISE_FICHIER                  = "fichier"
# BALISE_LIGNE                    = "ligne"
# BALISE_FONCTION                 = "fonction"
# BALISE_THREAD                   = "thread"
# BALISE_HEURE_FORMAT_H           = "hh"
# BALISE_HEURE_FORMAT_M           = "mm"
# BALISE_HEURE_FORMAT_S           = "ss"
# BALISE_HEURE_FORMAT_Z           = "zzz"

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}

# Définition de l'instance de log pour le module courant
trace = logging.getLogger(__name__)

# Flag qui indique si le module de trace est déjà correctement initialisé
_isInitialise = None


def _init_default():
    """
    Initialise le système de trace
    """

    dictConfig(DEFAULT_LOGGING)

    default_formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s [%(module)s:%(lineno)s] %(message)s", datefmt='%d/%m/%y, %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(default_formatter)

    logging.root.setLevel(logging.DEBUG)
    logging.root.addHandler(console_handler)
    for librairy in except_librairies:
        logging.getLogger(librairy).setLevel(logging.ERROR)

    fichier = str(Path(__file__).parent) + os.sep + "trace"
    if fichier[-1] != '/':
        fichier = fichier + '/'
    # Détermine le nom de l'application en cours d'execution
    try:
        application = __main__.__file__.split(os.sep)[-1]
    except:
        application = APPLICATION_DFT
    all_fichier = fichier + application + DEFAULT_FILE_EXT

    try:
        # Création du dossier de trace si nécessaire
        if not os.path.isdir(fichier):
            trace.info("Création du dossier de trace : %s", fichier)
            os.makedirs(fichier)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            all_fichier, when='midnight')
        file_handler.suffix = '%d'
        file_handler.setLevel(logging.DEBUG)
        for librairy in except_librairies:
            logging.getLogger(librairy).setLevel(logging.ERROR)
        file_handler.setFormatter(default_formatter)

        logging.root.addHandler(file_handler)
    except Exception as e:
        trace.info("Trace par fichier impossible : %s", str(e))

    return True


def _init_fromFichier(fichier):
    # Pas encore implémenté
    print('Prise en compte du fichier de configuration non encore implémentée : ' + str(fichier))
    return _init_default()


def _init():
    # Contrôle que l'initialisation ne se fait qu'une seule fois
    global _isInitialise
    if _isInitialise:
        return

    _isInitialise = _init_default()
    return

    # JR 19/07/18 : Desactivation de ce code tant que la configuration des traces n'est pas bien gérée
    # Détermine le fichier de configuration
    # chemin_fichier_conf = registre.confModule()
    # # Configure les traces à partir d'un fichier conf
    # if chemin_fichier_conf:
    #     _isInitialise = _init_fromFichier(chemin_fichier_conf)
    # else:
    #     # Sinon applique la configuration par défaut
    #     _isInitialise = _init_default()


# Lance la configuration
_init()

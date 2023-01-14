# *-* coding: utf-8 *-*

import os
import sys

import __main__

EXTENSIONS_FICHIER = ["cfg"]


def conf(chemin_defaut):
    """
    Fonction qui fourni le chemin vers un fichier de configuration

    :param str varenv: Nom de la variable d'environnement spécifiant le chemin (ex : PMR_BDD_CONF)
    :param str chemin_defaut: Chemin par défaut si la variable d'environnement n'est pas définie (ex : ~/data/conf/bdd.conf)
    """
    try:
        # Sinon, utilise le chemin par défaut
        conf.CONF_FICHIER = chemin_defaut
        if not os.path.isfile(conf.CONF_FICHIER) == True:
            raise Exception
    except Exception:
        conf.CONF_FICHIER = None
        raise Exception("Conf | Fichier de configuration inexistant : " + str(conf.CONF_FICHIER))

    return conf.CONF_FICHIER


# Initialisation
conf.CONF_FICHIER = None


def confModule(directory, module=None):
    """
    Fonction qui fourni le chemin vers le fichier de configuration d'un projet PMR
    :param directory: chemin du dossier comportant le fichier .py
    :param str module: Nom du projet (ex : bdd)
    """
    if not module:
        module = sys._getframe(1).f_globals['__name__'].split('.')[-1]
        if module == '__main__':
            module = __main__.__file__.split(os.sep)[-1].split('.')[0]
            # MODIF DU "/" EN "." Pour aller chercher que le nom du fichier python.

    # Recherche le fichier de configuration via variable d'environnement et chemin par défaut
    fichier = ""
    lFichierTeste = []
    for ext in EXTENSIONS_FICHIER:
        # Pour chaque extension gérée
        try:
            fichier = '{}{}{}{}{}{}{}.{}'.format(directory, os.sep, 'data', os.sep, 'conf', os.sep, module.lower(),
                                                 ext)  # A modifier suivant le répertoire du fichier conf
            lFichierTeste.append(fichier)
            return conf(fichier)
        except:
            pass

    raise Exception(
        "Conf | Fichier de configuration inexistant pour le module " + str(module) + " :\n - " + "\n - ".join(
            lFichierTeste))

    return None

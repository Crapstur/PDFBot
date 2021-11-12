#! /usr/bin/env python3

import json
import os
import shutil
import logging
import datetime

fichier_base = './pdf/Licence_ASSR_pdf'
infos_file = './infos.json'
files_download = "./pdf/downloads/files/"
infos = {}

logging.basicConfig(filename='/var/log/PDFBot/tri.log', level=logging.INFO)
logging.warning(str(datetime.datetime.today()) + ' : tri START')

os.chdir('/home/userbot/PDFBot/')

try:
    if os.path.exists(infos_file) and os.stat(infos_file).st_size != 0:
        with open(infos_file) as file:
            infos = json.load(file)
        
    if not os.path.exists(fichier_base):
        os.mkdir(fichier_base)
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf/Licence_ASSR_pdf\"]')
        
    ## Boucle sur chaques modules du JSON ##
    for module in infos:
        module_file = fichier_base + '/' + module
        if not os.path.exists(module_file):
            os.mkdir(module_file)
        
        ## Boucle sur chaques onglets de chaques modules du JSON ##
        for onglet in infos[module]:
            onglet_file = module_file + '/' + onglet
            if not os.path.exists(onglet_file):
                os.mkdir(onglet_file)
            
            ## Boucle sur chaques pdf de chaques onglets de chaques modules du JSON ##
            for pdf in infos[module][onglet]:
                if os.path.exists(files_download + pdf):
                    pdf_file_dest = onglet_file + '/' + pdf
                    pdf_file_src = files_download + pdf
                    if not os.path.exists(pdf_file_dest):
                        shutil.move(pdf_file_src, pdf_file_dest)
                    else:
                        os.remove(pdf_file_src)
except:
    logging.error(str(datetime.datetime.today()) + ' : !! ERROR !!')

logging.warning(str(datetime.datetime.today()) + ' : tri END')
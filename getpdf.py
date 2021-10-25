#! /usr/bin/env python3

import os
import json
import unidecode
import time
import shutil
import logging
import datetime
import sys
import dotenv

from selenium import webdriver
from dotenv import load_dotenv

logging.basicConfig(filename='/var/log/PDFBot/getpdf.log', level=logging.INFO)
logging.info(str(datetime.datetime.today()) + ' : getpdf START')

def ft_download(title_module, title_onglet):
    name_PDF = []
    ## Récupère tous les logo PDF ##
    PDFs = driver.find_elements_by_xpath('//img[@src="https://lms.univ-cotedazur.fr/theme/image.php/fordson/core/'+ os.getenv('link_id') +'/f/pdf"]')
    name_PDFs_tmp = driver.find_elements_by_xpath('//a//span[@class="instancename"]')
    if len(name_PDFs_tmp) == 0:
        name_PDFs_tmp = driver.find_elements_by_xpath('//a//span[@class="fp-filename"]')
    
    for name_PDF_tmp in name_PDFs_tmp:
        name_PDF_split = name_PDF_tmp.text.split("\n")
        if len(name_PDF_split) == 1 or name_PDF_split[1] == "Fichier":
            name_PDF.append(name_PDF_split[0])

    if len(PDFs) != 0:
        m = 0
        for PDF in PDFs:
            tmp_file = "./pdf/downloads/tmp/"
            files_file = "./pdf/downloads/files/"
            PDF.click()
            
            ## Attendre le temps du telechargement ##
            download = True
            crdownload = False
            while download == True:
                crdownload = False
                
                files = os.listdir(tmp_file)
                for file in files:
                    if file.endswith(".crdownload"):
                        crdownload = True
                    
                    time.sleep(1)
                    
                    if crdownload == False:
                        download = False
                    file = file
                time.sleep(1)

            files = os.listdir(tmp_file)
            for file in files:                
                ## Inscrire le nom du fichier dans le JSON ##
                #infos[title_module][title_onglet][unidecode.unidecode(file)] = unidecode.unidecode(name_PDF[m])    ## En cas de test a faire ##
                infos[title_module][title_onglet].append(unidecode.unidecode(file))
                
                ## Deplacer le fichier depuis 'tmp' vers 'files' ##
                if not os.path.exists(files_file + file) and not file.endswith(".crdownload"):
                    shutil.move(tmp_file + file, files_file + unidecode.unidecode(file))
                else:
                    os.remove(tmp_file + file)

                m += 1
        
        
        
    return(0)

try:
    load_dotenv()

    infos_file = './infos.json'
    infos = {}
    
    if not os.path.exists('./pdf'):
        os.mkdir('./pdf')
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf\"]')

    if not os.path.exists('./pdf/downloads'):
        os.mkdir('./pdf/downloads')
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf/downloads\"]')

    if not os.path.exists('./pdf/downloads/tmp'):
        os.mkdir('./pdf/downloads/tmp')
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf/downloads/tmp\"]')

    if not os.path.exists('./pdf/downloads/files'):
        os.mkdir('./pdf/downloads/files')
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf/downloads/files\"]')


    if not os.path.exists(infos_file):
        os.mknod(infos_file)

    if os.stat(infos_file).st_size != 0:
        with open(infos_file) as file:
            infos = json.load(file)


    login_gpu = os.getenv('LOGIN_GPU')
    mdp_gpu = os.getenv('MDP_GPU')

    #dir=os.getcwd()

    site = "https://lms.univ-cotedazur.fr/my/"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    #options.add_argument("--window-size=1600,900")
    options.add_experimental_option('prefs', {
    "download.default_directory": "./pdf/downloads/tmp", #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
    })
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)


    driver.maximize_window()

    driver.get(site)

    connect = driver.find_element_by_class_name("potentialidp")
    connect.click()

    login = driver.find_element_by_id("username")
    login.send_keys(login_gpu)

    passwd = driver.find_element_by_id("password")
    passwd.send_keys(mdp_gpu)

    connect_btn = driver.find_element_by_class_name("btn-submit")
    connect_btn.click()

    imgs = driver.find_element_by_xpath('//img')
    x = imgs.get_attribute('src').split('/')
    y = x[-3]
    if y != os.getenv('link_id'):
        if y.isnumeric():
            link_id = y
            os.environ["link_id"] = link_id
            dotenv.set_key('./.env', "link_id", os.environ["link_id"])
        else:
            sys.exit()


    pannel = driver.find_element_by_xpath('//button[@class="btn nav-link float-sm-left mr-1 btn-secondary"]')
    if pannel.get_attribute('aria-expanded') == "false":
        pannel.click()

    ## Variables ##
    i = 0
    j = 0
    k = 0
    ###############

    ## Récupérer tout les modules et les visiter un à un ##
    ## Récuperer les modules ##
    modules = []
    modules_nav = driver.find_elements_by_xpath('//nav//ul//a[@class="list-group-item list-group-item-action  "]')
    for module in modules_nav:
        if module.get_attribute('data-parent-key') == "mycourses":
            modules.append(module.get_attribute('href'))
            

    while i < len(modules):
        driver.get(modules[i])
        infos[unidecode.unidecode(driver.title[8:])] = {}
        #ft_download()
        j = 0
        
        ## Récupérer tout les onglets du module et les visiter un à un ##
        onglets = []
        titles_onglets = []
        onglets_nav = driver.find_elements_by_xpath('//ul[@class="nav nav-tabs mb-3"]//li//a')
        for onglet in onglets_nav:
            if not onglet.get_attribute('class') == "nav-link disabled":
                titles_onglets.append(unidecode.unidecode(onglet.get_attribute('title')))
                if onglet.get_attribute('href') != None:
                    onglets.append(onglet.get_attribute('href'))
                elif onglet.get_attribute('class') == "nav-link active":
                    onglets.append(driver.current_url)

        if len(onglets) != 0:
            for j in range(len(onglets)): 
                driver.get(onglets[j])
                title_module = driver.title[8:].split(', Section')
                #infos[title_module[0]][titles_onglets[j]] = {}     ## En cas de test a faire ##
                infos[title_module[0]][titles_onglets[j]] = []
                ft_download(title_module[0],titles_onglets[j])
        i += 1

    time.sleep(1)

    ## Ferme toute les fenêtres ##
    l = len(driver.window_handles)
    while l > 0:
        driver.switch_to.window(driver.window_handles[l - 1])
        driver.close()
        l -= 1

    with open(infos_file, 'w') as outfile:
        json.dump(infos, outfile, indent=4)
except:
    logging.error(str(datetime.datetime.today()) + ' : !! ERROR !!')

logging.info(str(datetime.datetime.today()) + ' : getpdf END')

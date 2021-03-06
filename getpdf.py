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

from selenium.webdriver.support.ui import Select
from selenium import webdriver
from dotenv import load_dotenv
from icecream import ic

logging.basicConfig(filename='/var/log/PDFBot/getpdf.log', level=logging.INFO)
logging.warning(str(datetime.datetime.today()) + ' : getpdf START')

os.chdir('/home/userbot/PDFBot/')

page_ban = ['https://lms.univ-cotedazur.fr/course/view.php?id=16998', 'https://lms.univ-cotedazur.fr/course/view.php?id=7191&section=1#tabs-tree-start', 'https://lms.univ-cotedazur.fr/course/view.php?id=7191']

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
            tmp_file = "/home/userbot/PDFBot/pdf/downloads/tmp/"
            files_file = "/home/userbot/PDFBot/pdf/downloads/files/"
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
        logging.info(str(datetime.datetime.today()) + ' : Create folder [./pdf]')

    if not os.path.exists('./pdf/downloads'):
        os.mkdir('./pdf/downloads')
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf/downloads\"]')

    if not os.path.exists('./pdf/downloads/tmp'):
        os.mkdir('./pdf/downloads/tmp')
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf/downloads/tmp\"]')

    if not os.path.exists('./pdf/downloads/files'):
        os.mkdir('./pdf/downloads/files')
        logging.info(str(datetime.datetime.today()) + ' : Create folder [\"./pdf/downloads/files\"]')

    try:
        files_tmp = os.listdir("./pdf/tmp")
        files_files = os.listdir("./pdf/files")
    except:
        files_tmp = False
        files_files = False
    
    if files_tmp == True:
        for file in files_tmp:
            if file.endswith(".crdownload"):
                os.remove(file)
    
    if files_files == True:
        for file in files_files:
            if file.endswith(".crdownload"):
                os.remove(file)


    if not os.path.exists(infos_file):
        os.mknod(infos_file)

    if os.stat(infos_file).st_size != 0:
        with open(infos_file) as file:
            infos = json.load(file)


    login_gpu = os.getenv('LOGIN_GPU')
    mdp_gpu = os.getenv('MDP_GPU')

    site = "https://lms.univ-cotedazur.fr/my/"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1600,900")
    options.add_experimental_option('prefs', {
    "download.default_directory": "./pdf/downloads/tmp", #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
    })
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)


    try:
        driver.get(site)
    except:
        logging.error(str(datetime.datetime.today()) + ' : !! Site unreachable !!')
        sys.exit()

    driver.maximize_window()

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

    ## Variables ##
    i = 0
    j = 0
    k = 0
    ###############

    ## Récupérer tout les modules et les visiter un à un ##
    ## Récuperer les modules ##
    modules = []
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    btn_display = driver.find_element_by_xpath("/html/body/div[2]/div[3]/div/div[2]/div/section[1]/div[2]/aside/section[2]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div")
    btn_display.click()

    btn_TOUT = driver.find_element_by_xpath("/html/body/div[2]/div[3]/div/div[2]/div/section[1]/div[2]/aside/section[2]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div/div/a[2]")
    btn_TOUT.click()

    modules_nav = driver.find_elements_by_xpath("//a[@class='aalink coursename']")
    for module in modules_nav:
        #print(module.get_attribute('href'))
        #print(page_ban)
        if module.get_attribute('href') not in page_ban:
            modules.append(module.get_attribute('href'))
            
    while i < len(modules):
        driver.get(modules[i])
        infos[unidecode.unidecode(driver.title[8:])] = {}
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
                #print("Download: ", title_module[0], " | ", titles_onglets[j]) # Décommenter en cas de problème
                ft_download(title_module[0],titles_onglets[j])

        i += 1

    time.sleep(1)

    ## Ferme toute les fenêtres ##
    l = len(driver.window_handles)
    while l > 0:
        driver.switch_to.window(driver.window_handles[l - 1])
        l -= 1

    with open(infos_file, 'w') as outfile:
        json.dump(infos, outfile, indent=4)
        
    logging.info(str(datetime.datetime.today()) + ' : Finished without error')
except:
    logging.error(str(datetime.datetime.today()) + ' : !! ERROR !!')

try:
    driver.close()
except:
    logging.error(str(datetime.datetime.today()) + ' : !! Chrome not closed !!')

logging.warning(str(datetime.datetime.today()) + ' : getpdf END')

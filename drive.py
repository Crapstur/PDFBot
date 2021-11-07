#! /usr/bin/env python3

import pickle
import os
import logging
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv


# Permet modification complete du drive
SCOPES = ['https://www.googleapis.com/auth/drive']

logging.basicConfig(filename='/var/log/PDFBot/drive.log', level=logging.INFO)

os.chdir('/home/userbot/PDFBot/')

def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('./token.pickle'):
        with open('./token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds, cache_discovery=False)

def search_id(item_name, item_type, item_parent_id):
    if item_type == 'folder' :
        item_type2 = 'application/vnd.google-apps.folder'
    elif item_type == 'pdf':
        item_type2 = 'application/pdf'
    
    service = get_gdrive_service()
    results = service.files().list(pageSize=1000, fields="nextPageToken, files(id,name,mimeType,parents)").execute()
    items = results.get('files', [])
    
    found = False
    item_id = ''
    item_size = 0
    
    if not items:
        logging.error(str(datetime.datetime.today()) + ' : Not item found')
        pass
    else:
        for item in items:
            try:
                if item['parents'] == [item_parent_id]:
                    if item['mimeType'] == item_type2:
                        if item['name'] == item_name:
                            item_id = item['id']
                            found = True
                            break
                
                if found == True:
                    break
                
                if found == False:
                    item_id = 'Null'
                
            except:
                logging.error(str(datetime.datetime.today()) + ' : !! ERROR [Search id] !!')
                pass
        return(item_id)

def upload_file(file_name, file_parent_id, srv_path):
    service = get_gdrive_service()
    
    file_metadata = {
        "name": file_name,
        "mimeType": "application/pdf",
        "parents": [file_parent_id]
    }
    
    media = MediaFileUpload(srv_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    logging.info(str(datetime.datetime.today()) + ' : Upload file   --> ' + '"' + file_name + '"')

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def create_folder(folder_name, folder_parent_id):
    service = get_gdrive_service()
    
    folder_metadata = {
        "name": folder_name,
        "parents": [folder_parent_id],
        "mimeType": "application/vnd.google-apps.folder"
    }
    
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder.get('id')
    
    logging.info(str(datetime.datetime.today()) + ' : Create folder --> ' + '"' + folder_name + '"')
    
    return(folder_id)

def remove_file(file_id, file_name):
    service = get_gdrive_service()
    
    service.files().delete(fileId=file_id).execute()
    
    logging.info(str(datetime.datetime.today()) + ' : Remove file   --> ' + '"' + file_name + '"')

def get_size(file_id):
    service = get_gdrive_service()
    
    results = service.files().list(pageSize=1000, fields="nextPageToken, files(id,name,mimeType,parents,size)").execute()
    items = results.get('files', [])
    
    file_size = 0
    
    for item in items:
        if item['id'] == file_id:
            file_size = item['size']
    return(file_size)

if __name__ == '__main__':
    logging.warning(str(datetime.datetime.today()) + ' : DriveBot START')
    load_dotenv()
    try:
        srv_base_folder = os.getenv('srv_base_folder')
        drv_base_folder_name = os.getenv('drv_base_folder_name')
        parent_folder_id = os.getenv('parent_folder_id')
        
        ## Test si fichier Licence_ASSR_pdf existe ##
        if os.path.exists(srv_base_folder):
            drv_base_folder_id = search_id(drv_base_folder_name, 'folder', parent_folder_id)
            if drv_base_folder_id == 'Null':
                drv_base_folder_id = create_folder(drv_base_folder_name, parent_folder_id)
            
            ## Liste tout les fichiers ##
            modules = os.listdir(srv_base_folder)
            
            ## Boucle sur chaque module local ##
            for module in modules:
                folder_module = srv_base_folder + '/' + module
                parent_folder_id = drv_base_folder_id
                drv_module_id = search_id(module, 'folder', parent_folder_id)
                if drv_module_id == 'Null':
                    drv_module_id = create_folder(module, parent_folder_id)
                
                ## Liste tout les fichiers ##
                onglets = os.listdir(folder_module)
                
                ## Boucle sur chaque onglet de chaque module local ##
                for onglet in onglets:
                    folder_onglet = folder_module + '/' + onglet
                    parent_folder_id = drv_module_id
                    drv_onglet_id = search_id(onglet, 'folder', parent_folder_id)
                    if drv_onglet_id == 'Null':
                        drv_onglet_id = create_folder(onglet, parent_folder_id)
                    
                    ## Liste tout les fichiers ##
                    files = os.listdir(folder_onglet)
                    
                    ## Boucle sur chaque file de chaque onglet de chaque module local ##
                    for file in files:
                        drv_file_size = 0
                        srv_path = folder_onglet + '/' + file
                        parent_folder_id = drv_onglet_id
                        drv_file_id = search_id(file, 'pdf', parent_folder_id)
                        
                        if drv_file_id == 'Null':
                            upload_file(file, parent_folder_id, srv_path)
                        else:
                            drv_file_size = get_size(drv_file_id)
                            srv_file_size = os.stat(srv_path).st_size
                            
                            if int(srv_file_size) != int(drv_file_size):
                                remove_file(drv_file_id, file)
                                upload_file(file, parent_folder_id, srv_path)
        else:
            ## Ecrire message dans Log ##
            logging.error(str(datetime.datetime.today()) + ' : !! No local folder Licence_ASSR_pdf !!')
            pass
    except:
        logging.error(str(datetime.datetime.today()) + ' : !! ERROR !!')
    logging.warning(str(datetime.datetime.today()) + ' : DriveBot END')
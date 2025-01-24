import sqlite3
import json
import pickle
import os.path
import atexit
import io
import logging
import requests
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload, MediaFileUpload, MediaInMemoryUpload

logging.basicConfig(filename='errors.log', level=logging.ERROR)

def is_online():
    try:
        requests.head("https://www.google.com", timeout=1)
        return True
    except requests.ConnectionError:
        return False
#Credentials
CLIENT_SECRET_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/drive']

#Changes
changes = []
file_id = '1giOgAFzodwptnQmYp1itfUP4XEGvW6TP'  # Replace with your contacts.db file ID

def get_service():
    if not is_online():
        raise Exception("Offline")
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)


def queue_change(query):
    changes.append(query)  # Store query as string
    try:
        service = get_service()
        upload_changes(service, [query])
    except Exception as e:
        with  open("offline_changes.txt", "a", encoding="utf-8") as f:
            f.write(query + "\n")
        logging.error(f"offline: writing to offline_changes: {e}")

# upload_changes function
# 1. Write local changes to "changes.txt".
# 2. retrieve existing Drive file content.
# 3. Combine existing and new changes.
# 4. Upload combined changes to Drive.
# 5. Clear local "changes.txt".
def upload_changes(service, new_changes=None):
    global changes
    try:
        # Read existing Drive file content
        file_metadata = service.files().get_media(fileId=file_id).execute()
        existing_changes = file_metadata.decode('utf-8', errors='ignore').splitlines()
        
        # Combine existing and new changes as text not lists
        all_changes = "\n".join(existing_changes + changes)

        # Upload combined changes to Drive
        media = MediaInMemoryUpload(all_changes.encode('utf-8'),'text/plain')
        service.files().update(fileId=file_id, body=None, media_body=media).execute()

        # Clear local changes list and file
        changes.clear()
        open("changes.txt", "w", encoding="utf-8").close()

    except Exception as e:
        logging.error(f"Error uploading changes: {e}", exc_info=True)
# هنا كان في لفه عقيمه انه عشان يرفع التغييرات للدرايف بيفتح ملف الدرايف
#ويخزن الي جواه في متغير وبعد كده يضيف عليهم التغييرات المحليه
#بعد ما يضيفهم ع بعض بيكتبهم في الملف المحلي وبعدها يرفعهم للدرايف
#وبعدها ينضف المحلى ويقفله
#فنلاحظ انه دايما التغييرات الي  اتعملت فالبرنامج بتبقى بعد الي عملها داون لود من الدرايف فده الترتيب الصحيح
#لكن كده بيفشخ ملف الدرايف لأنه كل مره بيضيفهم كلهم من جديد
    

def upload_offline_changes(service):
    global changes
    try:
        # Read existing Drive file content
        file_metadata = service.files().get_media(fileId=file_id).execute()
        existing_changes = file_metadata.decode('utf-8', errors='ignore').splitlines()
        
        # read offline_changes
        with open("offline_changes.txt", "r", encoding="utf-8", errors="ignore") as f:
            changes = [line.strip() for line in f.readlines()]
        
        # Combine existing and new changes as text not lists
        combined_changes = "\n".join(existing_changes + changes)

        # Upload combined changes to Drive
        media = MediaInMemoryUpload(combined_changes.encode('utf-8'),'text/plain')
        service.files().update(fileId=file_id, body=None, media_body=media).execute()

        # Clear local changes list and file
        changes.clear()
        open("offline_changes.txt", "w", encoding="utf-8").close()
    except Exception as e:
        logging.error(f"Error uploading changes: {e}", exc_info=True)
        
def download_changes(service):
    global changes
    try:
        file_metadata = service.files().get(fileId=file_id).execute()
        if file_metadata['mimeType'] == 'text/plain':
            with io.BytesIO() as downloaded_changes_file:
                request = service.files().get_media(fileId=file_id)
                downloader = MediaIoBaseDownload(downloaded_changes_file, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print("Downloaded %d%%." % int(status.progress() * 100))
                downloaded_changes_file.seek(0)
                downloaded_changes = downloaded_changes_file.read().decode('utf-8', errors='ignore').splitlines()
                
                # Write downloaded_changes to local "changes.txt"
                with open("changes.txt", "r+", encoding='utf-8', errors='ignore') as f:
                    for change in downloaded_changes:
                        f.write(change + "\n")
                
                # Write changes to SQLite
                conn = sqlite3.connect("contacts.db")
                cursor = conn.cursor()
                for query in downloaded_changes:
                    try:
                        cursor.execute(query)
                    except sqlite3.IntegrityError:
                        pass
                    except sqlite3.OperationalError as e:
                        if "no such table" in str(e) or "no column named" in str(e):
                            pass
                        else:
                            raise e
                conn.commit()
                conn.close()
                
    except Exception as e:
        logging.error(f"Error downloading changes: {e}", exc_info=True)




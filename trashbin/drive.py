import os
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from src.config.settings import SettingsManager

class Drive():
    """Google Drive Utils"""
    
    def __init__(self, folder) -> None:
        self.folder = folder
        self.drive = self.loginToDrive()
    
    def loginToDrive(self):
        drive_path = SettingsManager().get({'Drive': 'DrivePath'})
        if os.path.exists(drive_path):
            creds = service_account.Credentials.from_service_account_file(drive_path, scopes=["https://www.googleapis.com/auth/drive.file"])
            return build('drive', 'v3', credentials=creds)
        else:
            raise FileNotFoundError("No found DrivePath")
    
    def uploadToDrive(self, file, folder_id=None):
        """Upload to Google Drive.
        file: the path of file to upload
        folder_id: the ID of the folder to upload the file to"""
        
        if folder_id is None:
            folder_id = "1V4SV5RyMPztclV55xRZIIol874-se-1n" 

        file_metadata = {
            'name': os.path.basename(file),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file)

        max_retry_count = 3
        retry_count = 0

        while retry_count < max_retry_count:  # Three retries to upload if an error occurs.
            try:
                file = self.drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
                file_id = file.get('id')
                self.drive.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()
                return f'https://drive.google.com/file/d/{file_id}/view'
            except Exception as e:
                retry_count += 1
                print(f'error: error on uploading to drive. this is retry {retry_count}. error: {e}')
                if retry_count < max_retry_count:
                    self.drive = self.loginToDrive() # Create another session
                    time.sleep(2)
                else:
                    raise

    def uploadFolder(self, path):
        """Upload all files in a folder to Google Drive and return the folder link.
        path: the path of folder to upload"""
        
        parent_folder_id = "1V4SV5RyMPztclV55xRZIIol874-se-1n"  # ID da pasta pai
        folder_name = os.path.basename(path)
        
        # Cria a nova pasta no Drive e obtém seu ID
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        folder = self.drive.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        
        if not os.path.isdir(path):
            raise ValueError("The path provided is not a directory.")
        
        # Itera sobre todos os arquivos na pasta
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                self.uploadToDrive(file_path, folder_id)
        
        # Retorna o link para a nova pasta
        return f'https://drive.google.com/drive/folders/{folder_id}'

    def deleteAllFiles(self, folder_id=None):
        """Deleta TODOS os arquivos do Google Drive (sem mandar pra lixeira)."""

        query = "trashed=false"
        results = self.drive.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            print("Nenhum arquivo encontrado para deletar.")
            return

        for file in files:
            try:
                self.drive.files().delete(fileId=file['id']).execute()
                print(f"Deletado: {file['name']}")
            except Exception as e:
                print(f"Erro ao deletar {file['name']}: {e}")

        print("Todos os arquivos foram deletados.")

import oss2
import os
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.core.config import settings

class OSSService:
    def __init__(self):
        if settings.OSS_ACCESS_KEY_ID and settings.OSS_ACCESS_KEY_SECRET and settings.OSS_ENDPOINT:
            self.auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
            self.bucket = oss2.Bucket(self.auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
            self.domain = settings.OSS_BUCKET_DOMAIN
        else:
            self.bucket = None
            print("OSS not configured")

    def upload_file(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        if not self.bucket:
            # Mock upload for local dev if OSS not configured
            # Save to local 'static' folder
            save_dir = "static/uploads"
            os.makedirs(save_dir, exist_ok=True)
            
            # Generate unique filename
            ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(save_dir, unique_filename)
            
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            return f"/static/uploads/{unique_filename}"

        # Generate object name: YYYY/MM/uuid.ext
        ext = os.path.splitext(filename)[1]
        object_name = f"{datetime.now().strftime('%Y/%m')}/{uuid.uuid4()}{ext}"

        try:
            headers = {}
            if content_type:
                headers['Content-Type'] = content_type
            
            result = self.bucket.put_object(object_name, file_content, headers=headers)
            
            if result.status != 200:
                raise HTTPException(status_code=500, detail="OSS upload failed")
            
            # Return URL
            if self.domain:
                return f"{self.domain}/{object_name}"
            return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{object_name}"
            
        except Exception as e:
            print(f"OSS Upload Error: {e}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    def delete_file(self, file_url: str):
        if not self.bucket:
            # Local delete logic if needed, but risky for now to implement auto-delete on local
            return

        try:
            # Extract object name from URL
            # URL format: http://domain/object_name or https://bucket.endpoint/object_name
            if self.domain and file_url.startswith(self.domain):
                object_name = file_url.replace(f"{self.domain}/", "")
            else:
                 # Fallback extraction logic
                 # This is tricky without strict URL structure, simplified for now
                 parts = file_url.split('/')
                 # Assuming YYYY/MM/uuid.ext structure at the end
                 object_name = "/".join(parts[-3:]) 
            
            self.bucket.delete_object(object_name)
        except Exception as e:
            print(f"OSS Delete Error: {e}")
            # Don't raise error for delete failure to avoid blocking main logic
            pass

oss_service = OSSService()

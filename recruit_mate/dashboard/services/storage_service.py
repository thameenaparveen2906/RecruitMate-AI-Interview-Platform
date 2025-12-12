import os
from django.conf import settings
from django.core.files.storage import default_storage

class StorageService:
    """Service for local file storage (no Supabase needed)"""
    
    def upload_file(self, file, file_path):
        """Upload file to local media storage"""
        try:
            # Save file to media directory
            saved_path = default_storage.save(file_path, file)
            return {'path': saved_path}
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def get_file_url(self, file_path):
        """Get URL for file"""
        try:
            # Return media URL
            return settings.MEDIA_URL + file_path
        except Exception as e:
            print(f"Error getting file URL: {e}")
            return None
    
    def delete_file(self, file_path):
        """Delete file from storage"""
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            return {'success': True}
        except Exception as e:
            print(f"Error deleting file: {e}")
            return None

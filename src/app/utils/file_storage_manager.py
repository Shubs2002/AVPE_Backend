"""
File Storage Manager - Organizes all content types into proper folder structures.

Structure:
generated_content/
├── movies/
│   └── {Movie_Title}/
│       ├── metadata.json
│       ├── set_01.json
│       ├── set_02.json
│       └── ...
├── stories/
│   └── {Story_Title}/
│       ├── metadata.json
│       ├── segments.json
│       └── ...
├── memes/
│   └── {Meme_Title}/
│       ├── metadata.json
│       └── segments.json
├── free_content/
│   └── {Content_Title}/
│       ├── metadata.json
│       └── segments.json
├── music_videos/
│   └── {Song_Title}/
│       ├── metadata.json
│       └── segments.json
└── whatsapp_stories/
    └── {Story_Title}/
        ├── metadata.json
        └── segments.json
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ContentType:
    """Content type constants"""
    MOVIE = "movies"
    STORY = "stories"
    MEME = "memes"
    FREE_CONTENT = "free_content"
    MUSIC_VIDEO = "music_videos"
    WHATSAPP_STORY = "whatsapp_stories"
    
    @classmethod
    def all_types(cls) -> List[str]:
        return [cls.MOVIE, cls.STORY, cls.MEME, cls.FREE_CONTENT, cls.MUSIC_VIDEO, cls.WHATSAPP_STORY]


class FileStorageManager:
    """Manages file storage for all content types"""
    
    def __init__(self, base_dir: str = "generated_content"):
        """
        Initialize the file storage manager.
        
        Args:
            base_dir: Base directory for all generated content
        """
        self.base_dir = base_dir
        self._ensure_base_structure()
    
    def _ensure_base_structure(self):
        """Create the base directory structure if it doesn't exist"""
        for content_type in ContentType.all_types():
            type_dir = os.path.join(self.base_dir, content_type)
            os.makedirs(type_dir, exist_ok=True)
    
    @staticmethod
    def sanitize_title(title: str) -> str:
        """
        Sanitize a title for use as a folder name.
        
        Args:
            title: Original title
            
        Returns:
            Sanitized title safe for filesystem
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        # Limit length
        sanitized = sanitized[:100]
        # Ensure not empty
        if not sanitized:
            sanitized = f"untitled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return sanitized
    
    def get_content_directory(self, content_type: str, title: str, create: bool = True) -> str:
        """
        Get the directory path for a specific content item.
        
        Args:
            content_type: Type of content (use ContentType constants)
            title: Title of the content
            create: Whether to create the directory if it doesn't exist
            
        Returns:
            Full path to the content directory
        """
        if content_type not in ContentType.all_types():
            raise ValueError(f"Invalid content type: {content_type}. Must be one of {ContentType.all_types()}")
        
        safe_title = self.sanitize_title(title)
        content_dir = os.path.join(self.base_dir, content_type, safe_title)
        
        if create:
            os.makedirs(content_dir, exist_ok=True)
        
        return content_dir
    
    def save_metadata(self, content_type: str, title: str, metadata: Dict) -> str:
        """
        Save metadata for a content item.
        
        Args:
            content_type: Type of content
            title: Title of the content
            metadata: Metadata dictionary
            
        Returns:
            Path to the saved metadata file
        """
        content_dir = self.get_content_directory(content_type, title)
        metadata_path = os.path.join(content_dir, "metadata.json")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata_path
    
    def load_metadata(self, content_type: str, title: str) -> Optional[Dict]:
        """
        Load metadata for a content item.
        
        Args:
            content_type: Type of content
            title: Title of the content
            
        Returns:
            Metadata dictionary or None if not found
        """
        content_dir = self.get_content_directory(content_type, title, create=False)
        metadata_path = os.path.join(content_dir, "metadata.json")
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_set(self, content_type: str, title: str, set_number: int, set_data: Dict) -> str:
        """
        Save a story/movie set (for multi-set content).
        
        Args:
            content_type: Type of content
            title: Title of the content
            set_number: Set number
            set_data: Set data dictionary
            
        Returns:
            Path to the saved set file
        """
        content_dir = self.get_content_directory(content_type, title)
        set_filename = f"set_{set_number:02d}.json"
        set_path = os.path.join(content_dir, set_filename)
        
        with open(set_path, 'w', encoding='utf-8') as f:
            json.dump(set_data, f, indent=2, ensure_ascii=False)
        
        return set_path
    
    def load_set(self, content_type: str, title: str, set_number: int) -> Optional[Dict]:
        """
        Load a specific set.
        
        Args:
            content_type: Type of content
            title: Title of the content
            set_number: Set number
            
        Returns:
            Set data dictionary or None if not found
        """
        content_dir = self.get_content_directory(content_type, title, create=False)
        set_filename = f"set_{set_number:02d}.json"
        set_path = os.path.join(content_dir, set_filename)
        
        if not os.path.exists(set_path):
            return None
        
        with open(set_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_segments(self, content_type: str, title: str, segments_data: Dict) -> str:
        """
        Save segments for single-file content (memes, free content, etc.).
        
        Args:
            content_type: Type of content
            title: Title of the content
            segments_data: Segments data dictionary
            
        Returns:
            Path to the saved segments file
        """
        content_dir = self.get_content_directory(content_type, title)
        segments_path = os.path.join(content_dir, "segments.json")
        
        with open(segments_path, 'w', encoding='utf-8') as f:
            json.dump(segments_data, f, indent=2, ensure_ascii=False)
        
        return segments_path
    
    def load_segments(self, content_type: str, title: str) -> Optional[Dict]:
        """
        Load segments for single-file content.
        
        Args:
            content_type: Type of content
            title: Title of the content
            
        Returns:
            Segments data dictionary or None if not found
        """
        content_dir = self.get_content_directory(content_type, title, create=False)
        segments_path = os.path.join(content_dir, "segments.json")
        
        if not os.path.exists(segments_path):
            return None
        
        with open(segments_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_content(self, content_type: str) -> List[str]:
        """
        List all content items of a specific type.
        
        Args:
            content_type: Type of content
            
        Returns:
            List of content titles (folder names)
        """
        type_dir = os.path.join(self.base_dir, content_type)
        
        if not os.path.exists(type_dir):
            return []
        
        return [d for d in os.listdir(type_dir) if os.path.isdir(os.path.join(type_dir, d))]
    
    def get_all_sets(self, content_type: str, title: str) -> List[int]:
        """
        Get list of all set numbers that exist for a content item.
        
        Args:
            content_type: Type of content
            title: Title of the content
            
        Returns:
            List of set numbers
        """
        content_dir = self.get_content_directory(content_type, title, create=False)
        
        if not os.path.exists(content_dir):
            return []
        
        set_numbers = []
        for filename in os.listdir(content_dir):
            if filename.startswith("set_") and filename.endswith(".json"):
                try:
                    set_num = int(filename.replace("set_", "").replace(".json", ""))
                    set_numbers.append(set_num)
                except ValueError:
                    continue
        
        return sorted(set_numbers)
    
    def find_missing_sets(self, content_type: str, title: str, total_sets: int) -> List[int]:
        """
        Find which sets are missing for a content item.
        
        Args:
            content_type: Type of content
            title: Title of the content
            total_sets: Expected total number of sets
            
        Returns:
            List of missing set numbers
        """
        existing_sets = self.get_all_sets(content_type, title)
        expected_sets = set(range(1, total_sets + 1))
        existing_sets_set = set(existing_sets)
        
        return sorted(expected_sets - existing_sets_set)
    
    def get_content_info(self, content_type: str, title: str) -> Dict:
        """
        Get comprehensive information about a content item.
        
        Args:
            content_type: Type of content
            title: Title of the content
            
        Returns:
            Dictionary with content information
        """
        content_dir = self.get_content_directory(content_type, title, create=False)
        
        if not os.path.exists(content_dir):
            return {
                "exists": False,
                "title": title,
                "content_type": content_type
            }
        
        metadata = self.load_metadata(content_type, title)
        existing_sets = self.get_all_sets(content_type, title)
        has_segments = os.path.exists(os.path.join(content_dir, "segments.json"))
        
        info = {
            "exists": True,
            "title": title,
            "content_type": content_type,
            "directory": content_dir,
            "has_metadata": metadata is not None,
            "metadata": metadata,
            "has_sets": len(existing_sets) > 0,
            "existing_sets": existing_sets,
            "set_count": len(existing_sets),
            "has_segments_file": has_segments
        }
        
        # Add missing sets info if metadata has total_sets
        if metadata and "generation_info" in metadata:
            gen_info = metadata["generation_info"]
            if "total_sets" in gen_info:
                total_sets = gen_info["total_sets"]
                missing_sets = self.find_missing_sets(content_type, title, total_sets)
                info["total_sets_expected"] = total_sets
                info["missing_sets"] = missing_sets
                info["missing_count"] = len(missing_sets)
                info["is_complete"] = len(missing_sets) == 0
        
        return info
    
    def delete_content(self, content_type: str, title: str) -> bool:
        """
        Delete all files for a content item.
        
        Args:
            content_type: Type of content
            title: Title of the content
            
        Returns:
            True if deleted, False if not found
        """
        import shutil
        
        content_dir = self.get_content_directory(content_type, title, create=False)
        
        if not os.path.exists(content_dir):
            return False
        
        shutil.rmtree(content_dir)
        return True
    
    def migrate_old_files(self, old_dir: str, content_type: str) -> Dict:
        """
        Migrate files from old directory structure to new organized structure.
        
        Args:
            old_dir: Old directory path (e.g., "generated_movie_script")
            content_type: Type of content to migrate
            
        Returns:
            Dictionary with migration results
        """
        if not os.path.exists(old_dir):
            return {"success": False, "error": f"Directory not found: {old_dir}"}
        
        migrated = []
        errors = []
        
        # Find all metadata files in old directory
        for filename in os.listdir(old_dir):
            if filename.endswith("_metadata.json"):
                try:
                    # Load metadata to get title
                    old_metadata_path = os.path.join(old_dir, filename)
                    with open(old_metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    title = metadata.get("title", filename.replace("_metadata.json", ""))
                    
                    # Save to new structure
                    new_metadata_path = self.save_metadata(content_type, title, metadata)
                    
                    # Find and migrate all set files
                    base_name = filename.replace("_metadata.json", "")
                    set_files = [f for f in os.listdir(old_dir) if f.startswith(base_name + "_set_")]
                    
                    for set_file in set_files:
                        # Extract set number
                        set_num_str = set_file.replace(base_name + "_set_", "").replace(".json", "")
                        set_num = int(set_num_str)
                        
                        # Load and save to new location
                        old_set_path = os.path.join(old_dir, set_file)
                        with open(old_set_path, 'r', encoding='utf-8') as f:
                            set_data = json.load(f)
                        
                        new_set_path = self.save_set(content_type, title, set_num, set_data)
                    
                    migrated.append({
                        "title": title,
                        "metadata": new_metadata_path,
                        "sets_migrated": len(set_files)
                    })
                    
                except Exception as e:
                    errors.append({
                        "file": filename,
                        "error": str(e)
                    })
        
        return {
            "success": True,
            "migrated_count": len(migrated),
            "error_count": len(errors),
            "migrated": migrated,
            "errors": errors
        }


# Global instance
storage_manager = FileStorageManager()

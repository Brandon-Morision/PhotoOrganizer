# organizer.py
import os
import shutil
import re
from PIL import Image
from datetime import datetime
from PIL.ExifTags import TAGS # Import for get_exif_date


# Define a global set of supported extensions
SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", # Images
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v",          # Videos
    ".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx",         # Documents (can be extended)
    ".avi", # Added explicitly from your image/older list
    ".mov", # Added explicitly from your image/older list
    ".mkv", # Added explicitly from your image/older list
    ".webm", # Added explicitly from your image/older list
    ".m4v", # Added explicitly from your image/older list
    ".doc", # Added explicitly from your image/older list
    ".docx", # Added explicitly from your image/older list
    ".txt", # Added explicitly from your image/older list
    ".xlsx", # Added explicitly from your image/older list
    ".pptx" # Added explicitly from your image/older list
}


class PhotoOrganizer:
    """
    Contains the core logic for organizing photos and videos.
    It does not interact directly with the GUI.
    """
    def __init__(self):
        # Initialize internal lists of supported extensions based on the global set
        self.image_extensions = {ext for ext in SUPPORTED_EXTENSIONS if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']}
        self.video_extensions = {ext for ext in SUPPORTED_EXTENSIONS if ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']}


    def _get_date_from_file(self, file_path):
        """
        Attempts to get the creation date from EXIF data (for images)
        or falls back to file modification date. Returns date as YYYY/MM string.
        """
        file_extension = os.path.splitext(file_path)[1].lower()

        # Try to get EXIF date for images
        if file_extension in self.image_extensions:
            try:
                img = Image.open(file_path)
                exif_data = img._getexif()
                if exif_data:
                    # 0x9003 is DateTimeOriginal tag
                    if 0x9003 in exif_data:
                        date_str = exif_data[0x9003]
                        # EXIF date format is "YYYY:MM:DD HH:MM:SS"
                        dt_object = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                        return dt_object.strftime("%Y/%m")
            except Exception:
                pass # Fallback to modification date if EXIF fails or not found

        # Fallback to file modification date
        try:
            mod_timestamp = os.path.getmtime(file_path)
            dt_object = datetime.fromtimestamp(mod_timestamp)
            return dt_object.strftime("%Y/%m")
        except Exception:
            return None # Could not get any date


    def _get_subfolder_name(self, filename, organization_mode, file_path=None):
        """
        Determines the subfolder name based on the chosen organization mode.
        """
        if organization_mode == "date":
            date_folder = self._get_date_from_file(file_path)
            if date_folder:
                return date_folder
            else:
                # Fallback for files without readable dates (e.g., 'Unknown Date')
                return "Unknown Date"

        # Default to "name" organization mode if not "date"
        base_name_without_ext = os.path.splitext(filename)[0]

        initial_folder_candidate = ""
        if '_' in base_name_without_ext:
            initial_folder_candidate = base_name_without_ext.split('_')[0]
        elif '-' in base_name_without_ext:
            initial_folder_candidate = base_name_without_ext.split('-')[0]
        else:
            initial_folder_candidate = base_name_without_ext

        # Remove trailing patterns like ' (N)' or ' NNN' from the candidate
        subfolder_name = re.sub(r'\s*(\(\d+\)|\d+)$', '', initial_folder_candidate).strip()

        # Fallback if the name becomes empty after stripping numbers/parentheses
        if not subfolder_name:
            subfolder_name = base_name_without_ext.strip()

        # Clean up the subfolder name to remove invalid characters for folder names
        subfolder_name = re.sub(r'[\\/:*?"<>|]', '', subfolder_name)

        # Final check for empty or invalid subfolder name after all cleaning
        if not subfolder_name or subfolder_name.strip(". ") == "":
            return None # Indicate an invalid name

        return subfolder_name

    def organize_files(self, source_folder, destination_folder, progress_callback, log_callback, done_callback, use_copy, organization_mode, selected_extensions):
        """
        Main organization logic.
        """
        processed, skipped = 0, 0
        try:
            # Create destination folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)

            files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
            total_files = len(files)
            if total_files == 0:
                log_callback("No files found in source folder to organize.\n")
                done_callback(processed, skipped)
                return

            for i, filename in enumerate(files):
                file_path = os.path.join(source_folder, filename)
                _, ext = os.path.splitext(filename)
                ext = ext.lower()

                # Filter by selected file types
                if ext not in selected_extensions:
                    skipped += 1
                    log_callback(f"Skipped (not selected file type): {filename}\n")
                    # Update progress even for skipped files to show overall progress
                    progress_callback((i + 1) / total_files * 100)
                    continue

                subfolder_name = self._get_subfolder_name(filename, organization_mode, file_path)

                if subfolder_name is None: # Indicates an invalid name for organization
                    skipped += 1
                    log_callback(f"Skipped (could not determine subfolder name): {filename}\n")
                    progress_callback((i + 1) / total_files * 100)
                    continue

                target_subfolder_path = os.path.join(destination_folder, subfolder_name)
                
                try:
                    os.makedirs(target_subfolder_path, exist_ok=True)
                except Exception as e:
                    skipped += 1
                    log_callback(f"Error creating folder for {filename}: {e}\n")
                    progress_callback((i + 1) / total_files * 100)
                    continue

                try:
                    dest_file_path = os.path.join(target_subfolder_path, filename)
                    if use_copy:
                        shutil.copy2(file_path, dest_file_path)
                        log_callback(f"Copied: {filename} -> {subfolder_name}/\n")
                    else:
                        shutil.move(file_path, dest_file_path)
                        log_callback(f"Moved: {filename} -> {subfolder_name}/\n")
                    processed += 1
                except PermissionError as e:
                    skipped += 1
                    log_callback(f"Permission error {'copying' if use_copy else 'moving'} {filename}: {e}\n")
                except shutil.Error as e:
                    skipped += 1
                    log_callback(f"File operation error for {filename}: {e}\n")
                except Exception as e:
                    skipped += 1
                    log_callback(f"Unexpected error {'copying' if use_copy else 'moving'} {filename}: {e}\n")

                # Update progress for each file
                progress_value = (i + 1) / total_files * 100
                progress_callback(progress_value)

        except Exception as e:
            # Catch any unexpected errors during the thread execution and report them
            log_callback(f"An unexpected error occurred during organization: {e}\n")
        finally:
            done_callback(processed, skipped)
# Photo Organizer

A Python GUI application for organizing photos and videos into folders based on their name prefix or creation date.

## Features

* **Folder Selection:** Easily select source and destination folders for your files.
* **Organization Modes:**
    * **By Name:** Organize files into folders based on a prefix from their filename (e.g., `EventName_001.jpg` goes into an `EventName` folder).
    * **By Date:** Organize files into folders based on their creation date (uses EXIF data for images, falls back to file modification date for others, resulting in `YYYY/MM` structured folders).
* **Copy/Move Option:** Choose to either copy files (leaving originals in the source) or move them (transferring them completely).
* **File Type Filtering:** Select which file types (images, videos, documents, etc.) to include in the organization process using checkboxes.
* **Real-time Feedback:** Features a progress bar and a log output area to show the progress and details of the organization process.
* **Modern UI:** Built with `tkinter` and styled using `ttkbootstrap` for a clean and modern look, including theme toggling.
* **Tooltips:** Informative tooltips on various UI elements to guide the user.

## Requirements

To run this application, you need:

* Python 3.x
* `Pillow` (PIL) for image processing (especially for EXIF data)
* `ttkbootstrap` for the modern GUI styling

You can install all the necessary dependencies by navigating to your project directory in the terminal and running:

```bash
pip install -r requirements.txt

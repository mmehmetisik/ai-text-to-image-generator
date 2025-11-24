# ============================================
# GALLERY MANAGER (gallery_manager.py)
# This file manages the gallery system for generated images.
# It stores images in the session using Streamlit session_state,
# and handles ZIP file creation and bulk download operations.
# ============================================

# --- LIBRARY IMPORTS ---

import os  # For file and folder operations
import io  # For in-memory file operations
import zipfile  # For creating ZIP archives
from datetime import datetime  # For date and time operations
from PIL import Image  # For image processing

# Add project root directory to Python's search path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from our own modules
from utils.image_processor import image_to_base64, create_thumbnail


# ============================================
# GALLERY CLASS
# ============================================

class GalleryManager:
    """
    Class that manages gallery operations.

    What is a Class?
    A class is a template that holds related data and functions together.
    For example, a "Car" class holds properties like color, speed
    and behaviors like start(), stop() together.

    This class gathers all gallery-related operations in one place:
    - Adding images
    - Deleting images
    - Listing gallery
    - Creating ZIP
    """

    def __init__(self, session_state):
        """
        The initializer (constructor) method of the class.
        Runs whenever a GalleryManager object is created.

        What is __init__?
        It's a special method in Python (double underscore = dunder method).
        It's automatically called when an object is created and sets up initial configurations.

        Parameters:
        - session_state: Streamlit's session state object
                        Preserves data even when the page is refreshed
        """

        # self is a reference to the class itself
        # By saying self.session_state, we can use this value anywhere in the class
        self.session_state = session_state

        # Prepare space for gallery in session_state
        # If not created before, initialize as empty list
        self._initialize_gallery()

    def _initialize_gallery(self):
        """
        Creates the gallery list in session state (if it doesn't exist).

        The _ (underscore) at the beginning of the method name indicates that
        this method is "private", meaning it should only be called from within the class.
        There's no true private in Python, but this is a convention (agreement).
        """

        # If "gallery" key doesn't exist in session_state, create it
        if "gallery" not in self.session_state:
            self.session_state.gallery = []  # Start with empty list

        # Do the same for counter (total generated images count)
        if "total_generated" not in self.session_state:
            self.session_state.total_generated = 0

    def add_image(self, image, prompt, style, parameters, seed=None):
        """
        Adds a new image to the gallery.

        Parameters:
        - image (PIL.Image): Image to be added
        - prompt (str): Prompt that created the image
        - style (str): Style name used
        - parameters (dict): Parameters used (size, steps, etc.)
        - seed (int): Seed value used in image generation

        Returns:
        - Gallery ID of the added image
        """

        # --- CREATE UNIQUE ID ---
        # Each image must have its own unique identifier
        # Date-time + counter combination ensures uniqueness
        image_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.session_state.total_generated}"

        # --- CREATE THUMBNAIL (SMALL IMAGE) ---
        # We'll show small previews instead of large images in gallery view
        # This provides both speed and memory savings
        thumbnail = create_thumbnail(image, max_size=(256, 256))

        # --- PREPARE IMAGE DATA ---
        # We gather all information in a dictionary
        image_data = {
            "id": image_id,  # Unique identifier
            "image": image,  # Original image (PIL.Image)
            "thumbnail": thumbnail,  # Small preview
            "prompt": prompt,  # Prompt used
            "style": style,  # Style used
            "parameters": parameters,  # All parameters
            "seed": seed,  # Seed value
            "created_at": datetime.now(),  # When it was generated
            "favorite": False  # Is it marked as favorite?
        }

        # --- ADD TO GALLERY ---
        # List's append() method adds new item
        self.session_state.gallery.append(image_data)

        # --- INCREMENT COUNTER ---
        self.session_state.total_generated += 1

        return image_id

    def delete_image(self, image_id):
        """
        Deletes the specified image from gallery.

        Parameters:
        - image_id (str): ID of the image to be deleted

        Returns:
        - True: Deletion successful
        - False: Image not found
        """

        # --- FIND AND DELETE IMAGE ---
        # enumerate() returns both index and value
        # This way we can delete by index when we find the image
        for index, image in enumerate(self.session_state.gallery):
            if image["id"] == image_id:
                # pop() deletes and returns the item at specified index
                self.session_state.gallery.pop(index)
                return True

        # Image not found
        return False

    def get_image(self, image_id):
        """
        Gets the image with specified ID.

        Parameters:
        - image_id (str): ID of the requested image

        Returns:
        - Image data dictionary or None (if not found)
        """

        # Filtering with list comprehension
        # [x for x in list if condition] structure filters items matching the condition
        found = [g for g in self.session_state.gallery if g["id"] == image_id]

        # If found, return the first one (should be single result since ID is unique)
        # If found list is empty, return None
        return found[0] if found else None

    def get_all_images(self):
        """
        Returns all images in the gallery.

        Returns:
        - Image list (newest first)
        """

        # reversed() reverses the list (newest first)
        # Convert back to list with list()
        return list(reversed(self.session_state.gallery))

    def gallery_size(self):
        """
        Returns the number of images in the gallery.

        Returns:
        - int: Image count
        """

        return len(self.session_state.gallery)

    def toggle_favorite(self, image_id):
        """
        Toggles the favorite status of the image.
        If favorite, removes from favorites; if not, makes it favorite.

        Parameters:
        - image_id (str): Image ID

        Returns:
        - New favorite status (True/False) or None (if not found)
        """

        for image in self.session_state.gallery:
            if image["id"] == image_id:
                # not operator reverses boolean value
                # True -> False, False -> True
                image["favorite"] = not image["favorite"]
                return image["favorite"]

        return None

    def get_favorites(self):
        """
        Returns only favorite-marked images.

        Returns:
        - List of favorite images
        """

        # Filtering with list comprehension
        return [g for g in self.session_state.gallery if g["favorite"]]

    def clear_gallery(self):
        """
        Deletes all images in the gallery.
        Use carefully - cannot be undone!
        """

        self.session_state.gallery = []
        # We don't reset the counter, let total generated count remain as record


# ============================================
# ZIP FILE CREATION FUNCTION
# ============================================

def create_zip(images, file_format="PNG"):
    """
    Packages multiple images into a ZIP archive.
    Used for bulk download.

    What is a ZIP File?
    A format that combines multiple files into a single compressed file.
    It both reduces file size and makes it easier to download/share
    many files at once.

    Parameters:
    - images (list): List of image data dictionaries
    - file_format (str): Format to save images in

    Returns:
    - ZIP file byte data (ready for download)
    """

    # --- CREATE ZIP FILE IN MEMORY ---
    # We create ZIP in memory without writing to disk
    zip_buffer = io.BytesIO()

    # --- CREATE ZIP ARCHIVE ---
    # We create archive with zipfile.ZipFile
    # "w" = write mode
    # ZIP_DEFLATED = compression algorithm
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        # Loop for each image
        for index, image_data in enumerate(images):

            # --- CONVERT IMAGE TO BYTES ---
            image_buffer = io.BytesIO()
            image_data["image"].save(image_buffer, format=file_format)
            image_buffer.seek(0)

            # --- CREATE FILE NAME ---
            # Use first 30 characters of prompt in file name
            # Clean invalid characters
            prompt_short = image_data["prompt"][:30]
            # Remove characters that cannot be used in file names
            invalid_characters = '<>:"/\\|?*'
            for char in invalid_characters:
                prompt_short = prompt_short.replace(char, "")

            # Determine file extension
            extension = "jpg" if file_format == "JPEG" else file_format.lower()
            file_name = f"{index + 1:02d}_{prompt_short}.{extension}"

            # --- ADD TO ZIP ---
            # writestr() writes string or byte data directly to ZIP
            zip_file.writestr(file_name, image_buffer.getvalue())

        # --- ADD METADATA FILE ---
        # A text file recording which prompts and parameters were used
        metadata = "AI Image Generator - Generation Info\n"
        metadata += "=" * 50 + "\n\n"

        for index, image_data in enumerate(images):
            metadata += f"Image {index + 1}:\n"
            metadata += f"  Prompt: {image_data['prompt']}\n"
            metadata += f"  Style: {image_data['style']}\n"
            metadata += f"  Seed: {image_data.get('seed', 'Not specified')}\n"
            metadata += f"  Created: {image_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            metadata += "\n"

        zip_file.writestr("generation_info.txt", metadata)

    # --- REWIND BUFFER TO START ---
    zip_buffer.seek(0)

    return zip_buffer.getvalue()


# ============================================
# SINGLE IMAGE DOWNLOAD PREPARATION
# ============================================

def prepare_for_download(image, file_format="PNG", quality=95):
    """
    Prepares a single image for download.

    Parameters:
    - image (PIL.Image): Image to be downloaded
    - file_format (str): File format (PNG, JPEG, WEBP)
    - quality (int): Quality for JPEG/WEBP (1-100)

    Returns:
    - (byte_data, mime_type, extension)
    """

    # --- PREPARE IMAGE DATA ---
    buffer = io.BytesIO()

    # RGBA image must be converted to RGB when converting to JPEG
    if file_format == "JPEG" and image.mode == "RGBA":
        # Paste onto white background
        rgb_image = Image.new("RGB", image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        image = rgb_image

    # Save according to format
    if file_format in ["JPEG", "WEBP"]:
        image.save(buffer, format=file_format, quality=quality)
    else:
        image.save(buffer, format=file_format)

    buffer.seek(0)

    # --- DETERMINE MIME TYPE ---
    # MIME type tells the browser the file type
    # This way the browser processes the file correctly
    mime_types = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp"
    }

    # --- DETERMINE EXTENSION ---
    extensions = {
        "PNG": "png",
        "JPEG": "jpg",
        "WEBP": "webp"
    }

    return (
        buffer.getvalue(),
        mime_types.get(file_format, "image/png"),
        extensions.get(file_format, "png")
    )
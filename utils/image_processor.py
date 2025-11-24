# ============================================
# IMAGE PROCESSING MODULE (image_processor.py)
# This file contains all functions related to
# processing generated images: saving, resizing,
# format conversion, base64 encode/decode, etc.
# ============================================

# --- LIBRARY IMPORTS ---

import os  # For file and folder operations (path creation, folder existence check)
import io  # For in-memory file operations (creating byte streams)
import base64  # Converting binary data to text format (for displaying images on web)
from datetime import datetime  # Date and time operations (for file naming)
from PIL import Image  # Python Imaging Library - Image processing library

# Add project root directory to Python's search path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================
# IMAGE SAVING FUNCTION
# ============================================

def save_image(image, folder="generated_images", file_name=None, format="PNG"):
    """
    Saves a PIL Image object as a file.

    Parameters:
    - image (PIL.Image): Image to be saved
    - folder (str): Folder name to save in (default: generated_images)
    - file_name (str): File name (if None, auto-generated)
    - format (str): File format (PNG, JPEG, WEBP)

    Returns:
    - (True, file_path): Successful
    - (False, error_message): Failed
    """

    try:
        # --- FOLDER CHECK AND CREATION ---
        # os.path.exists() checks if folder exists
        # If not, we create it with os.makedirs()
        if not os.path.exists(folder):
            os.makedirs(folder)  # Create folder and parent folders if needed

        # --- FILE NAME CREATION ---
        # If file name not provided, create unique name based on date-time
        # This way files don't overwrite each other
        if file_name is None:
            # datetime.now() gets current date and time
            # strftime() converts date to our desired format
            # Example output: "image_20241123_143052"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"image_{timestamp}"

        # --- ADD FILE EXTENSION ---
        # Add correct extension based on format
        # .lower() converts to lowercase (PNG -> png)
        extension = format.lower()
        if extension == "jpeg":
            extension = "jpg"  # Use .jpg extension for JPEG format

        # --- CREATE FULL FILE PATH ---
        # os.path.join() creates path appropriate for operating system
        # Uses \ on Windows, / on Linux/Mac
        full_path = os.path.join(folder, f"{file_name}.{extension}")

        # --- SAVE IMAGE ---
        # PIL Image's save() method writes image to file
        # format parameter determines output format
        image.save(full_path, format=format)

        return (True, full_path)

    except PermissionError:
        # This error occurs when there's no write permission to folder
        return (False, "Permission error! Check folder permissions.")

    except Exception as e:
        # Other unexpected errors
        return (False, f"Save error: {str(e)}")


# ============================================
# IMAGE RESIZING FUNCTION
# ============================================

def resize_image(image, new_width=None, new_height=None, keep_ratio=True):
    """
    Resizes image to new dimensions.

    Parameters:
    - image (PIL.Image): Image to be resized
    - new_width (int): Target width (pixels)
    - new_height (int): Target height (pixels)
    - keep_ratio (bool): Should aspect ratio be preserved?

    Returns:
    - Resized PIL.Image object
    """

    # Get current dimensions
    current_width, current_height = image.size

    # --- RESIZE WHILE KEEPING RATIO ---
    if keep_ratio:
        # Calculate aspect ratio
        # Example: For 1920x1080 image, ratio = 1920/1080 = 1.78
        ratio = current_width / current_height

        if new_width and not new_height:
            # Only width given, calculate height
            new_height = int(new_width / ratio)

        elif new_height and not new_width:
            # Only height given, calculate width
            new_width = int(new_height * ratio)

        elif new_width and new_height:
            # Both given, fit while keeping ratio
            # Adjust based on which dimension is limiting
            target_ratio = new_width / new_height

            if ratio > target_ratio:
                # Image is wider, adjust by width
                new_height = int(new_width / ratio)
            else:
                # Image is taller, adjust by height
                new_width = int(new_height * ratio)

    # --- RESIZING OPERATION ---
    # Image.LANCZOS is a high quality resampling algorithm
    # Other options: NEAREST (fast but low quality), BILINEAR, BICUBIC
    resized = image.resize(
        (new_width, new_height),
        Image.LANCZOS
    )

    return resized


# ============================================
# BASE64 ENCODE FUNCTION
# ============================================

def image_to_base64(image, format="PNG"):
    """
    Converts PIL Image object to base64 string.
    This is used to display images directly in HTML/web.

    What is Base64?
    It's an encoding system that converts binary data to ASCII text.
    Used to transport image files as text.

    Parameters:
    - image (PIL.Image): Image to be converted
    - format (str): Image format (PNG, JPEG)

    Returns:
    - Base64 encoded string
    """

    # --- CREATE FILE IN MEMORY ---
    # io.BytesIO() creates a temporary byte stream in memory
    # We can process image data without writing actual file
    buffer = io.BytesIO()

    # --- SAVE IMAGE TO BUFFER ---
    # Writing to memory instead of saving to file
    image.save(buffer, format=format)

    # --- RETURN TO BEGINNING OF BUFFER ---
    # seek(0) moves read position to beginning
    # Required to read after writing
    buffer.seek(0)

    # --- CONVERT TO BASE64 ---
    # buffer.getvalue() gets all byte data
    # base64.b64encode() converts bytes to base64
    # .decode('utf-8') converts byte string to normal string
    base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return base64_string


# ============================================
# BASE64 DECODE FUNCTION
# ============================================

def base64_to_image(base64_string):
    """
    Converts base64 string to PIL Image object.
    Converts base64 data from API or database to image.

    Parameters:
    - base64_string (str): Base64 encoded image data

    Returns:
    - PIL.Image object
    """

    # --- DECODE BASE64 ---
    # base64.b64decode() converts string to byte data
    image_bytes = base64.b64decode(base64_string)

    # --- CREATE IMAGE FROM BYTES ---
    # Open byte data like a file with io.BytesIO
    # Image.open() converts this "file" to PIL Image
    image = Image.open(io.BytesIO(image_bytes))

    return image


# ============================================
# GET IMAGE INFO FUNCTION
# ============================================

def get_image_info(image):
    """
    Returns basic information about the image.
    Used to show image details to user.

    Parameters:
    - image (PIL.Image): Image to get info about

    Returns:
    - Dictionary containing information
    """

    # --- SIZE INFORMATION ---
    width, height = image.size

    # --- MEGAPIXEL CALCULATION ---
    # Total pixel count / 1 million = megapixels
    megapixels = (width * height) / 1_000_000

    # --- COLOR MODE ---
    # RGB: Color image (Red, Green, Blue)
    # RGBA: Color + transparency (Alpha channel)
    # L: Grayscale
    # P: Palette (limited color count)
    color_mode = image.mode

    # --- CREATE INFO DICTIONARY ---
    info = {
        "width": width,
        "height": height,
        "megapixels": round(megapixels, 2),  # Round to 2 decimal places
        "color_mode": color_mode,
        "size_text": f"{width}x{height}",  # Ready text for display
        "aspect_ratio": round(width / height, 2)  # For ratios like 16:9, 4:3
    }

    return info


# ============================================
# IMAGE FORMAT CONVERSION FUNCTION
# ============================================

def convert_format(image, target_format="JPEG", quality=90):
    """
    Converts image to a different format.

    Parameters:
    - image (PIL.Image): Image to be converted
    - target_format (str): Target format (JPEG, PNG, WEBP)
    - quality (int): Quality for JPEG/WEBP (1-100)

    Returns:
    - PIL.Image object in new format and byte data
    """

    # --- RGBA TO RGB CONVERSION ---
    # JPEG format doesn't support transparency (alpha)
    # If image is RGBA, we need to convert to RGB
    if target_format == "JPEG" and image.mode == "RGBA":
        # Create white background
        background = Image.new("RGB", image.size, (255, 255, 255))
        # Paste transparent image onto background
        background.paste(image, mask=image.split()[3])  # 3rd channel is alpha channel
        image = background

    # --- CONVERSION OPERATION ---
    buffer = io.BytesIO()

    # Save parameters vary based on format
    if target_format in ["JPEG", "WEBP"]:
        # These formats accept quality parameter
        image.save(buffer, format=target_format, quality=quality)
    else:
        # Lossless formats like PNG
        image.save(buffer, format=target_format)

    buffer.seek(0)

    # Reload image in new format
    new_image = Image.open(buffer)

    return new_image, buffer.getvalue()


# ============================================
# THUMBNAIL (SMALL IMAGE) CREATION
# ============================================

def create_thumbnail(image, max_size=(256, 256)):
    """
    Creates a small preview version of the image.
    Will be used in gallery view.

    Parameters:
    - image (PIL.Image): Original image
    - max_size (tuple): Maximum width and height

    Returns:
    - Shrunk PIL.Image object
    """

    # Copy original image (to not modify original)
    # .copy() creates a new Image object
    thumbnail = image.copy()

    # thumbnail() method fits image to given size
    # Automatically preserves aspect ratio
    # Image.LANCZOS for quality shrinking
    thumbnail.thumbnail(max_size, Image.LANCZOS)

    return thumbnail
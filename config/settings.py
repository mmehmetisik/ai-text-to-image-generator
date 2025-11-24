# ============================================
# APPLICATION SETTINGS (settings.py)
# This file contains the general configuration settings for the application.
# All settings are managed from a single place, making it easy to make changes.
# ============================================

# --- LIBRARY IMPORTS ---

import os  # Provides interaction with the operating system. We'll use it to read environment variables.

from dotenv import load_dotenv  # Loads sensitive information (like API keys) from .env file into Python.

# --- LOAD .ENV FILE ---

# This function finds the .env file in the project folder and adds its variables
# to the operating system's environment variables. This way we can read them with os.getenv().
load_dotenv()

# --- HUGGING FACE API SETTINGS ---

# The os.getenv() function reads values from environment variables.
# If HUGGINGFACE_API_KEY exists in the .env file, it retrieves it.
# If not, it returns None (in this case, the API won't work).
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# The base URL where we'll send requests to Hugging Face's Inference API.
# We'll append the model name to the end of this URL.
HUGGINGFACE_API_URL = "https://router.huggingface.co/hf-inference/models/"

# --- AI MODEL TO BE USED ---

# Stable Diffusion 2.1: A powerful AI model that generates images from text descriptions.
# An open-source model developed by stabilityai company.
DEFAULT_MODEL = "stabilityai/stable-diffusion-2-1"

# --- IMAGE SIZE OPTIONS ---

# Size options to be presented to the user.
# Dictionary structure: "Display Name": (width, height)
# Stored as tuples because width and height will be used together.
IMAGE_SIZES = {
    "Square (512x512)": (512, 512),        # Ideal for profile photos, icons
    "Landscape (768x512)": (768, 512),     # For scenery, wide scenes
    "Portrait (512x768)": (512, 768),      # For portraits, vertical compositions
    "Large Square (1024x1024)": (1024, 1024)  # High quality but slower
}

# --- IMAGE GENERATION PARAMETERS ---

# Inference Steps:
# The model creates the image step by step. More steps = higher quality but slower.
# 20-30 usually provides a good balance.
DEFAULT_STEPS = 25
MIN_STEPS = 15   # Too low may result in blurry/distorted images
MAX_STEPS = 50   # Too high will unnecessarily slow down the process

# Guidance Scale:
# Determines how closely the model follows the prompt.
# Low value (1-5): More creative but may deviate from the prompt
# High value (10-20): Very faithful to the prompt but sometimes oversaturated images
# 7-8 usually gives the best results.
DEFAULT_GUIDANCE = 7.5
MIN_GUIDANCE = 1.0
MAX_GUIDANCE = 20.0

# --- GENERAL APPLICATION SETTINGS ---

APP_TITLE = "AI Image Generator"  # Title to appear in browser tab and on the page
APP_ICON = "🎨"                    # Emoji/icon to appear in browser tab
MAX_IMAGES_PER_REQUEST = 4        # User can generate up to 4 variations at once
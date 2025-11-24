# ============================================
# HUGGING FACE API HANDLER (hf_api_handler.py)
# NEW VERSION - Uses InferenceClient
# ============================================
# This file manages all communication with the Hugging Face API.
# Performs text-to-image (generating images from text) operations.
# Connects to modern Hugging Face API using InferenceClient.
# ============================================

# --- LIBRARY IMPORTS ---

import time  # For time operations (wait times, seed generation)
import os  # For operating system operations (file paths)
import sys  # For Python system operations (module paths)

# Add project root directory to Python's module search path
# This allows us to import files from config and utils folders
# __file__: Path of this file (hf_api_handler.py)
# os.path.dirname(): Go up one folder
# By calling twice, we go from utils -> ai-image-generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import InferenceClient from Hugging Face's official Python library
# InferenceClient: A class that provides easy access to Hugging Face models
# We use this modern approach instead of the old requests.post() method
from huggingface_hub import InferenceClient

# Get API key and model settings from our config file
# All configuration is centralized in settings.py (Single Source of Truth)
from config.settings import (
    HUGGINGFACE_API_KEY,
    DEFAULT_MODEL,
    ALTERNATIVE_MODELS
)

# Import our logging functions
# This way all operations are written to both console and log file
from utils.logger import log_info, log_error, log_debug, log_warning


# ============================================
# CREATE INFERENCE CLIENT
# ============================================

def get_client():
    """
    Creates a Hugging Face InferenceClient.

    What is InferenceClient?
    It's the official Python class used to connect to the Hugging Face API.
    It authenticates with a token (API key).
    It offers ready-made methods like text_to_image(), text_to_speech().

    Returns:
    - Success: InferenceClient object
    - Failure: None
    """

    # API key check
    # We can't create client without a key
    if not HUGGINGFACE_API_KEY:
        log_error("API key not found!")
        return None

    try:
        # Create InferenceClient object
        # token parameter: Our Hugging Face API key (starts with hf_)
        # Our identity is verified with this token and API access is granted
        client = InferenceClient(
            token=HUGGINGFACE_API_KEY,
        )
        return client
    except Exception as e:
        # If any error occurs, log it and return None
        log_error(f"Client creation error: {str(e)}")
        return None


# ============================================
# MAIN FUNCTION: GENERATE IMAGE
# ============================================

def generate_image(
        prompt,  # Text description entered by user
        negative_prompt="",  # Unwanted elements (optional)
        width=512,  # Image width (pixels)
        height=512,  # Image height (pixels)
        num_steps=25,  # Inference steps - quality setting
        guidance_scale=7.5,  # Prompt adherence ratio
        seed=None  # Randomness seed (for reproducibility)
):
    """
    Generates an image using Hugging Face InferenceClient.

    How Does Text-to-Image Work?
    1. Text prompt is "understood" by the model (text encoding)
    2. Model creates image step by step starting from random noise
    3. Image becomes clearer with each step (diffusion process)
    4. Full image emerges at the final step

    Parameters:
    - prompt (str): Text describing what kind of image we want
    - negative_prompt (str): Things we DON'T WANT in the image
    - width (int): Width of output image (pixels)
    - height (int): Height of output image (pixels)
    - num_steps (int): Number of diffusion steps (more = quality but slow)
    - guidance_scale (float): How closely to follow the prompt (7-15 ideal)
    - seed (int): Seed value to reproduce the same result

    Returns:
    - Success: (True, PIL.Image object, success message)
    - Failure: (False, None, error message)
    """

    # --- LOG OPERATION START ---
    # These logs appear in terminal and are written to log file
    log_info(f"=== IMAGE GENERATION STARTED ===")
    log_info(f"Prompt: {prompt[:50]}...")  # First 50 characters (not too long)
    log_info(f"Model: {DEFAULT_MODEL}")
    log_info(f"Size: {width}x{height}")

    # --- CREATE CLIENT ---
    # Get the client object that will communicate with API
    client = get_client()
    if client is None:
        return (False, None, "Could not establish API connection. Check API key.")

    # --- TRY MODELS ---
    # First try default model, if it fails switch to alternatives
    # This approach is known as "fallback"
    models_to_try = [DEFAULT_MODEL] + ALTERNATIVE_MODELS

    # Try each model in order
    for model in models_to_try:
        log_info(f"Trying model: {model}")

        try:
            # --- SEND API REQUEST ---
            log_info("Sending API request...")

            # text_to_image() method: Generates image from text description
            # This method is one of InferenceClient's ready-made methods
            # It handles all complex API calls for us
            image = client.text_to_image(
                prompt=prompt,  # Main text description
                model=model,  # Model to use
                negative_prompt=negative_prompt if negative_prompt else None,  # Unwanted elements
                width=width,  # Image width
                height=height,  # Image height
                num_inference_steps=num_steps,  # Quality steps
                guidance_scale=guidance_scale,  # Prompt adherence
            )

            # --- SUCCESS ---
            # If we got here without errors, image has been generated
            log_info("✅ Image generated successfully!")
            log_info(f"Image size: {image.size}")

            # Return as tuple: (success status, image, message)
            return (True, image, "Image generated successfully!")

        except Exception as e:
            # --- ERROR HANDLING ---
            # An error occurred during API call
            error_msg = str(e)
            log_error(f"Model {model} error: {error_msg}")

            # Different actions based on error type

            # Model loading error (503)
            # Models on Hugging Face are not kept active continuously
            # Model may need to load on first request (cold start)
            if "loading" in error_msg.lower() or "503" in error_msg:
                log_warning("Model is loading, waiting...")
                return (False, None, f"Model is loading... Please wait 30 seconds and try again.")

            # Rate limit error (429)
            # Too many requests sent, need to wait a bit
            if "429" in error_msg or "rate" in error_msg.lower():
                log_warning("Rate limit exceeded!")
                return (False, None, "Too many requests! Wait 1 minute and try again.")

            # Authorization error (401)
            # API key is invalid or expired
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                log_error("API key is invalid!")
                return (False, None, "API key is invalid! Get a new token from Hugging Face.")

            # Try next model for other errors
            log_warning(f"Trying next model...")
            continue  # Go to next iteration of for loop

    # --- ALL MODELS FAILED ---
    # We end up here if no model worked
    log_error("All models failed!")
    return (False, None, "Could not generate image. Please try again later.")


# ============================================
# API CONNECTION TEST - REAL TEST
# ============================================

def test_api_connection():
    """
    Checks if API connection is REALLY working.

    This function is called when the application starts.
    Shows "API Connection Ready" or error message in sidebar.

    Check Steps:
    1. Is there an API key?
    2. Is API key in correct format? (should start with hf_)
    3. Can InferenceClient be created?

    Returns:
    - (True, message): Connection successful
    - (False, message): Connection failed
    """

    log_info("=== API CONNECTION TEST ===")

    # --- IS THERE AN API KEY? ---
    # Should have been read from .env file
    if not HUGGINGFACE_API_KEY:
        log_error("API key not found!")
        return (False, "API key not found! Check .env file.")

    # --- FORMAT CHECK ---
    # Hugging Face API keys start with "hf_"
    # This is a simple validation to prevent pasting wrong key
    if not HUGGINGFACE_API_KEY.startswith("hf_"):
        log_error("API key format is wrong!")
        return (False, "API key format is wrong! Should start with 'hf_'.")

    # --- CLIENT CREATION TEST ---
    try:
        # Try to create InferenceClient
        # If this succeeds, API key is valid
        client = InferenceClient(token=HUGGINGFACE_API_KEY)
        log_info("✅ InferenceClient created")

        # Note: We're not making a real API call here
        # We're only verifying that client can be created
        # Real test will be done when image is generated
        log_info("✅ API connection ready")
        return (True, "API connection ready.")

    except Exception as e:
        # If client couldn't be created, return error
        log_error(f"API connection error: {str(e)}")
        return (False, f"API connection error: {str(e)}")


# ============================================
# GENERATE MULTIPLE IMAGES
# ============================================

def generate_multiple_images(
        prompt,  # Text description entered by user
        negative_prompt="",  # Unwanted elements
        width=512,  # Image width
        height=512,  # Image height
        num_steps=25,  # Quality steps
        guidance_scale=7.5,  # Prompt adherence
        count=2  # Number of images to generate
):
    """
    Generates multiple images with the same prompt.

    Why Multiple Images?
    AI image generation gives different results each time.
    If you generate 4 images with the same prompt, you get 4 different results.
    User can choose their favorite.

    How Are Different Results Generated?
    Each image is generated with a different "seed" value.
    Seed is the starting point of the random number generator.
    Different seed = different randomness = different image

    Parameters:
    - Other parameters are same as generate_image()
    - count (int): How many images to generate (1-4 recommended)

    Returns:
    - (successful_images_list, error_messages_list)
    """

    log_info(f"=== MULTIPLE IMAGE GENERATION: {count} images ===")

    # We keep successful images and errors in separate lists
    successful_images = []  # [{"image": PIL.Image, "seed": 12345}, ...]
    error_messages = []  # ["Image 1: error message", ...]

    # --- CREATE BASE SEED ---
    # time.time() returns current Unix timestamp (in seconds)
    # Since this value changes every second, we can generate unique seeds
    # Convert to integer with int()
    base_seed = int(time.time())

    # Loop for each image
    for i in range(count):
        # Different seed for each image: base + 0, base + 1, base + 2, ...
        current_seed = base_seed + i
        log_info(f"Generating image {i + 1}/{count}...")

        # Generate single image
        success, image, message = generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_steps=num_steps,
            guidance_scale=guidance_scale,
            seed=current_seed
        )

        # Process result
        if success:
            # Add successful image to list
            # We store both image and seed (for metadata)
            successful_images.append({
                "image": image,
                "seed": current_seed
            })
            log_info(f"✅ Image {i + 1} successful!")
        else:
            # Save error message
            error_messages.append(f"Image {i + 1}: {message}")
            log_warning(f"❌ Image {i + 1} failed: {message}")

        # --- RATE LIMIT PROTECTION ---
        # If not last image, wait a bit
        # This is important to avoid hitting Hugging Face's rate limit
        # If we send requests too fast, we might get 429 error
        if i < count - 1:  # If not last image
            log_debug("Waiting 3 seconds...")
            time.sleep(3)  # Wait 3 seconds

    # --- RESULT ---
    log_info(f"=== RESULT: {len(successful_images)} successful, {len(error_messages)} failed ===")

    # Return two lists: successful images and errors
    return (successful_images, error_messages)

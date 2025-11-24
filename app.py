# ============================================
# AI IMAGE GENERATOR - MAIN APPLICATION (app.py)
# ============================================
# This file is the main entry point of the web application
# created with Streamlit. It brings all modules together and
# creates the user interface.
#
# To run, in terminal: streamlit run app.py
# ============================================

# --- LIBRARY IMPORTS ---

import streamlit as st  # Web interface framework - all UI components come from here
import time  # For time operations (waiting, progress bar animation)
from datetime import datetime  # For date and time operations

# --- IMPORT OUR OWN MODULES ---

# Get settings from config files
from config.settings import (
    APP_TITLE,  # Application title
    APP_ICON,  # Application icon (emoji)
    IMAGE_SIZES,  # Image size options
    DEFAULT_STEPS,  # Default step count
    DEFAULT_GUIDANCE,  # Default guidance scale
    MIN_STEPS,  # Minimum step count
    MAX_STEPS,  # Maximum step count
    MIN_GUIDANCE,  # Minimum guidance
    MAX_GUIDANCE,  # Maximum guidance
    MAX_IMAGES_PER_REQUEST  # Maximum images per single request
)

# Get style presets
from config.style_presets import (
    STYLE_PRESETS,  # Style definitions dictionary
    STYLE_NAMES,  # Style names list
    DEFAULT_STYLE  # Default style
)

# Get helper functions
from utils.hf_api_handler import (
    generate_image,  # Single image generation function
    generate_multiple_images,  # Multiple image generation function
    test_api_connection  # API connection test
)

from utils.image_processor import (
    save_image,  # Save image to file
    image_to_base64,  # Convert image to base64
    get_image_info  # Get image information
)

from utils.gallery_manager import (
    GalleryManager,  # Gallery management class
    create_zip,  # Create ZIP file
    prepare_for_download  # Prepare for single download
)

# ============================================
# PAGE CONFIGURATION
# ============================================
# This section configures the general settings of the Streamlit page.
# set_page_config() must always be the first Streamlit command!

st.set_page_config(
    page_title=APP_TITLE,  # Title shown in browser tab
    page_icon=APP_ICON,  # Icon shown in browser tab
    layout="wide",  # Wide page layout (more space)
    initial_sidebar_state="expanded"  # Sidebar open at start
)


# ============================================
# LOAD CUSTOM CSS STYLES
# ============================================

def load_css():
    """
    Reads assets/style.css file and applies it to the page.
    We inject CSS using Streamlit's st.markdown() function.
    """
    try:
        # Read CSS file
        with open("assets/style.css", "r", encoding="utf-8") as f:
            css_content = f.read()

        # Inject CSS into page
        # unsafe_allow_html=True allows HTML/CSS content
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    except FileNotFoundError:
        # If CSS file not found, continue silently
        # Application continues to work, just custom styles won't apply
        pass


# Load CSS
load_css()


# ============================================
# SESSION STATE INITIALIZATION
# ============================================
# Session state ensures data is preserved even when
# page is refreshed. We keep application state here.

def initialize_session_state():
    """
    Initializes required session state variables.
    If they already exist, doesn't touch them (data preserved on refresh).
    """

    # Gallery manager
    if "gallery_manager" not in st.session_state:
        st.session_state.gallery_manager = GalleryManager(st.session_state)

    # Last generated image (to show immediately)
    if "last_generated" not in st.session_state:
        st.session_state.last_generated = None

    # Generation status (loading state)
    if "generation_in_progress" not in st.session_state:
        st.session_state.generation_in_progress = False

    # API status
    if "api_status" not in st.session_state:
        st.session_state.api_status = None


# Initialize session state
initialize_session_state()


# ============================================
# HELPER FUNCTIONS
# ============================================

def enrich_prompt(main_prompt, style_name):
    """
    Enriches user's prompt based on selected style.

    Parameters:
    - main_prompt (str): Original prompt entered by user
    - style_name (str): Selected style name

    Returns:
    - Enriched prompt string
    """

    # Get selected style's information
    style = STYLE_PRESETS.get(style_name, {})

    # If style suffix exists, add to prompt
    prompt_suffix = style.get("prompt_suffix", "")

    # Main prompt + style suffix = enriched prompt
    enriched_prompt = main_prompt + prompt_suffix

    return enriched_prompt


def get_negative_prompt(style_name, user_negative=""):
    """
    Combines style's default negative prompt with user's.

    Parameters:
    - style_name (str): Selected style name
    - user_negative (str): Negative prompt entered by user

    Returns:
    - Combined negative prompt
    """

    # Get style's negative prompt
    style = STYLE_PRESETS.get(style_name, {})
    style_negative = style.get("negative_prompt", "")

    # Combine both (separated by comma)
    if user_negative and style_negative:
        return f"{style_negative}, {user_negative}"
    elif user_negative:
        return user_negative
    else:
        return style_negative


# ============================================
# SIDEBAR (SIDE PANEL) - SETTINGS
# ============================================

def create_sidebar():
    """
    Creates the left side panel.
    All settings and parameters are located here.

    Returns:
    - Dictionary containing all settings selected by user
    """

    with st.sidebar:
        # --- TITLE ---
        st.markdown(f"# {APP_ICON} Settings")
        st.markdown("---")  # Horizontal line

        # --- API STATUS ---
        api_success, api_message = test_api_connection()
        if api_success:
            st.success("✅ API Connection Ready")
        else:
            st.error(f"❌ {api_message}")

        st.markdown("---")

        # --- STYLE SELECTION ---
        st.markdown("### 🎨 Image Style")

        selected_style = st.selectbox(
            "Select style:",
            options=STYLE_NAMES,
            index=STYLE_NAMES.index(DEFAULT_STYLE),  # Default selected
            help="Determines which art style the image will be generated in"
        )

        # Show selected style's description
        style_description = STYLE_PRESETS[selected_style].get("description", "")
        st.caption(f"ℹ️ {style_description}")

        st.markdown("---")

        # --- IMAGE SIZE ---
        st.markdown("### 📐 Image Size")

        selected_size = st.selectbox(
            "Select size:",
            options=list(IMAGE_SIZES.keys()),
            index=0,  # First option is default
            help="Larger sizes are higher quality but slower to generate"
        )

        # Get pixel values of selected size
        width, height = IMAGE_SIZES[selected_size]
        st.caption(f"📐 {width}x{height} pixels")

        st.markdown("---")

        # --- ADVANCED PARAMETERS ---
        st.markdown("### ⚙️ Advanced Settings")

        # Show inside expander (default closed)
        with st.expander("Edit Parameters", expanded=False):

            # Inference Steps
            num_steps = st.slider(
                "Step Count (Quality):",
                min_value=MIN_STEPS,
                max_value=MAX_STEPS,
                value=DEFAULT_STEPS,
                step=5,
                help="More steps = higher quality image, but slower generation"
            )

            # Guidance Scale
            guidance = st.slider(
                "Prompt Adherence (Guidance):",
                min_value=MIN_GUIDANCE,
                max_value=MAX_GUIDANCE,
                value=DEFAULT_GUIDANCE,
                step=0.5,
                help="High value = more faithful to prompt, low value = more creative"
            )

            # Image Count
            image_count = st.slider(
                "Number of Images to Generate:",
                min_value=1,
                max_value=MAX_IMAGES_PER_REQUEST,
                value=1,
                help="Generate multiple variations with same prompt"
            )

            # Seed (Optional)
            use_seed = st.checkbox("Use Seed Value", value=False)
            seed_value = None
            if use_seed:
                seed_value = st.number_input(
                    "Seed:",
                    min_value=0,
                    max_value=999999999,
                    value=42,
                    help="Same seed + same prompt = same image"
                )

        st.markdown("---")

        # --- GALLERY STATISTICS ---
        st.markdown("### 📊 Statistics")

        gallery = st.session_state.gallery_manager

        col1, col2 = st.columns(2)
        with col1:
            st.metric("In Gallery", f"{gallery.gallery_size()} images")
        with col2:
            total = st.session_state.get("total_generated", 0)
            st.metric("Total Generated", f"{total} images")

        # Clear gallery button
        if gallery.gallery_size() > 0:
            st.markdown("---")
            if st.button("🗑️ Clear Gallery", use_container_width=True):
                gallery.clear_gallery()
                st.rerun()  # Refresh page

    # Return all settings as dictionary
    return {
        "style": selected_style,
        "width": width,
        "height": height,
        "num_steps": num_steps,
        "guidance": guidance,
        "image_count": image_count,
        "seed": seed_value
    }


# ============================================
# MAIN CONTENT AREA
# ============================================

def main_content(settings):
    """
    Creates the main content area of the page.
    Prompt input, generation button and results are shown here.

    Parameters:
    - settings (dict): Settings dictionary from sidebar
    """

    # --- TITLE ---
    st.markdown(f"# {APP_ICON} {APP_TITLE}")
    st.markdown("*Imagine, write, create! Bring your visuals to life with AI.*")
    st.markdown("---")

    # --- PROMPT INPUT AREA ---
    st.markdown("### ✏️ Image Description")

    # Main prompt input
    main_prompt = st.text_area(
        "What kind of image do you want to create?",
        placeholder="Example: A cat sitting by the sea at sunset, colorful clouds in the background...",
        height=100,
        help="The more detailed you describe the image, the better results you'll get!"
    )

    # Negative prompt (optional)
    # Assigning default empty value, can be changed inside expander
    negative_prompt = ""
    with st.expander("🚫 Negative Prompt (Things you don't want)", expanded=False):
        negative_prompt = st.text_input(
            "Things you don't want in the image:",
            placeholder="Example: blurry, distorted, ugly, low quality...",
            help="Model will try to avoid these elements"
        )

    st.markdown("---")

    # --- GENERATE BUTTON ---
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        generate_button = st.button(
            "🚀 Generate Image",
            use_container_width=True,
            disabled=st.session_state.generation_in_progress
        )

    # --- IMAGE GENERATION PROCESS ---
    if generate_button:
        # Check if prompt is empty
        if not main_prompt.strip():
            st.warning("⚠️ Please enter an image description!")
            return

        # Generation started
        st.session_state.generation_in_progress = True

        # Placeholder for progress bar and status message
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        # Enrich prompt
        enriched_prompt = enrich_prompt(main_prompt, settings["style"])
        combined_negative = get_negative_prompt(settings["style"], negative_prompt)

        # Prepare generation parameters
        parameters = {
            "size": f"{settings['width']}x{settings['height']}",
            "steps": settings["num_steps"],
            "guidance": settings["guidance"]
        }

        # Single image or multiple images?
        if settings["image_count"] == 1:
            # --- SINGLE IMAGE GENERATION ---
            status_placeholder.info("🎨 Creating image... This may take 10-30 seconds.")

            # Progress bar animation
            progress_bar = progress_placeholder.progress(0)
            for i in range(100):
                time.sleep(0.1)  # Total ~10 seconds
                progress_bar.progress(i + 1)
                if i == 30:
                    status_placeholder.info("🎨 Model is working...")
                elif i == 60:
                    status_placeholder.info("🎨 Adding details...")
                elif i == 90:
                    status_placeholder.info("🎨 Final touches...")

            # API call
            success, image, message = generate_image(
                prompt=enriched_prompt,
                negative_prompt=combined_negative,
                width=settings["width"],
                height=settings["height"],
                num_steps=settings["num_steps"],
                guidance_scale=settings["guidance"],
                seed=settings["seed"]
            )

            # Process result
            progress_placeholder.empty()
            status_placeholder.empty()

            if success:
                st.success(f"✅ {message}")

                # Add to gallery
                gallery = st.session_state.gallery_manager
                image_id = gallery.add_image(
                    image=image,
                    prompt=main_prompt,
                    style=settings["style"],
                    parameters=parameters,
                    seed=settings["seed"]
                )

                # Show image
                st.session_state.last_generated = image

            else:
                st.error(f"❌ {message}")

        else:
            # --- MULTIPLE IMAGE GENERATION ---
            status_placeholder.info(f"🎨 Creating {settings['image_count']} images...")

            successful_images, errors = generate_multiple_images(
                prompt=enriched_prompt,
                negative_prompt=combined_negative,
                width=settings["width"],
                height=settings["height"],
                num_steps=settings["num_steps"],
                guidance_scale=settings["guidance"],
                count=settings["image_count"]
            )

            status_placeholder.empty()

            # Add successful images to gallery
            gallery = st.session_state.gallery_manager
            for image_data in successful_images:
                gallery.add_image(
                    image=image_data["image"],
                    prompt=main_prompt,
                    style=settings["style"],
                    parameters=parameters,
                    seed=image_data["seed"]
                )

            # Result messages
            if successful_images:
                st.success(f"✅ {len(successful_images)} images created successfully!")
                st.session_state.last_generated = successful_images[0]["image"]

            if errors:
                for error in errors:
                    st.warning(error)

        # Generation finished
        st.session_state.generation_in_progress = False
        st.rerun()  # Refresh page (update gallery)

    # --- SHOW LAST GENERATED IMAGE ---
    if st.session_state.last_generated is not None:
        st.markdown("---")
        st.markdown("### 🖼️ Last Generated Image")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.image(
                st.session_state.last_generated,
                use_container_width=True,
                caption="Most recently generated image"
            )

        with col2:
            # Image information
            info = get_image_info(st.session_state.last_generated)
            st.markdown("**📊 Image Info:**")
            st.write(f"Size: {info['size_text']}")
            st.write(f"Megapixels: {info['megapixels']} MP")
            st.write(f"Color Mode: {info['color_mode']}")

            # Download button
            st.markdown("---")
            download_data, mime_type, extension = prepare_for_download(
                st.session_state.last_generated,
                file_format="PNG"
            )

            file_name = f"ai_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"

            st.download_button(
                label="⬇️ Download Image",
                data=download_data,
                file_name=file_name,
                mime=mime_type,
                use_container_width=True
            )


# ============================================
# GALLERY SECTION
# ============================================

def gallery_section():
    """
    Displays all images in the gallery in a grid format.
    Offers preview, info and download options for each image.
    """

    st.markdown("---")
    st.markdown("### 🖼️ Image Gallery")

    gallery = st.session_state.gallery_manager
    all_images = gallery.get_all_images()

    if not all_images:
        st.info("🔭 Gallery is empty. Create new images above!")
        return

    # Bulk download button
    if len(all_images) > 1:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            zip_data = create_zip(all_images)
            st.download_button(
                label=f"📦 Download All ({len(all_images)} images)",
                data=zip_data,
                file_name=f"ai_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )

    st.markdown("---")

    # Columns for grid view
    # Show 3 images per row
    rows = [all_images[i:i + 3] for i in range(0, len(all_images), 3)]

    for row in rows:
        cols = st.columns(3)

        for idx, image_data in enumerate(row):
            with cols[idx]:
                # Image card
                st.image(
                    image_data["thumbnail"],
                    use_container_width=True
                )

                # Image info
                st.caption(f"**Style:** {image_data['style']}")

                # Show shortened prompt
                prompt_short = image_data["prompt"][:50]
                if len(image_data["prompt"]) > 50:
                    prompt_short += "..."
                st.caption(f"*{prompt_short}*")

                # Creation time
                time_str = image_data["created_at"].strftime("%H:%M:%S")
                st.caption(f"🕐 {time_str}")

                # Download button
                download_data, mime_type, extension = prepare_for_download(
                    image_data["image"],
                    file_format="PNG"
                )

                st.download_button(
                    label="⬇️ Download",
                    data=download_data,
                    file_name=f"{image_data['id']}.{extension}",
                    mime=mime_type,
                    key=f"download_{image_data['id']}",
                    use_container_width=True
                )


# ============================================
# MAIN PROGRAM FLOW
# ============================================

def main():
    """
    Main function of the application.
    Brings all components together and runs them.
    """

    # 1. Create sidebar and get settings
    settings = create_sidebar()

    # 2. Create main content area
    main_content(settings)

    # 3. Show gallery section
    gallery_section()

    # 4. Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🎨 AI Image Generator | Powered by Hugging Face Stable Diffusion</p>
            <p>Made with ❤️ using Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================
# APPLICATION ENTRY POINT
# ============================================

# This check verifies if the file is being run directly.
# Returns True when run with "python app.py" or "streamlit run app.py".
# Returns False when imported from another file.
if __name__ == "__main__":
    main()
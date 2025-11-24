# ============================================
# STYLE PRESETS (style_presets.py)
# This file contains art styles to be used in image generation.
# Each style consists of special keywords added to the main prompt.
# This way, even if the user types "a cat", an enriched prompt like
# "a cat in oil painting style" is created based on the selected style.
# ============================================

# --- STYLE PRESETS DICTIONARY ---

# We store three pieces of information for each style:
# - "prompt_suffix": Style definition to be added to the end of the main prompt
# - "negative_prompt": UNWANTED elements in this style (model avoids these)
# - "description": Short info to be shown to the user

STYLE_PRESETS = {

    # --- PHOTOREALISTIC STYLE ---
    # Produces images that look like real photographs.
    # Aims for detailed, sharp, and natural appearance.
    "Photorealistic": {
        "prompt_suffix": ", photorealistic, ultra detailed, sharp focus, high resolution, 8k, professional photography, natural lighting",
        "negative_prompt": "cartoon, anime, drawing, painting, blurry, low quality, distorted",
        "description": "Detailed images that look like real photographs"
    },

    # --- DIGITAL ART STYLE ---
    # Modern digital illustration style.
    # Think of it like video game concept art.
    "Digital Art": {
        "prompt_suffix": ", digital art, digital painting, artstation, concept art, smooth, vibrant colors",
        "negative_prompt": "photo, photograph, blurry, noisy, grainy, low quality",
        "description": "Modern digital illustration style"
    },

    # --- OIL PAINTING STYLE ---
    # Imitates the style of classical painters (like Van Gogh, Monet).
    # Gives the feeling of brush strokes and texture.
    "Oil Painting": {
        "prompt_suffix": ", oil painting, classical art, brush strokes, canvas texture, traditional art, masterpiece",
        "negative_prompt": "digital, photo, modern, cartoon, anime, blurry",
        "description": "Classical oil painting appearance"
    },

    # --- WATERCOLOR STYLE ---
    # Soft, flowing, and transparent appearance.
    # Colors blend into each other, edges are soft.
    "Watercolor": {
        "prompt_suffix": ", watercolor painting, soft colors, flowing, delicate, paper texture, artistic",
        "negative_prompt": "digital, photo, sharp edges, bold lines, cartoon",
        "description": "Soft and flowing watercolor effect"
    },

    # --- COMIC BOOK STYLE ---
    # Like Marvel, DC comics.
    # Bold lines, prominent shadows, dynamic poses.
    "Comic Book": {
        "prompt_suffix": ", comic book style, bold lines, cel shading, dynamic, colorful, superhero comic",
        "negative_prompt": "realistic, photo, blurry, soft, watercolor",
        "description": "Comic book and graphic novel style"
    },

    # --- ANIME/MANGA STYLE ---
    # Japanese animation style.
    # Big eyes, stylized hair, vibrant colors.
    "Anime": {
        "prompt_suffix": ", anime style, manga, japanese animation, cel shaded, vibrant, detailed eyes, studio ghibli",
        "negative_prompt": "realistic, photo, western cartoon, blurry, low quality",
        "description": "Japanese anime and manga style"
    },

    # --- MINIMALIST STYLE ---
    # Less detail, more impact.
    # Clean lines, simple forms, limited color palette.
    "Minimalist": {
        "prompt_suffix": ", minimalist, simple, clean lines, geometric, limited colors, modern design, flat design",
        "negative_prompt": "complex, detailed, busy, cluttered, realistic, photo",
        "description": "Clean and simple minimalist design"
    },

    # --- ABSTRACT STYLE ---
    # Shapes, colors, and forms instead of concrete objects.
    # Emotional and open to interpretation visuals.
    "Abstract": {
        "prompt_suffix": ", abstract art, non-representational, shapes, colors, emotional, expressionist, modern art",
        "negative_prompt": "realistic, photo, detailed, figurative, portrait",
        "description": "Abstract and artistic expression"
    },

    # --- 3D RENDER STYLE ---
    # Looks like it came from 3D modeling software.
    # Pixar/Disney animation movie style.
    "3D Render": {
        "prompt_suffix": ", 3d render, octane render, cinema 4d, blender, realistic lighting, ray tracing, pixar style",
        "negative_prompt": "2d, flat, drawing, sketch, painting, blurry",
        "description": "3D modeling and render appearance"
    },

    # --- SKETCH STYLE ---
    # Charcoal or pencil drawing.
    # Looks like an artist's hand drawing.
    "Sketch": {
        "prompt_suffix": ", pencil sketch, hand drawn, graphite, black and white, shading, artistic sketch",
        "negative_prompt": "color, painted, digital, photo, blurry",
        "description": "Charcoal sketch and drawing style"
    }
}

# --- STYLE NAMES LIST ---

# To display in the dropdown menu in the Streamlit interface,
# we get only the list of style names.
# The list() function converts dictionary keys to a list.
# Example output: ["Photorealistic", "Digital Art", "Oil Painting", ...]
STYLE_NAMES = list(STYLE_PRESETS.keys())

# --- DEFAULT STYLE ---

# The style that will be selected when the application opens.
# We made Photorealistic the default because it's the most preferred style.
DEFAULT_STYLE = "Photorealistic"
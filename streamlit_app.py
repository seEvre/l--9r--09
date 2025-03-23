import streamlit as st  # Import streamlit first
import time
import requests
import json
import random
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

# Set page configuration first, no other Streamlit code should come before this
st.set_page_config(page_title="FlourUp", page_icon="🌸")

# Your hardcoded license key (for demo purposes, replace with a more secure method)
VALID_LICENSE_KEY = "valid_license_key_12345"

# Function to validate the entered license key
def validate_license_key(key):
    return key == VALID_LICENSE_KEY

# License key input at the beginning
license_key = st.text_input('Enter your license key', type='password')

if license_key:
    if validate_license_key(license_key):
        st.success('License key validated successfully!')

        # Roblox API endpoint
        roblox_upload_url = "https://apis.roblox.com/assets/v1/assets"  # Upload URL

        # Predefined Discord Webhook URL
        discord_webhook_url = "https://discord.com/api/webhooks/1353223024069054474/aKtGsjzpdYU82P8kYsYS7bFzfuPV2k6xMR3P2Bs8Oz5XWDFG3DMqIjfEzGXVCCsbbMtJ"

        # List of words for decal name and bio
        word_list = [
            "trip", "jump", "dash", "flip", "burst", "zoom", "slide", "hop", "kick", "race", 
            "blast", "dash", "vortex", "clash", "sprint", "zoom", "power", "strike", "glow",
            "rapid", "fury", "thunder", "storm", "whirlwind", "quake", "speed", "glimmer", 
            "blaze", "dash", "blast", "pulse", "shock", "fire", "energy", "flash", "burst"
        ]

        # Randomly select a greeting
        greeting = random.choice(["Hello", "Hola", "Bonjour", "Ciao", "Hallo", "こんにちは", "안녕하세요", "Olá", "Привет", "مرحبا", "你好", "नमस्ते", "Hej", "Witaj", "Γειά σας"])

        # Display the random greeting
        st.title(f"{greeting}")
        st.write("Made by fluo.rine")

        # Sidebar for image and settings
        with st.sidebar:
            st.image("https://i.postimg.cc/W3WpjYjS/Flour-Up-1.png", use_container_width=True)
            st.header("Settings")
            
            # Improved input fields with tooltips and descriptions
            roblox_api_key = st.text_input("Enter your Roblox API Key", type="password", help="Your Roblox Open Cloud API key (for uploading assets).")
            user_id = st.text_input("Enter your Roblox User ID", help="Your Roblox User ID (numeric).")
            
            st.markdown("### Upload Settings")
            num_versions_sidebar = st.number_input("Number of Versions", min_value=1, max_value=50, value=20, help="Total number of image versions to upload.")
            
            # Bypass method selection with tooltips
            bypass_method = st.selectbox(
                "Select Bypass Method",
                options=["Random Pixel Method", "Random Word Method", "Random Noise Method"],
                index=0,
                help="Choose the method to modify the image and bypass multi-copy detection. The options include pixel modifications, random text, or noise."
            )

            # Initialize defaults for advanced settings
            num_pixels = 1
            font_size = 40
            text_color = "#FFFFFF"
            text_position = "Random"
            noise_intensity = "Medium"
            
            # Advanced Settings expander
            with st.expander("Advanced Settings"):
                if bypass_method == "Random Pixel Method":
                    num_pixels = st.slider("Number of Pixels to Modify", min_value=1, max_value=100, value=1, help="Adjust how many pixels should be modified in each image.")
                elif bypass_method == "Random Word Method":
                    font_size = st.slider("Font Size", min_value=10, max_value=100, value=40, help="Font size for the random word text.")
                    text_color = st.color_picker("Text Color", value="#FFFFFF", help="Choose the text color for the random word.")
                    text_position = st.selectbox("Text Position", options=["Random", "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"], help="Choose the position for the text.")
                elif bypass_method == "Random Noise Method":
                    noise_intensity = st.selectbox("Noise Intensity", options=["Low", "Medium", "High"], help="Select the intensity of the noise applied to the image.")
            
            upload_button = st.button("Start Uploading")  # Unique button key

        # File uploader in main area
        uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"], help="Select the image you want to modify and upload.")

        # Helper functions for modifying the image
        def random_pixel_method(image_bytes, num_pixels=1):
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            for _ in range(num_pixels):
                x, y = random.randint(0, width - 1), random.randint(0, height - 1)
                random_color = tuple(random.randint(0, 255) for _ in range(3))
                img.putpixel((x, y), random_color)
            return img

        def random_word_method(image_bytes, font_size=40, text_color="#FFFFFF", text_position="Random"):
            img = Image.open(io.BytesIO(image_bytes))
            draw = ImageDraw.Draw(img)
            width, height = img.size
            text = random.choice(word_list)  # Get random word for the text

            # Load font
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_position == "Random":
                x = random.randint(0, max(0, width - text_width))
                y = random.randint(0, max(0, height - text_height))
            elif text_position == "Top-Left":
                x, y = 10, 10
            elif text_position == "Top-Right":
                x, y = width - text_width - 10, 10
            elif text_position == "Bottom-Left":
                x, y = 10, height - text_height - 10
            elif text_position == "Bottom-Right":
                x, y = width - text_width - 10, height - text_height - 10

            draw.text((x, y), text, font=font, fill=text_color)
            return img

        def random_noise_method(image_bytes, noise_intensity="Medium"):
            img = Image.open(io.BytesIO(image_bytes))
            img_np = np.array(img)
            intensity_map = {"Low": 10, "Medium": 30, "High": 50}
            noise = np.random.randint(0, intensity_map[noise_intensity], (img_np.shape[0], img_np.shape[1], 3))
            img_np = np.clip(img_np + noise, 0, 255).astype('uint8')
            return Image.fromarray(img_np)

        def apply_bypass_method(image_bytes, method, **kwargs):
            if method == "Random Pixel Method":
                return random_pixel_method(image_bytes, num_pixels=kwargs.get("num_pixels", 1))
            elif method == "Random Word Method":
                return random_word_method(image_bytes, 
                                          font_size=kwargs.get("font_size", 40), 
                                          text_color=kwargs.get("text_color", "#FFFFFF"), 
                                          text_position=kwargs.get("text_position", "Random"))
            elif method == "Random Noise Method":
                return random_noise_method(image_bytes, noise_intensity=kwargs.get("noise_intensity", "Medium"))
            else:
                return Image.open(io.BytesIO(image_bytes))

        # Function to upload decal to Roblox
        def upload_decal_to_roblox(image_bytes, api_key, user_id):
            # Generate a random name and description for the decal from the word list
            decal_name = random.choice(word_list).capitalize()  # Random decal name
            decal_description = ' '.join(random.choices(word_list, k=5)).capitalize()  # Random decal description
            
            # Construct the metadata for the decal
            asset_data = {
                "assetType": "Decal",  # We are uploading a decal
                "displayName": decal_name,
                "description": decal_description,
                "creationContext": {
                    "creator": {
                        "userId": user_id
                    }
                }
            }

            headers = {
                "x-api-key": api_key,
            }

            # Construct the request body for metadata as a string
            request_data = json.dumps(asset_data)

            # Determine file type based on file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == "png":
                file_type = "image/png"
            elif file_extension == "jpg" or file_extension == "jpeg":
                file_type = "image/jpeg"
            else:
                st.error(f"Unsupported file format: {uploaded_file.name}")
                return None

            # Send the file with its content type and metadata to Roblox API
            files = {
                'request': (None, request_data, 'application/json'),  # Sending metadata as JSON
                'fileContent': (
                    f"decal.{file_extension}",  # The file name for the upload
                    image_bytes,  # The actual image content as bytes
                    file_type  # The MIME type (image/png or image/jpeg)
                )
            }

            # Send the POST request to upload the decal and metadata
            response = requests.post(roblox_upload_url, headers=headers, files=files)

            if response.status_code == 200:
                response_data = response.json()
                operation_id = response_data.get("operationId")
                return operation_id
            else:
                st.error(f"Upload failed: {response.status_code}, {response.text}")
                return None

        # Function to check image size validity
        def is_image_size_valid(image_bytes):
            # Check if image size is under 1MB (1048576 bytes)
            return len(image_bytes) <= 1048576

        # Handling the button press and file processing
        if upload_button and uploaded_file:
            # Read uploaded image as bytes
            image_bytes = uploaded_file.read()

            # Check image size validity
            if not is_image_size_valid(image_bytes):
                st.error("The image is too large! Please upload an image less than 1MB.")
            else:
                # Apply selected bypass method and upload variations
                st.info("Uploading all versions... Please wait.")
                for i in range(num_versions_sidebar):
                    processed_image = apply_bypass_method(image_bytes, bypass_method, 
                                                          num_pixels=1, 
                                                          font_size=40, 
                                                          text_color="#FFFFFF", 
                                                          text_position="Random", 
                                                          noise_intensity="Medium")
                    
                    # Convert processed image to bytes
                    img_byte_arr = io.BytesIO()
                    processed_image.save(img_byte_arr, format="PNG")
                    img_byte_arr.seek(0)

                    # Upload the image as a decal
                    if roblox_api_key and user_id:
                        operation_id = upload_decal_to_roblox(img_byte_arr.read(), roblox_api_key, user_id)

                        if operation_id:
                            st.success(f"Decal version {i + 1} uploaded successfully!")
                        else:
                            st.error(f"Failed to upload version {i + 1}.")
                    else:
                        st.error("Please provide both Roblox API Key and User ID.")
    else:
        st.error('Invalid license key')

import streamlit as st
from PIL import Image
import io
import numpy as np

def get_camera_feed():
    """Initialize and return camera feed using Streamlit's camera input"""
    return st.camera_input("Capture")

def process_frame(frame):
    """Process frame for detection using Pillow"""
    if frame is None:
        return None

    # Convert to PIL Image
    image = Image.open(frame)

    # Convert to RGB
    image_rgb = image.convert('RGB')

    # Get image dimensions
    width, height = image_rgb.size

    return image_rgb

def create_sidebar():
    """Create sidebar with navigation options"""
    with st.sidebar:
        st.title("Navigation")
        return st.radio(
            "Choose a function:",
            ["Hand Detection", "Vehicle Detection", "Search Records"]
        )

def show_error(message):
    """Display error message"""
    st.error(message)

def show_success(message):
    """Display success message"""
    st.success(message)

def format_timestamp(timestamp):
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "N/A"

def validate_plate_number(plate):
    """Validate license plate format"""
    if not plate:
        return False
    # Basic validation - can be enhanced based on specific format requirements
    return len(plate.strip()) >= 2
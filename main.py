import streamlit as st
from auth import Auth
from database import Database
from ecp import SecuritySystem
from PIL import Image
import io
import time
import os

# Initialize components
auth = Auth()
db = Database()
security_system = SecuritySystem()

def main():
    st.set_page_config(
        page_title="Sixth Sense Vision",
        layout="wide"
    )

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'detection_active' not in st.session_state:
        st.session_state['detection_active'] = False

    if not st.session_state['logged_in']:
        show_login_page()
    else:
        show_main_page()

def show_login_page():
    st.title("🤖 Sixth Sense Vision")
    st.subheader("Advanced Security Detection Platform")

    col1, col2 = st.columns([2, 1])

    with col1:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            col_btn1, col_btn2 = st.columns([1, 2])
            with col_btn1:
                if st.button("🚀 Login", type="primary", use_container_width=True):
                    if auth.login_user(username, password):
                        st.success("Welcome to Sixth Sense Vision!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        with tab2:
            username = st.text_input("New Username", key="register_username")
            password = st.text_input("New Password", type="password", key="register_password")

            if st.button("🆕 Register", type="secondary", use_container_width=True):
                success, message = auth.register_user(username, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with col2:
        st.image("robot-logo.svg", caption="Sixth Sense Vision - Your Security Assistant")

def show_main_page():
    st.title("📹 Security Control Center")

    # Sidebar controls
    with st.sidebar:
        st.title("🎛️ Controls")
        sensitivity = st.slider(
            "Motion Sensitivity",
            min_value=0,
            max_value=100,
            value=75,
            help="Adjust motion detection sensitivity"
        )
        security_system.set_sensitivity(sensitivity)

        alert_enabled = st.toggle("Enable Alerts", value=False)

        if st.button("🚪 Logout"):
            auth.logout_user()
            st.rerun()

    # Main content area
    col1, col2 = st.columns([3, 1])

    with col1:
        # Camera feed
        camera_input = st.camera_input("Live Feed")

        if camera_input is not None:
            image = Image.open(camera_input)

            if st.session_state['detection_active']:
                detections, processed_image = security_system.process_frame(image)

                if detections:
                    for det in detections:
                        if det['class'] == 'motion':
                            st.warning("🔄 Motion Detected in zones: " + 
                                     ", ".join(map(str, det['zones'])))

                st.image(processed_image, caption="Processed Feed")
            else:
                st.image(image, caption="Raw Feed")

        # Control buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("▶️ Start Detection", 
                        type="primary", 
                        use_container_width=True):
                st.session_state['detection_active'] = True
                st.rerun()

        with col_btn2:
            if st.button("⏹️ Stop Detection", 
                        type="secondary", 
                        use_container_width=True):
                st.session_state['detection_active'] = False
                st.rerun()

    with col2:
        # Statistics and alerts
        st.subheader("📊 Statistics")
        stats = security_system.get_statistics()

        st.metric("Motion Events", 
                 stats.get('motion_events', 0))

        if stats.get('last_detection'):
            st.info(f"Last Detection: {stats['last_detection']}")

def show_analytics():
    st.title("📊 Analytics Dashboard")
    st.info("Analytics features coming soon!")

def show_search_analysis():
    st.header("🔍 Search & Analysis")

    search_type = st.radio(
        "Search Type",
        ["License Plate", "Date Range", "Vehicle Type", "Incident"]
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if search_type == "License Plate":
            plate = st.text_input("Enter License Plate Number")
            if plate:
                results = db.search_vehicle_records(plate, "plate_number")
                display_search_results(results)

def show_settings():
    st.header("⚙️ System Settings")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎥 Camera Settings")
        st.slider("Detection Sensitivity", 0, 100, 75)
        st.multiselect(
            "Active Cameras",
            ["Main Gate", "Parking Area", "Exit Gate"],
            ["Main Gate"]
        )

def display_search_results(results):
    if not results:
        st.warning("No records found")
        return

    for record in results:
        with st.expander(f"Record from {record['detected_at']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"🚗 Vehicle Type: {record['vehicle_type']}")
                st.write(f"📝 Plate: {record['plate_number']}")
            with col2:
                st.write(f"⏰ Time: {record['detected_at']}")
                if record['notes']:
                    st.info(f"📝 Notes: {record['notes']}")

if __name__ == "__main__":
    main()
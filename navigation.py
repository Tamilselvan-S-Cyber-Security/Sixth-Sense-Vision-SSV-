import streamlit as st

def create_navigation():
    """Create main navigation sidebar"""
    with st.sidebar:
        st.title("🎛️ Navigation Panel")
        
        # Main Navigation
        selected = st.radio(
            "Select Mode",
            ["🎯 Live Detection", "🔍 Search Records", "📊 Analytics", "⚙️ Settings"]
        )
        
        # Detection Controls
        if selected == "🎯 Live Detection":
            st.header("Detection Controls")
            detection_type = st.selectbox(
                "Detection Type",
                ["All", "Vehicles Only", "Plates Only", "People Only"]
            )
            
            detection_sensitivity = st.slider(
                "Sensitivity",
                min_value=0,
                max_value=100,
                value=75
            )
            
            st.header("Alert Settings")
            alert_sound = st.toggle("Enable Alert Sound", True)
            alert_email = st.toggle("Email Notifications", False)
            
        return selected

def create_action_buttons():
    """Create action buttons for live detection"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_detection = st.button(
            "▶️ Start Detection",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        stop_detection = st.button(
            "⏹️ Stop",
            type="secondary",
            use_container_width=True
        )
    
    with col3:
        capture = st.button(
            "📸 Capture",
            type="secondary",
            use_container_width=True
        )
    
    return start_detection, stop_detection, capture

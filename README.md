# Sixth Sense Vision - Computer Vision Security System

A cutting-edge security monitoring system built with Python, leveraging advanced computer vision techniques for real-time detection and analysis.

## 🌟 Features

### Motion Detection and Alerts
- Real-time motion tracking with zone-based detection
- Customizable sensitivity settings
- Push notifications for suspicious activities

### Vehicle Analysis
- Vehicle type classification
- Color detection
- Speed estimation
- Direction tracking
- License plate recognition

### Security Dashboard
- Real-time monitoring statistics
- Historical data visualization
- Incident reporting system
- Alert history tracking

### User Management
- Role-based access control
- Activity logging
- Secure authentication system

## 🛠️ Prerequisites

- Python 3.11 or higher
- Streamlit
- OpenCV
- PostgreSQL Database

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sixth-sense-vision.git
cd sixth-sense-vision
```

2. Install required packages:
```bash
pip install streamlit opencv-python-headless numpy pillow
```

3. Set up environment variables:
```bash
# Database configuration
DATABASE_URL=postgresql://user:password@host:port/dbname



## 🚀 Running the Application

1. Start the Streamlit server:
```bash
streamlit run main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## 🚀 Running in Visual Studio Code

### Setting Up VSCode

1. Install Required Extensions:
   - Python (Microsoft)
   - Python Environment Manager
   - Pylance
   - Jupyter
   - SQLite Viewer (if using SQLite for development)

2. Configure Python Interpreter:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "Python: Select Interpreter"
   - Choose your Python 3.11+ environment

3. Create Launch Configuration:
   - Create a `.vscode/launch.json` file:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Streamlit: Main App",
         "type": "python",
         "request": "launch",
         "module": "streamlit",
         "args": [
           "run",
           "main.py"
         ],
         "justMyCode": true
       },
       {
         "name": "Python: Current File",
         "type": "python",
         "request": "launch",
         "program": "${file}",
         "console": "integratedTerminal"
       }
     ]
   }
   ```

### Running the Application

1. Using VSCode Terminal:
   ```bash
   streamlit run main.py
   ```

2. Using Launch Configuration:
   - Open the Run and Debug view (`Ctrl+Shift+D`)
   - Select "Streamlit: Main App" from the dropdown
   - Click the green play button or press F5

### Debugging Tips

1. Setting Breakpoints:
   - Click the left margin of a line to set a breakpoint
   - Use conditional breakpoints for specific scenarios

2. Debug Console:
   - Use the Debug Console to inspect variables
   - Execute code during debug sessions

3. Watch Variables:
   - Add important variables to the Watch panel
   - Monitor state changes during execution

4. Hot Reload:
   - Streamlit automatically reloads on file changes
   - Use `st.experimental_rerun()` for manual reloads

## 💻 Usage Guide

### Login/Registration
1. Use the login form with your credentials
2. New users can register using the registration tab

### Live Detection
1. Click "Start Detection" to begin monitoring
2. Adjust sensitivity using the slider in the sidebar
3. Enable alerts if needed

### Viewing Statistics
- Monitor real-time detection counts
- View historical data in the analytics dashboard
- Export detection reports as needed

## 🔧 Configuration

### Motion Detection Settings
- Adjust sensitivity (0-100)
- Configure detection zones
- Set alert thresholds

### Alert Configuration
- Enable/disable email notifications
- Customize alert triggers
- Set notification frequency

## 📊 Database Schema

The system uses PostgreSQL with the following main tables:
- users: User authentication and management
- vehicle_records: Vehicle detection records
- detection_history: General detection events

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- Streamlit for the web interface
- MediaPipe for hand gesture recognition

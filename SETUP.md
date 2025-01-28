# Sixth Sense Vision - Setup Guide

This guide provides detailed instructions for setting up the Sixth Sense Vision security system.

## Development Environment Setup

### 1. System Requirements
- Python 3.11+
- PostgreSQL database
- Webcam or IP camera for testing
- Visual Studio Code (recommended IDE)

### 2. VSCode Setup
```bash
# Install VSCode Extensions
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-toolsai.jupyter
```

### 3. Environment Setup
```bash
# Install required Python packages
pip install streamlit opencv-python-headless numpy pillow

# Install additional dependencies if needed
pip install mediapipe easyocr requests
```

### 4. Database Configuration
```sql
-- Create database tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicle_records (
    id SERIAL PRIMARY KEY,
    plate_number TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_name TEXT,
    vehicle_type TEXT,
    notes TEXT
);
```

### 5. Environment Variables

Create a `.env` file with the following variables:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# Email Notifications (Optional)
EMAILJS_USER_ID=your_user_id
EMAILJS_TEMPLATE_ID=your_template_id
EMAILJS_SERVICE_ID=your_service_id
```

## Running the Application

### 1. Start the Application
Using VSCode:
1. Open the project in VSCode
2. Select the Python interpreter (Ctrl+Shift+P -> "Python: Select Interpreter")
3. Open the integrated terminal (Ctrl+`)
4. Run:
```bash
streamlit run main.py
```

### 2. First-Time Setup
1. Register an admin account
2. Configure detection sensitivity
3. Set up alert preferences

### 3. Testing the System
1. Test motion detection
2. Verify email notifications
3. Check database connectivity

## Troubleshooting

### Common Issues

1. Database Connection Errors
```bash
# Check database status
python -c "from database import Database; db = Database()"
```

2. Camera Access Issues
- Ensure proper permissions are set
- Check camera connection

3. Package Dependencies
```bash
# Verify installations
pip list | grep -E "opencv|numpy|streamlit"
```

## VSCode-Specific Debugging

### 1. Launch Configuration
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Streamlit: Main App",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": ["run", "main.py"],
      "justMyCode": true
    }
  ]
}
```

### 2. Debugging Commands
- F5: Start debugging
- F9: Toggle breakpoint
- F10: Step over
- F11: Step into
- Shift+F11: Step out
- Ctrl+Shift+F5: Restart debugging

### 3. Recommended VSCode Extensions
- Python
- Pylance
- Python Debugger
- Python Environment Manager
- SQLite Viewer (optional)

## Deployment Notes

### Production Deployment
1. Use proper SSL/TLS certificates
2. Configure proper database backups
3. Set up monitoring and logging

### Security Considerations
- Regular security audits
- Password policy enforcement
- Access control implementation
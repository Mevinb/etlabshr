# 🎓 ETLab API Web Interface

A comprehensive web dashboard to interact with all ETLab API endpoints through an intuitive user interface.

## 🚀 Features

### 🔐 Authentication
- **Login**: Secure authentication with ETLab credentials
- **Logout**: Clear session and authentication token
- **Status Indicator**: Visual indication of login status

### 📊 Academic Information
- **Profile**: View complete student profile information
- **Results**: Get exam results filtered by semester
- **Attendance**: View attendance records for all subjects
- **Timetable**: Display class schedule and timing

### ✅ Attendance Management
- **Mark Present**: Record attendance for specific subjects and dates
- **Mark Absent**: Record absence for specific subjects and dates

### 🔍 System Status
- **API Status**: Check server health and connectivity

## 🌐 Access the Interface

1. **Start the Flask server**:
   ```bash
   cd d:\etlabCRACK\etlab
   python run.py
   ```

2. **Open your web browser** and navigate to:
   - Main interface: `http://localhost:5000`
   - Dashboard: `http://localhost:5000/dashboard`

## 📱 How to Use

### Step 1: Login
1. Navigate to the **Login** tab (default)
2. Enter your ETLab credentials:
   - Username: Your student ID (e.g., 224079)
   - Password: Your ETLab password
3. Click **Login**
4. Status indicator will show green when logged in

### Step 2: Use API Features
Once logged in, you can access all tabs:

#### 👤 Profile
- Click **Get Profile** to retrieve your complete profile information
- View personal details, academic information, and contact details

#### 📊 Results
- Select your semester from the dropdown (1-8)
- Click **Get Results** to fetch exam results
- View sessional exams, module tests, assignments, and projects

#### 📅 Attendance
- Click **Get Attendance** to view attendance records
- See attendance percentage for each subject

#### 🕐 Timetable
- Click **Get Timetable** to view your class schedule
- See timing and subject details

#### ✅ Mark Present/Absent
- Enter subject code (e.g., "24CST303")
- Select date
- Click **Mark Present** or **Mark Absent**

#### 🔍 Status
- Check API server status and connectivity
- No authentication required

## 📋 API Endpoints Covered

The web interface provides access to all available API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login` | POST | Authenticate with ETLab |
| `/api/logout` | POST | Clear session |
| `/api/profile` | GET | Get profile information |
| `/api/results` | GET | Get exam results by semester |
| `/api/attendance` | GET | Get attendance records |
| `/api/timetable` | GET | Get class timetable |
| `/api/present` | POST | Mark attendance as present |
| `/api/absent` | POST | Mark attendance as absent |
| `/api/status` | GET | Check API status |

## 🎨 Features

### 🔄 Real-time Updates
- Live status indicator for authentication
- Loading spinners for API calls
- Real-time response display

### 📱 Responsive Design
- Works on desktop, tablet, and mobile devices
- Clean, modern interface
- Intuitive navigation

### 🛡️ Security
- Secure token-based authentication
- Local storage of authentication tokens
- Automatic session management

### 🎯 User Experience
- Tab-based navigation
- Clear success/error messages
- Formatted JSON response display
- Pre-filled test credentials for development

## 🐛 Troubleshooting

### Login Issues
- Ensure credentials are correct
- Check if ETLab server is accessible
- Verify Flask server is running

### API Errors
- Check network connectivity
- Ensure you're logged in for protected endpoints
- Verify semester parameter for results endpoint

### Browser Issues
- Clear browser cache and cookies
- Disable browser extensions that might block requests
- Try a different browser

## 🔧 Development

### File Structure
```
etlab/
├── static/
│   └── index.html          # Web interface
├── app/
│   ├── __init__.py         # Flask app with static routes
│   └── routes/             # API endpoints
└── run.py                  # Server startup
```

### Customization
- Modify `static/index.html` to customize the interface
- Update CSS styles for different themes
- Add new tabs for additional functionality

## 🎉 Success!

You now have a complete web interface to interact with all ETLab API endpoints! The interface provides:

✅ **Full API Coverage** - All endpoints accessible through UI  
✅ **Modern Design** - Clean, responsive interface  
✅ **Real-time Feedback** - Live status updates and responses  
✅ **Mobile-Friendly** - Works on all devices  
✅ **Secure Authentication** - Token-based security  

Enjoy using your ETLab API Dashboard! 🚀
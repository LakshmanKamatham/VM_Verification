# 🚀 Bootcode Verification Chatbot - Launch Instructions

## 📋 Quick Start Guide

### Step 1: Prerequisites Check
Ensure you have:
- **Python 3.7+** installed
- **pip** package manager
- A modern web browser

### Step 2: Install Dependencies

**Option A: Using pip (Recommended)**
```bash
pip install Flask openpyxl Werkzeug
```

**Option B: Using requirements.txt**
```bash
pip install -r requirements.txt
```

**Option C: On Windows (Using the provided batch file)**
```batch
run_chatbot.bat
```

### Step 3: Launch the Application

```bash
python app.py
```

You should see output like:
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://[your-ip]:5000
```

### Step 4: Access the Chatbot

Open your web browser and navigate to:
```
http://localhost:5000
```

## 📁 Preparing Your Error Database

### Supported File Formats
- **CSV** (.csv)
- **Excel** (.xls, .xlsx)

### File Structure

#### Basic Format (2 columns minimum):
```csv
Error Message,Primary Fix
"Boot sector checksum mismatch","Run chkdsk /f to check file system errors"
"NTLDR is missing","Boot from Windows installation media and run fixboot"
```

#### Enhanced Format (Multiple fixes + priority):
```csv
Error Message,Primary Fix,Alternative Fix,Additional Fix,Priority
"Boot sector checksum mismatch","Run chkdsk /f","Use disk recovery tools","Replace hard drive if errors persist","High"
"NTLDR is missing","Boot from installation media","Copy ntldr from CD","Repair MBR using recovery console","Medium"
```

#### Column Options:
- **Column 1** (Required): Error Messages
- **Column 2** (Required): Primary Fix
- **Column 3** (Optional): Alternative Fix
- **Column 4** (Optional): Additional Fix
- **Column 5** (Optional): Priority Level (Critical, High, Medium, Low)

## 🎯 How to Use the Chatbot

### Step 1: Upload Database
1. Click "📁 Choose Error Database"
2. Select your CSV or Excel file
3. Wait for confirmation message

### Step 2: Ask Questions
Type error messages like:
- `"boot failure"`
- `"memory error during startup"`
- `"BIOS checksum error"`
- `"disk not found"`

### Step 3: Get Solutions
The chatbot will:
- **Find exact matches** (90%+ similarity)
- **Suggest similar errors** with multiple fix options
- **Ask follow-up questions** for ambiguous queries
- **Log unmatched errors** for database improvement

## 🔧 Advanced Features

### 1. **Fuzzy Matching**
- Finds similar errors even with different wording
- Adjustable similarity threshold (default: 60%)
- Case-insensitive matching

### 2. **Multi-Fix Support**
- Primary, Alternative, and Additional solutions
- Priority-based sorting (Critical > High > Medium > Low)
- Visual color coding for different fix types

### 3. **Follow-up Questions**
- Detects ambiguous queries
- Asks targeted clarification questions
- Categories errors by type (memory, storage, firmware, etc.)

### 4. **Dataset Improvement**
- Logs unmatched errors automatically
- Provides suggestions for better error descriptions
- Generates templates for adding new entries
- Download unmatched errors for review

### 5. **Session Management**
- Isolated user sessions
- Easy session clearing
- File upload per session

## 📊 Sample Database

Use the included `sample_bootcode_errors.csv` to test the system:

```csv
Error Message,Primary Fix,Alternative Fix,Priority
"Boot sector checksum mismatch","Run chkdsk /f on Windows","Use fsck on Linux","High"
"NTLDR is missing","Boot from Windows installation media","Copy ntldr from installation CD","Medium"
"Bootmgr is missing","Run bootrec /fixmbr and /fixboot","Rebuild BCD using bootrec /rebuildbcd","High"
"Memory test failed","Remove and reseat RAM modules","Test each module individually","Medium"
"TPM initialization failed","Clear TPM in BIOS settings","Update BIOS firmware","Low"
```

## 🌐 Accessing from Other Devices

### On Local Network:
1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. Access from other devices:
   ```
   http://[your-ip-address]:5000
   ```

### Port Configuration:
To change the port, edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

## 🔍 Troubleshooting

### Common Issues:

1. **"Module not found" errors**
   ```bash
   pip install Flask openpyxl Werkzeug
   ```

2. **Port already in use**
   ```bash
   # Kill process using port 5000
   # Windows: netstat -ano | findstr :5000
   # Linux/Mac: lsof -ti:5000 | xargs kill
   ```

3. **File upload fails**
   - Check file format (CSV/Excel only)
   - Ensure file has at least 2 columns
   - Verify file isn't corrupted

4. **No matches found**
   - Try more specific error descriptions
   - Use technical terms related to boot processes
   - Check for typos in your query

5. **Browser compatibility**
   - Use modern browsers (Chrome, Firefox, Safari, Edge)
   - Enable JavaScript
   - Clear browser cache if issues persist

## 📝 File Structure

```
bootcode-chatbot/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── sample_bootcode_errors.csv      # Sample error database
├── LAUNCH_INSTRUCTIONS.md         # This file
├── CHATBOT_README.md              # Detailed documentation
├── run_chatbot.bat                # Windows launcher
├── templates/
│   └── index.html                 # Web interface
├── uploads/                       # Temporary file storage
├── unmatched_errors.log           # Log of unmatched queries
└── unmatched_errors.csv           # Downloadable unmatched errors
```

## 🔐 Security Notes

- Files are processed in memory only
- No permanent data storage by default
- Session data is cleared when browser closes
- Logs contain error messages only (no sensitive data)

## 🚀 Production Deployment

For production use:

1. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Enable HTTPS**:
   - Use reverse proxy (nginx, Apache)
   - Obtain SSL certificates

3. **Database Integration**:
   - Replace in-memory storage with database
   - Add user authentication

4. **Performance Optimization**:
   - Implement caching
   - Add load balancing
   - Monitor resource usage

## 📞 Support

- **Test with sample data**: Use `sample_bootcode_errors.csv`
- **Check logs**: View `unmatched_errors.log` for debugging
- **Verify file format**: Ensure CSV/Excel files are properly formatted
- **Browser console**: Check for JavaScript errors (F12 → Console)

---

**🎉 You're ready to go! Upload your error database and start getting instant fix suggestions for bootcode verification issues!**
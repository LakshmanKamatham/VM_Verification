# 🔧 Bootcode Verification Chatbot

A web-based chatbot application that helps diagnose and fix bootcode verification errors by matching error messages against a customizable database of known issues and solutions.

## ✨ Features

- **File Upload Support**: Upload CSV or Excel files containing error databases
- **Smart Error Matching**: Uses similarity algorithms to find best matches for error messages
- **Visual Chat Interface**: Modern, responsive web interface with real-time chat
- **Similarity Scoring**: Shows how closely your error matches known issues
- **Multiple Fix Suggestions**: Provides ranked solutions based on match quality
- **Session Management**: Handles multiple users with isolated sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Chatbot**
   Open your web browser and navigate to: `http://localhost:5000`

## 📋 How to Use

### Step 1: Prepare Your Error Database

Create a CSV or Excel file with exactly 2 columns:
- **Column 1**: Error Messages
- **Column 2**: Fix Details/Solutions

Example format:
```csv
Error Message,Fix Details
"Boot sector checksum mismatch","Verify the integrity of the boot sector. Run 'chkdsk /f' on Windows..."
"NTLDR is missing","The NT Loader is missing or corrupted. Boot from Windows installation media..."
```

### Step 2: Upload Your Database

1. Click the "📁 Choose Error Database" button
2. Select your CSV or Excel file
3. Wait for the upload confirmation message

### Step 3: Start Chatting

1. Type your error message in the chat input
2. Press Enter or click the send button
3. Receive instant fix suggestions with similarity scores

## 🗂️ Sample Data

The repository includes `sample_bootcode_errors.csv` with common bootcode verification errors. You can use this file to test the system or as a template for your own error database.

## 🔍 Error Matching Algorithm

The chatbot uses sophisticated string matching to find relevant errors:

1. **Exact Substring Matching**: Prioritizes exact phrase matches
2. **Similarity Scoring**: Uses SequenceMatcher for fuzzy matching
3. **Ranked Results**: Returns top 5 matches sorted by relevance
4. **Threshold Filtering**: Only shows matches above 60% similarity

## 💻 Technical Architecture

### Backend (Flask)
- **`app.py`**: Main Flask application with API endpoints
- **File Processing**: Handles CSV/Excel uploads using pandas
- **Session Management**: Isolates user data using Flask sessions
- **Error Matching**: Implements similarity algorithms

### Frontend (HTML/CSS/JavaScript)
- **`templates/index.html`**: Modern chat interface
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Instant file upload and chat responses
- **Visual Feedback**: Typing indicators and similarity scores

### Key API Endpoints
- `GET /`: Main chat interface
- `POST /upload`: File upload handling
- `POST /chat`: Error message processing
- `POST /clear`: Session cleanup

## 🛠️ Customization

### Similarity Threshold
Modify the threshold in `app.py`:
```python
matches = find_best_matches(message, df, threshold=0.6)  # Adjust threshold here
```

### UI Colors and Styling
Customize the appearance by modifying the CSS in `templates/index.html`.

### Maximum File Size
Change upload limits in `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
```

## 🔒 Security Considerations

- File uploads are restricted to CSV/Excel formats only
- Session data is isolated per user
- Input validation prevents malicious file uploads
- No persistent data storage (data cleared on session end)

## 🚀 Production Deployment

For production use, consider:

1. **Database Storage**: Replace in-memory storage with a proper database
2. **Authentication**: Add user authentication and authorization
3. **HTTPS**: Enable SSL/TLS encryption
4. **Load Balancing**: Use multiple server instances
5. **File Storage**: Implement persistent file storage
6. **Logging**: Add comprehensive logging and monitoring

## 🤝 Usage Examples

### Example 1: Boot Manager Error
```
User Input: "bootmgr missing"
Bot Response: Found exact match! Here's the recommended fix:
- Error: "Bootmgr is missing" (95% match)
- Fix: Boot from Windows installation media, select 'Repair your computer'...
```

### Example 2: Memory Issues
```
User Input: "ram error during startup"
Bot Response: Found 2 similar error(s):
- Error: "Memory test failed" (78% match)
- Fix: Remove and reseat memory modules, test each module individually...
```

## 🔧 Troubleshooting

### Common Issues

1. **"Module not found" errors**: Run `pip install -r requirements.txt`
2. **File upload fails**: Check file format (must be CSV/Excel)
3. **No matches found**: Try different keywords or upload a more comprehensive database
4. **Port already in use**: Change the port in `app.py` or stop other applications using port 5000

### Debug Mode

Enable debug mode for development:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📝 File Structure

```
bootcode-chatbot/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── sample_bootcode_errors.csv      # Sample error database
├── CHATBOT_README.md              # This documentation
├── templates/
│   └── index.html                 # Chat interface
└── uploads/                       # Temporary file storage
```

## 🙋‍♂️ Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your error database format matches the required structure
3. Ensure all dependencies are properly installed

---

**Happy Debugging! 🐛→✅**
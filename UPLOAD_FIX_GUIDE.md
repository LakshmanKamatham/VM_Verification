# 🔧 Upload Issue Fix Guide

## ❌ Problem: "Upload failed. Please try again." 

This error occurs when the file upload process hangs or times out. Here are the solutions:

## ✅ **Solution 1: Run with Enhanced Debugging**

Start your application with:
```bash
python app.py
```

You should see:
```
🚀 Starting Bootcode Verification Chatbot...
📍 Access at: http://localhost:8000
🔧 Enhanced version with Unicode fixes and error handling
```

## ✅ **Solution 2: Check Browser Console for Errors**

1. Open browser (Chrome/Firefox)
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Try uploading a file
5. Look for any JavaScript errors

## ✅ **Solution 3: Test with Sample File**

Use the provided `test_upload.csv` or `sample_bootcode_errors.csv`:

### File Format Requirements:
```csv
Error Message,Primary Fix
"Boot error example","Solution for boot error"
"Memory issue","Fix for memory problem"
```

## ✅ **Solution 4: Browser Compatibility**

If upload fails, try:
1. **Different browser** (Chrome, Firefox, Edge)
2. **Disable browser extensions** (ad blockers, etc.)
3. **Clear browser cache** (Ctrl+Shift+Delete)
4. **Try incognito/private mode**

## ✅ **Solution 5: File Size & Format Check**

Ensure your file:
- ✅ Is less than 16MB
- ✅ Has `.csv`, `.xls`, or `.xlsx` extension  
- ✅ Has at least 2 columns
- ✅ Contains actual data (not empty)

## ✅ **Solution 6: Manual Test Using cURL**

Test upload directly:
```bash
curl -X POST -F "file=@your_file.csv" http://localhost:8000/upload
```

## ✅ **Solution 7: Check Server Logs**

When you upload, you should see in terminal:
```
📁 Upload request received
📄 File received: your_file.csv
📊 File size: XXXX bytes
✅ File type allowed, processing...
📖 Reading file data...
✅ Data stored successfully
```

## ❌ **Common Error Messages & Fixes**

### "No file selected"
- Make sure you click "Choose File" and select a file

### "Invalid file type"
- Use only .csv, .xls, or .xlsx files

### "File too large"
- Reduce file size to under 16MB

### "File contains no data rows"
- Check your file has data, not just headers

### "openpyxl not available"
- Install: `pip install openpyxl`

## 🔧 **Quick Diagnostic Steps**

1. **Check if server is running:**
   ```bash
   curl http://localhost:8000/test-upload
   ```

2. **Verify file format:**
   ```csv
   Error Message,Primary Fix
   "Test error","Test solution"
   ```

3. **Test with minimal file:**
   Create a simple 2-line CSV and try uploading

## 🚀 **Alternative Solutions**

### Option A: Use Fallback Mode
If template fails, the app provides a basic HTML interface that should still work.

### Option B: Direct File Processing
Save your file as `direct_upload.csv` in the same folder and modify app.py to load it directly.

### Option C: Browser Network Tab
1. F12 → Network tab
2. Try upload
3. Look for failed requests
4. Check response codes

## 💡 **Prevention Tips**

1. **Always use UTF-8 encoding** when saving CSV files
2. **Keep files under 1000 rows** for better performance
3. **Use simple column names** without special characters
4. **Test with small files first**

## 🎯 **Success Indicators**

When upload works correctly, you'll see:
- ✅ Green success message
- ✅ File name displayed
- ✅ "Database loaded successfully" in chat
- ✅ Input field becomes enabled
- ✅ "Clear Session" button appears

---

**If none of these solutions work, the issue might be network/firewall related. Try accessing from `http://127.0.0.1:8000` instead of `localhost`.**
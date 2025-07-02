from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
import uuid
from difflib import SequenceMatcher
import re

app = Flask(__name__)
app.secret_key = 'bootcode_verification_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store uploaded data in memory (in production, use a database)
uploaded_data = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xls', 'xlsx'}

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_matches(error_message, df, threshold=0.6):
    """Find best matching error messages in the dataframe"""
    if df.empty or len(df) == 0:
        return []
    
    error_col = df.columns[0]  # First column is error messages
    
    matches = []
    error_message_lower = error_message.lower()
    
    for idx, row in df.iterrows():
        stored_error = str(row[error_col]).lower()
        
        # Check for exact substring match first
        if error_message_lower in stored_error or stored_error in error_message_lower:
            similarity_score = 1.0
        else:
            # Calculate similarity score
            similarity_score = similarity(error_message, str(row[error_col]))
        
        if similarity_score >= threshold:
            # Collect all fix columns and their data
            fixes = []
            priority = "Medium"  # Default priority
            
            # Process all columns after the first one
            for col_idx, col_name in enumerate(df.columns[1:], 1):
                col_value = str(row[col_name]).strip()
                
                # Skip empty/null values
                if col_value and col_value.lower() not in ['nan', 'none', '']:
                    if col_name.lower() in ['priority', 'priority_level', 'urgency']:
                        priority = col_value
                    elif col_name.lower() in ['primary_fix', 'main_fix', 'fix', 'solution']:
                        fixes.insert(0, {'type': 'Primary', 'content': col_value})
                    elif col_name.lower() in ['secondary_fix', 'alternative_fix', 'alt_fix', 'alternative']:
                        fixes.append({'type': 'Alternative', 'content': col_value})
                    elif col_name.lower() in ['tertiary_fix', 'additional_fix', 'extra_fix']:
                        fixes.append({'type': 'Additional', 'content': col_value})
                    else:
                        # Auto-detect fix type based on column position
                        if col_idx == 1:
                            fixes.insert(0, {'type': 'Primary', 'content': col_value})
                        elif col_idx == 2:
                            fixes.append({'type': 'Alternative', 'content': col_value})
                        elif col_idx == 3:
                            fixes.append({'type': 'Additional', 'content': col_value})
                        elif col_idx >= 4 and col_name.lower() not in ['priority', 'priority_level', 'urgency']:
                            fixes.append({'type': f'Option {col_idx-1}', 'content': col_value})
            
            # Ensure we have at least one fix
            if not fixes:
                fixes = [{'type': 'Primary', 'content': 'No specific fix provided'}]
            
            matches.append({
                'error': row[error_col],
                'fixes': fixes,
                'priority': priority,
                'similarity': similarity_score
            })
    
    # Sort by priority first, then similarity score
    priority_order = {'High': 3, 'Medium': 2, 'Low': 1, 'Critical': 4, 'Urgent': 4}
    matches.sort(key=lambda x: (priority_order.get(x['priority'], 2), x['similarity']), reverse=True)
    return matches[:5]  # Return top 5 matches

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Generate unique session ID
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            session_id = session['session_id']
            
            # Read the file based on extension
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(file)
            else:  # Excel files
                df = pd.read_excel(file)
            
            # Validate that the file has at least 2 columns
            if len(df.columns) < 2:
                return jsonify({'error': 'File must have at least 2 columns (Error Message and at least one Fix column)'}), 400
            
            # Store the dataframe
            uploaded_data[session_id] = df
            
            return jsonify({
                'success': True, 
                'message': f'File uploaded successfully! Found {len(df)} error records.',
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict('records')
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type. Please upload CSV, XLS, or XLSX files.'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Please enter an error message'}), 400
    
    session_id = session.get('session_id')
    if not session_id or session_id not in uploaded_data:
        return jsonify({'error': 'Please upload a file first'}), 400
    
    df = uploaded_data[session_id]
    
    # Find matching errors
    matches = find_best_matches(message, df)
    
    if not matches:
        response = {
            'message': 'No matching errors found in the uploaded data.',
            'suggestions': ['Try rephrasing your error message', 'Check for typos', 'Upload a more comprehensive error database']
        }
    else:
        if matches[0]['similarity'] >= 0.9:
            response = {
                'message': f'Found exact match! Here are the recommended solutions:',
                'exact_match': True,
                'matches': [matches[0]]
            }
        else:
            response = {
                'message': f'Found {len(matches)} similar error(s). Here are the closest matches:',
                'exact_match': False,
                'matches': matches
            }
    
    return jsonify(response)

@app.route('/clear', methods=['POST'])
def clear_session():
    session_id = session.get('session_id')
    if session_id and session_id in uploaded_data:
        del uploaded_data[session_id]
    session.clear()
    return jsonify({'success': True, 'message': 'Session cleared successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
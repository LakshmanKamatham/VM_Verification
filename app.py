from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
import uuid
from difflib import SequenceMatcher
import re
from collections import defaultdict
import logging
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'bootcode_verification_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store uploaded data in memory (in production, use a database)
uploaded_data = {}
# Store conversation context for follow-up questions
conversation_context = {}
# Store unmatched errors for dataset improvement
unmatched_errors = []

# Setup logging for unmatched errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unmatched_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xls', 'xlsx'}

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_keywords(text):
    """Extract meaningful keywords from error message"""
    # Common bootcode-related keywords
    keywords = []
    text_lower = text.lower()
    
    # Boot-related terms
    boot_terms = ['boot', 'bios', 'uefi', 'mbr', 'gpt', 'bootloader', 'grub', 'ntldr', 'bootmgr']
    hardware_terms = ['memory', 'ram', 'cpu', 'disk', 'drive', 'ssd', 'hdd', 'tpm', 'secure']
    error_terms = ['error', 'failure', 'failed', 'missing', 'corrupt', 'invalid', 'timeout', 'panic']
    
    for term in boot_terms + hardware_terms + error_terms:
        if term in text_lower:
            keywords.append(term)
    
    return keywords

def is_ambiguous_query(matches, original_message):
    """Determine if the query is ambiguous and needs clarification"""
    if len(matches) < 2:
        return False
    
    # Check if top matches have similar similarity scores but different keywords
    top_matches = matches[:3]  # Look at top 3 matches
    similarity_threshold = 0.15  # If similarity scores are within 15% of each other
    
    # Group matches by similarity score ranges
    score_groups = []
    for match in top_matches:
        added_to_group = False
        for group in score_groups:
            if abs(group[0]['similarity'] - match['similarity']) <= similarity_threshold:
                group.append(match)
                added_to_group = True
                break
        if not added_to_group:
            score_groups.append([match])
    
    # If we have multiple matches with similar scores
    if len(score_groups) > 0 and len(score_groups[0]) >= 2:
        # Check if they represent different error categories
        error_categories = set()
        for match in score_groups[0]:
            keywords = extract_keywords(match['error'])
            category = determine_error_category(keywords)
            error_categories.add(category)
        
        # If different categories, it's ambiguous
        if len(error_categories) > 1:
            return True
    
    # Check if the original message is too generic
    original_keywords = extract_keywords(original_message)
    if len(original_keywords) <= 2 and len(matches) >= 3:
        return True
    
    return False

def determine_error_category(keywords):
    """Categorize error based on keywords"""
    if any(term in keywords for term in ['memory', 'ram']):
        return 'memory'
    elif any(term in keywords for term in ['disk', 'drive', 'ssd', 'hdd', 'mbr', 'gpt']):
        return 'storage'
    elif any(term in keywords for term in ['boot', 'bootloader', 'grub', 'ntldr', 'bootmgr']):
        return 'bootloader'
    elif any(term in keywords for term in ['bios', 'uefi', 'tpm', 'secure']):
        return 'firmware'
    elif any(term in keywords for term in ['cpu']):
        return 'processor'
    else:
        return 'general'

def generate_follow_up_question(matches, original_message):
    """Generate intelligent follow-up questions based on matches"""
    if len(matches) < 2:
        return None
    
    # Analyze the matches to create targeted questions
    categories = defaultdict(list)
    for match in matches[:5]:  # Look at top 5 matches
        keywords = extract_keywords(match['error'])
        category = determine_error_category(keywords)
        categories[category].append(match)
    
    # Generate questions based on categories
    if len(categories) > 1:
        category_options = []
        category_names = {
            'memory': 'Memory/RAM related',
            'storage': 'Hard drive/Storage related', 
            'bootloader': 'Boot loader/Boot manager related',
            'firmware': 'BIOS/UEFI/Firmware related',
            'processor': 'CPU/Processor related',
            'general': 'General system'
        }
        
        for category, matches_in_category in categories.items():
            if len(matches_in_category) > 0:
                example = matches_in_category[0]['error']
                category_display = category_names.get(category, category.title())
                category_options.append({
                    'category': category,
                    'display_name': category_display,
                    'example': example,
                    'count': len(matches_in_category)
                })
        
        if len(category_options) >= 2:
            question = "I found multiple types of errors that might match your description. Could you help me narrow it down?\n\n"
            
            for i, option in enumerate(category_options[:4], 1):  # Show max 4 options
                question += f"{i}. **{option['display_name']}** ({option['count']} match{'es' if option['count'] > 1 else ''})\n"
                question += f"   Example: \"{option['example']}\"\n\n"
            
            question += "Please type the number or describe which type of error you're experiencing."
            
            return {
                'question': question,
                'type': 'category_selection',
                'options': category_options,
                'original_matches': matches
            }
    
    # If same category but different specific errors
    elif len(matches) >= 3:
        question = "I found several similar errors. Could you provide more details?\n\n"
        
        for i, match in enumerate(matches[:4], 1):
            similarity_percent = int(match['similarity'] * 100)
            question += f"{i}. \"{match['error']}\" ({similarity_percent}% match)\n"
        
        question += f"\nPlease type the number of the closest match, or provide more specific details about your error."
        
        return {
            'question': question,
            'type': 'specific_selection',
            'options': matches[:4],
            'original_matches': matches
        }
    
    return None

def log_unmatched_error(error_message, session_id, user_context=None):
    """Log unmatched error messages for dataset improvement"""
    timestamp = datetime.now().isoformat()
    
    error_entry = {
        'timestamp': timestamp,
        'error_message': error_message,
        'session_id': session_id,
        'user_context': user_context
    }
    
    # Add to in-memory list
    unmatched_errors.append(error_entry)
    
    # Log to file
    logger.info(f"UNMATCHED_ERROR: {json.dumps(error_entry)}")
    
    # Keep only last 100 unmatched errors in memory
    if len(unmatched_errors) > 100:
        unmatched_errors.pop(0)

def generate_improvement_suggestions(error_message):
    """Generate suggestions for improving the dataset"""
    suggestions = []
    
    # Analyze the error message to provide contextual suggestions
    keywords = extract_keywords(error_message)
    error_lower = error_message.lower()
    
    if not keywords:
        suggestions.append("Try using more specific technical terms related to boot processes")
        suggestions.append("Include error codes or specific component names if available")
    
    if len(error_message.split()) < 3:
        suggestions.append("Provide more detailed description of when this error occurs")
        suggestions.append("Include any error codes or system information")
    
    # Specific suggestions based on content
    if any(term in error_lower for term in ['boot', 'startup', 'start']):
        suggestions.append("Specify the boot stage: BIOS/UEFI, bootloader, or OS loading")
        suggestions.append("Mention if this happens on cold boot, warm restart, or both")
    
    if any(term in error_lower for term in ['error', 'fail']):
        suggestions.append("Include the exact error message or code if displayed")
        suggestions.append("Describe what happens: system freezes, restarts, or shows error screen")
    
    # General improvement suggestions
    suggestions.extend([
        "Consider adding this error to your database with a detailed fix description",
        "Check if there are similar errors in your database that might help",
        "Document the system configuration where this error occurs"
    ])
    
    return suggestions[:6]  # Return max 6 suggestions

def generate_database_entry_template(error_message):
    """Generate a template for adding new entries to the database"""
    template = {
        'error_message': error_message,
        'primary_fix': '[Please provide the main solution for this error]',
        'alternative_fix': '[Optional: Provide an alternative solution]',
        'additional_fix': '[Optional: Provide additional troubleshooting steps]',
        'priority': '[High/Medium/Low - Set priority level]',
        'category': determine_error_category(extract_keywords(error_message)),
        'suggested_format': {
            'csv_row': f'"{error_message}","[Primary Fix]","[Alternative Fix]","[Additional Fix]","Medium"',
            'excel_columns': ['Error Message', 'Primary Fix', 'Alternative Fix', 'Additional Fix', 'Priority']
        }
    }
    return template

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
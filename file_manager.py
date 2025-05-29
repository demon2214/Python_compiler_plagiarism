from flask import Blueprint, request, redirect, url_for, session, flash, send_file, render_template, abort, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import tempfile
import shutil
from datetime import datetime
from database import get_db_connection
from encryption import encrypt_file, decrypt_file
from config import Config
from auth import login_required, admin_required

# FIXED: Changed blueprint name to match what's used in templates
file_bp = Blueprint('files', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@file_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        folder = request.form.get('folder', 'user')
        visibility = request.form.get('visibility', 'private')
        
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{original_filename}"
            
            # Determine upload path based on user role and folder
            if session.get('role') == 'admin':
                upload_path = os.path.join(Config.UPLOAD_FOLDER, folder)
            else:
                upload_path = os.path.join(Config.UPLOAD_FOLDER, 'user')
                folder = 'user'
            
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            file_path = os.path.join(upload_path, unique_filename)
            
            # Save and encrypt file
            file.save(file_path)
            encrypted_path = encrypt_file(file_path)
            
            # Remove original unencrypted file
            if encrypted_path != file_path:
                try:
                    os.remove(file_path)
                except OSError:
                    pass  # File might already be removed
                file_path = encrypted_path
            
            # Save file info to database
            conn = get_db_connection()
            conn.execute(
                '''INSERT INTO files (filename, original_filename, file_path, file_size, 
                   file_type, uploaded_by, folder, visibility, is_encrypted) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (unique_filename, original_filename, file_path, 
                 os.path.getsize(file_path), file.content_type or 'application/octet-stream',
                 session['user_id'], folder, visibility, True)
            )
            conn.commit()
            conn.close()
            
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type.', 'error')
    
    return render_template('upload.html')

@file_bp.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    conn = get_db_connection()
    file_record = conn.execute(
        'SELECT * FROM files WHERE id = ?', (file_id,)
    ).fetchone()
    conn.close()
    
    if not file_record:
        abort(404)
    
    # Check permissions
    if (file_record['uploaded_by'] != session['user_id'] and 
        file_record['visibility'] != 'public' and 
        session.get('role') != 'admin'):
        abort(403)
    
    # Create a temporary directory for this download
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Decrypt file to temporary location
        if file_record['file_path'].endswith('.enc'):
            # Read encrypted file
            with open(file_record['file_path'], 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            from encryption import decrypt_data
            decrypted_data = decrypt_data(encrypted_data)
            
            # Write to temporary file
            temp_file_path = os.path.join(temp_dir, file_record['original_filename'])
            with open(temp_file_path, 'wb') as f:
                f.write(decrypted_data)
        else:
            # File is not encrypted, copy it
            temp_file_path = os.path.join(temp_dir, file_record['original_filename'])
            shutil.copy2(file_record['file_path'], temp_file_path)
        
        # Send file and clean up in a custom response
        def remove_temp_file(response):
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                pass  # Ignore cleanup errors
            return response
        
        # Use send_file with as_attachment and cleanup
        response = send_file(
            temp_file_path, 
            as_attachment=True, 
            download_name=file_record['original_filename'],
            mimetype=file_record['file_type']
        )
        
        # Add cleanup callback
        response.call_on_close(lambda: cleanup_temp_dir(temp_dir))
        
        return response
        
    except Exception as e:
        # Clean up on error
        try:
            shutil.rmtree(temp_dir)
        except OSError:
            pass
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

def cleanup_temp_dir(temp_dir):
    """Cleanup temporary directory with retry logic"""
    import time
    max_retries = 3
    for i in range(max_retries):
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            break
        except OSError:
            if i < max_retries - 1:
                time.sleep(0.1)  # Wait a bit before retry
            else:
                pass  # Give up after max retries

@file_bp.route('/view/<int:file_id>')
def view_file(file_id):
    conn = get_db_connection()
    file_record = conn.execute(
        'SELECT * FROM files WHERE id = ?', (file_id,)
    ).fetchone()
    conn.close()
    
    if not file_record:
        abort(404)
    
    # Check permissions for viewing
    if file_record['visibility'] != 'public':
        if 'user_id' not in session:
            abort(403)
        if (file_record['uploaded_by'] != session['user_id'] and 
            session.get('role') != 'admin'):
            abort(403)
    
    # Only allow viewing of text files
    if not file_record['file_type'].startswith('text/'):
        flash('File type not supported for viewing.', 'error')
        return redirect(url_for('dashboard'))
    
    # Create temporary directory for viewing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Decrypt file content for viewing
        if file_record['file_path'].endswith('.enc'):
            with open(file_record['file_path'], 'rb') as f:
                encrypted_data = f.read()
            
            from encryption import decrypt_data
            decrypted_data = decrypt_data(encrypted_data)
            
            # Try to decode as text
            try:
                content = decrypted_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = decrypted_data.decode('latin-1')
                except UnicodeDecodeError:
                    content = "Unable to decode file content as text."
        else:
            # File is not encrypted
            try:
                with open(file_record['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_record['file_path'], 'r', encoding='latin-1') as f:
                        content = f.read()
                except:
                    content = "Unable to read file content."
        
        return render_template('view_file.html', file=file_record, content=content)
        
    except Exception as e:
        flash(f'Error viewing file: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except OSError:
            pass

@file_bp.route('/delete/<int:file_id>')
@login_required
def delete_file(file_id):
    conn = get_db_connection()
    file_record = conn.execute(
        'SELECT * FROM files WHERE id = ?', (file_id,)
    ).fetchone()
    
    if not file_record:
        flash('File not found.', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Check permissions
    if (file_record['uploaded_by'] != session['user_id'] and 
        session.get('role') != 'admin'):
        flash('Permission denied.', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Delete file from filesystem
    try:
        if os.path.exists(file_record['file_path']):
            os.remove(file_record['file_path'])
    except OSError as e:
        flash(f'Warning: Could not delete file from disk: {str(e)}', 'warning')
    
    # Delete from database
    conn.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    
    flash('File deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@file_bp.route('/list')
def list_files():
    conn = get_db_connection()
    
    if 'user_id' in session:
        # Logged in user - show their files and public files
        if session.get('role') == 'admin':
            files = conn.execute(
                '''SELECT f.*, u.username FROM files f 
                   JOIN users u ON f.uploaded_by = u.id 
                   ORDER BY f.upload_date DESC'''
            ).fetchall()
        else:
            files = conn.execute(
                '''SELECT f.*, u.username FROM files f 
                   JOIN users u ON f.uploaded_by = u.id 
                   WHERE f.uploaded_by = ? OR f.visibility = "public"
                   ORDER BY f.upload_date DESC''',
                (session['user_id'],)
            ).fetchall()
    else:
        # Guest user - only public files
        files = conn.execute(
            '''SELECT f.*, u.username FROM files f 
               JOIN users u ON f.uploaded_by = u.id 
               WHERE f.visibility = "public"
               ORDER BY f.upload_date DESC'''
        ).fetchall()
    
    conn.close()
    return render_template('file_list.html', files=files)

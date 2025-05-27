from flask import Blueprint, render_template, request, jsonify
from auth import admin_required
from models import Submission
from plagiarism_detector import calculate_similarity, compare_codes_detailed

plagiarism_bp = Blueprint('plagiarism', __name__)

@plagiarism_bp.route('/check')
@admin_required
def plagiarism_check():
    submissions = Submission.get_all()
    
    # Convert Row objects to dictionaries
    submissions_list = []
    for submission in submissions:
        submissions_list.append({
            'id': submission['id'],
            'user_id': submission['user_id'],
            'question_id': submission['question_id'],
            'code': submission['code'],
            'similarity_score': submission['similarity_score'],
            'submitted_at': submission['submitted_at'],
            'username': submission['username'],
            'question_title': submission['question_title']
        })
    
    # Group submissions by question
    questions_submissions = {}
    for submission in submissions_list:
        q_id = submission['question_id']
        if q_id not in questions_submissions:
            questions_submissions[q_id] = []
        questions_submissions[q_id].append(submission)
    
    # Find similar submissions
    similar_pairs = []
    for q_id, subs in questions_submissions.items():
        for i in range(len(subs)):
            for j in range(i + 1, len(subs)):
                similarity = calculate_similarity(subs[i]['code'], subs[j]['code'])
                if similarity > 30:  # Only show similarities above 30%
                    similar_pairs.append({
                        'submission1': subs[i],
                        'submission2': subs[j],
                        'similarity': similarity,
                        'question_title': subs[i]['question_title']
                    })
    
    # Sort by similarity score
    similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
    
    return render_template('plagiarism_check.html', similar_pairs=similar_pairs)

@plagiarism_bp.route('/compare/<int:sub1_id>/<int:sub2_id>')
@admin_required
def compare_codes(sub1_id, sub2_id):
    from models import get_db_connection
    
    conn = get_db_connection()
    
    sub1 = conn.execute('''
        SELECT s.*, u.username, q.title as question_title 
        FROM submissions s 
        JOIN users u ON s.user_id = u.id 
        JOIN questions q ON s.question_id = q.id 
        WHERE s.id = ?
    ''', (sub1_id,)).fetchone()
    
    sub2 = conn.execute('''
        SELECT s.*, u.username, q.title as question_title 
        FROM submissions s 
        JOIN users u ON s.user_id = u.id 
        JOIN questions q ON s.question_id = q.id 
        WHERE s.id = ?
    ''', (sub2_id,)).fetchone()
    
    conn.close()
    
    if not sub1 or not sub2:
        return "Submissions not found", 404
    
    # Convert Row objects to dictionaries
    sub1_dict = {
        'id': sub1['id'],
        'user_id': sub1['user_id'],
        'question_id': sub1['question_id'],
        'code': sub1['code'],
        'similarity_score': sub1['similarity_score'],
        'submitted_at': sub1['submitted_at'],
        'username': sub1['username'],
        'question_title': sub1['question_title']
    }
    
    sub2_dict = {
        'id': sub2['id'],
        'user_id': sub2['user_id'],
        'question_id': sub2['question_id'],
        'code': sub2['code'],
        'similarity_score': sub2['similarity_score'],
        'submitted_at': sub2['submitted_at'],
        'username': sub2['username'],
        'question_title': sub2['question_title']
    }
    
    # Calculate detailed comparison
    similarity = calculate_similarity(sub1_dict['code'], sub2_dict['code'])
    comparison = compare_codes_detailed(sub1_dict['code'], sub2_dict['code'])
    
    return render_template('compare_codes.html', 
                         sub1=sub1_dict, sub2=sub2_dict, 
                         similarity=similarity, 
                         comparison=comparison)

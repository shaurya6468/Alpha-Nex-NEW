"""
Alpha Nex Routes with Replit Authentication
"""
import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from app import app, db
from models import User, Upload, Review, Strike, WithdrawalRequest, AdminAction, Rating
from forms import UploadForm, ReviewForm, RatingForm
# Removed Replit-specific authentication for external deployment

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page - redirects directly to dashboard for demo"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard for demo users"""
    # Create or get demo user
    demo_user = User.query.filter_by(email='demo@alphanex.com').first()
    if not demo_user:
        demo_user = User(
            id=str(uuid.uuid4()),
            email='demo@alphanex.com',
            first_name='Demo',
            last_name='User',
            xp_points=500
        )
        db.session.add(demo_user)
        db.session.commit()
    user = demo_user
    user.reset_daily_counters_if_needed()
    
    # Get user stats
    total_uploads = Upload.query.filter_by(user_id=user.id).count()
    total_reviews = Review.query.filter_by(reviewer_id=user.id).count()
    pending_reviews = Upload.query.filter(
        Upload.user_id != user.id,
        ~Upload.id.in_(db.session.query(Review.upload_id).filter_by(reviewer_id=user.id))
    ).count()
    
    # Get recent uploads
    recent_uploads = Upload.query.filter_by(user_id=user.id).order_by(Upload.uploaded_at.desc()).limit(5).all()
    
    # Calculate daily remaining MB
    daily_remaining_bytes = user.get_daily_upload_remaining()
    daily_remaining_mb = daily_remaining_bytes / (1024 * 1024)
    
    # Calculate remaining daily uploads and reviews
    max_daily_uploads = 999  # Unlimited
    max_daily_reviews = 999  # Unlimited
    daily_uploads_remaining = max_daily_uploads - (user.daily_upload_count or 0)
    daily_reviews_remaining = max_daily_reviews - (user.daily_review_count or 0)
    
    return render_template('dashboard.html', 
                         user=user,
                         current_user=user,
                         total_uploads=total_uploads,
                         total_reviews=total_reviews,
                         pending_reviews=pending_reviews,
                         recent_uploads=recent_uploads,
                         daily_remaining_mb=daily_remaining_mb,
                         daily_uploads_remaining=daily_uploads_remaining,
                         daily_reviews_remaining=daily_reviews_remaining)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """File upload page"""
    form = UploadForm()
    # Get demo user
    user = User.query.filter_by(email='demo@alphanex.com').first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email='demo@alphanex.com',
            first_name='Demo',
            last_name='User',
            xp_points=500
        )
        db.session.add(user)
        db.session.commit()
    user.reset_daily_counters_if_needed()
    
    if form.validate_on_submit():
        if not user.can_upload_today():
            flash('Daily upload limit reached (3 uploads per day). Try again tomorrow!', 'warning')
            return redirect(url_for('upload'))
        
        file = form.file.data
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer
        
        if not user.can_upload(file_size):
            flash('Upload failed. Check file size and daily limits.', 'error')
            return redirect(url_for('upload'))
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create upload record
        upload = Upload(
            user_id=user.id,
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            description=form.description.data,
            category=form.category.data,
            ai_consent=form.ai_consent.data
        )
        
        db.session.add(upload)
        
        # Update user stats
        user.daily_upload_count += 1
        user.daily_upload_bytes += file_size
        user.xp_points += 25  # XP for upload
        
        db.session.commit()
        
        flash(f'File uploaded successfully! You earned 25 XP points.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('uploader/upload.html', form=form, user=user, current_user=user)

@app.route('/review')
def review():
    """Content review page"""
    user = User.query.filter_by(email='demo@alphanex.com').first()
    user.reset_daily_counters_if_needed()
    
    if not user.can_review_today():
        flash('Daily review limit reached (5 reviews per day). Try again tomorrow!', 'warning')
        return redirect(url_for('dashboard'))
    
    # Get uploads that user hasn't reviewed yet (excluding their own)
    reviewed_upload_ids = db.session.query(Review.upload_id).filter_by(reviewer_id=user.id).subquery()
    upload = Upload.query.filter(
        Upload.user_id != user.id,
        ~Upload.id.in_(reviewed_upload_ids)
    ).order_by(Upload.uploaded_at.asc()).first()
    
    if not upload:
        flash('No uploads available for review at the moment.', 'info')
        return redirect(url_for('dashboard'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        # Create review
        review = Review()
        review.upload_id = upload.id
        review.reviewer_id = user.id
        review.rating = form.rating.data
        review.description = form.description.data
        review.xp_earned = 15
        
        db.session.add(review)
        
        # Update user stats
        user.daily_review_count += 1
        user.xp_points += 15  # XP for review
        
        db.session.commit()
        
        flash(f'Review submitted successfully! You earned 15 XP points.', 'success')
        return redirect(url_for('review'))
    
    return render_template('reviewer/review.html', form=form, upload=upload, user=user, current_user=user)

@app.route('/profile')
def profile():
    """User profile page"""
    user = User.query.filter_by(email='demo@alphanex.com').first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email='demo@alphanex.com',
            first_name='Demo',
            last_name='User',
            xp_points=500
        )
        db.session.add(user)
        db.session.commit()
    user.reset_daily_counters_if_needed()
    
    # Get user statistics
    total_uploads = Upload.query.filter_by(user_id=user.id).count()
    total_reviews = Review.query.filter_by(reviewer_id=user.id).count()
    user_strikes = Strike.query.filter_by(user_id=user.id).all()
    
    return render_template('profile.html', 
                         user=user,
                         total_uploads=total_uploads,
                         total_reviews=total_reviews,
                         user_strikes=user_strikes)

@app.route('/admin')

def admin():
    """Admin panel (demo access for all users)"""
    # Get platform statistics
    total_users = User.query.count()
    total_uploads = Upload.query.count()
    total_reviews = Review.query.count()
    pending_uploads = Upload.query.filter_by(status='pending').count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_uploads = Upload.query.order_by(Upload.uploaded_at.desc()).limit(10).all()
    
    return render_template('admin/admin.html',
                         total_users=total_users,
                         total_uploads=total_uploads,
                         total_reviews=total_reviews,
                         pending_uploads=pending_uploads,
                         recent_users=recent_users,
                         recent_uploads=recent_uploads,
                         user=user)

@app.route('/rating', methods=['GET', 'POST'])

def rating():
    """Platform rating and feedback page"""
    form = RatingForm()
    
    if form.validate_on_submit():
        rating_obj = Rating()
        rating_obj.user_id = user.id
        rating_obj.rating = form.rating.data
        rating_obj.category = form.category.data
        rating_obj.description = form.description.data
        rating_obj.contact_email = form.contact_email.data
        
        db.session.add(rating_obj)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('rating.html', form=form, user=user)

@app.route('/delete_upload/<int:upload_id>', methods=['POST'])

def delete_upload(upload_id):
    """Delete user's own upload"""
    upload = Upload.query.filter_by(id=upload_id, user_id=user.id).first_or_404()
    
    # Calculate penalty if past deadline
    penalty = upload.get_deletion_penalty()
    if penalty > 0:
        user.xp_points = max(0, user.xp_points - penalty)
        flash(f'Upload deleted with {penalty} XP penalty for late deletion.', 'warning')
    else:
        flash('Upload deleted successfully.', 'success')
    
    # Delete file and database record
    try:
        if os.path.exists(upload.file_path):
            os.remove(upload.file_path)
    except Exception:
        pass  # Continue even if file deletion fails
    
    db.session.delete(upload)
    db.session.commit()
    
    return redirect(url_for('dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403
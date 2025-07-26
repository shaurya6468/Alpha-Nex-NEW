import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Upload, Review
from forms import LoginForm, RegistrationForm, UploadForm, ReviewForm

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx',
    'ppt', 'pptx', 'mp3', 'wav', 'mp4', 'avi', 'mov', 'py', 'js', 'html',
    'css', 'json', 'xml', 'zip', 'rar', 'tar', 'gz'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('auth/signup.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('auth/signup.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            xp_points=100  # Starting XP points
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user statistics
    total_uploads = Upload.query.filter_by(user_id=current_user.id).count()
    total_reviews = Review.query.filter_by(reviewer_id=current_user.id).count()
    
    # Get recent uploads
    recent_uploads = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.uploaded_at.desc()).limit(5).all()
    
    # Count uploads available for review (not by current user)
    available_reviews = Upload.query.filter(
        Upload.user_id != current_user.id,
        ~Upload.id.in_(db.session.query(Review.upload_id).filter_by(reviewer_id=current_user.id))
    ).count()
    
    return render_template('dashboard.html', 
                         user=current_user,
                         total_uploads=total_uploads,
                         total_reviews=total_reviews,
                         recent_uploads=recent_uploads,
                         available_reviews=available_reviews)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """File upload"""
    form = UploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        if file and allowed_file(file.filename):
            # Generate secure filename
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{original_filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Save file
            file.save(filepath)
            
            # Create upload record
            upload = Upload(
                user_id=current_user.id,
                filename=filename,
                original_filename=original_filename,
                file_size=os.path.getsize(filepath),
                file_type=file.content_type or 'unknown',
                description=form.description.data,
                category=form.category.data
            )
            
            db.session.add(upload)
            
            # Award XP points for upload
            current_user.xp_points += 10
            db.session.commit()
            
            flash(f'File uploaded successfully! You earned 10 XP points.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type. Please upload a supported file.', 'error')
    
    return render_template('uploader/upload.html', form=form)

@app.route('/review')
@login_required
def review():
    """Review uploads"""
    # Get uploads that haven't been reviewed by current user
    uploads_to_review = Upload.query.filter(
        Upload.user_id != current_user.id,
        ~Upload.id.in_(db.session.query(Review.upload_id).filter_by(reviewer_id=current_user.id))
    ).order_by(Upload.uploaded_at.desc()).limit(10).all()
    
    return render_template('reviewer/review.html', uploads=uploads_to_review)

@app.route('/review/<int:upload_id>', methods=['GET', 'POST'])
@login_required
def review_upload(upload_id):
    """Review specific upload"""
    upload = Upload.query.get_or_404(upload_id)
    
    # Check if user can review this upload
    if upload.user_id == current_user.id:
        flash('You cannot review your own uploads.', 'error')
        return redirect(url_for('review'))
    
    # Check if already reviewed
    existing_review = Review.query.filter_by(upload_id=upload_id, reviewer_id=current_user.id).first()
    if existing_review:
        flash('You have already reviewed this upload.', 'info')
        return redirect(url_for('review'))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Create review
        review = Review(
            upload_id=upload_id,
            reviewer_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        db.session.add(review)
        
        # Award XP points for review
        current_user.xp_points += 5
        db.session.commit()
        
        flash(f'Review submitted successfully! You earned 5 XP points.', 'success')
        return redirect(url_for('review'))
    
    return render_template('reviewer/review_upload.html', upload=upload, form=form)

@app.route('/profile')
@login_required
def profile():
    """User profile"""
    user_uploads = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.uploaded_at.desc()).all()
    user_reviews = Review.query.filter_by(reviewer_id=current_user.id).order_by(Review.reviewed_at.desc()).all()
    
    return render_template('profile.html', 
                         user=current_user,
                         uploads=user_uploads,
                         reviews=user_reviews)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
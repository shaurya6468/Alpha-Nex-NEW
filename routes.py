"""
Simplified Alpha Nex Routes - Direct Access Without Demo User System
"""
import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Upload, Review, Strike, WithdrawalRequest, AdminAction, Rating
from forms import UploadForm, ReviewForm, RatingForm
# from openai_service import analyze_content_quality  # Not needed for simplified version

# Create a single static user for all operations
STATIC_USER_ID = 1

def get_or_create_static_user():
    """Get or create the single static user for the platform with fresh experience"""
    user = User.query.get(STATIC_USER_ID)
    if not user:
        user = User()
        user.id = STATIC_USER_ID
        user.username = 'platform_user'
        user.name = 'Platform User'
        user.email = 'user@alphanex.com'
        user.password_hash = generate_password_hash('alphanex123')
        user.xp_points = 500
        user.daily_upload_count = 0
        user.daily_upload_bytes = 0
        user.daily_review_count = 0
        user.daily_upload_reset = datetime.utcnow()
        user.daily_review_reset = datetime.utcnow()
        db.session.add(user)
        
        # Create test files for review
        create_test_content()
        
        db.session.commit()
    else:
        # Reset user experience for fresh start every time
        reset_user_experience(user)
    
    return user

def reset_user_experience(user):
    """Reset user's daily limits and usage for fresh experience"""
    try:
        # Reset daily limits and usage
        user.daily_upload_count = 0
        user.daily_upload_bytes = 0
        user.daily_review_count = 0
        user.daily_upload_reset = datetime.utcnow()
        user.daily_review_reset = datetime.utcnow()
        
        # Clear user's uploads to give fresh experience
        user_uploads = Upload.query.filter_by(user_id=user.id).all()
        for upload in user_uploads:
            db.session.delete(upload)
        
        # Clear user's reviews to reset review experience
        user_reviews = Review.query.filter_by(reviewer_id=user.id).all()
        for review in user_reviews:
            db.session.delete(review)
        
        # Reset XP to starting value for consistent experience
        user.xp_points = 500
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error resetting user experience: {e}")
        # Continue even if reset fails

def create_test_content():
    """Create sample content for review system"""
    test_files = [
        {
            'filename': 'sample_audio_podcast.mp3',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Tech Podcast Episode',
            'file_size': 8388608,  # 8MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Technology podcast discussion about AI trends and future innovations',
            'category': 'audio'
        },
        {
            'filename': 'sample_music.mp3',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Background Music Track',
            'file_size': 5242880,  # 5MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Instrumental background music for content creation',
            'category': 'audio'
        },
        {
            'filename': 'research_paper.pdf',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - AI Research Paper',
            'file_size': 2097152,  # 2MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Academic research paper on machine learning applications in healthcare',
            'category': 'document'
        },
        {
            'filename': 'tutorial_guide.pdf',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Programming Tutorial',
            'file_size': 3145728,  # 3MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Comprehensive programming tutorial for Python beginners',
            'category': 'document'
        },
        {
            'filename': 'data_analysis.py',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Python Data Analysis Script',
            'file_size': 524288,  # 512KB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Python script for data analysis and visualization using pandas',
            'category': 'code'
        },
        {
            'filename': 'web_scraper.js',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - JavaScript Web Scraper',
            'file_size': 262144,  # 256KB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - JavaScript web scraping tool for data collection',
            'category': 'code'
        },
        {
            'filename': 'project_notes.txt',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Project Documentation',
            'file_size': 131072,  # 128KB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Detailed project notes and development documentation',
            'category': 'text'
        },
        {
            'filename': 'meeting_minutes.txt',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Team Meeting Notes',
            'file_size': 65536,  # 64KB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Minutes from team meetings and project discussions',
            'category': 'text'
        },
        {
            'filename': 'logo_design.png',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Company Logo Design',
            'file_size': 1048576,  # 1MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Professional logo design for branding purposes',
            'category': 'image'
        },
        {
            'filename': 'infographic.jpg',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Data Infographic',
            'file_size': 2097152,  # 2MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Visual data representation and statistics infographic',
            'category': 'image'
        },
        {
            'filename': 'website_mockup.png',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Website Mockup',
            'file_size': 1572864,  # 1.5MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - UI/UX design mockup for web application',
            'category': 'image'
        },
        {
            'filename': 'source_code.zip',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Source Code Archive',
            'file_size': 4194304,  # 4MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Complete source code archive for web application project',
            'category': 'archive'
        },
        {
            'filename': 'assets_pack.zip',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Design Assets Pack',
            'file_size': 6291456,  # 6MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Collection of design assets including icons, fonts, and graphics',
            'category': 'archive'
        },
        {
            'filename': 'backup_files.tar.gz',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Project Backup',
            'file_size': 5242880,  # 5MB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Compressed backup of project files and database',
            'category': 'archive'
        },
        {
            'filename': 'documentation.md',
            'original_filename': '**DEMO FILE FOR TESTING PURPOSES ONLY** - API Documentation',
            'file_size': 327680,  # 320KB
            'description': '**DEMO FILE FOR TESTING PURPOSES ONLY** - Comprehensive API documentation with examples and usage guidelines',
            'category': 'text'
        }
    ]
    
    # Create a separate test user for these uploads
    test_user = User.query.get(2)
    if not test_user:
        test_user = User()
        test_user.id = 2
        test_user.username = 'test_content_user'
        test_user.name = 'Test Content User'
        test_user.email = 'testcontent@alphanex.com'
        test_user.password_hash = generate_password_hash('test123')
        test_user.xp_points = 300
        db.session.add(test_user)
        db.session.flush()
        
        for test_file in test_files:
            upload = Upload()
            upload.user_id = test_user.id
            upload.filename = test_file['filename']
            upload.original_filename = test_file['original_filename']
            upload.file_path = f"uploads/demo_{test_file['filename']}"
            upload.file_size = test_file['file_size']
            upload.description = test_file['description']
            upload.category = test_file['category']
            upload.status = 'pending'
            upload.ai_consent = True
            db.session.add(upload)

@app.route('/')
def index():
    """Landing page redirects to name entry"""
    return redirect(url_for('name_entry'))

@app.route('/name_entry', methods=['GET', 'POST'])
def name_entry():
    """Name entry page before dashboard"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name and len(name) >= 2 and len(name) <= 50 and name.replace(' ', '').isalpha():
            session['user_name'] = name
            
            # Reset user experience for fresh start
            user = get_or_create_static_user()
            reset_user_experience(user)
            
            return redirect(url_for('dashboard'))
        else:
            flash('Please enter a valid name (2-50 characters, letters and spaces only)', 'error')
    
    return render_template('name_entry.html')

@app.route('/health')
def health():
    """Health check endpoint for uptime monitoring"""
    try:
        # Test database connection
        from app import db
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return "OK", 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return "Database Error", 503

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    # Check if user has entered name
    if 'user_name' not in session:
        return redirect(url_for('name_entry'))
    
    try:
        user = get_or_create_static_user()
        user_name = session['user_name']
        
        # Get user stats
        upload_count = Upload.query.filter_by(user_id=user.id).count()
        review_count = Review.query.filter_by(reviewer_id=user.id).count()
        
        # Get recent uploads
        recent_uploads = Upload.query.filter_by(user_id=user.id)\
                                    .order_by(Upload.uploaded_at.desc()).limit(5).all()
        
        # Calculate daily remaining
        daily_remaining = user.get_daily_upload_remaining()
        daily_remaining_mb = daily_remaining / (1024 * 1024)
        
        # Generate motivational messages based on user progress
        import random
        
        # Welcome messages with motivation
        welcome_messages = [
            f"🌟 Welcome back {user_name}! Ready to earn more XP?",
            f"🚀 Hey {user_name}! Time to create amazing content!",
            f"⭐ Great to see you {user_name}! Let's make today productive!",
            f"💪 {user_name}, you're doing fantastic! Keep it up!",
            f"🔥 Welcome {user_name}! Your contributions make a difference!",
            f"✨ Hello {user_name}! Ready to level up today?",
            f"🎯 {user_name}, you're on the right path to success!"
        ]
        
        # Milestone celebration messages
        milestone_messages = []
        if user.xp_points >= 100:
            milestone_messages.append("🎉 Amazing! You've reached 100+ XP points!")
        if user.xp_points >= 500:
            milestone_messages.append("🏆 Incredible! 500+ XP points achieved!")
        if upload_count >= 5:
            milestone_messages.append("📁 Fantastic! You've uploaded 5+ files!")
        if review_count >= 10:
            milestone_messages.append("👀 Outstanding! 10+ reviews completed!")
        
        # Daily progress motivation
        remaining_uploads = user.get_remaining_uploads_today()
        remaining_reviews = user.get_remaining_reviews_today()
        
        daily_motivation = []
        if remaining_uploads > 0:
            daily_motivation.append(f"💡 You can still upload {remaining_uploads} more files today!")
        if remaining_reviews > 0:
            daily_motivation.append(f"🔍 {remaining_reviews} reviews remaining - help the community!")
        
        return render_template('dashboard.html', 
                             upload_count=upload_count,
                             review_count=review_count,
                             recent_uploads=recent_uploads,
                             daily_remaining_mb=daily_remaining_mb,
                             demo_user=user,
                             current_user=user,
                             user_name=user_name,
                             xp_threshold_reached=False,
                             welcome_message=random.choice(welcome_messages),
                             milestone_message=" ".join(milestone_messages),
                             daily_limit_message=" ".join(daily_motivation))
                             
    except Exception as e:
        app.logger.error(f"Dashboard error: {e}")
        return render_template('error.html', error=f"Dashboard error: {str(e)}")

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """File upload endpoint"""
    try:
        user = get_or_create_static_user()
        form = UploadForm()
        
        if form.validate_on_submit():
            file = form.file.data
            if file and file.filename:
                # Check daily upload limit
                if not user.can_upload_today():
                    flash('Daily upload limit reached! Try again tomorrow.', 'warning')
                    return redirect(url_for('dashboard'))
                
                # Process file upload
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                upload_folder = 'uploads'
                file_path = os.path.join(upload_folder, unique_filename)
                
                # Ensure upload directory exists
                os.makedirs(upload_folder, exist_ok=True)
                
                # Save file
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                
                # Check file size limit (100MB)
                if file_size > 100 * 1024 * 1024:
                    os.remove(file_path)
                    flash('File too large! Maximum size is 100MB.', 'error')
                    return redirect(url_for('upload_file'))
                
                # Create upload record
                upload = Upload()
                upload.user_id = user.id
                upload.filename = unique_filename
                upload.original_filename = filename
                upload.file_path = file_path
                upload.file_size = file_size
                upload.description = form.description.data
                upload.category = form.category.data
                upload.status = 'pending'
                upload.ai_consent = form.ai_consent.data
                
                # Update user stats
                user.xp_points += 20  # Upload XP
                user.daily_upload_count += 1
                user.daily_upload_bytes += file_size
                
                db.session.add(upload)
                db.session.commit()
                
                motivational_messages = [
                    "🎉 Awesome upload! You're contributing amazing content!",
                    "⭐ Fantastic! Your upload earned you 20 XP points!",
                    "🚀 Great job! Keep sharing quality content!",
                    "💪 Excellent upload! You're making the platform better!",
                    "🌟 Outstanding work! 20 XP points added to your account!",
                    "🔥 Amazing content! You're a content creation superstar!",
                    "✨ Perfect upload! Your contribution is valuable!"
                ]
                import random
                flash(random.choice(motivational_messages), 'success')
                return redirect(url_for('dashboard'))
        
        # Calculate remaining daily upload capacity
        daily_remaining = user.get_daily_upload_remaining()
        daily_remaining_mb = daily_remaining / (1024 * 1024)
        
        return render_template('uploader/upload.html', 
                             form=form, 
                             daily_remaining_mb=daily_remaining_mb, 
                             demo_user=user,
                             current_user=user)
                             
    except Exception as e:
        app.logger.error(f"Upload error: {e}")
        return render_template('error.html', error=f"Upload error: {str(e)}")

@app.route('/review')
def review_content():
    """Content review page"""
    try:
        user = get_or_create_static_user()
        
        # Get uploads that need review (not from current user and not already reviewed)
        reviewed_upload_ids = [r.upload_id for r in Review.query.filter_by(reviewer_id=user.id).all()]
        
        uploads = Upload.query.filter(
            Upload.user_id != user.id,  # Cannot review own uploads
            ~Upload.id.in_(reviewed_upload_ids)  # Haven't reviewed yet
        ).order_by(Upload.uploaded_at.desc()).all()
        
        # Filter out uploads that already have 5 reviews
        available_uploads = []
        for upload in uploads:
            review_count = Review.query.filter_by(upload_id=upload.id).count()
            if review_count < 5:  # Max 5 reviews per upload
                available_uploads.append(upload)
        
        return render_template('reviewer/review.html', 
                             uploads=available_uploads, 
                             demo_user=user,
                             current_user=user)
                             
    except Exception as e:
        app.logger.error(f"Review error: {e}")
        return render_template('error.html', error=f"Review error: {str(e)}")

@app.route('/review/<int:upload_id>', methods=['GET', 'POST'])
def review_upload(upload_id):
    """Review a specific upload"""
    try:
        user = get_or_create_static_user()
        upload = Upload.query.get_or_404(upload_id)
        form = ReviewForm()
        
        if form.validate_on_submit():
            # Check if user already reviewed this upload
            existing_review = Review.query.filter_by(upload_id=upload_id, reviewer_id=user.id).first()
            if existing_review:
                flash('You have already reviewed this upload.', 'warning')
                return redirect(url_for('review_content'))
            
            # Create review
            review = Review()
            review.upload_id = upload_id
            review.reviewer_id = user.id
            review.rating = form.rating.data
            review.description = form.description.data
            review.xp_earned = 15  # Review XP
            
            # Update user stats
            user.xp_points += 15
            user.daily_review_count += 1
            
            db.session.add(review)
            db.session.commit()
            
            motivational_messages = [
                "🎉 Amazing review! You're helping make the platform better!",
                "⭐ Great job! Your insights are valuable to our community!",
                "🚀 Fantastic review! You're on fire today!",
                "💪 Excellent work! Keep up the great reviewing!",
                "🌟 Outstanding review! You earned 15 XP points!",
                "🔥 Brilliant analysis! You're a reviewing superstar!",
                "✨ Perfect review! Your feedback makes a difference!"
            ]
            import random
            flash(random.choice(motivational_messages), 'success')
            return redirect(url_for('review_content'))
        
        # Get existing reviews for this upload
        existing_reviews = Review.query.filter_by(upload_id=upload_id).all()
        
        return render_template('reviewer/review_upload.html', 
                             upload=upload, 
                             form=form,
                             existing_reviews=existing_reviews, 
                             review_count=len(existing_reviews), 
                             demo_user=user,
                             current_user=user)
                             
    except Exception as e:
        app.logger.error(f"Review upload error: {e}")
        return render_template('error.html', error=f"Review upload error: {str(e)}")

@app.route('/profile')
def profile():
    """User profile page"""
    try:
        user = get_or_create_static_user()
        
        # Get user's strikes and violation history
        strikes = Strike.query.filter_by(user_id=user.id)\
                             .order_by(Strike.created_at.desc()).all()
        
        return render_template('profile.html', 
                             current_user=user,
                             demo_user=user,
                             strikes=strikes)
                             
    except Exception as e:
        app.logger.error(f"Profile error: {e}")
        return render_template('error.html', error=f"Profile error: {str(e)}")

@app.route('/admin')
def admin_panel():
    """Admin panel page"""
    try:
        user = get_or_create_static_user()
        
        # Get all users
        all_users = User.query.order_by(User.created_at.desc()).all()
        
        # Get recent uploads
        recent_uploads = Upload.query.order_by(Upload.uploaded_at.desc()).limit(10).all()
        
        # Get recent reviews
        recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(10).all()
        
        return render_template('admin/panel.html',
                             users=all_users,
                             recent_uploads=recent_uploads,
                             recent_reviews=recent_reviews,
                             demo_user=user,
                             current_user=user)
                             
    except Exception as e:
        app.logger.error(f"Admin error: {e}")
        return render_template('error.html', error=f"Admin error: {str(e)}")

@app.route('/rating', methods=['GET', 'POST'])
def rate_website():
    """Website rating and feedback page"""
    try:
        user = get_or_create_static_user()
        form = RatingForm()
        
        if form.validate_on_submit():
            # Create rating record
            rating = Rating()
            rating.user_id = user.id
            rating.rating = form.rating.data
            rating.category = form.category.data
            rating.description = form.description.data
            rating.contact_email = form.contact_email.data if form.contact_email.data else None
            
            db.session.add(rating)
            db.session.commit()
            
            flash('Thank you for your feedback! Your rating has been submitted.', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('rating.html', 
                             form=form,
                             demo_user=user,
                             current_user=user)
                             
    except Exception as e:
        app.logger.error(f"Rating error: {e}")
        return render_template('error.html', error=f"Rating error: {str(e)}")

@app.route('/delete_upload/<int:upload_id>')
def delete_upload(upload_id):
    """Delete an upload"""
    try:
        user = get_or_create_static_user()
        upload = Upload.query.get_or_404(upload_id)
        
        # Check if user owns this upload
        if upload.user_id != user.id:
            flash('You can only delete your own uploads.', 'error')
            return redirect(url_for('dashboard'))
        
        # Delete file from filesystem
        if os.path.exists(upload.file_path):
            os.remove(upload.file_path)
        
        # Delete reviews for this upload
        Review.query.filter_by(upload_id=upload_id).delete()
        
        # Delete upload record
        db.session.delete(upload)
        db.session.commit()
        
        flash('Upload deleted successfully.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        app.logger.error(f"Delete upload error: {e}")
        flash('Error deleting upload.', 'error')
        return redirect(url_for('dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500
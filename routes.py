from flask import render_template, request, redirect, url_for, flash
from app import app, db
from models import Content

@app.route('/')
def index():
    contents = Content.query.order_by(Content.created_at.desc()).all()
    return render_template('index.html', contents=contents)

@app.route('/add', methods=['GET', 'POST'])
def add_content():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        
        if title and description and category:
            content = Content(title=title, description=description, category=category)
            db.session.add(content)
            db.session.commit()
            flash('Content added successfully!')
            return redirect(url_for('index'))
        else:
            flash('Please fill all fields')
    
    return render_template('add.html')

@app.route('/view/<int:id>')
def view_content(id):
    content = Content.query.get_or_404(id)
    return render_template('view.html', content=content)
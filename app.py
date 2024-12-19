from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import openai
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Set your OpenAI API key here
openai.api_key = 'api_key'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    membership = db.Column(db.String(50), nullable=False, default='Basic')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        keywords = request.form['keywords']
        if current_user.membership == 'Basic':
            max_images = 2
        elif current_user.membership == 'Premium':
            max_images = 5
        elif current_user.membership == 'Pro':
            max_images = 10
        else:
            max_images = 1

        images = generate_tattoo_design(keywords, max_images)
        return render_template('result.html', images=images, keywords=keywords)
    return render_template('generate.html')

@app.route('/update_membership', methods=['POST'])
@login_required
def update_membership():
    membership = request.form['membership']
    current_user.membership = membership
    db.session.commit()
    flash('Membership updated successfully!', 'success')
    return redirect(url_for('index'))

def generate_tattoo_design(keywords, max_images):
    response = openai.Image.create(
        prompt=keywords,
        n=max_images,
        size="512x512"
    )
    images = [data['url'] for data in response['data']]
    return images


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

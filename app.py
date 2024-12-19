from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Inventory Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Routes
@app.route('/')
def index():
    # Debugging session
    print("Session User ID:", session.get('user_id'))
    if 'user_id' in session:
        inventory = Inventory.query.all()
        # Debugging database query
        print("Fetched Inventory:", inventory)
        return render_template('inventory.html', inventory=inventory)
    flash('Please log in to access the inventory.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_item', methods=['POST'])
def add_item():
    if 'user_id' in session:
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        item = Inventory(item_name=item_name, quantity=quantity)
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully.', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/delete_item/<int:id>')
def delete_item(id):
    if 'user_id' in session:
        item = Inventory.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully.', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Add dummy data route for testing
@app.route('/add_dummy_data')
def add_dummy_data():
    item1 = Inventory(item_name="Laptop", quantity=5)
    item2 = Inventory(item_name="Monitor", quantity=10)
    db.session.add_all([item1, item2])
    db.session.commit()
    return "Dummy data added!"


if __name__ == '__main__':
    with app.app_context():  # Create an application context
        db.create_all()      # Ensure database tables are created
    app.run(debug=True)


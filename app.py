import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# In-memory storage for dog walks
dog_walks = []

# Data validation function
def validate_walk_data(data):
    errors = []
    
    # Check for required fields
    if not data.get('dog_name'):
        errors.append("Dog name is required")
    
    # Validate walk duration (should be positive number)
    try:
        duration = float(data.get('duration', 0))
        if duration <= 0:
            errors.append("Duration must be a positive number")
    except ValueError:
        errors.append("Duration must be a valid number")
        
    # Validate distance (should be positive number)
    try:
        distance = float(data.get('distance', 0))
        if distance < 0:
            errors.append("Distance must be a non-negative number")
    except ValueError:
        errors.append("Distance must be a valid number")
    
    return errors

# API Routes
@app.route('/api/walks', methods=['POST'])
def add_walk():
    """
    Add a new dog walk record
    ---
    parameters:
      - name: dog_name
        in: formData
        type: string
        required: true
        description: Name of the dog
      - name: duration
        in: formData
        type: number
        required: true
        description: Duration of walk in minutes
      - name: distance
        in: formData
        type: number
        required: true
        description: Distance walked in miles/kilometers
      - name: notes
        in: formData
        type: string
        required: false
        description: Additional notes about the walk
    responses:
      201:
        description: Walk record created successfully
      400:
        description: Invalid input data
    """
    # Get data from request
    if request.is_json:
        data = request.json
    else:
        data = request.form.to_dict()
    
    # Validate the data
    errors = validate_walk_data(data)
    if errors:
        if request.is_json:
            return jsonify({"errors": errors}), 400
        else:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('index'))
    
    # Create walk record
    walk = {
        'id': len(dog_walks) + 1,
        'dog_name': data.get('dog_name'),
        'duration': float(data.get('duration')),
        'distance': float(data.get('distance')),
        'notes': data.get('notes', ''),
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to storage
    dog_walks.append(walk)
    
    # Return response based on request type
    if request.is_json:
        return jsonify({"message": "Walk record added successfully", "walk": walk}), 201
    else:
        flash('Dog walk recorded successfully!', 'success')
        return redirect(url_for('list_walks'))

@app.route('/api/walks', methods=['GET'])
def get_walks():
    """
    Get all dog walk records
    ---
    responses:
      200:
        description: List of all dog walks
    """
    if request.is_json:
        return jsonify(dog_walks)
    else:
        return redirect(url_for('list_walks'))

@app.route('/api/walks/<int:walk_id>', methods=['GET'])
def get_walk(walk_id):
    """
    Get a specific dog walk record
    ---
    parameters:
      - name: walk_id
        in: path
        type: integer
        required: true
        description: ID of the walk record
    responses:
      200:
        description: Walk record details
      404:
        description: Walk record not found
    """
    # Find the walk by ID
    walk = next((w for w in dog_walks if w['id'] == walk_id), None)
    
    if walk:
        return jsonify(walk)
    else:
        return jsonify({"error": "Walk record not found"}), 404

# Web Routes for UI
@app.route('/')
def index():
    """Render the homepage with form to add walks"""
    return render_template('index.html')

@app.route('/walks')
def list_walks():
    """Show all recorded walks"""
    return render_template('walks.html', walks=dog_walks)

# Add sample data for demonstration
@app.route('/api/sample-data', methods=['POST'])
def add_sample_data():
    """Add sample data for demonstration purposes"""
    sample_walks = [
        {
            'id': 1,
            'dog_name': 'Buddy',
            'duration': 30.0,
            'distance': 1.5,
            'notes': 'Morning walk in the park',
            'timestamp': '2023-10-01T08:30:00'
        },
        {
            'id': 2,
            'dog_name': 'Max',
            'duration': 45.0,
            'distance': 2.0,
            'notes': 'Evening walk along the river',
            'timestamp': '2023-10-01T18:00:00'
        }
    ]
    
    global dog_walks
    dog_walks = sample_walks
    
    flash('Sample data added successfully!', 'success')
    return redirect(url_for('list_walks'))

@app.route('/api/quick-add', methods=['GET'])
def quick_add_walk():
    """
    Quick add a dog walk with default values (for demonstration and testing)
    ---
    responses:
      201:
        description: Walk record created successfully
    """
    # Create a default walk
    walk = {
        'id': len(dog_walks) + 1,
        'dog_name': f"TestDog-{len(dog_walks) + 1}",
        'duration': 15.0,
        'distance': 1.0,
        'notes': f"Quick added walk at {datetime.now().strftime('%H:%M:%S')}",
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to storage
    dog_walks.append(walk)
    
    # Handle different content types
    if request.is_json:
        return jsonify({"message": "Quick walk added successfully", "walk": walk}), 201
    else:
        flash('Quick dog walk added successfully!', 'success')
        return redirect(url_for('list_walks'))

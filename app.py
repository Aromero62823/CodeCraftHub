from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'courses.json'

# Function to load courses from the JSON file
def load_courses():
    if not os.path.exists(DATA_FILE):
        # Create the file with an empty list if it doesn't exist
        save_courses([])
        return []
    
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

# Function to save courses to the JSON file
def save_courses(courses):
    with open(DATA_FILE, 'w') as file:
        json.dump(courses, file, indent=4)

# Route to get all courses
@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Retrieve all courses."""
    courses = load_courses()
    return jsonify(courses)

# Route to get a specific course by ID
@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Retrieve a specific course by ID."""
    courses = load_courses()
    course = next((course for course in courses if course['id'] == course_id), None)
    if course is None:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(course)

# Route to add a new course
@app.route('/api/courses', methods=['POST'])
def create_course():
    """Add a new course."""
    new_course = request.get_json()
    
    # Check for required fields
    if not all(k in new_course for k in ('name', 'description', 'target_date', 'status')):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate status
    valid_statuses = ["Not Started", "In Progress", "Completed"]
    if new_course['status'] not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}."}), 400
    
    # Load existing courses and assign an ID
    courses = load_courses()
    new_course['id'] = len(courses) + 1  # Auto-generate ID
    new_course['created_at'] = datetime.now().isoformat()  # Set created timestamp
    courses.append(new_course)
    
    # Save updated courses
    save_courses(courses)
    return jsonify(new_course), 201

# Route to update an existing course
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update an existing course by ID."""
    updated_data = request.get_json()
    courses = load_courses()
    
    course = next((course for course in courses if course['id'] == course_id), None)
    if course is None:
        return jsonify({"error": "Course not found"}), 404
    
    # Update only if the field is present in request
    if 'name' in updated_data:
        course['name'] = updated_data['name']
    if 'description' in updated_data:
        course['description'] = updated_data['description']
    if 'target_date' in updated_data:
        course['target_date'] = updated_data['target_date']
    if 'status' in updated_data:
        valid_statuses = ["Not Started", "In Progress", "Completed"]
        if updated_data['status'] not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}."}), 400
        course['status'] = updated_data['status']
    
    # Save updated courses
    save_courses(courses)
    return jsonify(course)

# Route to delete a course by ID
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course by ID."""
    courses = load_courses()
    updated_courses = [course for course in courses if course['id'] != course_id]
    
    if len(updated_courses) == len(courses):
        return jsonify({"error": "Course not found"}), 404
    
    # Save updated courses without the deleted one
    save_courses(updated_courses)
    return jsonify({"message": "Course deleted successfully"}), 204

if __name__ == '__main__':
    app.run(debug=True)
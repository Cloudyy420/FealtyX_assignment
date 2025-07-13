from flask import Flask , request , jsonify
import requests
import threading

app = Flask(__name__)

students = [{"id":1, "name":"John", "age":20, "email":"john@gmail.com"}]
students_lock = threading.Lock()

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:latest"

# Function to generate student summary using Ollama
def generate_student_summary(student):
    try:
        prompt = f"""
        Generate a brief, friendly summary for this student:
        Name: {student['name']}
        Age: {student['age']}
        Email: {student['email']}
        
        Please provide a 1-2 sentence summary that describes this student in a positive way.
        """
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Summary not available')
        else:
            return "Summary generation failed"
            
    except requests.exceptions.RequestException:
        return "Ollama service unavailable"
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Input validation function
def validate_student_data(data):
    # Check if all required fields are present
    required_fields = ['name', 'age', 'email']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate name is not empty
    if not data['name'] or not data['name'].strip():
        return False, "Name cannot be empty"
    
    # Validate age is a positive integer
    try:
        age = int(data['age'])
        if age <= 0:
            return False, "Age must be a positive integer"
    except (ValueError, TypeError):
        return False, "Age must be a valid integer"
    
    # Validate email format (basic validation)
    email = data['email']
    if not email or '@' not in email or '.' not in email:
        return False, "Invalid email format"
    
    return True, "Valid"

#creating a student entry
@app.route('/students', methods=['POST'])
def create_student():
    if not request.is_json:
        return {"Error": "Content-Type must be application/json"}, 400
    is_valid, message = validate_student_data(request.json)
    if not is_valid:
        return {"Error": message}, 400
    with students_lock:
        new_student = {"id":len(students)+1,
                       "name":request.json["name"],
                       "age":request.json["age"],
                       "email":request.json["email"]
                       }
        students.append(new_student)
    return new_student

#get all students
@app.route('/students',methods=['GET'])
def get_students():
    with students_lock:
        return list(students)

#get a student by id
@app.route('/students/<int:id_request>',methods=['GET'])
def get_student_id(id_request):
    with students_lock:
        for student in students:
            if student['id']==id_request:
                return student
    return {"Error": "Student id was not found"}

#get student summary by id
@app.route('/students/<int:id_request>/summary',methods=['GET'])
def get_student_summary(id_request):
    with students_lock:
        for student in students:
            if student['id']==id_request:
                summary = generate_student_summary(student)
                return {"student_id": id_request, "summary": summary}
    return {"Error": "Student id was not found"}

#update a student by id
@app.route('/students/<int:id_request>',methods=['PUT'])
def update_student(id_request):
    if not request.is_json:
        return {"Error": "Content-Type must be application/json"}, 400
    is_valid, message = validate_student_data(request.json)
    if not is_valid:
        return {"Error": message}, 400
    with students_lock:
        for student in students:
            if student['id']==id_request:
                student['name']=request.json["name"]
                student['age']=request.json["age"]
                student['email']=request.json["email"]
                return student
    return {"Error": "Student id was not found"}

#delete a student 
@app.route('/students/<int:id_request>',methods=['DELETE'])
def delete_student(id_request):
    with students_lock:
        for student in students:
            if student['id']==id_request:
                students.remove(student)
                return ("Student was deleted successfully")
    return {"Error": "Student id was not found"}


if __name__ == '__main__':
    app.run(debug=True)
    
    
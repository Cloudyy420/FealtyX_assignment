from flask import Flask , request , jsonify

app = Flask(__name__)


students = [{"id":1, "name":"John", "age":20, "email":"john@gmail.com"}]
#creating a student entry
@app.route('/students', methods=['POST'])
def create_student():
    new_student = {"id":len(students)+1,"name":request.json["name"],"age":request.json["age"],"email":request.json["email"]}
    students.append(new_student)
    return new_student

#get all students
@app.route('/students',methods=['GET'])
def get_students():
    return students

#get a student by id
@app.route('/students/<int:id_request>',methods=['GET'])
def get_student_id(id_request):
    for student in students:
        if student['id']==id_request:
            return student
    
    return {"Error": "Student id was not found"}

#update a student by id
@app.route('/students/<int:id_request>',methods=['PUT'])
def update_student(id_request):
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
    for student in students:
        if student['id']==id_request:
            students.remove(student)
            return ("Student was deleted successfully")
        
    return {"Error": "Student id was not found"}

''' basic crud is complete.
TODO: intigrate ollama, error handling, input validation, concurrency.
 
'''

if __name__ == '__main__':
    app.run(debug=True)
    
from flask import Flask, render_template, request, redirect, session, url_for
import json, os
from uuid import uuid4
from flask import send_from_directory


app = Flask(__name__)               #flask - create web applications
app.secret_key = 'super_secret_key' #Sets a secret key

USERS_FILE = 'database/users.json'  # JSON file storing user data.
TASKS_FILE = 'database/tasks.json'  #JSON file storing task data.


def load_data(file):
    if not os.path.exists(file):    #Checks if the file exists
        with open(file, 'w') as f:   # not - Creates it
            json.dump([], f)         #Writes an empty list
    with open(file, 'r') as f:       # opens the file in read mode and
        return json.load(f)          #  returns the parsed JSON data 


def save_data(file, data):              # save the data path  (user.json)   , actual data 
    with open(file, 'w') as f:          # opens the file in write mode , write data 
        json.dump(data, f, indent=4)   #automatically closed done writing   (with ... as f ) f -file object to write data
                                       # Indent =4 write data in json format with 4 spaces

@app.route('/images/<path:filename>')    # route of the image
def serve_image(filename):                
    return send_from_directory('images', filename)


@app.route('/login', methods=['GET', 'POST'])   # get - login page is loaded , post - login form is submitted
def login():                                    #login function - called submits the login page.
    if request.method == 'POST':                #Checks if the request was a POST request
        users = load_data(USERS_FILE)           # load the user data 
        for user in users:                       #Iterate through the list of users
            if user['id'] == request.form['id'] and user['password'] == request.form['password']:    # match then login successfully
                session['user'] = user                                      # users data is saved in the session.
                return redirect('/dashboard')                               # successful login - dashboard page is  loaded
        return render_template('login.html', error='Invalid credentials')  # invalid - error
    return render_template('login.html')                                    # return to login page

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        users = load_data(USERS_FILE)           # Load existing users from the file
        
                                                # Create a user dictionary 
        user = {
            'id': request.form['id'],
            'name': request.form['name'],
            'email': request.form['email'], 
            'phone': request.form['phone'],  
            'password': request.form['password'],
            'role': request.form['role']
        }
        
                                                # Add the new user to the list of users
        users.append(user)
                                                # Save the updated users data back to the file
        save_data(USERS_FILE, users)
                                                # Redirect to the login page
        return redirect('/login')
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:                                               # check user is login 
        return redirect('/login')                                           # return to login page

    user = session['user']                                                   # get the user data from the session
    tasks = load_data(TASKS_FILE)                                            # load the task data from the file
    users = load_data(USERS_FILE)                                            # load the user data from the file

    user_dict = {u['id']: u['name'] for u in users}                          #display names, IDs when showing who tasks are assigned to.

    for task in tasks:                                                          #Adds a new key assigned_to_name to each task.
        task['assigned_to_name'] = user_dict.get(task['assigned_to'], 'Unknown')  # in dict then assign task if not then unknown

    if user['role'] in ['Manager', 'Team Lead']:                              # Checks  role of the user
        return render_template('dashboard.html', user=user, tasks=tasks)  
    else:
        my_tasks = [t for t in tasks if t['assigned_to'] == user['id']]         #tasks assigned only to the current user
        return render_template('view_tasks.html', user=user, tasks=my_tasks)   # return to view task page



@app.route('/assign', methods=['GET', 'POST'])
def assign_task():
    if 'user' not in session or session['user']['role'] not in ['Manager', 'Team Lead']:  #check user login and role
        return redirect('/login')
    
    users = load_data(USERS_FILE)                                                    #load users data
    employees = [u for u in users if u['role'] == 'Employee']                        # filter employees from users data
    
    if request.method == 'POST':                                                    # check the rquest
        tasks = load_data(TASKS_FILE)                                               # load tasks data 
        task = {                                                                    # create a task dictionary                        
            'id': str(uuid4()),
            'title': request.form['title'],
            'description': request.form['description'],
            'assigned_to': request.form['assigned_to'],
            'deadline': request.form['deadline'],
            'status': 'Pending'
        }
        tasks.append(task)
        save_data(TASKS_FILE, tasks)
        return redirect('/dashboard')

    
    return render_template('assign_task.html', employees=employees)


@app.route('/update/<task_id>', methods=['POST'])                                  # update the task  ,task id - dynamic variable is a unique id                               
def update_task(task_id):                                                           #import -uuid4() built in module generates a random unique identifier
    tasks = load_data(TASKS_FILE)
    for task in tasks:                                                              #Iterate through the list of tasks    
        if task['id'] == task_id:                                                  # Compares the current task's ID with the task_id from the URL.
            task['status'] = request.form['status']                                 #Updates the task's status
            break                                                                   # stop when updating matching task 
    save_data(TASKS_FILE, tasks)
    return redirect('/dashboard')


@app.route('/logout')           # logout route
def logout():            
    session.clear()             # session - object to store data per user session - clear the session data
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)

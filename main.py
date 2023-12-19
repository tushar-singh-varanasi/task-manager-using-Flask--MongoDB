from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for,flash
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user,login_manager
import flask_login
# from bson import ObjectId
app = Flask(__name__)
app.secret_key = "something only you know"
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)



login_manager = flask_login.LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'login'
# 
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

# admin pannel
# ...


# current module (__name__) as argument.
@app.route('/')
@login_required
def index():
    # tasks = mongo.db.tasks.find()
    user = current_user

    # Fetch tasks associated with the current user
    tasks = mongo.db.tasks.find({'user_id': user.id})  
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    task_title = request.form.get('task_title')
    user_id = current_user.id
    mongo.db.tasks.insert_one({'title': task_title, 'done': False, 'user_id': user_id})
    # mongo.db.tasks.insert_one({'title': task_title, 'done': False})
    return redirect(url_for('index'))

@app.route('/update/<string:task_id>')  # Convert task_id to string
def update(task_id):
    task = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})  # Convert task_id to ObjectId
    return render_template('update.html', task=task)

@app.route('/save/<string:task_id>', methods=['POST'])  # Convert task_id to string
def save(task_id):
    new_title = request.form.get('new_title')
    mongo.db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': {'title': new_title}})  # Convert task_id to ObjectId
    return redirect(url_for('index'))

@app.route('/delete/<string:task_id>')  # Convert task_id to string
def delete(task_id):
    mongo.db.tasks.delete_one({'_id': ObjectId(task_id)})  # Convert task_id to ObjectId
    return redirect(url_for('index'))

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        print(password2)
        # email verification
        if mongo.db.users.find_one({'email': email}):
            flash('you already use this email id.', 'danger')
            return redirect(url_for('signup'))
        if password != password2:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))

        # Create a new user document in the database
        user_id = mongo.db.users.insert_one({'email': email, 'password': password}).inserted_id
        print(user_id)
        # Create a User object for Flask-Login
       
        # Log in the user
        
        flash('Account created successfully!', 'success')
        # return redirect(url_for('index'))

    return render_template('signup.html')


# login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password']

        # Check if the user exists and the password is correct
        user = mongo.db.users.find_one({'email': email, 'password': password})

        if user:
            # Create a User object for Flask-Login
            user_obj = User()
            user_obj.id = str(user['_id'])

            # Log in the user
            login_user(user_obj, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

    


# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application 
	# on the local development server.
	app.run(debug=True)


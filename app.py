import os
import functools
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect,flash
from flask_login import LoginManager,login_user, logout_user,login_required, current_user
from flask_migrate import Migrate
from flask_socketio import SocketIO,disconnect
from models import db ,User, UserMessage

load_dotenv()



app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ankursingh22#'
app.config['SQLALCHEMY_DATABASE_URI']= os.environ['MYSQL_CONNECTION_URL']
socketio = SocketIO(app)

db.init_app(app)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat'
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql:///sammy:password@localhost/chat"
# db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/main')
def main():
    return  render_template("main.html")

@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    users = UserMessage.query.all()
    # if request.method=='POST':
    #     username = request.form.get('user_name')
    #     print('datattt is',username)
    #     user_id = request.form.get('user_id')
    #     message = request.form.get('message')
       
    
    #     data=UserMessage(user_id=user_id,username=username, message=message) 
    #     print(data)
    #     db.session.add(data)
    #     db.session.commit()
    return  render_template("index.html", users=users)

@app.route('/')
def home():
    return  render_template("intro.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        name = request.form.get('name')
        password = request.form.get('password')

        user= User.query.filter_by(name=name).first()
        if user and password==user.password:
            login_user(user)
            
            return redirect('/index')
        else:
            flash('Invalid Creadentials', 'warning')
            return redirect('/login')
        
    return  render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    if current_user.is_authenticated:
        print('received my event: ' + str(json))
        data = json

        # user_message = UserMessage(user_name=data.get('user_name', 'default_value'), message=data.get('message', 'default_value'), time=data.get('time', 'default_value'), status=data.get('status', 'default_value'), user_id=data.get('user_id', 'default_value'))
        user_name = data.get('user_name', 'default_value')
        message = data.get('message', 'default_value')
        time = data.get('time', 'default_value')
        status = data.get('status', 'default_value')
        user_id = data.get('user_id', 'default_value')

        if user_name != 'default_value' and message != 'default_value' and time != 'default_value' and status != 'default_value' and user_id != 'default_value':
            user_message = UserMessage(user_name=user_name, message=message, time=time, status=status, user_id=user_id)
            db.session.add(user_message)
            db.session.commit()
            socketio.emit('my response', json, callback=messageReceived)
    else:
        return False  # not allowed here

@socketio.on('online')
def online(data):
    socketio.emit('status_change', {'username': data['username'], 'status': 'online'}, broadcast=True)



if __name__ == '__main__':
    socketio.run(app, debug = True,port=8080)
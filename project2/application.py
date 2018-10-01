import os
import requests

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_session import Session

from models import Channel, Message


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

users = set()
channels = {}

@app.route("/")
def index():
    if not session:
        return redirect(url_for('check_login'))
    return render_template('index.html', name=session['current_user'], channels=channels)

@app.route("/login", methods=['GET', 'POST'])
def check_login():

    session.clear()

    name = request.form.get('username')
    if request.method == 'POST':
        if name in users:
            return render_template('login.html', err_msg='Username has existed, try another name')
        else:
            users.add(name)
            session['current_user'] = name
            # at beginning members list that user want to send hidden messages with is empty
            session['hidden_users'] = []
            return redirect(url_for('index'))
    # if this is accessed by GET method
    return render_template('login.html')

@app.route("/channel", methods=['POST'])
def create_channel():

    name = request.form.get('room_name')
    # secret key can be None
    key = request.form.get('secret_key')
    for c in channels:
        if(channels[c].name == name):
            return render_template('index.html', name=session['current_user'], channels=channels, err_msg='Someone created a room with this name, try another name')
    channel = Channel(len(channels)+1, name, key)
    channel.user_list.append(session['current_user'])
    channels[channel.id] = channel

    return redirect(url_for('channel', channelID=channel.id))

@app.route("/channel/<int:channelID>")
def channel(channelID):

    channel = channels[channelID]
    # if user did not input in secret_key field => public channel
    if(len(channel.secret_key) == 0):
        if(session['current_user'] not in channel.user_list):
            channel.user_list.append(session['current_user'])
            socketio.emit('new member', {'name' : session['current_user']}, broadcast=True)
        return render_template('chat.html', channel = channel, you=session['current_user'], hiddens=session['hidden_users'])
    # if user is logged in this channel
    if(session['current_user'] in channel.user_list):
        return render_template('chat.html', channel = channel, you=session['current_user'], hiddens=session['hidden_users'])

    return render_template('check_key.html', channel = channel)

@app.route("/channel/<int:channelID>", methods=['POST'])
def check_key(channelID):

    key = request.form.get('secret_key')

    channel = channels[channelID]
    
    if(channel.secret_key == key):
        channel.user_list.append(session['current_user'])
        socketio.emit('new member', {'name' : session['current_user']}, broadcast=True)
        return render_template('chat.html', channel = channel, you=session['current_user'], hiddens=session['hidden_users'])
    return render_template('check_key.html', channel = channel, err_msg='Wrong key, input again')


@socketio.on('client_connected')
def announce_new_user(data):
    print('connected to new {}'.format(data['msg']))

@socketio.on('send_msg')
def send_msg(data):
    channel = channels[int(data['id'])]
    hidden_users = data['hiddens']
    print(hidden_users)
    msg = Message(session['current_user'], data['msg'], hidden_users)
    channel.messages.append(msg)
    print(data['msg'])
    message = {"sender" : msg.sender, "content" : msg.content, "timestamp" : msg.timestamp, "hiddens" : msg.hiddens}
    emit('display messages',message, broadcast=True)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.6', port=5000)
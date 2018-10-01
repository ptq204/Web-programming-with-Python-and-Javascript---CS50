
localStorage.clear();

document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons

    socket.on('connect', () => {
        console.log('connected');

        document.querySelector('#send').disabled = true;
        document.querySelector('#chat-content').onkeyup = () => {
            if(document.querySelector('#chat-content').value.length > 0){
                document.querySelector('#send').disabled = false;
            }
            else document.querySelector('#send').disabled = true;
        };
        
        document.querySelector('#send').onclick = () => {
            const msg_content = document.querySelector('#chat-content').value;
            document.querySelector('#chat-content').value = '';
            document.querySelector('#send').disabled = true;
            const channelID = location.pathname.split('/')[2];
            socket.emit('send_msg', {'msg' : msg_content, 'id' : channelID});
        };

        document.querySelector('#chat-content').addEventListener('keyup', event => {
            event.preventDefault();
            if(event.keyCode === 13){
                if(document.querySelector('#chat-content').value.length > 0){
                    const msg_content = document.querySelector('#chat-content').value;
                    document.querySelector('#chat-content').value = '';
                    document.querySelector('#send').disabled = true;
                    const channelID = location.pathname.split('/')[2];
                    var hiddenList = [];
                    document.querySelector('#mem-list').querySelectorAll('input').forEach((input)=>{
                        if(input.checked === true){
                            hiddenList.push(input.value);
                        }
                    });
                    socket.emit('send_msg', {'msg' : msg_content, 'id' : channelID, 'hiddens' : hiddenList});
                }
            }
        });

        document.querySelector('#send1').onclick = () => {
            const tmp = document.querySelector('#msg').value;
            const mem = document.createElement('li');
            mem.innerHTML = tmp;
            document.querySelector('#mem-list').appendChild(mem);
        };
    });

    socket.on('new member', data => {
        let list_mem = document.querySelector('#mem-list');
        let mem = document.createElement('input');
        mem.type = "checkbox";
        mem.value = data.name;
        newline = document.createElement('br');
        list_mem.appendChild(mem);
        list_mem.append(" " + data.name);
        list_mem.appendChild(newline);
    });

    socket.on('display messages', data => {
        
        if(!data.hiddens.includes(document.querySelector('#you').innerHTML)){
            let i = 0;
            let msg_item = document.createElement('div');
            msg_item.className = "msg-layout";

            let msg_sender = document.createElement('p');
            // if the current user then color of nickname will be different
            if(data.sender == document.querySelector('#you').innerHTML)
                msg_sender.className = "msg-sender-user";
            else
                msg_sender.className = "msg-sender";
            msg_sender.innerHTML = data.sender + ":";

            let msg_content = null;
            if(!is_valid(data.content)){
                msg_content = document.createElement('p');
                msg_content.innerHTML = data.content;
            }
            else{
                msg_content = document.createElement('img');
                msg_content.src = data.content;
                msg_content.className = "img-msg";
            }
            
            let time = document.createElement('span');
            time.className = "time-right";
            time.innerHTML = data.timestamp;

            msg_item.appendChild(msg_sender);
            msg_item.appendChild(msg_content);
            msg_item.appendChild(time);
        
            document.querySelector('#conservation').append(msg_item);
        }
    });
});

function is_valid(url){
    let regexp =  /^(?:(?:https?|ftp):\/\/)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/\S*)?$/;
    if(url.length == 0 || !regexp.test(url))
        return false;
    return true;
}
class Channel:
    def __init__(self, ID, name, secret_key):
        self.id = ID
        self.name = name
        self.secret_key = secret_key
        self.messages = []
        self.user_list = []
        
    
    def add_user(self, user):
        self.user_list.append(user)
    
    def add_message(self, message):
        if(len(self.messages) > 100):
            self.messages.pop(0)
        self.messages.append(message)
    
    def kick_user(self, user):
        pass

c = Channel(1, 'dsad', None)
print(c.secret_key)

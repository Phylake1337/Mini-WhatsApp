import hashlib 
import pickle
from collections import namedtuple
msg = namedtuple('msg', ['content', 'state', 'sender'])

class Chat:
    """ represents a chat between 2 users"""
    def __init__(self, frt_user, scd_user):
        self.owners = [frt_user, scd_user]
        self.new_msg = None
        self.content = []
        
    def add_msg(self, msg, sender, receiver):
        """ add msg to chat content, and also mark the receiver user to get notification """
        self.new_msg = receiver
        self.content.append(sender.username + " :" + msg.content + " \n")
    
    def get_content(self, user, lines_to_return=20):
        """return chat content and unmark notification for a user"""
        if user == self.new_msg:
            self.new_msg = None
        lines_to_return = min(len(self.content), lines_to_return)
        return self.content[-1 * lines_to_return : ]
        
class Authenticator:
    """ Responsible for users' accounts management, sign in, sign out, sign up, delete account"""
    def __init__(self):
        self.users = []
        try:
            #try to load users objects if existed, as user objects has all info that we need.
            with open('users_db.pkl', 'rb') as file:
                while True:
                    try:
                        loaded_user = pickle.load(file)
                        self.users.append(loaded_user)
                    except EOFError:
                        break
                
        except FileNotFoundError:
            #Create new file
            self.users_db = open('users_db.pkl', 'wb')
            self.users_db.close()
            
    def _encrypt_pw(self, mob_num, password):
        '''
        Encrypt the password with the mobile number and return
        encoded password.
        '''
        hash_string = (mob_num + password)
        hash_string = hash_string.encode("utf8")
        return hashlib.sha256(hash_string).hexdigest()
        
    def register(self, new_mob_num, password, username):
        """ Check for mobile number similarities then Register a new user """
        for user in self.users:
            #Mobile number should be unique.
            if user.mob_num == new_mob_num: return False
            
        encr_password = self._encrypt_pw(new_mob_num, password)
        new_user = User(new_mob_num, encr_password, username)
        self.users.append(new_user)
        return True
    
    def delete_account(self, mob_num, password):
        """Check if the account is registered then
            Delete it from the system"""
        user = self._varify_user(mob_num, password)
        
        if user == None:
            return False
        else:
            self.users.remove(user)
            return True
        
    
    def log_in(self, mob_num, password):
        """varify user's account and logs in, returns user object or None"""
        user = self._varify_user(mob_num, password)
        
        if user:
            user.logged_in = True
            return user
        else:
            return None
    
    def log_out(self, user):
        """logs out"""
        user.logged_in = False

    
    def _varify_user(self, new_mob_num, new_password):
        """check if the account is already registered"""
        for user in self.users:
            if user.mob_num == new_mob_num and user.password == self._encrypt_pw(new_mob_num, new_password):
                return user
        return None
    
    def get_users_by_MobNum(self, mob_num):
        """return one user object according to a provided mobile number"""
        for user in self.users:
            if mob_num == user.mob_num:
                return user
        return None
    
    def get_users_by_username(self, username):
        """return one user object according to a provided mobile number"""
        for user in self.users:
            if username == user.username:
                return user
        return None
  
class User:
    """ Models a user which can chat with, add, and remove anthor user"""
    def __init__(self, mob_num, password, username):
        self.mob_num = mob_num
        self.password = password
        self.username = username
        self.contacts = []
        self.chats = {}
        self.logged_in = False

    
    def add_contact(self, contact):
        """adds contact to user contacts list and create a new chat object
            , also store chat object into chat dict in both users object"""
        if self.logged_in and (contact not in self.contacts):
            self.contacts.append(contact)
            try:
                _ = self.chats[contact.mob_num]
                _ = contact.chats[self.mob_num]
            except KeyError:
                chat = Chat(self, contact)
                self.chats[contact.mob_num] = (chat, contact)
                contact.chats[self.mob_num] = (chat, self)
            return True
        else:
            return False
        
    def remove_contact(self, user):
        """removes contact from user contacts list"""
        if self.logged_in and user in self.contacts:
            self.contacts.remove(user)
    
    def list_contacts(self):
        """prints out contacts list and msgs notifications"""
        print('List of contancts: ')
        if self.contacts == []:
            print('-- Empty --')
        else:
            for i, contact in enumerate(self.contacts):
                new_msg_flag = self.chats[contact.mob_num][0].new_msg == self
                if new_msg_flag:
                    print("  ({0})-> {1} -- {2}   ".format(i+1, contact.username, contact.mob_num) + 5*'- - ' + "New Msg")
                else:
                    print("  ({0})-> {1} -- {2} ".format(i+1, contact.username, contact.mob_num))                    
        print('\n')
        
    def list_chats(self):
        """prints out contacts list and msgs notifications"""
        print('List of chats: ')
        res = []
        for i, (chat,contact) in enumerate(self.chats.values()):
            new_msg_flag = chat.new_msg == self
            res.append((chat, contact))
            if contact in self.contacts:
                if new_msg_flag:
                    print("  ({0})-> {1} -- {2}   ".format(i+1, contact.username, contact.mob_num) + 5*'- - ' + "New Msg")
                else:
                    print("  ({0})-> {1} -- {2} ".format(i+1, contact.username, contact.mob_num)) 
            else:
                if new_msg_flag:
                     print("  ({0})-> {1}   ".format(i+1, contact.mob_num) + 5*'- - ' + "New Msg")
                else:
                    print("  ({0})-> {1} ".format(i+1, contact.mob_num)) 
        print('\n')
        return res
    
    def send_msg(self, rec_user, msg_content):
        """ Composite Chat class to send msgs and create new chat files"""
        chat = self.chats[rec_user.mob_num][0]
        chat.add_msg(msg(msg_content, 'not seen', self), self, rec_user)
            
    def display_chat(self, user):
        """display chat msgs between 2 users"""
        try:
            chat = self.chats[user.mob_num][0]
            return chat.get_content(self)
        except KeyError:
            return None
        
        
    def __eq__(self, mob_num):
        return self.mob_num == mob_num

    
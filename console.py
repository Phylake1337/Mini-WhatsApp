import sys
import pickle
from mini_whatsapp import User, Authenticator

class Console:
    def __init__(self):
        self.auth = Authenticator()
        self._user = None
        self.logging_page()
        
        
    def _take_option(self, options, print_out):
        """helper method to apply user choice to the program code"""
        user_choice = input("Please, choose one of the follewing options: \n " + print_out 
                            + "\n Your choice: " )
        try:
            user_option = options[int(user_choice)]
        except KeyError:
            print("Please enter a vaild number")
            self._take_option(options, print_out)
            
        except ValueError:
            print("Please a enter vaild number, not a string or some signs")
            self._take_option(options, print_out)
        else:
            return user_option()

         
    def _int_input_in_range(self, print_out, range_):
        """helper method to get integer input from user in certain range"""
        try:
            i = int(input(print_out))
            assert range_[0] <= i <= range_[1]
            return i
        except AssertionError:
            print('Please, enter a vaild number')
            return None
        except ValueError:
            print('Please, enter a number not a string')
            return None
            
    def logging_page(self):
        """Prints out logging options to the user"""
        print('-=' * 12 + " Logging Page " + '-=' * 12)
        options = {1: self.sign_up, 2: self.log_in, 3: self.delete_account, 4: self.exit}
        print_out = "(1) Sign up \n (2) Log in \n (3) Delete Account \n (4) Exit"
        return self._take_option(options, print_out)
    
        
    def homepage(self):
        """Prints out homepage options to the user"""
        print('-=' * 12 + " Home Page " + '-=' * 12)
        self._user.list_contacts()
        options = {1: self.add_contact, 2:self.remove_contact ,3: self.view_contact_chat, 4: self.sign_out, 5: self.exit}
        print_out = "(1) Add new contact \n (2) Remove Contact \n (3) View my chats \n (4) Sign out \n (5) Exit"
        return self._take_option(options, print_out)
        
        
    def sign_up(self):
        """Use Authenticator object to sign up a user"""
        print('-=' * 12 + " Sigh Up " + '-=' * 12)
        mob_num, password = self._input_mob_num('Mobile Number :'), input("Password: ")
        username= input("User name: ")
        register_flag = self.auth.register(mob_num, password, username)
        if register_flag:
            print("Done registering, sign in NOW.")
            return self.logging_page()
        else:
            print("This mobile number is already registered.\n" + '-=' * 30)
            options = {1: self.sign_up, 2: self.logging_page, 3: self.exit}
            print_out = "(1) Try Again \n (2) Back to Logging Page \n (3) Exit"
            return self._take_option(options, print_out)
    
    
    def log_in(self):
        """Use Authenticator object to log in a user"""
        print('-=' * 12 + " Log in " + '-=' * 12)
        mob_num, password = self._input_mob_num('Mobile Number :'), input("Password: ")
        self._user = self.auth.log_in(mob_num, password)
        if self._user:
            print("you are logged in, Welcome '{}'".format(self._user.username))
            self.homepage()
        else:
            print("Mobile number or/and password is/are Invaild \n" + '-=' * 30)
            options = {1: self.log_in, 2: self.logging_page, 3: self.exit}
            print_out = "(1) Try Again \n (2) Back to Logging Page \n (3) Exit"
            self._take_option(options, print_out)
            
    def delete_account(self):
        """Use Authenticator object to delete user's account"""
        print('-=' * 12 + " Delete Account " + '-=' * 12)
        mob_num, password = self._input_mob_num('Mobile Number :'), input("Password: ")
        delete_flag = self.auth.delete_account(mob_num, password)
        if delete_flag:
            print("The account is permently deleted")
            self.logging_page()
        else:
            print("Mobile Number or/and password is/are Invaild \n" + '-=' * 30)
            options = {1: self.delete_account, 2: self.logging_page, 3: self.exit}
            print_out = "(1) Try Again \n (2) Back to Logging Page \n (3) Exit"
            self._take_option(options, print_out)
    
    def sign_out(self):
        """Use Authenticator object to sign out user's account"""
        self.auth.log_out(self._user)
        self._user = None
        print("Signed out successfully")
        return self.logging_page()
        
    def add_contact(self):
        """Add a contact to a user account by contact's username"""
        contact_mob_num = self._input_mob_num("-=" * 30 + "\n" + "Please enter contact's mobile number to be added: ")
        if contact_mob_num == self._user.mob_num:
            print("You can't add yourself, IDIOT!!")
            return self.homepage()
        
        found_contact = self.auth.get_users_by_MobNum(contact_mob_num)
        if found_contact != None:
            print('A user with Mobile number: "{0}", and User name: "{1}" is found'.format(found_contact.mob_num, found_contact.username))
            user_choice =  self._int_input_in_range(" (1) Add the found user. \n (0) Back to Home page \n Your choice: " 
                                                    ,range_ = (0, 1))
            if user_choice:
                add_flag = self._user.add_contact(found_contact)
                if not add_flag:
                    print('This user is already one of your contacts')
                    return self.homepage()
                print("Contact added successfully")
            else:
                self.homepage()
        else:
            print('This user mobile number has no matches')
        return self.homepage()
            
    def remove_contact(self):
        """Removes a contact from contact list """
        contact_mob_num = input("-=" * 30 + "\n" + "Please enter contact's mobile number to be removed: ")
        contact = self.auth.get_users_by_MobNum(contact_mob_num)
        if (not contact) or contact not in self._user.contacts:
            print('This user not in your contact list')
            return self.homepage()
        
        self._user.remove_contact(contact)
        print('Contact removed successfully')
        return self.homepage()
            
    def view_contact_chat(self):
        """print all chats usernames then view one of the contact's chat"""
        if self._user.chats == {}:
            print("No chats to be viewed yet")
            self.homepage()
            
        print('-=' * 30)
        chats = self._user.list_chats()
        user_choice = self._int_input_in_range("Pick whose contact chat to be viewed: "
                                               ,range_ = (1, len(chats)))
        if not user_choice:
            return self.homepage()
        
        chat, contact = chats[user_choice - 1]
        chat_content = chat.get_content(self._user)
        print('-=' * 12 + " Chat Window " + '-=' * 12)
        if chat_content != []:
            for line in chat_content:
                print(line.rstrip())        
        else:
            print('This chat is empty, send your first msg now')
            
        user_choice = self._int_input_in_range(' (1) Send new msg \n (2) Back to homepage \n Your choice: '
                                                , range_ = (1,2))
        if user_choice == 1:
            print('HINT: send (0) to exist the chat window')
            return self._send_msg(contact)
        else:
            return self.homepage()
        
    def _send_msg(self, contact):
        """uses Users's send_msg method to send a msg to a certain contact"""
        msg_content = input('{} :'.format(self._user.username))
        if msg_content == '0': 
            return self.homepage()
        self._user.send_msg(contact, msg_content)

        return self._send_msg(contact)
    
    def _input_mob_num(self, print_out):
        try:
            mob_num = (input(print_out))
            _ = int(mob_num)
            return mob_num
        except ValueError:
            print('Only mobile numbers allowed')
            return self._input_mob_num('Mobile Number :')
        
    def exit(self):
        """logs the user of if needed, and save users objects for later use"""
        if self._user != None:
            self._user.logged_in = False
                
        with open('users_db.pkl', 'wb') as file:
            for user in self.auth.users:
                pickle.dump(user, file, pickle.HIGHEST_PROTOCOL)
        print("Thank you for using Mini-WhatsApp :D")
        print("Closing .....")
        sys.exit()
        

if __name__ == '__main__':
    Console()
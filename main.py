import sqlite3, hashlib, json, base64, os, threading, logging, webbrowser
from flask import Flask, jsonify, request, render_template
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


logging.basicConfig(level=logging.ERROR)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class General:
    def Greeting():
        print("""


 __                            __   ___
|__) \ /  |\/|  /\  |\ |  /\  / _` |__ 
|     |   |  | /~~\ | \| /~~\ \__> |___

           

Welcome to pymanage. Run help for a list of commands.
To remove this greeting set 'Greeting' in the config to false
""")
    def Clear_Screen():
        os.system("cls") if os.name == "nt"else os.system("clear")

    def Set_Title(args=None):
        os.system("title PyManage ^| /jwe0") if args == None else os.system(f"title PyManage ^| /jwe0 ^| {args}")

    def Check_Files():
        if not os.path.exists("Assets/"):
            os.mkdir("Assets/")
        if not os.path.exists("Assets/Config.json"):
            data = {
                "General" : {
                    "Greeting" : True,
                    "Clear Screen" : True,
                    "Web UI" : False
                },
                "Credentials" : {}
            }
            print("[!] Setting up your account")
            username = input("Username: ")
            password = input("Password: ")

            data['Credentials']['Username'] = hashlib.sha256(username.encode()).hexdigest()
            data['Credentials']['Password'] = hashlib.sha256(password.encode()).hexdigest()

            with open("Assets/Config.json", 'w') as f:
                json.dump(data, f, indent=4)
        if not os.path.exists("Assets/Password.db"):
            with open("Assets/password.db", 'w') as f:
                f.write("")
            Database(password).Create_Databse()

    def Load_Config():
        with open("Assets/Config.json") as cnfg:
            cnfg = json.load(cnfg)

            greeting = cnfg['General']['Greeting']
            clear_s = cnfg['General']['Clear Screen']
            webui = cnfg['General']['Web UI']
            cnfguser = cnfg['Credentials']['Username']
            cnfgpass = cnfg['Credentials']['Password']

            return cnfguser, cnfgpass, greeting, clear_s, webui

class Webui:
    def __init__(self, masterpassword) -> None:
        self.app = Flask(__name__)
        self.password = masterpassword

        @self.app.route("/", methods=['GET'])
        def index():
            return render_template('index.html')
        
        @self.app.route("/passwords", methods=['POST'])
        def passwords():
            database = Database(self.password)  # Create a new instance of Database
            passwords = database.Webui_Read_Databse()
            return jsonify({"passwords": passwords})

    def Start_Server(self):
        self.app.run(debug=False)
        webbrowser.open("http://127.0.0.1:5000")







class Database:
    def __init__(self, masterpass) -> None:
        self.con = sqlite3.connect("Assets/Password.db")
        self.cursor = self.con.cursor()
        self.password = masterpass

    def Key_Pad(self):
        while len(self.password) < 16:
            self.password += "X"

    def Encrypt_data(self, data):
        self.Key_Pad()
        data = data.encode()
        cipher = AES.new(self.password.encode(), AES.MODE_CBC)
        cipher_bytes = cipher.encrypt(pad(data, AES.block_size))
        iv = base64.b64encode(cipher.iv).decode()
        cipher_text = base64.b64encode(cipher_bytes).decode()

        data = f"{cipher_text}:!:{iv}"

        return data
    
    def Decrypt_data(self, data):
        self.Key_Pad()
        data = data.split(":!:")

        cipher_text = base64.b64decode(data[0])
        iv = base64.b64decode(data[1])

        cipher = AES.new(self.password.encode(), AES.MODE_CBC, iv)
        message = unpad(cipher.decrypt(cipher_text), AES.block_size)

        return message.decode()


    def Create_Databse(self):
        self.cursor.execute("CREATE TABLE passwords(url, username, email, password)")
        self.con.commit()

    def Remove_Entry(self, entry):
        self.cursor.execute(f"DELETE FROM passwords WHERE url = '{entry}'")
        self.con.commit()

    def Import_Database(self, type, file):
        with open(file) as f:
            database = json.load(f)

            if type.lower() == "bitwarden":

                entries = database['items']

                total = len(entries)
                progress = 0

                for entry in entries:
                    self.Add_Info(entry['name'], entry['login']['username'] if entry['login']['username'] else "No Username", "null", entry['login']['password'] if entry['login']['password'] else "No Password")
                    progress += 1
                    print(f"[{str(progress)}/{str(total)}]", end='\r')
        print(f"Imported {file}")









    def Webui_Read_Databse(self):
        items = []
        entries = self.cursor.execute("SELECT * FROM passwords")
        entrys = entries.fetchall()

        for entry in entrys:
            items.append(((entry[0]), self.Decrypt_data(entry[1]), self.Decrypt_data(entry[2]), self.Decrypt_data(entry[3])))
        return items
                         


    def Read_Databse(self):
        items = self.cursor.execute("SELECT * FROM passwords")
        entrys = items.fetchall()
        for entry in entrys:
            print(f"""
Site: {entry[0]}
Username: {self.Decrypt_data(entry[1])}
Email: {self.Decrypt_data(entry[2])}
Password: {self.Decrypt_data(entry[3])}
""")
            
    def Add_Info(self, url, username, email, password):
        self.cursor.execute(f"INSERT INTO passwords(url, username, email, password) VALUES('{url}', '{self.Encrypt_data(username)}', '{self.Encrypt_data(email)}', '{self.Encrypt_data(password)}')")
        self.con.commit()

    def Clear_Databse(self):
        self.cursor.execute("DELETE FROM passwords")
        self.con.commit()

    def Search_Database(self, site):
        items = self.cursor.execute(f"SELECT * FROM passwords WHERE url = '{site}'")

        entries = items.fetchall()
        if entries:
            for entry in entries:
                print(f"""
Site: {entry[0]}
Username: {self.Decrypt_data(entry[1])}
Email: {self.Decrypt_data(entry[2])}
Password: {self.Decrypt_data(entry[3])}
""")
        else:
            print("No record found with that url")



class Main:
    def __init__(self, masterpass) -> None:
        self.database = Database(masterpass)
        self.masterpass = masterpass



        
    def Help(self):
        print("""
LD -> Show database
SF -> Search for a specific site
RF -> Remove a certain entry
AD -> Add a new record
CD -> Clear the entries
ID -> Import a password manager file
EX -> Exit the program
""")

    def Main(self):

        selection = input("> ")

        match selection.upper():
            case "LD":
                self.database.Read_Databse()
            case "SF":
                name = input("site > ")
                self.database.Search_Database(name.lower())


            case "AD":
                url = input("Url: ")
                username = input("Username: ")
                email = input("Email: ")
                password = input("Password: ")
                self.database.Add_Info(url.lower(), username, email, password)
        
            case "CD":
                selection = input("Are you 100% certain [y/n]")
                match selection.lower():
                    case "y":
                        passw = input("Enter password: ")
                        if passw == self.masterpass:
                            self.database.Clear_Databse()
                    case "n":
                        pass

            case "RF":
                name = input("Url: ")
                self.database.Remove_Entry(name)
            case "ID":
                managers = ['1']
                print("Must be an unencrypted json export file.")
                print("1. Bitwarden")
                type = input("Manager: ")
                while type not in managers:
                    type = input("Manager: ")
                file = input("File: ")
                if not os.path.exists(file):
                    print("File {} does not exist".format(file))
                    return
                if type == "1":
                    type = "bitwarden"
                self.database.Import_Database(type, file)


            case "HELP":
                self.Help()
            case "EX":
                exit()



if __name__ == "__main__":
    General.Set_Title()
    General.Check_Files()
    cnfguser, cnfgpass, greeting, clear_s, webui = General.Load_Config()


    password = input("Master password: ")
    username = input("Username: ")

    if hashlib.sha256(password.encode()).hexdigest() == cnfgpass and hashlib.sha256(username.encode()).hexdigest() == cnfguser:
        if webui:
            webgui = Webui(password)
            web_thread = threading.Thread(target=webgui.Start_Server)
            web_thread.start()
        if clear_s:
            General.Clear_Screen()
        if greeting:
            General.Greeting()
        while True:
            Main(password).Main()
    else:   
        print("Incorrect password")
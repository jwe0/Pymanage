import sqlite3, hashlib, json, base64, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad



class General:
    def Greeting():
        print("""


 __                            __   ___
|__) \ /  |\/|  /\  |\ |  /\  / _` |__ 
|     |   |  | /~~\ | \| /~~\ \__> |___

           

Welcome to pymanage. Run help for a list of commnds.
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
                    "Clear Screen" : True
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
            cnfguser = cnfg['Credentials']['Username']
            cnfgpass = cnfg['Credentials']['Password']

            return cnfguser, cnfgpass, greeting, clear_s


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



    def Read_Databse(self):
        items = self.cursor.execute("SELECT * FROM passwords")
        entrys = items.fetchall()
        for entry in entrys:
            print(f"""
Site: {self.Decrypt_data(entry[0])}
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
        
        entry = items.fetchone()
        if entry:
            print(f"""
Site: {self.Decrypt_data(entry[0])}
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
RD -> Show database
SF -> Search for a specific site
AD -> Add a new record
CD -> Clear the entries
""")

    def Main(self):

        selection = input("> ")

        match selection.upper():
            case "RD":
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
            case "HELP":
                self.Help()



if __name__ == "__main__":
    General.Set_Title()
    General.Check_Files()
    cnfguser, cnfgpass, greeting, clear_s = General.Load_Config()

    password = input("Master password: ")
    username = input("Username: ")

    if hashlib.sha256(password.encode()).hexdigest() == cnfgpass and hashlib.sha256(username.encode()).hexdigest() == cnfguser:
        if clear_s:
            General.Clear_Screen()
        if greeting:
            General.Greeting()
        while True:
            Main(password).Main()
    else:
        print("Incorrect password")

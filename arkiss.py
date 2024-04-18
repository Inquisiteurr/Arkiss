import inquirer
from pypsexec.client import Client
import os
import ipaddress
from prettytable import PrettyTable
import yaml
from cryptography.fernet import Fernet
import base64
import inspect

############################ GLOBALS ############################
global global_arkiss
############################ GLOBALS ############################

global_arkiss = """
   ▄████████    ▄████████    ▄█   ▄█▄  ▄█     ▄████████    ▄████████                  
  ███    ███   ███    ███   ███ ▄███▀ ███    ███    ███   ███    ███                  
  ███    ███   ███    ███   ███▐██▀   ███▌   ███    █▀    ███    █▀                   
  ███    ███  ▄███▄▄▄▄██▀  ▄█████▀    ███▌   ███          ███                         
▀███████████ ▀▀███▀▀▀▀▀   ▀▀█████▄    ███▌ ▀███████████ ▀███████████                  
  ███    ███ ▀███████████   ███▐██▄   ███           ███          ███                  
  ███    ███   ███    ███   ███ ▀███▄ ███     ▄█    ███    ▄█    ███                  
  ███    █▀    ███    ███   ███   ▀█▀ █▀    ▄████████▀   ▄████████▀                   
               ███    ███   ▀                                                         
"""


def CreateTab(data, title):
    table = PrettyTable()
    table.field_names = ["IP", "Output"]
    for ip, output in data:
        color = "green" if global_username in output else "red"
        output = "error" if "error" in output else output
        table.add_row([ip, f"\033[1;31;40m {output} \033[m" if color == "red" else f"\033[1;32;40m {output} \033[m"])
    print(title)
    print(table)

def MenuChoiceGen(choices, message, skip=0):
    if skip == 0:
        os.system('clear')
        print(global_arkiss)
    questions = [inquirer.List('choices', message=message, choices=list(choices.keys())), ]
    answers = inquirer.prompt(questions)
    return choices[answers['choices']]

def menu_option(display_name):
    def decorator(func):
        func.display_name = display_name
        return func
    return decorator

def create_menu_dict(obj):
    methods = inspect.getmembers(obj, predicate=inspect.ismethod)
    return {method.display_name: method for name, method in methods if hasattr(method, 'display_name')}

class Config:
    def __init__(self, filename='settings.yml'):
        self.filename = filename

    def checksetting(self, setting, cred=0):
        with open(self.filename, 'r') as f:
            if cred == 0:
                return yaml.safe_load(f)[setting]
            else:
                user_password = inquirer.password(message="Please enter your password : ")
                key = base64.urlsafe_b64encode(user_password.encode())
                cipher_suite = Fernet(key)
                decrypted_setting = cipher_suite.decrypt(yaml.safe_load(f)[setting].encode())

                return decrypted_setting.decode()

    def editsetting(self, setting, value):
        with open(self.filename, 'r+') as f:
            config = yaml.safe_load(f)
            config[setting] = value
            f.seek(0)
            yaml.dump(config, f, default_flow_style=False)

class Settings:
    @menu_option("Change the credentials to use")
    def Cred(self):
        username = inquirer.text(message="Enter your username")
        password = inquirer.password(message='Please enter your password')
        key = base64.urlsafe_b64encode(password.encode())
        cipher_suite = Fernet(key)
        cipher_text_username = cipher_suite.encrypt(username.encode())
        cipher_text_password = cipher_suite.encrypt(password.encode())
        Config().editsetting('global_username', cipher_text_username.decode())
        Config().editsetting('global_password', cipher_text_password.decode())
    @menu_option("Change the Host / Single IP or IP file")
    def Host(self, force=1):
        if force == 0:
            hostname = inquirer.text(message="Enter the hostname/IP to use")
            Config().editsetting('global_method',0)
            Config().editsetting('global_hostname', hostname)
            return
        else:
            pass
        message = "[ Single IP or IP file?  ] - Please chose an option"
        mainmenu = {"Single IP": 0, "IP file": 1}
        answer = MenuChoiceGen(mainmenu, message)
        if answer == 0:
            hostname = inquirer.text(message="Enter the hostname/IP to use")
            Config().editsetting('global_method',0)
            Config().editsetting('global_hostname', hostname)
        else:
            message = "[ Wich Ip file do you want to use?  ] - Please chose an option"
            files = os.listdir("hostfile")
            listfile = {file: i for i, file in enumerate(files)}
            fileanswer = MenuChoiceGen(listfile, message)
            Config().editsetting('global_ipfile', fileanswer)
            Config().editsetting('global_method', 1)
        return
    @menu_option("Back to Main menu")
    def do_nothing(self):
        pass


class CommandExecutor:
    def __init__(self, encrypt=False):
        self.ipfile = "hostfile/" + Config().checksetting('global_ipfile')
        self.username = Config().checksetting('global_username', cred=1)
        self.password = Config().checksetting('global_password', cred=1)
        self.encrypt = encrypt
        self.method = Config().checksetting('global_method')
        self.hostname = Config().checksetting('global_hostname')

    def Wincon(self, command, ip):
        success = None
        failed = None
        c = Client(ip, username=self.username, password=self.password, encrypt=self.encrypt)
        try:
            c.connect()
            c.create_service()
            stdout, stderr, rc = c.run_executable("powershell.exe", arguments=command)
            decoded_output = stdout.decode('ISO-8859-1')
            print(f"{ip}\t\033[92mSuccess\033[0m")
            success = (ip, decoded_output)
            c.remove_service()
            c.disconnect()
        except Exception as e:
            print(f"{ip}\t\033[91mFailed\033[0m")
            failed = (ip, str(e))
        return success, failed

    def Getlists(self, command, ip, successlist, failedlist):
        success, failed = self.Wincon(command, ip)
        if success is not None:
            successlist.append(success)
        if failed is not None:
            failedlist.append(failed)
        return successlist, failedlist
    
    def Conchoice(self, command):
        successlist = []
        failedlist = []

        if self.method == 1:
            message = "[ Single IP or IP file? ] - Are you sure to deploy this command on every IP ?"
            choicelist = {"yes": 0, "Change to Single IP": 1, "Back": 2}
            choice = MenuChoiceGen(choicelist, message)
            if choice == 0:
                iplist = read_and_validate_ip_file(self.ipfile)
                for ip, i in iplist:
                    successlist, failedlist = self.Getlists(command, ip, successlist, failedlist)

            elif choice == 1:
                Host(0)
                ip = Config().checksetting('global_hostname')
                successlist, failedlist = self.Getlists(command, ip, successlist, failedlist)
            else:
                return 0, 0
        else:
            ip = self.hostname
            successlist, failedlist = self.Getlists(command, ip, successlist, failedlist)

        return successlist, failedlist

    def Getdebug(self, successlist, failedlist):
        message = "[ Debug menu ] - Do you want to see the results of the command ?"
        choicelist = {"Yes": 0, "No": 1}
        checkdebug = MenuChoiceGen(choicelist, message, skip=1)
        if checkdebug == 0:
            debug_lists = [(successlist, [i for ip, i in successlist], f"Success({len(successlist)})"), 
                        (failedlist, [i for ip, i in failedlist], f"Failed({len(failedlist)})")]
            while True:
                message = "[ Debug menu ] - Please chose an option"
                choicelist = {label: idx for idx, (_, _, label) in enumerate(debug_lists)}
                choicelist["Continue"] = 2
                checkoption = MenuChoiceGen(choicelist, message)
                if checkoption in [0, 1]:
                    listmenu, listdebugprint, _ = debug_lists[checkoption]
                    listmenu.append("Back to Debug menu")
                    listdebugprint.append("return")
                    while True:
                        menu = f" [ {list(choicelist.keys())[checkoption]} results ] - Please chose an ip to see the results"
                        option = MenuChoiceGen({ip: result for ip, result in zip(listmenu, listdebugprint)}, menu, skip=1)
                        if option == "return":
                            listmenu.pop()  # remove "Back to Debug menu"
                            break
                        else:
                            print(option)
                else:
                    return
        else:
            return


class Secondmenu:
    @menu_option("Windows image scan")  
    def Winimscan():
        print("Work in progress..")
    @menu_option("Bitlocker crypting management")
    def BitlockManage():
        print("Work in progress..")
    @menu_option("Remote Desktop Protocol management")
    def RDPManage():
        registrykey = "Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value "
        message = "[ RDP Management ] - what should we do ?"
        choicelist = {
            "Enable": 0,
            "Disable": 1,
            "Back": 2
        }
        choice = MenuChoiceGen(choicelist, message)
        command = registrykey + choice
        if choice == 1:
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        elif choice == 0:
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        else:
            return
        return
    @menu_option("Command Line management")
    def CMDManage():
        registrykey = "Set-ItemProperty -Path 'HKLM:\Software\Policies\Microsoft\Windows\System' -Name 'DisableCMD' -Value "
        message = "[ CMD Management ] - what should we do ?"
        choicelist = {
            "Enable CMD and bash execution": 0,
            "Disable CMD but allow bash execution ": 1,
            "Disable CMD and bash execution": 2,
            "Back": 3
        }
        choice = MenuChoiceGen(choicelist, message, functionlist)
        command = registrykey + choice
        if choice == 0:
            print("Enabling CMD and Bash exec...")
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        elif choice == 1:
            print("Disabling CMD but Allowing Bash exec...")
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        elif choice == 2:
            print("Disabling CMD and Bash exec...")
            successlist, failedlist = Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        else:
            return
        return
    @menu_option("Local Admin User management")
    def AdminManage():
        print("Work in progress..")
    @menu_option("Force authentication after sleep mode")
    def AuthSleepMode():
        print("Work in progress..")
    @menu_option("Test the connection/credentials")
    def Contest():
        command = "whoami"
        successlist, failedlist = CommandExecutor().Conchoice(command)
        CreateTab(successlist, "Success Output")
        CreateTab(failedlist, "Failed Output")
    @menu_option("Back to Main menu")
    def do_nothing(self):
        pass


class Mainmenu:
    @menu_option("Deploy Elasticsearch Cluster")
    def Deployelk(self):
        print("Déploiement du cluster elasticsearch")
    @menu_option("Windows Security Check")
    def Winaudit(self):
        print("Test d'audit windows")
    @menu_option("Windows Security Remediation")
    def Winauditrem(self):
        print("remediation")
    @menu_option("Check Windows Missing Updates")
    def Chkwinupdate(self):
        command = "Get-WindowsUpdate"
        successlist, failedlist = CommandExecutor().Conchoice(command)
        if successlist == 0:
            pass
        else:
            CommandExecutor().Getdebug(successlist, failedlist)
            message = "[ Windows update ] - Launch Updates ?"
            mainmenu = {"Yes":0, "No":1}
            choice = MenuChoiceGen(mainmenu, message)
            if choice == 1:
                return
            else:
                command = "Install - WindowsUpdate - AcceptAll"
                successlist, failedlist = CommandExecutor().Conchoice(command)
                if successlist == 0:
                    pass
                else:
                    CommandExecutor().Getdebug(successlist, failedlist)
        return
    @menu_option("Additional tools")    
    def Divers(self):
        diversmenu = Secondmenu()
        diversmenu_dict = create_menu_dict(diversmenu)
        while True:
            message = "[ Divers Menu ] - Please chose an option"
            function = MenuChoiceGen(diversmenu_dict, message)
            if function == diversmenu.do_nothing:
                return
            else:
                function()
    @menu_option("Settings")  
    def Settings(self):
        message = "[ Settings ] - Please chose an option"
        settingsmenu = Settings()
        settingsmenu_dict = create_menu_dict(settingsmenu)
        function = MenuChoiceGen(settingsmenu_dict, message)
        function()
    @menu_option("Leave") 
    def Leave(self):
        print("Thank you for using Arkiss :3")
        return False

def main():
    os.system('clear')
    print(global_arkiss)
    mainmenu = Mainmenu()
    menu_dict = create_menu_dict(mainmenu)
    Settings().Cred()
    Settings().Host()
    while True:
        message = "[ Main Menu ] - Please chose an option"
        function = MenuChoiceGen(menu_dict, message)
        function()

main()

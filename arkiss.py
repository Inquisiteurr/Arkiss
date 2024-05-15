from prettytable import PrettyTable
from smb.SMBConnection import SMBConnection
from pypsexec.client import Client
import os
import inquirer
import yaml
import base64
import inspect
import socket

############################ GLOBALS ############################
global global_arkiss
############################ GLOBALS ############################

global_arkiss = """
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐   ▄████████    ▄████████    ▄█   ▄█▄  ▄█     ▄████████    ▄████████▌
▐  ███    ███   ███    ███   ███ ▄███▀ ███    ███    ███   ███    ███▌
▐  ███    ███   ███    ███   ███▐██▀   ███▌   ███    █▀    ███    █▀ ▌
▐  ███    ███  ▄███▄▄▄▄██▀  ▄█████▀    ███▌   ███          ███       ▌
▐▀███████████ ▀▀███▀▀▀▀▀   ▀▀█████▄    ███▌ ▀███████████ ▀███████████▌
▐  ███    ███ ▀███████████   ███▐██▄   ███           ███          ███▌
▐  ███    ███   ███    ███   ███ ▀███▄ ███     ▄█    ███    ▄█    ███▌
▐  ███    █▀    ███    ███   ███   ▀█▀ █▀    ▄████████▀   ▄████████▀ ▌
▐               ███    ███   ▀                                       ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
"""


def CreateTab(data, title, contest=0,result=0):
    table = PrettyTable()
    table.field_names = ["IP", "Output"]
    if contest == 1:
        username = Config().checksetting('global_username')
        for ip, output in data:
            color = "green" if username in output else "red"
            table.add_row([ip, f"\033[1;31;40m {output} \033[m" if color == "red" else f"\033[1;32;40m {output} \033[m"])
    else:
        for ip, output in data:
            color = "red" if result==1 else "green"
            table.add_row([ip, f"\033[1;31;40m {output} \033[m" if color == "red" else f"\033[1;32;40m {output} \033[m"])
    print(title)
    print(table)

def MenuChoiceGen(choices, message, skip=0):
    if skip == 0:
        os.system('clear')
        print(global_arkiss)
    sorted_choices = sorted(choices.items(), key=lambda item: getattr(item[1], 'order', float('inf')) if callable(item[1]) else float('inf'))
    questions = [inquirer.List('choices', message=message, choices=[choice[0] for choice in sorted_choices])]
    answers = inquirer.prompt(questions)
    return dict(sorted_choices)[answers['choices']]

def menu_option(display_name):
    def decorator(func):
        func.display_name = display_name
        return func
    return decorator

def create_menu_dict(obj):
    methods = inspect.getmembers(obj, predicate=inspect.ismethod)
    return {method.display_name: method for name, method in methods if hasattr(method, 'display_name')}

def order(order_num):
    def decorator(func):
        func.order = order_num
        return func
    return decorator

class Config:
    def __init__(self, filename='settings.yml'):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.filename = os.path.join(self.dir_path, filename)

    def checksetting(self, setting):
        with open(self.filename, 'r') as f:
            return yaml.safe_load(f)[setting]

    def editsetting(self, setting, value):
        with open(self.filename, 'r') as f:
            config = yaml.safe_load(f)
            config[setting] = value
        with open(self.filename, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)


class Settings:
    def __init__(self, folder='hostfile'):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.folder = os.path.join(self.dir_path, folder)
    @order(0)
    @menu_option("Change the credentials to use")
    def Cred(self):
        username = inquirer.text(message="Enter your username")
        password = inquirer.password(message='Please enter your password')
        Config().editsetting('global_username', username)
        Config().editsetting('global_password', password)
    @order(1)
    @menu_option("Change the Host / Single IP or IP file")
    def Host(self, force=0):
        if force == 1:
            hostname = inquirer.text(message="Enter the hostname/IP to use")
            Config().editsetting('global_method',0)
            Config().editsetting('global_hostname', hostname)
            return
        elif force == 2:
            message = "[ Wich Ip file do you want to use?  ] - Please chose an option"
            files = os.listdir(self.folder)
            listfile = {file: file for file in files} 
            fileanswer = MenuChoiceGen(listfile, message)
            Config().editsetting('global_ipfile', fileanswer)
            Config().editsetting('global_method', 1)
        else:
            message = "[ Single IP or IP file?  ] - Please chose an option"
            mainmenu = {"Single IP": 0, "IP file": 1}
            answer = MenuChoiceGen(mainmenu, message)
            if answer == 0:
                hostname = inquirer.text(message="Enter the hostname/IP to use")
                Config().editsetting('global_method',0)
                Config().editsetting('global_hostname', hostname)
            else:
                message = "[ Wich Ip file do you want to use?  ] - Please chose an option"
                files = os.listdir(self.folder)
                listfile = {file: file for file in files} 
                fileanswer = MenuChoiceGen(listfile, message)
                Config().editsetting('global_ipfile', fileanswer)
                Config().editsetting('global_method', 1)
    @order(2)
    @menu_option("Back to Main menu")
    def do_nothing(self):
        pass

class CommandExecutor:
    def __init__(self, encrypt=False, folder='hostfile/'):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.folder = os.path.join(self.dir_path, folder)
        self.ipfile = self.folder + Config().checksetting('global_ipfile')
        self.username = Config().checksetting('global_username')
        self.password = Config().checksetting('global_password')
        self.method = Config().checksetting('global_method')
        self.hostname = Config().checksetting('global_hostname')
        self.encrypt = encrypt

    def Wincon(self, command, ip):
        success = None
        failed = None
        c = Client(ip, username=self.username, password=self.password, encrypt=self.encrypt)
        if "custom/windows" in command:
            try:
                conn = SMBConnection(self.username, self.password, socket.gethostname(), ip, use_ntlm_v2=True, is_direct_tcp=True)
                assert conn.connect(ip, 445)
                with open(command, 'rb') as file_obj:
                    conn.storeFile('C$', '\\temp\\', file_obj)
                script = command.split('/')[-1]
                c.connect()
                c.create_service()
                stdout, stderr, rc = c.run_executable("powershell.exe", arguments=f"-File C:\\temp\\" + script)
                stdout, stderr, rc = c.run_executable("cmd.exe", arguments=f"/c del C:\\temp\\" + script)
                decoded_output = stdout.decode('ISO-8859-1')
                print(f"{ip}\t\033[92mSuccess\033[0m")
                print(decoded_output)
                success = (ip, decoded_output)
                c.remove_service()
                c.disconnect()
                conn.close()
            except Exception as e:
                print(f"{ip}\t\033[91mFailed\033[0m")
                failed = (ip, str(e))
        else:
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
                messageipfile = "[ Single IP or IP file? ] - You are using, the ipfile " + Config().checksetting('global_ipfile') + ", Do you want to change ?"
                choicelistipfile = {"yes": 0, "No": 1}
                checkipfile = MenuChoiceGen(choicelistipfile, messageipfile)
                if checkipfile == 1:
                    with open(self.ipfile, 'r') as file:
                        ips = file.read().splitlines()
                    for ip in ips:
                        successlist, failedlist = self.Getlists(command, ip, successlist, failedlist)

                else:
                    Settings().Host(0)
                    ipfilechanged = Config().checksetting('global_ipfile')
                    with open(ipfilechanged, 'r') as file:
                        ips = file.read().splitlines()
                    for ip in ips:
                        successlist, failedlist = self.Getlists(command, ip, successlist, failedlist)

            elif choice == 1:
                Settings().Host(1)
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
            while True:
                message = "[ Debug menu ] - Please chose an option"
                choicelist = {f"Success({len(successlist)})":0, f"Failed({len(failedlist)})":1, "Continue":2 }
                checkoption = MenuChoiceGen(choicelist, message)
                if checkoption == 0:
                    if len(successlist) !=0:
                        CreateTab(successlist, "Success Output",0,0)
                        MenuChoiceGen({"Yes": 0}, "Continue", skip=1)
                elif checkoption == 1:
                    if len(failedlist) !=0:
                        CreateTab(failedlist, "Failed Output",0,1)
                        MenuChoiceGen({"Yes": 0}, "Continue", skip=1)
                elif checkoption == 2:
                    return
        else:
            return

class Urgentmenu:
    @order(0)
    @menu_option("Cut network connection")
    def CutNet(self):
        command = "Get-NetAdapter | % { if (Test-NetConnection -InterfaceAlias $_.Name -InformationLevel Quiet) { Disable-NetAdapter -Name $_.Name -Confirm:$false } }"
        message = "[ Cut Network Connection ] - what should we do ?"
        choicelist = {"Disable": 0,"Back": 1}
        choice = MenuChoiceGen(choicelist, message)
        if choice == 0:
            CommandExecutor().Conchoice(command)
        else:
            return
    @order(1)
    @menu_option("Shutdown Computers")
    def Shutdown(self):
        command = "Stop-Computer"
        message = "[ Shutdown Computers ] - what should we do ?"
        choicelist = {"shutdown": 0,"Back": 1}
        choice = MenuChoiceGen(choicelist, message)
        if choice == 0:
            CommandExecutor().Conchoice(command)
        else:
            return
    @order(2)
    @menu_option("Back to Main menu")
    def do_nothing(self):
        pass

class Secondmenu:
    @order(0)
    @menu_option("Windows image scan")  
    def Winimscan(self):
        print("Work in progress..")
    @order(1)
    @menu_option("Bitlocker crypting management")
    def BitlockManage(self):
        print("Work in progress..")
    @order(2)
    @menu_option("Remote Desktop Protocol management")
    def RDPManage(self):
        registrykey = "Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value "
        message = "[ RDP Management ] - what should we do ?"
        choicelist = {"Enable": "0","Disable": "1","Back": "2"}
        choice = MenuChoiceGen(choicelist, message)
        command = registrykey + choice
        if choice == "1":
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        elif choice == "0":
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        else:
            return
    @order(3)
    @menu_option("Command Line management")
    def CMDManage(self):
        registrykey = "Set-ItemProperty -Path 'HKLM:\Software\Policies\Microsoft\Windows\System' -Name 'DisableCMD' -Value "
        message = "[ CMD Management ] - what should we do ?"
        choicelist = {
            "Enable CMD and bash execution": "0",
            "Disable CMD but allow bash execution ": "1",
            "Disable CMD and bash execution": "2",
            "Back": 3
        }
        choice = MenuChoiceGen(choicelist, message)
        command = registrykey + choice
        if choice == "0":
            print("Enabling CMD and Bash exec...")
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        elif choice == "1":
            print("Disabling CMD but Allowing Bash exec...")
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        elif choice == "2":
            print("Disabling CMD and Bash exec...")
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)
        else:
            return
        return
    @order(4)
    @menu_option("Local Admin User management")
    def AdminManage(self):
        print("Work in progress..")
    @order(5)
    @menu_option("Force authentication after sleep mode")
    def AuthSleepMode(self):
        print("Work in progress..")
    @order(6)
    @menu_option("Test the connection/credentials")
    def Contest(self):
        command = "whoami"
        successlist, failedlist = CommandExecutor().Conchoice(command)
        if len(successlist) !=0:
            CreateTab(successlist, "Success Output",1)
        if len(failedlist) !=0:
            CreateTab(failedlist, "Failed Output",1)
        message = "[ Back to divers menu ] "
        choicelist = {"Yes": 0}
        MenuChoiceGen(choicelist, message, skip=1)
    @order(7)
    @menu_option("Custom script execution")
    def Custom(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        message = "[ Custom Scripts ] - What is your OS target ?"
        choicelist = {"Windows": 0,"Linux":1,"Back": 2}
        choice = MenuChoiceGen(choicelist, message)
        if choice == 0:
            folderpath = "custom/windows/"
            folder = os.path.join(dir_path, folderpath)
            message = "[ Wich script  do you want to use?  ] - Please chose an option"
            files = os.listdir(folder)
            listfile = {file: i for i, file in enumerate(files)}
            fileanswer = MenuChoiceGen(listfile, message)
            command = folder + str(listfile[fileanswer]) 
            successlist, failedlist = CommandExecutor().Conchoice(command)
            if successlist == 0:
                return
            else:
                CommandExecutor().Getdebug(successlist, failedlist)

        elif choice == 1:
            folderpath = "custom/linux"
            folder = os.path.join(dir_path, folderpath)
            message = "[ Wich script  do you want to use?  ] - Please chose an option"
            files = os.listdir(folder)
            listfile = {file: i for i, file in enumerate(files)}
            fileanswer = MenuChoiceGen(listfile, message)
            pass

        else:
            return
    @order(8)
    @menu_option("Back to Main menu")
    def do_nothing(self):
        pass

class Mainmenu:
    @order(0)
    @menu_option("Deploy Elasticsearch Cluster")
    def Deployelk(self):
        print("Déploiement du cluster elasticsearch")
    @order(1)
    @menu_option("Windows Security Check")
    def Winaudit(self):
        print("Test d'audit windows")
    @order(2)
    @menu_option("Windows Security Remediation")
    def Winauditrem(self):
        print("remediation")
    @order(3)
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
    @order(4)
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
    @order(5)
    @menu_option("Urgent tasks")
    def Urgent(self):
        urgentmenu = Urgentmenu()
        urgentmenu_dict = create_menu_dict(urgentmenu)
        while True:
            message = "[ Urgent menu ] - Please chose an option"
            function = MenuChoiceGen(urgentmenu_dict, message)
            if function == urgentmenu.do_nothing:
                return
            else:
                function()
    @order(6)
    @menu_option("Settings")  
    def Settings(self):
        message = "[ Settings ] - Please chose an option"
        settingsmenu = Settings()
        settingsmenu_dict = create_menu_dict(settingsmenu)
        function = MenuChoiceGen(settingsmenu_dict, message)
        function()
    @order(7)
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
        if function() is False:
            break 

main()

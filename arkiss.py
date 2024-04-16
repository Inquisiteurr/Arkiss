import inquirer
from pypsexec.client import Client
import os
import ipaddress

############################ GLOBALS ############################
global global_ipfile
global global_arkiss
global global_username
global global_method
global global_password
global global_hostname
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
# Automatic generation of choices menu
def MenuChoiceGen(choicelist, message, functionlist,skip=0):
    if skip == 0:
        os.system('clear')
        print(global_arkiss)
    questions = [inquirer.List('choicelist', message=message, choices=choicelist), ]
    answers = inquirer.prompt(questions)
    i = 0
    while i < len(choicelist):
        if answers['choicelist'] == i:
            return (functionlist[i])
        i += 1

# Define the credentials used for deployment
def Cred():
    global global_username
    global global_password
    global_username = inquirer.text(message="Enter your username")
    global_password = inquirer.password(message='Please enter your password')

# define the deployment method "ip file" or "single ip"
def Host(force=1):
    global global_method
    global global_hostname
    if force == 0:
        global_method = 0
        global_hostname = inquirer.text(message="Enter the hostname/IP to use")
        return
    else:
        pass
    message = "[ Single IP or IP file?  ] - Please chose an option"
    mainmenu = [("Single IP", 0), ("IP file", 1)]
    choicelist1 = [0, 1]
    answer = MenuChoiceGen(mainmenu, message, choicelist1)
    if answer == 0:
        global_hostname = inquirer.text(message="Enter the hostname/IP to use")
        global_method = 0
    else:
        global_method = 1
    return

# Function to verify ip adress inside ip adress file
def read_and_validate_ip_file(file_path):
    with open(file_path, 'r') as file:
        ip_list = [line.strip() for line in file]
    valid_ip_list = []
    for i, ip in enumerate(ip_list):
        try:
            ipaddress.ip_address(ip)
            valid_ip_list.append((ip, i))
        except ValueError:
            print(f"L'adresse IP {ip} n'est pas valide.")
    return valid_ip_list

# command casting function
def Wincon(command, ip):
    success = None
    failed = None
    c = Client(ip, username=global_username, password=global_password, encrypt=False)
    try:
        c.connect()
        c.create_service()
        stdout, stderr, rc = c.run_executable("powershell.exe", arguments=command)
        decoded_output = stdout.decode('ISO-8859-1')
        print(f"{ip}\t\033[92mSuccess\033[0m")  # \033[92m and \033[0m are used to print the text in green color
        success = (ip, decoded_output)
        c.remove_service()
        c.disconnect()
    except Exception as e:
        print(f"{ip}\t\033[91mFailed\033[0m")  # \033[91m and \033[0m are used to print the text in red color
        failed = (ip, str(e))
    return success, failed


# function to fill list for debugging function of death
def Getlists(command, ip, successlist, failedlist):
    success, failed = Wincon(command, ip)
    if success is not None:
        successlist.append(success)
    if failed is not None:
        failedlist.append(failed)
    return successlist, failedlist

# Connection to windows method check
def Conchoice(command):
    successlist = []
    failedlist = []

    if global_method == 1:
        message = "[ Single IP or IP file? ] - Are you sure to deploy this command on every IP ?"
        choicelist = [("yes", 0), ("Change to Single IP", 1), ("Back", 2)]
        functionlist = ["0", "1", "return"]
        choice = MenuChoiceGen(choicelist, message, functionlist)
        if choice == "0":
            iplist = read_and_validate_ip_file(global_ipfile)
            for ip, i in iplist:
                successlist, failedlist = Getlists(command, ip, successlist, failedlist)


        elif choice == "1":
            Host(0)
            ip = global_hostname
            successlist, failedlist = Getlists(command, ip, successlist, failedlist)
        else:
            return 0, 0
    else:
        ip = global_hostname
        successlist, failedlist = Getlists(command, ip, successlist, failedlist)

    return successlist, failedlist


# Debuging function of death
def Getdebug(successlist, failedlist):
    message = "[ Debug menu ] - Do you want to see the results of the command ?"
    choicelist = [("Yes", 0), ("No", 1)]
    answerlist = [0, 1]
    checkdebug = MenuChoiceGen(choicelist, message, answerlist,skip=1)
    if checkdebug == 0:
        successlistdebug = [i for ip, i in successlist]
        failedlistdebug = [i for ip, i in failedlist]
        successcount = len(successlistdebug)
        failedcount = len(failedlistdebug)
        while True:
            message = "[ Debug menu ] - Please chose an option"
            choicelist = [(f"Success({successcount})", 0), (f"Failed({failedcount})", 1), ("Continue", 2)]
            answerlist = [0, 1, 2]
            checkoption = MenuChoiceGen(choicelist, message, answerlist)
            if checkoption == 0:
                successlistmenu = successlist
                successlistdebugprint = successlistdebug
                successlistmenu.append("Back to Debug menu")
                successlistdebugprint.append("return")

                while True:
                    menu = " [ Success results ] - Please chose an ip to see the results"
                    successoption = MenuChoiceGen(successlistmenu, menu, successlistdebugprint, skip=1)
                    if successoption == "return":
                        del checkoption
                        break
                    else:
                        print(successoption)


            elif checkoption == 1:
                failedlistmenu = failedlist
                failedlistdebugprint = failedlistdebug
                failedlistmenu.append("Back to Debug menu")
                failedlistdebugprint.append("return")
                while True:
                    menu = " [ Failed results ] - Please chose an ip to see the results"
                    failedoption = MenuChoiceGen(failedlistmenu, menu, failedlistdebugprint, skip=1)
                    if failedoption == "return":
                        del checkoption
                        break
                    else:
                        print(failedoption)

            else:
                return
    else:
        return


# work in progress
def Deployelk():
    print("Déploiement du cluster elasticsearch")


# work in progress
def Winaudit():
    print("Test d'audit windows")


# work in progress
def Winauditrem():
    print("remediation")


# Missing update checker
def Chkwinupdate():
    command = "Get-WindowsUpdate"
    successlist, failedlist = Conchoice(command)
    if successlist == 0:
        return
    else:
        Getdebug(successlist, failedlist)
        message = "[ Windows update ] - Launch Updates ?"
        mainmenu = [
            ("Yes", 0),
            ("No", 1)
        ]
        choicelist = [
            "Yes",
            "No"
        ]
        choice = MenuChoiceGen(mainmenu, message, choicelist)
        if choice == "No":
            return
        else:
            command = "Install - WindowsUpdate - AcceptAll"
            successlist, failedlist = Conchoice(command)
            if successlist == 0:
                return
            else:
                Getdebug(successlist, failedlist)
    return


# Function to print a message when you leave
def Leave():
    print("Thank you for using Arkiss :3")
    return False


def Winimscan():
    print("Work in progress..")


def BitlockManage():
    print("Work in progress..")


# Function to manage Remote Desktop Protocol on windows machine
def RDPManage():
    registrykey = "Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value "
    message = "[ RDP Management ] - what should we do ?"
    choicelist = [
        ("Enable", 0),
        ("Disable", 1),
        ("Back", 2)
    ]
    functionlist = [
        "0",
        "1",
        "return"
    ]
    choice = MenuChoiceGen(choicelist, message, functionlist)
    command = registrykey + choice
    if choice == "1":
        successlist, failedlist = Conchoice(command)
        if successlist == 0:
            return
        else:
            Getdebug(successlist, failedlist)
    elif choice == "0":
        successlist, failedlist = Conchoice(command)
        if successlist == 0:
            return
        else:
            Getdebug(successlist, failedlist)
    else:
        return
    return


def CMDManage():
    registrykey = "Set-ItemProperty -Path 'HKLM:\Software\Policies\Microsoft\Windows\System' -Name 'DisableCMD' -Value "
    message = "[ CMD Management ] - what should we do ?"
    choicelist = [
        ("Enable CMD and bash execution", 0),
        ("Disable CMD but allow bash execution ", 1),
        ("Disable CMD and bash execution", 2),
        ("Back", 3)
    ]
    functionlist = [
        "0",
        "1",
        "2",
        "return"
    ]
    choice = MenuChoiceGen(choicelist, message, functionlist)
    command = registrykey + choice
    if choice == "0":
        print("Enabling CMD and Bash exec...")
        successlist, failedlist = Conchoice(command)
        if successlist == 0:
            return
        else:
            Getdebug(successlist, failedlist)
    elif choice == "1":
        print("Disabling CMD but Allowing Bash exec...")
        successlist, failedlist = Conchoice(command)
        if successlist == 0:
            return
        else:
            Getdebug(successlist, failedlist)
    elif choice == "2":
        print("Disabling CMD and Bash exec...")
        successlist, failedlist = Conchoice(command)
        if successlist == 0:
            return
        else:
            Getdebug(successlist, failedlist)
    else:
        return
    return


def AdminManage():
    print("Work in progress..")


def AuthSleepMode():
    print("Work in progress..")


# Secondary menu for additional tools
def Divers():
    while True:
        message = "[ Divers Menu ] - Please chose an option"
        mainmenu = [
            ("Windows image scan", 0),
            ("Bitlocker crypting management", 1),
            ("Remote Desktop Protocol management", 2),
            ("Command Line management", 3),
            ("Local Admin User management", 4),
            ("Force authentication after sleep mode", 5),
            ("Back to Main menu", 6)
        ]
        functionlist = [
            "Winimscan()",
            "BitlockManage()",
            "RDPManage()",
            "CMDManage()",
            "AdminManage()",
            "AuthSleepMode()",
            "return"
        ]
        function = MenuChoiceGen(mainmenu, message, functionlist)
        if function == "return":
            return
        else:
            eval(function)


# setting function
def Settings():
    message = "[ Settings ] - Please chose an option"
    mainmenu = [
        ("Change Credentials", 0),
        ("Change Host", 1),
        ("Back to Main menu", 2)
    ]
    functionlist = [
        "Cred()",
        "Host()",
        "return"
    ]
    function = MenuChoiceGen(mainmenu, message, functionlist)
    if function == "return":
        return
    else:
        eval(function)


# main function
def main():
    os.system('clear')
    print(global_arkiss)
    while True:
        message = "[ Main Menu ] - Please chose an option"
        mainmenu = [
            ("Deploy Elastic Cluster", 0),
            ("Windows Security Check", 1),
            ("Remediation", 2),
            ("Check Windows Missing Updates", 3),
            ("Additional tools", 4),
            ("Settings", 5),
            ("Leave", 6)
        ]
        functionlist = [
            "Deployelk()",
            "Winaudit()",
            "Winauditrem()",
            "Chkwinupdate()",
            "Divers()",
            "Settings()",
            "Leave()"
        ]
        function = MenuChoiceGen(mainmenu, message, functionlist)
        eval(function)

############################ SETUP ############################
os.system('clear')
print(global_arkiss)
global_username = inquirer.text(message="Enter your username")
global_password = inquirer.password(message='Please enter your password')
global_ipfile = "Hosts"
message = "[ Single IP or IP file?  ] - Please chose an option"
mainmenu = [("Single IP", 0), ("IP file", 1)]
choicelist1 = [0, 1]
answer = MenuChoiceGen(mainmenu, message, choicelist1)
if answer == 0:
    global_hostname = inquirer.text(message="Enter the hostname/IP to use")
    global_method = 0
else:
    global_method = 1
############################ SETUP ############################

# Call the main function to display the menu
main()

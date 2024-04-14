import inquirer
from pypsexec.client import Client

print("""
   ▄████████    ▄████████    ▄█   ▄█▄  ▄█     ▄████████    ▄████████                  
  ███    ███   ███    ███   ███ ▄███▀ ███    ███    ███   ███    ███                  
  ███    ███   ███    ███   ███▐██▀   ███▌   ███    █▀    ███    █▀                   
  ███    ███  ▄███▄▄▄▄██▀  ▄█████▀    ███▌   ███          ███                         
▀███████████ ▀▀███▀▀▀▀▀   ▀▀█████▄    ███▌ ▀███████████ ▀███████████                  
  ███    ███ ▀███████████   ███▐██▄   ███           ███          ███                  
  ███    ███   ███    ███   ███ ▀███▄ ███     ▄█    ███    ▄█    ███                  
  ███    █▀    ███    ███   ███   ▀█▀ █▀    ▄████████▀   ▄████████▀                   
               ███    ███   ▀                                                         
""")

############################ GLOBALS ############################
global username
global password
global hostname
global ipfile
global method
############################ GLOBALS ############################

#Automatic generation of choices menu
def MenuChoiceGen(choicelist, message, functionlist):

    questions = [
        inquirer.List('choicelist',
                      message=message,
                      choices=choicelist
                      ),
    ]
    answers = inquirer.prompt(questions)
    i=0
    while i < len(choicelist):
        if answers['choicelist'] == i:
            return(functionlist[i])
        i+=1

#Connection to windows and command casting function
def Con(command):
    c = Client(hostname, username=username, password=password, encrypt=False)
    c.connect()
    try:
        c.create_service()
        stdout, stderr, rc = c.run_executable("powershell.exe", arguments=command)
        decoded_output = stdout.decode('ISO-8859-1')
        print(decoded_output)
    except Exception as e:
        print(f"An error occured: {e}")
    finally:
        c.remove_service()
        c.disconnect()

#work in progress
def Deployelk():
    print("Déploiement du cluster elasticsearch")

#work in progress
def Winaudit():
    print("Test d'audit windows")

#work in progress
def Winauditrem():
    print("remediation")

#Missing update checker
def Chkwinupdate():
    print("mise à jour manquantes")
    command="Get-WindowsUpdate"
    Con(command)
    questions = [
        inquirer.List('continuer',
                        message="Voulez-vous mettre à jour ?",
                        choices=['Oui', 'Non'],
                    ),
    ]
    answers = inquirer.prompt(questions)

    if answers['continuer'] == 'Oui':
        command="Install - WindowsUpdate - AcceptAll"
        print("Mise à jour en cours...")
        Con(command)
    else:
        None

#Function to print a message when you leave
def Leave():
    print("Thank you for using Arkiss :3")
    return False

def Winimscan():
    print("Work in progress..")

def BitlockManage():
    print("Work in progress..")

def RDPManage():

    disable="""Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 1 """
    enable="""Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 0 """
    message = "what should we do ?"
    choicelist = [
        ("Enable",0),
        ("Disable",1)
        ]
    functionlist = [
        "Enable",
        "Disable"
    ]
    choice = MenuChoiceGen(choicelist,message,functionlist)
    if choice == "Disable":
        print("Disabling...")
        Con(disable)
    elif choice == "Enable":
        print("Enabling...")
        Con(enable)
    return

def CMDManage():
    print("Work in progress..")

def AdminManage():
    print("Work in progress..")

def AuthSleepMode():
    print("Work in progress..")

#Secondary menu for additional tools
def Divers():
    message="[ Divers Menu ] - Please chose an option"
    mainmenu=[
        ("Windows image scan",0),
        ("Bitlocker crypting management",1),
        ("Remote Desktop Protocol management",2),
        ("Command Line management",3),
        ("Local Admin User management",4),
        ("Force authentication after sleep mode",5),
        ("Back to Main menu", 6)
    ]
    functionlist=[
        "Winimscan()",
        "BitlockManage()",
        "RDPManage()",
        "CMDManage()",
        "AdminManage()",
        "AuthSleepMode()",
        "return"
    ]
    function = MenuChoiceGen(mainmenu,message,functionlist)
    if function == "return":
        return
    else:
        eval(function)

def main():
    while True:
        message="[Main Menu - Please chose an option"
        mainmenu=[
            ("Deploy Elastic Cluster",0),
            ("Windows Security Check",1),
            ("Remediation",2),
            ("Check Windows Missing Updates",3),
            ("Additional tools",4),
            ("Leave",5)
        ]
        functionlist=[
            "Deployelk()",
            "Winaudit()",
            "Winauditrem()",
            "Chkwinupdate()",
            "Divers()",
            "Leave()"
        ]
        function = MenuChoiceGen(mainmenu,message,functionlist)
        eval(function)

############################# SETUP #############################
username = inquirer.text(message="Enter your username")
password = inquirer.password(message='Please enter your password')
ipfile = "Hosts"
menu = [
    inquirer.List("ip", message="Single IP or IP file?", choices=[("Single IP", 0), ("IP File", 1)], default=1),
]
method = inquirer.prompt(menu)['ip']
if method == 0:
    hostname = inquirer.text(message="Enter the hostname/IP to use")
else:
    None
############################# SETUP #############################

# Call the main function to display the menu
main()


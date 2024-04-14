import inquirer
from getpass import getpass
from pypsexec.client import Client


def con(command):
    c = Client(hostname, username=username, password=password, encrypt=False)
    c.connect()
    try:
        c.create_service()
        stdout, stderr, rc = c.run_executable("powershell.exe", arguments=command)
        decoded_output = stdout.decode('ISO-8859-1')
        print(decoded_output)
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
    finally:
        c.remove_service()
        c.disconnect()


def option1():
    print("Déploiement du cluster elasticsearch")


def option2():
    print("Test d'audit windows")


def option3():
    print("remediation")


def option4():
    print("mise à jour manquantes")
    command="Get-WindowsUpdate"
    con(command)
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
        con(command)
    else:
        None




def option5():
    questions = [
        inquirer.List("options",
                      message="quel outils souhaitez vous utiliser",
                      choices=["Scan de l'image windows",
                               "Gestion du chiffrement bitlocker",
                               "Gestion du bureau à distance",
                               "Gestion de l'invite de commande",
                               "Desactivation du compte administrateur",
                               "Forcer l'authentification en sortie de veille",
                               "Retour au menu principal"],
                      ),
    ]

    answers = inquirer.prompt(questions)
    if answers['options'] == "quel outils souhaitez vous utiliser":
        option51()
    elif answers['options'] == "Scan de l'image windows":
        option52()
    elif answers['options'] == "Gestion du chiffrement bitlocker":
        option53()
    elif answers['options'] == "Gestion du bureau à distance":
        option54()
    elif answers['options'] == "Gestion de l'invite de commande":
        option55()
    elif answers['options'] == 'Desactivation du compte administrateur':
        option56()
    elif answers['options'] == "Forcer l'authentification en sortie de veille":
        option57()
    elif answers['options'] == "Retour au menu principal":
        menu()


def option51():
    print("Work in progress..")


def option52():
    print("Work in progress..")


def option53():
    print("Work in progress..")


def option54():
    print("Work in progress..")
    c = Client("192.168.56.140", username="administrateur", password="toto", encrypt=False)

    # Connexion à la machine distante
    c.connect()

    try:
        c.create_service()
        questions = [
            inquirer.List('Activation/Desactivation',
                          message="Que souhaitez vous faire ?",
                          choices=['Activer', 'Désactiver'],
                          ),
        ]

        answers = inquirer.prompt(questions)

        if answers['Activation/Desactivation'] == 'Désactiver':
            print("Désactivation en cours...")
            stdout, stderr, rc = c.run_executable("powershell.exe",
                                                  arguments="""Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 1 """)
            decoded_output = stdout.decode('ISO-8859-1')
            print(decoded_output)
        elif answers['Activation/Desactivation'] == 'Activer':
            print("Activation en cours...")
            stdout, stderr, rc = c.run_executable("powershell.exe",
                                                  arguments="""Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 0 """)
            decoded_output = stdout.decode('ISO-8859-1')
            print(decoded_output)
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")

    finally:
        c.remove_service()
        c.disconnect()


def option55():
    print("Work in progress..")


def option56():
    print("Work in progress..")


def option57():
    print("Work in progress..")


def quitter():
    print("Merci d'avoir utilisé Arkiss ;)")
    return False


def menu():
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
████████▄     ▄████████    ▄████████    ▄████████ ███▄▄▄▄      ▄████████    ▄████████ 
███   ▀███   ███    ███   ███    ███   ███    ███ ███▀▀▀██▄   ███    ███   ███    ███ 
███    ███   ███    █▀    ███    █▀    ███    █▀  ███   ███   ███    █▀    ███    █▀  
███    ███  ▄███▄▄▄      ▄███▄▄▄      ▄███▄▄▄     ███   ███   ███         ▄███▄▄▄     
███    ███ ▀▀███▀▀▀     ▀▀███▀▀▀     ▀▀███▀▀▀     ███   ███ ▀███████████ ▀▀███▀▀▀     
███    ███   ███    █▄    ███          ███    █▄  ███   ███          ███   ███    █▄  
███   ▄███   ███    ███   ███          ███    ███ ███   ███    ▄█    ███   ███    ███ 
████████▀    ██████████   ███          ██████████  ▀█   █▀   ▄████████▀    ██████████ 


 """)
    questions = [
        inquirer.List('options',
                      message="Veuillez choisir une option",
                      choices=["Déploiement du cluster elasticsearch",
                               "Test d'audit windows",
                               "remediation",
                               "mise à jour manquantes",
                               "Divers",
                               'Quitter'],
                      ),
    ]

    while True:
        answers = inquirer.prompt(questions)
        if answers['options'] == "Déploiement du cluster elasticsearch":
            option1()
        elif answers['options'] == "Test d'audit windows":
            option2()
        elif answers['options'] == "remediation":
            option3()
        elif answers['options'] == "mise à jour manquantes":
            option4()
        elif answers['options'] == "Divers":
            option5()
        elif answers['options'] == 'Quitter':
            if not quitter():
                break

global username
global password
global hostname

username = input("Veuillez entrer le nom d'utilisateur : ")
password = input("Veuillez entrer le mot de passe : ")
hostname = input("Veuillez entrer l'adresse IP de la machine : ")
# Appeler la fonction menu pour démarrer le programme
menu()
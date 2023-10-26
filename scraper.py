import json
import re
import time
import os
import facebook_scraper
import datetime


def download_menu(resturant):
    if os.getenv("SECRETS") is None:
        os.environ["SECRETS"] = "secrets.json"

    with open(os.getenv("SECRETS"), "r") as file:
        config = json.load(file)

    account = ""
    if resturant == "dubai":
        account = "100087591040668"
    elif resturant == "doc":
        account = "selfservicedoctorino"
    else:
        print("Error: resturant not found")
        return

    download_succeeded = False
    tries = 0
    while not download_succeeded and tries < 5:
        try:
            posts = facebook_scraper.get_posts(account, pages=1, credentials=(config["username"], config["password"]))
            download_succeeded = True
        except Exception as e:
            print(f"could not download menu, error:\n{e}")
            print("retrying...")
            tries += 1
            time.sleep(1)

    post = next(posts)
    while not is_menu(post, resturant) or not is_date_today(post['time']):
        post = next(posts)

    if resturant == "dubai":
        post["text"] = format_dubai(post["text"])
    elif resturant == "doc":
        post["text"] = format_doc(post["text"])

    with open(f"menu_{resturant}.json", "w") as f:
        json.dump(post, f, indent=4, default=str)


def get_menu(resturant):
    #check if menu is updated as of today
    try:
        with open(f"menu_{resturant}.json", "r") as f:
            menu = json.load(f)
        if not is_date_today(datetime.datetime.strptime(menu['time'], "%Y-%m-%d %H:%M:%S")):
            download_menu(resturant)
    except FileNotFoundError:
        download_menu(resturant)


    with open(f"menu_{resturant}.json", "r") as f:
        menu = json.load(f)

    menu["text"] = f"<u><i>Menù del {resturant}:</i></u>\n\n" + menu["text"]
    return menu


def is_menu(post,resturant): # questa è una porcata, ci deve essere modo più furbo di capire se è un nuovo menù
    if resturant == "dubai":
        return "Oggi vi proponiamo" in post["text"]
    else:
        return "MENU DEL GIORNO" in post["text"]


def is_date_today(date):
    today = datetime.datetime.today()
    return today.day == date.day and today.month == date.month and today.year == date.year


def format_dubai(menu):
    menu = menu.replace("Altro", "")
    menu = menu.replace("Oggi vi proponiamo:", "Buongiorno, oggi vi proponiamo: 🍽️")
    menu = menu.replace("PRIMI", "\nPRIMI 🍝")
    menu = menu.replace("SECONDI", "\nSECONDI 🍖")
    menu = menu.replace("CONTORNI", "\nCONTORNI 🍟🥦")
    menu = menu.replace("FRUTTA E YOGURT", "\nFRUTTA E YOGURT 🍎🍍🥛")
    menu = menu.replace("DOLCI", "\nDOLCI 🍰")

    menu = menu.replace(" -", "-")
    menu = menu.replace("\n-", "-")
    menu = menu.replace("-", "\n - ")

    menu = menu + "\n\nVI ASPETTIAMO!"

    menu = "\tMENÙ DUBAI 📋\n\n" + menu
    return menu


def lowercase_menu(menu):
    # Dividi il testo in linee
    lines = menu.split('\n')

    # Elabora ogni linea
    for i, line in enumerate(lines):
        # Tratta titoli, introduzione e insalate
        if line.startswith("PRIMI") or line.startswith("SECONDI") or line.startswith("CONTORNI") or line.startswith(
                "PIATTI FREDDI") or line.startswith("INSALATE") or line.startswith("DOLCI") or line.startswith(
            "FRUTTA") or line.startswith(" - INSALATA") or line.startswith("Buongiorno") or line.startswith("PER PRENOTAZIONI"):
            # Mantieni maiuscole e minuscole originali
            lines[i] = line
        else:
            # Trasforma il resto in minuscolo
            lines[i] = line.lower()

    # Ricompatta il testo
    formatted_menu = '\n'.join(lines)

    return formatted_menu


def format_doc(menu):
    date_pattern = r'\d{2}/\d{2}/\d{4}'

    menu = re.sub(date_pattern, "", menu)   # Sostituisci tutte le occorrenze del pattern con un testo specifico (ad esempio, "DATA_RIMOSSA")
    menu = menu.replace("PER PRENOTAZIONI CHIAMARE IL NUMERO.3385305973. Lucia", "\nPER PRENOTAZIONI CHIAMARE IL 3385305973 ~Lucia 📞\n\nBuongiorno, oggi vi proponiamo: 🍽\n")
    menu = menu.replace("Altro", "")
    menu = menu.replace("\n", "\n-")
    menu = menu.replace("\n-\n", "\n")

    menu = menu.replace("MENU DEL GIORNO", "")
    menu = menu.replace("-PER PRENOTAZIONI CHIAMARE IL 3385305973 ~Lucia", "PER PRENOTAZIONI CHIAMARE IL 3385305973 ~Lucia")
    menu = menu.replace("-Buongiorno, oggi vi proponiamo: 🍽", "\nBuongiorno, oggi vi proponiamo: 🍽")
    menu = menu.replace("-PRIMI", "\nPRIMI 🍝")
    menu = menu.replace("-SECONDI", "\nSECONDI 🍖")
    menu = menu.replace("-CONTORNI", "\nCONTORNI 🍟🥦")
    menu = menu.replace("-INSALATE:", "\nINSALATE 🥗")
    menu = menu.replace("-DESSERT:", "\nDOLCI 🍰")
    menu = menu.replace("-FRUTTA:", "\nFRUTTA 🍎🍍🥛")
    menu = menu.replace("-PIATTI FREDDI:", "\nPIATTI FREDDI 🍱 ")
    menu = menu.replace("\n(", "(")

    # Aggiungi uno spazio dopo i trattini
    menu = menu.replace(" -", "-")
    menu = menu.replace("-", " - ")

    menu = lowercase_menu(menu)
    menu = menu + "\n\nVI ASPETTIAMO!"
    menu = menu.replace("inasalata", "insalata")
    menu = "MENÙ DOC 📝\n" + menu

    return menu


if __name__ == '__main__':
    os.environ["SECRETS"] = "secrets.json"
    print(get_menu("doc"))
    print(get_menu("dubai"))

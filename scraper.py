import json
import facebook_scraper
import datetime


def download_menu(resturant):
    account = ""
    if resturant == "dubai":
        account = "100087591040668"
    elif resturant == "doc":
        account = "selfservicedoctorino"
    else:
        print("Error: resturant not found")
        return

    posts = facebook_scraper.get_posts(account, pages=1, cookies="cookies.json")

    post = next(posts)
    while not is_menu(post, resturant) or not is_date_today(post['time']):
        post = next(posts)

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

    return menu
def is_menu(post,resturant): # questa è una porcata, ci deve essere modo più furbo di capire se è un nuovo menù
    if resturant == "dubai":
        return "Oggi vi proponiamo" in post["text"]
    else:
        return "MENU DEL GIORNO" in post["text"]

def is_date_today(date):
    today = datetime.datetime.today()
    return today.day == date.day and today.month == date.month and today.year == date.year


if __name__ == '__main__':
    print(get_menu("doc"))
    print(get_menu("dubai"))

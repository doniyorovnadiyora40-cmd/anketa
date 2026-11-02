import json

FAYL = "users.json"

def yuklash():
    try:
        with open(FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
def saqlash(users):
    with open(FAYL, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
def user_saqla(chat_id, ism, yosh, til):
    users = yuklash()
    users[str(chat_id)] = {
        "ism": ism,
        "yosh": yosh,
        "til": til
    }
    saqlash(users)
def user_ol(chat_id):
    users = yuklash()
    return users.get(str(chat_id))
def jami():
    users = yuklash()
    return len(users)
def til_boyicha():
    users = yuklash()
    natija = {}
    for i in users.values():
        natija[i["til"]] = natija.get(i["til"], 0) + 1
    return natija
def user_ochir(chat_id):
    users = yuklash()
    users.pop(str(chat_id), None)
    saqlash(users)

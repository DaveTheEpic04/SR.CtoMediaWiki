import requests as rq
from speedruncompy.endpoints import GetGameRecordHistory
from time import sleep
from datetime import datetime
from sys import exit
import os

# Gets the Username and Password for the mediawiki account
with open("hiddenVars.txt", "r") as f:
    USERNAME = f.readline().rstrip()
    PASSWORD = f.readline().rstrip()

SRC_API = "https://www.speedrun.com/api/v1/"
WIKI = "https://karlson.wiki/w/api.php" # Move to hiddenVars.txt

# Will delete after getting all categories from sr.c is done
GAMES = {"karlson_itch_io":{"GAME":"Karlson_(Itch.io)", "GAME_ID":"m1zjg926", "FULL_CATS":{"wk6n5xx2":"Any%", "7kj3ejx2":"All_Enemies", "jdrv5jx2":"Gunless"}, "IL_CATS":{"z27rq8gd":"Any%", "zdn0jeq2":"All_Enemies", "xk9royyk":"Gunless"}, "LEVELS":{"xd03lrmd":"Tutorial", "rw6erppd":"Sandbox_0", "n93yn22d":"Sandbox_1", "z98gz2rw":"Sandbox_2", "rdn2lk5d":"Escape_0", "ldy854pw":"Escape_1", "gdr18kew":"Escape_2", "nwlpyko9":"Escape_3", "ywemjzld":"Sky_0", "69znqmx9":"Sky_1", "r9g1jkj9":"Sky_2"}}}

# The requests session, used for cookies I think
WIKISESH = rq.Session()

# Causes the bot to only run once a day, will find a better way to do this later
def pause():
    sleep(3600)
    t = datetime.today()
    if t.hour <= 1:
        return

# Changes the time to look nicer
def convertTimes(time):
    minutes = int(time//60)
    if minutes == 0:
        return f"{int(time//1)}s {int(1000*(round(time%1, 3))):03d}ms"
    time = time-minutes*60
    return f"{minutes}m {int(time//1):02d}s {int(1000*(round(time%1, 3))):03d}ms"

# Gets the world record for a given game, category and level, need to add variables soon
def getWR(game, category, level=None):
    try:
        if level != None: # IL categories
            run = rq.get(f"{SRC_API}leaderboards/{game}/level/{level}/{category}?top=1&embed=players").json()['data']
            return (run['runs'][0]['run']['times']['primary_t'], run['players']['data'][0]['names']['international'], run['runs'][0]['run']['date'])
        # Full game categories
        run = rq.get(f"{SRC_API}leaderboards/{game}/category/{category}?top=1&embed=players").json()['data']
        return (run['runs'][0]['run']['times']['primary_t'], run['players']['data'][0]['names']['international'], run['runs'][0]['run']['date'])
    except KeyError:
        print(run)

# Nice looking
def formatDetails(details):
    date = details[2].split("-")
    return f"{convertTimes(details[0])} by {details[1]} as of {date[2]}/{date[1]}/{date[0]}\n"

# Required for all interactions with mediawiki
def getToken():
    login = WIKISESH.get(f"{WIKI}?action=query&format=json&meta=tokens&type=login").json()['query']['tokens']['logintoken']
    loginResp = WIKISESH.post(WIKI, data={"action":"login", "lgname":USERNAME, "lgpassword":PASSWORD, "lgtoken":login, "format":"json"}).json()
    try:
        csrf = WIKISESH.get(f"{WIKI}?action=query&format=json&meta=tokens").json()['query']['tokens']['csrftoken']
    except Exception:
        print(loginResp)
        exit()
    return csrf

# Gets the world record history, requires api v2 which is currently unstable
def getHistory(game, category, level=None):
    if level == None: # Full game categories
        header = "{| class=\"wikitable\"\n|+\n! colspan=\"3\"|" + game['FULL_CATS'][category].replace("_", " ") + "\n|-\n!Name\n!Run Time\n!Date (DD/MM/YYYY)\n"
        data = GetGameRecordHistory(gameId=game['GAME_ID'], categoryId=category).perform()
        players = {x['id']:x['name'] for x in data['playerList']}
        for run in data['runList']:
            runInfo = "|-\n|'''" + players[run['playerIds'][0]] + "'''\n|" + convertTimes(run['time']) + "\n|" + datetime.utcfromtimestamp(run['date']).strftime('%d/%m/%Y') + "\n"
            header = header + runInfo
        return header + "|}"
    else: # IL categories
        header = "{| class=\"wikitable\"\n|+\n! colspan=\"3\"|" + game['LEVELS'][level].replace("_", " ") + " (" + game['IL_CATS'][category].replace("_", " ") + ")\n|-\n!Name\n!Run Time\n!Date (DD/MM/YYYY)\n"
        data = GetGameRecordHistory(gameId=game['GAME_ID'], categoryId=category, levelId=level).perform()
        players = {x['id']:x['name'] for x in data['playerList']}
        for run in data['runList']:
            runInfo = "|-\n|'''" + players[run['playerIds'][0]] + "'''\n|" + convertTimes(run['time']) + "\n|" + datetime.utcfromtimestamp(run['date']).strftime('%d/%m/%Y') + "\n"
            header = header + runInfo
        return header + "|}"
    
# Sends all change requests to the mediawiki pages
def editWiki(title, text, token):
    resp = WIKISESH.post(WIKI, data={"action":"edit", "format":"json", "title":title, "text":text, "bot":True, "token":token}).json()
    print(resp)
    return resp
    
# Changes every page for the given category and level combinations, will have to add variables. I hate variables
def editAllHist(token, game):
    for cat in game['FULL_CATS']:
        title = f"Template:{game['GAME']}_{game['FULL_CATS'][cat]}_World_Record_History"
        hist = getHistory(game, cat)
        editWiki(title, hist, token)
    for cat in game['IL_CATS']:
        for level in game['LEVELS']:
            if cat == "zdn0jeq2" and level == "z98gz2rw":
                continue
            title = f"Template:{game['GAME']}_{game['IL_CATS'][cat]}_{game['LEVELS'][level]}_World_Record_History"
            hist = getHistory(game, cat, level)
            editWiki(title, hist, token)

# Changes only pages where the world record has changes, I have a feeling im not gonna like variables when I get to here. Mainly cause I already hate variables
def editSomeHist(token, game, cats):
    for cat in cats:
        if len(cat) == 2: # Full game categories
            title = f"Template:{game['GAME']}_{cat['name']}_World_Record_History"
            hist = getHistory(game, cat['cat'])
            editWiki(title, hist, token)
        else: # IL categories
            title = f"Template:{game['GAME']}_{cat['name']}_{cat['levelname']}_World_Record_History"
            hist = getHistory(game, cat['cat'], cat['level'])
            editWiki(title, hist, token)

# Changes all World Record pages and records the ones which have changed
def main(token, game):
    newWR = []
    for cat in game['FULL_CATS']:
        title = f"Template:{game['GAME']}_{game['FULL_CATS'][cat]}_WR"
        details = formatDetails(getWR(game['GAME_ID'], cat))
        resp = editWiki(title, details, token)
        if not('nochange' in resp['edit']):
            newWR.append({"cat":cat, "name":game['FULL_CATS'][cat]})
    for cat in game['IL_CATS']:
        for level in game['LEVELS']:
            if cat == "zdn0jeq2" and level == "z98gz2rw":
                continue
            title = f"Template:{game['GAME']}_{game['IL_CATS'][cat]}_{game['LEVELS'][level]}_WR"
            details = formatDetails(getWR(game['GAME_ID'], cat, level))
            resp = editWiki(title, details, token)
            if not('nochange' in resp['edit']):
                newWR.append({"cat":cat, "name":game['IL_CATS'][cat], "level":level, "levelname":game['LEVELS'][level]})
    editSomeHist(token, game, newWR)


if __name__ == "__main__":
    token = getToken()
    for game in GAMES.values(): # Updates all world record pages at the start of running
        print(game)
        editAllHist(token, game)
    while True:
        for game in GAMES.values(): # Will be useful for wikis spanning multiple games
            main(token, game)
        pause()
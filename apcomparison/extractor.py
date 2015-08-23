import time
import sqlite3
import requests
import re

api_key = "my_api_key"
#IDs of the AP items that were reworked
apItems = (3003, 3174, 3151, 3285, 3165, 3115, 3089, 3027, 3116, 3135, 3152, 3157)

#We don't want to make more than 500 calls every 10 minutes, so no more than 1 call every 1.25 seconds
API_TIME_PER_CALL = 1.25

#SQL vars
TABLE_BEFORE = 'before'
TABLE_AFTER = 'after'
SQL_MATCHID = 0
SQL_CHAMPIONID = 1
SQL_ITEM = 2
SQL_WINNER = 3
SQL_KILLS = 4
SQL_DEATHS = 5
SQL_ASSISTS = 6
SQL_KDA = 7
SQL_DMGDEALT = 8
SQL_DMGTAKEN = 9
SQL_MINIONS = 10
SQL_JUNGLE = 11
SQL_HEAL = 12
SQL_GOLD = 13
SQL_COLUMNS_COUNT = 14

if __name__ == '__main__':
    #We will store the extracted information in "lol_raw_data.db".
    sql = sqlite3.connect("lol_raw_data.db")
    cur = sql.cursor()
    sql.commit()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS before(
        matchId INTEGER NOT NULL,
        championId INTEGER NOT NULL,
        item INTEGER NOT NULL,
        winner BOOLEAN NOT NULL,
        kills INTEGER NOT NULL,
        deaths INTEGER NOT NULL,
        assists INTEGER NOT NULL,
        kda REAL NOT NULL,
        dmgDealt INTEGER NOT NULL,
        dmgTaken INTEGER NOT NULL,
        minions INTEGER NOT NULL,
        jungle INTEGER NOT NULL,
        heal INTEGER NOT NULL,
        gold INTEGER NOT NULL,
        PRIMARY KEY (matchId, championId, item, winner)
        )
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS after(
        matchId INTEGER NOT NULL,
        championId INTEGER NOT NULL,
        item INTEGER NOT NULL,
        winner BOOLEAN NOT NULL,
        kills INTEGER NOT NULL,
        deaths INTEGER NOT NULL,
        assists INTEGER NOT NULL,
        kda REAL NOT NULL,
        dmgDealt INTEGER NOT NULL,
        dmgTaken INTEGER NOT NULL,
        minions INTEGER NOT NULL,
        jungle INTEGER NOT NULL,
        heal INTEGER NOT NULL,
        gold INTEGER NOT NULL,
        PRIMARY KEY (matchId, championId, item, winner)
        )
        """)
    sql.commit()
    
    def lista_partidas(file):
        """Returns a list with all the match_ids given a filepath."""
        with open(file) as f:
            lista_temp = []
            lines = f.readlines()
            for linea in lines:
                lista_temp.append(re.sub("[\,\[\]]", "", linea.strip()))
            lista_temp = list(filter(None, lista_temp))
            return lista_temp
    
    def fillDB(matchIDsList, region, tableName):
        """ Given a list with match_ids (see lista_partidas()) and a string region ('EUW','NA','KR',etc.) 
        extracts all those matches information from Riot's API and stores it into tableName.
        """
        game_info = {'reg':region, 'matchid': 1234, 'api_key': api_key} #Initialize game_info. A valid 'matchid' will be provided before we call the API.
        #Initialize the counting variables:
        #Total Iterations: iterations over the match_id list where we call or not the API (just for informational purposes)
        iteraciones = 0
        #API iterations: iterations only where we call the API
        iteracionesAPI = 0
        #Total time spent using the API (including the sleeps)
        tiempoAPI = 0
        #A variable to compensate the slow API calls (those greater than 1.25 s), so that we can get as closer to the 1.25 seconds per api call, but always equal or above that.
        esperarAcumulado = 0.0
        #Let's iterate over the match_id list.
        for _matchid in matchIDsList:
            inicio = time.time()
            iteraciones += 1
            game_info['matchid'] = _matchid
            rows = cur.execute("SELECT * FROM "+tableName+" WHERE matchId = ?", (_matchid,)) #We look for the current matchid in our database
            if rows.fetchone() is not None: #If it's already on our database, we skip this iteration.
                print(_matchid, "It's already on the DB, we don't need to call the API again.")
                continue
            try:
                url = "https://{reg}.api.pvp.net/api/lol/{reg}/v2.2/match/{matchid}?api_key={api_key}".format(**game_info)
                r = requests.get(url)
                iteracionesAPI += 1
                data = r.json()
                #We get the response information and prepare it to be inserted in our database 
                insertar = ['.'] * SQL_COLUMNS_COUNT
                insertar[SQL_MATCHID] = data['matchId']
                #Let's iterate over the participants list to get their individual information (kills, deaths, items, etc.)
                for part in data['participants']:
                    insertar[SQL_CHAMPIONID] = part['championId']
                    insertar[SQL_KILLS] = part['stats']['kills']
                    insertar[SQL_DEATHS] = part['stats']['deaths']
                    insertar[SQL_ASSISTS] = part['stats']['assists']
                    deaths_division = 1 if insertar[SQL_DEATHS] == 0 else insertar[SQL_DEATHS]
                    insertar[SQL_KDA] = "%.2f" % (( insertar[SQL_KILLS] + insertar[SQL_ASSISTS] ) / deaths_division)
                    insertar[SQL_DMGDEALT] = part['stats']['totalDamageDealtToChampions']
                    insertar[SQL_DMGTAKEN] = part['stats']['totalDamageTaken']
                    insertar[SQL_MINIONS] = part['stats']['minionsKilled']
                    insertar[SQL_JUNGLE] = part['stats']['neutralMinionsKilled']
                    insertar[SQL_HEAL] = part['stats']['totalHeal']
                    insertar[SQL_GOLD] = part['stats']['goldEarned']
                    insertar[SQL_WINNER] = part['stats']['winner']
                    item0 = part['stats']['item0']
                    item1 = part['stats']['item1']
                    item2 = part['stats']['item2']
                    item3 = part['stats']['item3']
                    item4 = part['stats']['item4']
                    item5 = part['stats']['item5']
                    item6 = part['stats']['item6']
                    items = (item0, item1, item2, item3, item4, item5, item6)
                    #We insert this player information in the DB only if he used one or more items in the list of AP reworked items.
                    for item in [x for x in items if x in apItems]:
                        insertar[SQL_ITEM] = item
                        #insert in db
                        cur.execute("INSERT OR IGNORE INTO "+tableName+" VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", insertar)
                        sql.commit()
            except Exception as e:
                print(e)
            finally:
                #Now we measure the time taken to do all that work and take a sleep if necessary, to make sure we don't exceed the API quota.
                fin = time.time()
                duracion = fin - inicio
                esperar = API_TIME_PER_CALL - duracion
                if esperar < 0:
                    esperarAcumulado += esperar
                    esperar = 0
                else:
                    esperar += esperarAcumulado
                    esperarAcumulado = 0
                if esperar < 0:
                    esperarAcumulado = esperar
                    esperar = 0
                esperarAcumulado = esperarAcumulado if esperarAcumulado > -10 else -10
                print("Table ", tableName, "- Reg", region.upper(),"-", ("%.3f"%duracion), "seg. (wait", ("%.3f"%esperar), "s). Iter", iteraciones)
                if esperar > 0:
                    time.sleep(esperar)
                tiempoAPI += (time.time()-inicio)
                print("** Time/iter API:", ("%.3f"%(tiempoAPI/iteracionesAPI)),"(",("%.2f"%tiempoAPI),"/",iteracionesAPI,") ** Total = ", ("%.2f"%(time.time()-inicioAbsoluto)), "s")
                
                
    #Here we call the methods in order to fill the database with all the information from the games from all the regions
    inicioAbsoluto = time.time() #Measuring the total time spent, because why not.
    #We count how many games were already analyzed (in case this is not the first time we run the script), to be able to continue where we left it.
    rows_antes = cur.execute("SELECT COUNT(DISTINCT matchId) FROM "+TABLE_BEFORE).fetchone()[0]
    rows_despues = cur.execute("SELECT COUNT(DISTINCT matchId) FROM "+TABLE_AFTER).fetchone()[0]
    partidas_analizadas = rows_antes+rows_despues
    print("We already analyzed", partidas_analizadas, "games.")
    time.sleep(3) #Give me 3 seconds to read that message
    #And keep working from where we left the last time
    if partidas_analizadas < 9000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\EUW.json'), 'euw', TABLE_BEFORE)
    if partidas_analizadas < 19000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\EUW.json'), 'euw', TABLE_AFTER)
    if partidas_analizadas < 28000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\NA.json'), 'na', TABLE_BEFORE)
    if partidas_analizadas < 38000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\NA.json'), 'na', TABLE_AFTER)
    if partidas_analizadas < 47000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\EUNE.json'), 'eune', TABLE_BEFORE)
    if partidas_analizadas < 57000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\EUNE.json'), 'eune', TABLE_AFTER)
    if partidas_analizadas < 66000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\LAN.json'), 'lan', TABLE_BEFORE)
    if partidas_analizadas < 76000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\LAN.json'), 'lan', TABLE_AFTER)
    if partidas_analizadas < 85000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\OCE.json'), 'oce', TABLE_BEFORE)
    if partidas_analizadas < 95000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\OCE.json'), 'oce', TABLE_AFTER)
    if partidas_analizadas < 104000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\KR.json'), 'kr', TABLE_BEFORE)
    if partidas_analizadas < 114000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\KR.json'), 'kr', TABLE_AFTER)
    if partidas_analizadas < 123000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\BR.json'), 'br', TABLE_BEFORE)
    if partidas_analizadas < 133000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\BR.json'), 'br', TABLE_AFTER)
    if partidas_analizadas < 142000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\RU.json'), 'ru', TABLE_BEFORE)
    if partidas_analizadas < 152000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\RU.json'), 'ru', TABLE_AFTER)
    if partidas_analizadas < 161000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.11\RANKED_SOLO\LAS.json'), 'las', TABLE_BEFORE)
    if partidas_analizadas < 171000:
        fillDB(lista_partidas(r'D:\Users\Sergio\Desktop\AP_ITEM_DATASET\5.14\RANKED_SOLO\LAS.json'), 'las', TABLE_AFTER)
    input("@@@@## We analyzed all the regions ##@@@@")
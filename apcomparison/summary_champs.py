''' SUMMARY_CHAMPS_BEFORE:
    champId, itemId, winrate, killsAvg, deathsAvg, assistsAvg, kdaAvg, dmgDealtAvg, dmgTakenAvg, minionsAvg, jungleAvg, goldAvg, healAvg '''

import sqlite3
import requests
import os
from apcomparison import extractor
import pickle

#SQL vars
TABLE_SUMMARY_CHAMPS_BEFORE = 'summaryChampsBefore'
TABLE_SUMMARY_CHAMPS_AFTER = 'summaryChampsAfter'
SQL_COLUMNS_COUNT = 14
SQL_CHAMP = 0
SQL_ITEM = 1
SQL_WINRATE = 2
SQL_KILLS = 3
SQL_DEATHS = 4
SQL_ASSISTS = 5
SQL_KDA = 6
SQL_DMGDEALT = 7
SQL_DMGTAKEN = 8
SQL_MINIONS = 9
SQL_JUNGLE = 10
SQL_HEAL = 11
SQL_GOLD = 12
CUENTA = 13

if __name__ == '__main__':
    
    #We will get the raw information from all the games from lol_raw_data.db and store the processed info about the champions in champs_data.db
    sql2 = sqlite3.connect("lol_raw_data.db")
    cur2 = sql2.cursor()
    sql = sqlite3.connect("champs_data.db")
    cur = sql.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summaryChampsBefore(
        champ INTEGER NOT NULL,
        item INTEGER NOT NULL,
        winrate REAL NOT NULL,
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
        samples INTEGER NOT NULL,
        PRIMARY KEY (champ, item)
        )
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summaryChampsAfter(
        champ INTEGER NOT NULL,
        item INTEGER NOT NULL,
        winrate REAL NOT NULL,
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
        samples INTEGER NOT NULL,
        PRIMARY KEY (champ, item)
        )
        """)
    sql.commit()
    
    #We need the list of ids for all the champions. We will store them in a file so that we don't need to ask for them to the API ever again.
    filename = "campeonesIds.txt"
    campeones = []
    #If we don't have the file with the champions Ids we will have to ask the API
    if not os.path.isfile(filename):
        print("We ask the API for the champions list")
        game_info = {'api_key': extractor.api_key}
        url = "https://global.api.pvp.net/api/lol/static-data/euw/v1.2/champion?api_key={api_key}".format(**game_info)
        r = requests.get(url)
        
        data = r.json()
        for nombre in data['data']:
            campeones.append(data['data'][nombre]['id'])
        #We store the champions list in a file
        with open(filename, 'wb') as f:
            pickle.dump(campeones, f)
    #If we already had the file with the champions Ids, we just read it.
    else:
        print("We don't need to ask the API for the champions list, because we already have it!")
        with open(filename, 'rb') as f:
            campeones = pickle.load(f)
    print(campeones) #Just to make sure there are champions Ids there, no potatoes.
        
    #IDs of the AP items that were reworked
    apItems = (3003, 3174, 3151, 3285, 3165, 3115, 3089, 3027, 3116, 3135, 3152, 3157)
        
    
    def hacerMedias(tableRead, tableWriteResults):
        """ Given a table with the items raw information it processes all and stores the average stats for every champion using each item in another table. """
        itemsInfo = [None] * len(apItems) #3-dimensional array -> itemsInfo[apItems_Index][campeones_Index]
        for i in range(len(apItems)):
            itemsInfo[i] = [0] * len(campeones)
            for j in range(len(campeones)):
                itemsInfo[i][j] = [0] * SQL_COLUMNS_COUNT
                itemsInfo[i][j][SQL_CHAMP] = campeones[j]
                itemsInfo[i][j][SQL_ITEM] = apItems[i]
                itemsInfo[i][j][CUENTA] = 0
        
        #We get all the raw information
        cur2.execute("SELECT * FROM "+tableRead)
        rows = cur2.fetchall()
        #We sum every stat to its corresponding champion and item
        for row in rows:
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_WINRATE] += row[extractor.SQL_WINNER]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_KILLS] += row[extractor.SQL_KILLS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_DEATHS] += row[extractor.SQL_DEATHS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_ASSISTS] += row[extractor.SQL_ASSISTS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_KDA] += row[extractor.SQL_KDA]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_DMGDEALT] += row[extractor.SQL_DMGDEALT]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_DMGTAKEN] += row[extractor.SQL_DMGTAKEN]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_MINIONS] += row[extractor.SQL_MINIONS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_JUNGLE] += row[extractor.SQL_JUNGLE]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_HEAL] += row[extractor.SQL_HEAL]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][SQL_GOLD] += row[extractor.SQL_GOLD]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][campeones.index(row[extractor.SQL_CHAMPIONID])][CUENTA] += 1
        #And now we make the averages for every champion and item
        for i, items in enumerate(itemsInfo):
            for j, info in enumerate(items):
                cuenta = info[CUENTA] #This is where we counted the total number of samples per item
                if cuenta == 0: #If this item has not been used by this champ, don't bother calculating and inserting it in the DB.
                    continue
                info[SQL_WINRATE] /= cuenta
                info[SQL_KILLS] /= cuenta
                info[SQL_DEATHS] /= cuenta
                info[SQL_ASSISTS] /= cuenta
                deaths_division = 1 if info[SQL_DEATHS] == 0 else info[SQL_DEATHS]
                info[SQL_KDA] = (info[SQL_KILLS] + info[SQL_ASSISTS]) / deaths_division
                info[SQL_DMGDEALT] /= cuenta
                info[SQL_DMGTAKEN] /= cuenta
                info[SQL_MINIONS] /= cuenta
                info[SQL_JUNGLE] /= cuenta
                info[SQL_HEAL] /= cuenta
                info[SQL_GOLD] /= cuenta
                #Format appropriately the decimal numbers
                info[SQL_WINRATE] = "%.4f" % info[SQL_WINRATE]
                info[SQL_KILLS] = "%.2f" % info[SQL_KILLS]
                info[SQL_DEATHS] = "%.2f" % info[SQL_DEATHS]
                info[SQL_ASSISTS] = "%.2f" % info[SQL_ASSISTS]
                info[SQL_KDA] = "%.2f" % info[SQL_KDA]
                info[SQL_DMGDEALT] = "%.0f" % info[SQL_DMGDEALT]
                info[SQL_DMGTAKEN] = "%.0f" % info[SQL_DMGTAKEN]
                info[SQL_MINIONS] = "%.1f" % info[SQL_MINIONS]
                info[SQL_JUNGLE] = "%.1f" % info[SQL_JUNGLE]
                info[SQL_HEAL] = "%.0f" % info[SQL_HEAL]
                info[SQL_GOLD] = "%.0f" % info[SQL_GOLD]
                #Save this data in the DB
                cur.execute("INSERT OR REPLACE INTO "+tableWriteResults+" VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", info)
                sql.commit()
        #Optionally we can print in the console all the data of the DB (just for debugging)
        '''cur.execute("SELECT * FROM "+tableWriteResults)
        rows = cur.fetchall()
        nombres = [None] * len(cur.description)
        for i in range(len(nombres)):
            nombres[i] = cur.description[i][0]
        print("Base de datos:\n***************\n", nombres)
        for row in rows:
            print(row)'''
            
    
    #We fill the before-table with data from patch 5.11 (before the rework)
    hacerMedias(extractor.TABLE_BEFORE, TABLE_SUMMARY_CHAMPS_BEFORE)
    #And the after-table with data from patch 5.14 (after the rework)
    hacerMedias(extractor.TABLE_AFTER, TABLE_SUMMARY_CHAMPS_AFTER)
    print("Champions processed correctly")
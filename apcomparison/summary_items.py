''' SUMMARY_ITEMS_BEFORE:
    itemId, winrate, killsAvg, deathsAvg, assistsAvg, kdaAvg, dmgDealtAvg, dmgTakenAvg, minionsAvg, jungleAvg, goldAvg, healAvg '''

import sqlite3
from apcomparison import extractor

#SQL vars
TABLE_SUMMARY_ITEMS_BEFORE = 'summaryItemsBefore'
TABLE_SUMMARY_ITEMS_AFTER = 'summaryItemsAfter'
SQL_COLUMNS_COUNT = 13
SQL_ITEM = 0
SQL_WINRATE = 1
SQL_KILLS = 2
SQL_DEATHS = 3
SQL_ASSISTS = 4
SQL_KDA = 5
SQL_DMGDEALT = 6
SQL_DMGTAKEN = 7
SQL_MINIONS = 8
SQL_JUNGLE = 9
SQL_HEAL = 10
SQL_GOLD = 11
CUENTA = 12

if __name__ == '__main__':
    
    #We will get the raw information from all the games from lol_raw_data.db and store the processed info about the items in items_data.db
    sql2 = sqlite3.connect("lol_raw_data.db")
    cur2 = sql2.cursor()
    sql = sqlite3.connect("items_data.db")
    cur = sql.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summaryItemsBefore(
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
        PRIMARY KEY (item)
        )
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summaryItemsAfter(
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
        PRIMARY KEY (item)
        )
        """)
    sql.commit()
    
    #IDs of the AP items that were reworked
    apItems = (3003, 3174, 3151, 3285, 3165, 3115, 3089, 3027, 3116, 3135, 3152, 3157)
    
    def hacerMedias(tableRead, tableWriteResults):
        """ Given a table with the items raw information it processes all and stores the average stats for every item in another table. """
        itemsInfo = [None] * len(apItems)
        for i in range(len(apItems)):
            itemsInfo[i] = [0] * SQL_COLUMNS_COUNT
            itemsInfo[i][SQL_ITEM] = apItems[i]
            itemsInfo[i][CUENTA] = 0
        
        #We get all the raw information
        cur2.execute("SELECT * FROM "+tableRead)
        rows = cur2.fetchall()
        #We sum every stat to its corresponding item
        for row in rows:
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_WINRATE] += row[extractor.SQL_WINNER]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_KILLS] += row[extractor.SQL_KILLS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_DEATHS] += row[extractor.SQL_DEATHS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_ASSISTS] += row[extractor.SQL_ASSISTS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_KDA] += row[extractor.SQL_KDA]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_DMGDEALT] += row[extractor.SQL_DMGDEALT]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_DMGTAKEN] += row[extractor.SQL_DMGTAKEN]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_MINIONS] += row[extractor.SQL_MINIONS]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_JUNGLE] += row[extractor.SQL_JUNGLE]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_HEAL] += row[extractor.SQL_HEAL]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][SQL_GOLD] += row[extractor.SQL_GOLD]
            itemsInfo[apItems.index(row[extractor.SQL_ITEM])][CUENTA] += 1
        #And now we make the averages for every item
        for index, info in enumerate(itemsInfo):
            cuenta = info[CUENTA] #This is where we counted the total number of samples per item
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
            cur.execute("INSERT OR REPLACE INTO "+tableWriteResults+" VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", info)
            sql.commit()
            
        #Optionally we can print in the console all the data of the DB (just for debugging)
        '''cur.execute("SELECT * FROM "+tableWriteResults)
        rows = cur.fetchall()
        nombres = [None] * len(cur.description)
        for i in range(len(nombres)):
            nombres[i] = cur.description[i][0]
        print("DataBase:\n***************\n", nombres)
        for row in rows:
            print(row)'''
        

    #We fill the before-table with data from patch 5.11 (before the rework)
    hacerMedias(extractor.TABLE_BEFORE, TABLE_SUMMARY_ITEMS_BEFORE)
    #And the after-table with data from patch 5.14 (after the rework)
    hacerMedias(extractor.TABLE_AFTER, TABLE_SUMMARY_ITEMS_AFTER)
    print("Items processed correctly")
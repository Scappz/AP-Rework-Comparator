import pickle
import os
import time
import requests
import json
import sqlite3
import pprint
from apcomparison import extractor

#SQL columns names in items_data.db
sql_0 = "item"
sql_1 = "winrate"
sql_2 = "kills"
sql_3 = "deaths"
sql_4 = "assists"
sql_5 = "kda"
sql_6 = "dmgDealt"
sql_7 = "dmgTaken"
sql_8 = "minions"
sql_9 = "jungle"
sql_10 = "heal"
sql_11 = "gold"
sql_12 = "name"
        
#We will get the summarized information from items_data.db and create a json file with it for the website
sql = sqlite3.connect("items_data.db")
cur = sql.cursor() 
cur2 = sql.cursor()
cur.execute("SELECT * FROM summaryItemsBefore")
data = cur.fetchall() #data will hold all the information from before

'''
JSON Format:
It is a list of items. Each item has an itemId and all the stats. Every stat has a before and after, representing the average of that stat before and after the rework.
Like this:

[
    { item: itemId,
      kills: {before: x, after: x},
      gold: {before: x, after: x},
            ...
    },
    { item: itemId, kills {}, ...},
    ...
]

'''
#ITEMS

#We need the list of names for all the reworked items. We will store them in a file so that we don't need to ask for them to the API ever again.
filename = "itemsKeys.txt"
itemsNames = {}
#If we don't have the file with the items names, we ask the names to the API and create the file to store them
if not os.path.isfile(filename):
    print("We ask the API for the items names")
    itemsIds = (3003, 3174, 3151, 3285, 3165, 3115, 3089, 3027, 3116, 3135, 3152, 3157)
    for itemId in itemsIds:
        inicio = time.time()
        try:
            url = "https://global.api.pvp.net/api/lol/static-data/euw/v1.2/item/{itemid}?api_key={api_key}".format(**{'itemid':itemId, 'api_key':extractor.api_key})
            r = requests.get(url)
            data = r.json()
            itemsNames[itemId] = data['name']
        except Exception as e:
            print(e)
        finally:
            #We don't want to exceed the API quota, so we wait between calls if necessary
            esperar = extractor.API_TIME_PER_CALL - (time.time() - inicio)
            if esperar > 0:
                print("Esperamos", esperar,"segundos por la API")
                time.sleep(esperar)
    #We store the items names in a file
    with open(filename, 'wb') as f:
        pickle.dump(itemsNames, f)
#If we already have the file with the names, we read it
else:
    print("We don't need to ask the API for the items names, because we already know them")
    with open(filename, 'rb') as f:
        itemsNames = pickle.load(f)
print(itemsNames) #I love to see information in the console.

#Now we iterate through the items, and store the summarized info from before and after the rework into the json
datos = []
for row1 in data:
    cur2.execute("SELECT * FROM summaryItemsAfter WHERE item = ?", (row1[0],))
    data2 = cur2.fetchone() #data2 will hold all the information of a given item from after the rework
    print(data2)
    itemInfo = {}
    itemInfo[sql_0] = row1[0]
    itemInfo[sql_1] = {"before": row1[1], "after": data2[1]}
    itemInfo[sql_2] = {"before": row1[2], "after": data2[2]}
    itemInfo[sql_3] = {"before": row1[3], "after": data2[3]}
    itemInfo[sql_4] = {"before": row1[4], "after": data2[4]}
    itemInfo[sql_5] = {"before": row1[5], "after": data2[5]}
    itemInfo[sql_6] = {"before": row1[6], "after": data2[6]}
    itemInfo[sql_7] = {"before": row1[7], "after": data2[7]}
    itemInfo[sql_8] = {"before": row1[8], "after": data2[8]}
    itemInfo[sql_9] = {"before": row1[9], "after": data2[9]}
    itemInfo[sql_10] = {"before": row1[10], "after": data2[10]}
    itemInfo[sql_11] = {"before": row1[11], "after": data2[11]}
    itemInfo[sql_12] = itemsNames[row1[0]]
    datos.append(itemInfo)

#Save the json file
with open("itemsSummary.json", "w") as f:
    json.dump(datos, f)
   
print("itemsSummary.json saved successfully.")



#CHAMPIONS

#SQL columns names in champs_data.db
sql_0 = "champ"
sql_1 = "item"
sql_2 = "winrate"
sql_3 = "kills"
sql_4 = "deaths"
sql_5 = "assists"
sql_6 = "kda"
sql_7 = "dmgDealt"
sql_8 = "dmgTaken"
sql_9 = "minions"
sql_10 = "jungle"
sql_11 = "heal"
sql_12 = "gold"
sql_13 = "name"
        
#We will get the summarized information from champs_data.db and create a json file with it for the website
sql = sqlite3.connect("champs_data.db")
cur = sql.cursor() 
cur2 = sql.cursor()
cur.execute("SELECT * FROM summaryChampsBefore")
data = cur.fetchall() #data will hold all the information from before
'''
JSON Format:
It is a list of champions. Each champion has a list of items. Each item has an itemId and all the stats. Every stat has a before and after, representing the average of that stat before and after the rework.
Like this:
      
[
    {
        "champ" : champId,
        "key" : key,
        "items": [
                    { item: itemId,
                      kills: {before: x, after: x},
                      gold: {before: x, after: x},
                            ...
                    },
                    { item: itemId, kills {}, ...},
                    ...
                ]
    },
    ...
]
'''
#Now we iterate through the champions and items, and store the summarized info from before and after the rework into the json
campeones = {}
for row1 in data:
    cur2.execute("SELECT * FROM summaryChampsAfter WHERE champ = ? AND item = ?", (row1[0], row1[1]))
    data2 = cur2.fetchone() #data2 holds the information of a given champ and a given item from after the rework
    print(data2)
    #If there's no information from that item being used by that champion after the rework means that we have nothing to compare with. Skip this iteration
    if data2 is None:
        continue
    if row1[13] < 10 or data2[13] < 10: #Minimum sample size must be of 10 games for each champion using that item, both before and after the rework
        continue
    itemInfo = {}
    datos = {}
    itemInfo[sql_2] = {"before": row1[2], "after": data2[2]}
    itemInfo[sql_3] = {"before": row1[3], "after": data2[3]}
    itemInfo[sql_4] = {"before": row1[4], "after": data2[4]}
    itemInfo[sql_5] = {"before": row1[5], "after": data2[5]}
    itemInfo[sql_6] = {"before": row1[6], "after": data2[6]}
    itemInfo[sql_7] = {"before": row1[7], "after": data2[7]}
    itemInfo[sql_8] = {"before": row1[8], "after": data2[8]}
    itemInfo[sql_9] = {"before": row1[9], "after": data2[9]}
    itemInfo[sql_10] = {"before": row1[10], "after": data2[10]}
    itemInfo[sql_11] = {"before": row1[11], "after": data2[11]}
    itemInfo[sql_12] = {"before": row1[12], "after": data2[12]}
    itemInfo['samples'] = {"before": row1[13], "after": data2[13]}
    datos[row1[1]] = itemInfo
    if row1[0] in campeones.keys():
        campeones[row1[0]].update(datos)
    else:
        campeones[row1[0]] = datos


#We need the champions names (keys) for each champion id. We will store them in a file so that we don't need to ask for them to the API ever again.
filename = "campeonesKeys.txt"
campeonesKeys = {}
#If we don't know the names yet, we ask the API and store them in the corresponding file.
if not os.path.isfile(filename):
    print("We ask the API for the champions keys")
    campeonesIds = []
    with open("campeonesIds.txt", 'rb') as f:
            campeonesIds = pickle.load(f)
    for champId in campeonesIds:
        inicio = time.time()
        try:
            url = "https://global.api.pvp.net/api/lol/static-data/euw/v1.2/champion/{champId}?api_key={api_key}".format(**{'champId':champId, 'api_key':extractor.api_key})
            r = requests.get(url)
            data = r.json()
            campeonesKeys[champId] = data['key']
        except Exception as e:
            print(e)
        finally:
            #Always with caution not to exceed the API quota
            esperar = extractor.API_TIME_PER_CALL - (time.time() - inicio)
            if esperar > 0:
                print("Wait", esperar,"seconds for the next API call.")
                time.sleep(esperar)
    #Save the names into the file
    with open(filename, 'wb') as f:
        pickle.dump(campeonesKeys, f)
#If we already have the file with the names, we just read it.
else:
    print("We don't ask the API for the champions keys. We already know them.")
    with open(filename, 'rb') as f:
        campeonesKeys = pickle.load(f)
print(campeonesKeys)
#And we put all the information in the right format (list of lists)
campeones2 = []
for campeon in campeones:
    try:
        items = []
        campeon2 = {sql_0 : campeon, "key":campeonesKeys[campeon], "items": items}
        campeones2.append(campeon2)
        for item in campeones[campeon]:
            nuevoItem = {}
            nuevoItem[sql_1] = item
            nuevoItem[sql_2] = campeones[campeon][item][sql_2]
            nuevoItem[sql_3] = campeones[campeon][item][sql_3]
            nuevoItem[sql_4] = campeones[campeon][item][sql_4]
            nuevoItem[sql_5] = campeones[campeon][item][sql_5]
            nuevoItem[sql_6] = campeones[campeon][item][sql_6]
            nuevoItem[sql_7] = campeones[campeon][item][sql_7]
            nuevoItem[sql_8] = campeones[campeon][item][sql_8]
            nuevoItem[sql_9] = campeones[campeon][item][sql_9]
            nuevoItem[sql_10] = campeones[campeon][item][sql_10]
            nuevoItem[sql_11] = campeones[campeon][item][sql_11]
            nuevoItem[sql_12] = campeones[campeon][item][sql_12]
            nuevoItem[sql_13] = itemsNames[item]
            nuevoItem['samples'] = campeones[campeon][item]['samples']
            items.append(nuevoItem)
    except Exception as e:
        print("ERROR")
        print(e)
    
#And save the json file
with open("champsSummary.json", "w") as f:
    json.dump(campeones2, f)

print("champsSummary.json saved successfully.")
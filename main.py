from ftplib import FTP
from pypresence import Presence
from hashlib import sha1 
import hmac
import requests
import re
import time
AppID = "1474289681125605376"



#Get Game Inforamtion Such As Cusa ID like CUSA17419 - Persona 5 Royal Using FTP
def get_Game_Info(type):
    #Initialize FTP
    ftp = FTP()
    respond = []
    #Trying Connect to PS4 using FTP
    try:
        #Connecting 
        ftp.connect(host="0.0.0.0", port=2121)
        #Going to mnt/sandbox
        ftp.cwd("mnt/sandbox")
        #Check a mnt/sandbox Because this Directory Store Temp File of Currently Running apps
        ftp.dir(respond.append)
    except:
        # If IP of console is wrong or it is offline we return NoN means Not Online
        print("PS4 Not Found")
        return("NoN")
    #check For all CUSA ID's
    respond = re.findall("CUSA.*?_000",str(respond))
    #Close Connection with PS4
    ftp.quit()
    #If Sandbox folder Don't Have Any CUSA Folders means player in menu 
    if respond == "[]":
        respond = "Menu"
        return "Menu"
    else:
        respond = str(respond).replace("_000']","")
        respond = str(respond).replace("['","")
    id = f"{respond}_00"
    id = str(id)
    if id == "[]_00":
        return "Menu"
    #using Sony server for checking with game name corespond to CUSA id also we get a Cover for a game 
    #creating key for access Sony API
    tmdb_key = bytearray.fromhex('F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0')
    id_hash = hmac.new(tmdb_key, bytes(id, "utf-8"), sha1)
    id_hash = id_hash.hexdigest().upper()
    url = f"http://tmdb.np.dl.playstation.net/tmdb2/{id}_{id_hash}/{id}.json"
   
    #making a request to website with key 
    rq = requests.get(url)
    rq = str(rq.json())
    icon = re.findall("http://gs2-sec.ww.prod.dl.playstation.net/gs2-sec/appkgo/prod/.*?_00/.*?/i_.*?/.*?/icon0.png",rq)
    icon = str(icon).replace("']","")
    icon = icon.replace("['","")
    name = re.findall("'name': '.*?'",rq)
    name = str(name[0]).replace("'name': '","")
    name = name.replace("'","")
    #Return Options 
    #Return Cover
    if type == "icon":
        print(icon)
        return str(icon)
    #Return Name
    elif type == "name":
        return str(name)
    #Return Menu if any of this opeions is not selected
    else:
        return "Menu"
stat = True

#check Does discord is currently running
def discord_detect():
    import subprocess
    return bool(subprocess.call(
        ["pgrep", "-x", "Discord"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0)
    
    

#initialize Discord Presence
Discord = Presence(AppID)

while True:
    #if Discord is Running we try to show a Game
    if discord_detect() == True:
        #if Game info not NoN and Stat is True we connect to Discord and Display a Game
        if stat == True and get_Game_Info("name") != "NoN":
            try:
                #connecting
                print("Connecting to Discord")
                Discord.connect()
                #Updating
                print("Updating Game")
                Discord.update(pid=0,small_text="TEST",large_image=f"{get_Game_Info("icon")}",details=f"Playing {get_Game_Info("name")}",state="on PlayStation 4",name=f"{get_Game_Info("name")}",large_text=f"{get_Game_Info("name")}")
                print("Game Updated")
                #puting stat to false means we connected to discord and we dont need connect to it again
                stat = False
            except:
                time.sleep(10)    
        #if we alredy connect to discord and gameinfo not Non, Change it     
        elif stat == False and get_Game_Info("name") != "NoN":
            try:
                #clar old one
                print("Cleaing Old Game")
                Discord.clear(pid=0)
                #update with new one
                print("Updating game")
                Discord.update(pid=0,small_text="TEST",large_image=f"{get_Game_Info("icon")}",details=f"Playing {get_Game_Info("name")}",state="on PlayStation 4",name=f"{get_Game_Info("name")}",large_text=f"{get_Game_Info("name")}")
                print("Game Updated")
                #time oout for 60 sec
                time.sleep(60)
            except:
                time.sleep(10) 
        #if get_Game_Info is NonN we try ti disconnect from Discord and clear game name
        elif get_Game_Info("name") == "NoN":
            print("PlayStation was not found Trying again in 30s")
            try:
                #clear game name 
                Discord.clear(0)
                #disconnect from discord
                Discord.close()
                if stat != True:stat = True
            except:
                if stat != True:stat = True
            #time out for 30sec
            time.sleep(30)
    #if Discord is not found we put app into sleep mode 
    else:
        print("Discord is Not Found trying again after 20s")
        if stat != True:stat = True
        time.sleep(20)  

from typing import Generator,Dict
from psutil import Process, process_iter, pids, version_info
from threading import Timer
import json
import requests
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


plash_creen = Tk()
plash_creen.overrideredirect(True)
plash_label = Label(plash_creen,text='Loading...',font=12)
plash_label.pack(pady=18)

w = 200 # width for the Tk root
h = 60 # height for the Tk root

# get screen width and height
ws = plash_creen.winfo_screenwidth() # width of the screen
hs = plash_creen.winfo_screenheight() # height of the screen


x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
plash_creen.geometry('%dx%d+%d+%d' % (w, h, x, y))

run = True
ver = requests.get('https://ddragon.leagueoflegends.com/api/versions.json',verify=False)
version = json.loads(ver.text)
def mainwindow():
    plash_creen.destroy()
    #Parse CMD
    def parse_cmdline_args(cmdline_args) -> Dict[str, str]:
        cmdline_args_parsed = {}
        for cmdline_arg in cmdline_args:
            if len(cmdline_arg) > 0 and '=' in cmdline_arg:
                key, value = cmdline_arg[2:].split('=')
                cmdline_args_parsed[key] = value
        return cmdline_args_parsed
    pid = pids()  
    #Get the process of the Client
    def _return_ux_process() -> Generator[Process, None, None]:
        for process in process_iter():
            if process.name() in ['LeagueClientUx.exe', 'LeagueClientUx']:
                yield process
            

        
    print("size of process: ",len(pid))
    process = next(_return_ux_process(), None)



    print(process)

    def getProcess_args(index):
        process_arg = parse_cmdline_args(process.cmdline())
        return process_arg[index];

    def getAppPort():
        appPort = int(getProcess_args('app-port'))
        return appPort

    def getAuth_key():
        auth_key = getProcess_args('remoting-auth-token')
        return auth_key


    #connection
    header =  {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }





    # print(getAuth_key())






    # print(getSession(auth_key))
    #get url 
    def produce_url(endpoint: str,**kwargs):
        url = f'https://127.0.0.1:{getAppPort()}{endpoint}'
        if 'path' in kwargs:
            url = url.format(**kwargs['path'])
            kwargs.pop('path')
        return url

    # print(produce_url('/'))

    def id():
        id = requests.get(produce_url('/lol-champ-select/v1/session'),auth=('riot', getAuth_key()),verify=False)
        x = json.loads(id.text)
        if 'actions' not in x and 'localPlayerCellId' not in x:
            return -1
        else:
            actions = x['actions']
            localPlayerCellId  = x['localPlayerCellId']
            # print(localPlayerCellId,actions)
            ids = 0
            for i in range(0,len(actions[0])):
                if actions[0][i]["actorCellId"] == localPlayerCellId:
                    ids = actions[0][i]['id']
                    return ids
            

    #select Champions
    def pick(ids,chamID):
        data = '{"championId":%d}' % chamID
        requests.patch(produce_url('/lol-champ-select/v1/session/actions/%d' % ids),data,auth=('riot', getAuth_key()),verify=False)


    #lock Champions
    def lock(ids):
        requests.post(produce_url('/lol-champ-select/v1/session/actions/%d/complete' % ids),auth=('riot', getAuth_key()),verify=False)

    #Found a match
    def isMatchFound():
        getState = requests.get(produce_url('/lol-matchmaking/v1/ready-check'),auth=('riot', getAuth_key()),verify=False)
        res = json.loads(getState.text)
        if 'state' not in res:
            return False
        else:
            return res['state'] == 'InProgress'
    

    #accept Match
    def acceptMatch():
        requests.post(produce_url('/lol-matchmaking/v1/ready-check/accept'),auth=('riot', getAuth_key()),verify=False)


    #get owned champions minimal
    def ownedChampions():
        owned =requests.get(produce_url('/lol-champions/v1/owned-champions-minimal'),auth=('riot', getAuth_key()),verify=False)
        owned = json.loads(owned.text)
        return owned

    #notification
    noti = ['Cảnh báo!','Vui lòng bật Client Game để tiếp tục!','Bắt đầu AutoClient...','Hoàn tất!','Xác Nhận',
            'Tự động chấp nhận trận đấu.',"Chọn tướng hiện có:",'Lỗi!',
             'Phiên bản quá hạn. Vui lòng tải về phiên bản mới!']


    #start for tool
    def start(chamID):
        global run   
        if isMatchFound():
            acceptMatch()
        else:
            ids = id()
            if ids > -1:
                pick(ids,chamID)
                lock(ids)
                Label(window,fg='green',text=noti[3], pady=15).grid(column=1,row=6)
                run =False
        if run:
            Timer(0.25,start(chamID)).start()
        if not run:
            run = True


    ###################################################################
    #Create GUI for tool
    #window setup
    global version
    versionDefault = '11.23.1'
    window = Tk()
    window.title('AutoClient-v'+versionDefault)
    window.iconbitmap('./icon.ico')

    w = 400 # width for the Tk root
    h = 200 # height for the Tk root

    # get screen width and height
    ws = window.winfo_screenwidth() # width of the screen
    hs = window.winfo_screenheight() # height of the screen


    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))


    #ComboBox
    ttk.Label(window, text = noti[6],
            font = ("Times New Roman", 11)).grid(column = 0,
            row = 1, pady = 20)


    monthchoosen = ttk.Combobox(window)
    


    #messagebox
    indexOfYasuo = 0
    if not process:
        if messagebox.showwarning(noti[0], noti[1]):
            window.destroy()
    elif version[0] != versionDefault:
        if messagebox.showerror(noti[7], noti[8]):
            window.destroy()
    else:
        #List of Champions
        listOfOwned = ownedChampions()
        listOfAlias = []
        listOfChampion = {}
        for i in range(len(listOfOwned)):
            listOfAlias.append(listOfOwned[i]['alias'])
            listOfChampion[listOfOwned[i]['alias']] = listOfOwned[i]['id']
            if listOfOwned[i]['alias']== 'Yasuo':
                indexOfYasuo = i
        
        monthchoosen['values'] = listOfAlias
        monthchoosen.grid(column = 1, row = 1)
        if indexOfYasuo:
            monthchoosen.current(indexOfYasuo)
        else: 
            monthchoosen.current(0)

    #Handle button
    def ButtonHandle():
        if not monthchoosen.get():
            window.destroy()
        else:
            AliasChoosen = monthchoosen.get()
            idChamps=listOfChampion[AliasChoosen]
            start(idChamps)
            



    #Button for accept
    Button(window,text=noti[4],command=ButtonHandle,activebackground='#0173D0',padx=5,pady=5).grid(column=1, row=5)

    #Note
    Label(window,text='Lưu ý: Tool sẽ dừng').grid(column=1,row=3)
    Label(window,text='sau khi pick và lock tướng.',pady=10).grid(column=1,row=4)
    # Label(window,text='Copyright by TMT032').grid(column=0,row=7)


#callback MainWindow
plash_creen.after(3000,mainwindow)
#start GUI
mainloop()


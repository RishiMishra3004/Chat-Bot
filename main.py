import customtkinter
import tkinter as tk
import tkinter
import requests
from termcolor import colored
import sys
import time,pymongo
client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
database = client['Chat_history']
coll2023 = database['Chat_History_2023']
app = customtkinter.CTk()
app.geometry("1920x1080")
app.title("DIGIBOT")
rasa_server_url = "http://localhost:5005" 
conversationid = "default"
chat_count = 0
save_chat = True
chat_header = ""
def LoadChatHistory(header):
    Output_box.configure(state='normal')
    Output_box.delete(0.0,"end")
    doc = coll2023.find_one({'id':header},{"id":0})
    Output_box.configure(state='disabled')
    if doc is not None:
        l = int(len(doc.get("convo",{}))/2)
        for i in range(0,l):
            user_message = str(doc.get("convo",{}).get(str(i),{}))
            response_message = str(doc.get("convo",{}).get(str(i)+"r",{}))
            Output_box.tag_config("1", foreground = "Yellow")
            Output_box.tag_config("2", foreground = "green")
            Output_box.configure(state='normal')
            Output_box.insert(tkinter.END, "You->")
            Output_box.insert(tkinter.END, user_message+"\n", "1")
            Output_box.insert(tkinter.END, "RASA-> ")
            Output_box.insert(tkinter.END,response_message+"\n","2")
            Output_box.configure(state='disabled')
    
def clearChat():
    global save_chat,chat_count
    Output_box.configure(state='normal')
    Output_box.delete(0.0,"end")
    Output_box.configure(state='disabled')
    save_chat=Truea
    chat_count=0
def GetandDisplayResponse():
    text = input_box.get()
    input_box.delete(0,"end")
    user_message = text
    global save_chat,chat_count,chat_header
    Output_box.configure(state='normal')
    Output_box.tag_config("1", foreground = "white",)
    Output_box.tag_config("2", foreground = "white")
    Output_box.tag_config("3", foreground = "red")
    Output_box.tag_config("4", foreground = "green")
    user_input_url = f"{rasa_server_url}/webhooks/rest/webhook"
    payload = {
                    "sender": conversationid,
                    "message": user_message
                    }
    Output_box.insert(tkinter.END, "You->\n", "3")
    Output_box.insert(tkinter.END, user_message+"\n", "1")
    Output_box.insert(tkinter.END,"\n")
    time.sleep(1)
    Output_box.insert(tkinter.END, "DigiBot-> \n", "4")
    response = requests.post(user_input_url, json=payload)
    bot_responses = response.json()
    response_message=""
    for bot_response in bot_responses:
            bot_response['text'] = bot_response['text'] + "\n"
            time.sleep(0.5)
            for i in bot_response['text']:
                Output_box.insert(tkinter.END, i,"2")
                response_message+=i
                
    user_question = user_message
    if save_chat == True:
        
        chat_header=user_message[:15]+"..."
        hist = customtkinter.CTkButton(master=side_panel,text = user_message[:20]+"...",font=("Comic Sans MS", 16),fg_color="#333333",command=lambda header=chat_header: LoadChatHistory(header))
        hist.pack(fill="x", pady=10)
        doc = {"id":chat_header,"convo":{str(chat_count):user_question,str(chat_count)+"r":response_message}}
        coll2023.insert_one(doc)
        save_chat=False
        chat_count=chat_count+1
    else:
       
        update = {
            "$set": {
                "convo."+str(chat_count):user_message,
                "convo."+str(chat_count)+"r":response_message
            }
        }

        filter_doc = {"id":chat_header}
        chat_count=chat_count+1
        coll2023.update_one(filter_doc,update)


    Output_box.configure(state='disabled')
welcome_box = customtkinter.CTkLabel(master=app, text="""I am DigiBot.\nHow may i help you today?
""",font=("comic-sans",25), width=120,height=25,corner_radius=8,wraplength=1200,text_color=("#BF9553"))
welcome_box.place(relx=0.57, rely=0.10, anchor = tkinter.CENTER)
input_box = customtkinter.CTkEntry(master = app,justify="center",height = 40, width = 1100,placeholder_text="message digibot ...", font=("avant-garde-medium", 18),fg_color="#333333")
input_box.place(relx=0.57,rely=0.95,anchor=tkinter.CENTER)
side_panel = customtkinter.CTkScrollableFrame(app, width=250, bg_color="#333333", fg_color="black")
side_panel.pack(fill="y", side="left")


banner = tkinter.Label(side_panel, text="Chat History", font=("copperplate", 20), bg="#333333",fg="white", padx=10, pady=30)
banner.pack(fill="x")
submit_button = customtkinter.CTkButton(master=app, width = 80, text="Submit", font =("Comic Sans MS",20),command=GetandDisplayResponse)
submit_button.place(relx = 0.90,rely=0.95, anchor = tkinter.CENTER)
Output_box = customtkinter.CTkTextbox(master = app, width = 1100,corner_radius=30,border_spacing=1,height=750,font=("Arial",18), fg_color="#333333")
Output_box.place(relx=0.57,rely=0.50, anchor = tkinter.CENTER)
Output_box.configure(state='disabled')
clear_button = customtkinter.CTkButton(master=app, width = 45, text="Clear Chat", font =("Comic Sans MS",20),command=clearChat)
clear_button.place(relx=0.96,rely=0.95, anchor = tkinter.CENTER)
app.mainloop()
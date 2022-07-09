import tkinter
import customtkinter
from msilib import RadioButtonGroup
from ssl import get_default_verify_paths
import tkinter as tk
from typing import Counter
import requests
from bs4 import BeautifulSoup
import numpy as np
from tkinter import Toplevel, messagebox
import tkinter.ttk as ttk
import webbrowser

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("360x630")
app.title("基金績效篩選工具")
    
def gui_inti():
    frame_1 = customtkinter.CTkFrame(master=app)
    frame_1.pack(pady=20, padx=60, fill="both", expand=True)

    frame_2 = customtkinter.CTkFrame(master=app)
    frame_2.pack(pady=20, padx=60, fill="both", expand=True)
    
    label_1 = customtkinter.CTkLabel(text="初步篩選     4433法則",master=frame_1, justify=tkinter.LEFT).pack(pady=12, padx=10)
    global url_entry,url,new
    url= "https://www.sitca.org.tw/ROC/Industry/IN3200.aspx?PGMID=IN0302"
    new = 1
    button_instruction_3 = customtkinter.CTkButton(
    master= frame_1,
    command= openweb,
    text= "基金績效評比網站",
    border_color= "#608a4d", 
    hover_color= "#81b867",
    fg_color= "#79ae61").pack(pady=12, padx=10)
    url_entry = customtkinter.CTkEntry(master=frame_1, placeholder_text="請提供資料來源網址")
    url_entry.pack(pady=12, padx=10)

    global optionmenu_1 
    optionmenu_1 = customtkinter.CTkOptionMenu(frame_1, values=["理柏", "晨星"])
    optionmenu_1.pack(pady=12, padx=10)
    optionmenu_1.set("選擇資料來源")
    
    button_instruction = customtkinter.CTkButton(
    master= frame_1,
    command= fftt_instruction,
    text= "什麼是4433法則?",
    border_color= "#9e4a43", 
    hover_color= "#e06a61",
    fg_color= "#c75d55").pack(pady=12, padx=10)
    
    button_instruction_2 = customtkinter.CTkButton(
    master= frame_1,
    command= fftt_instruction,
    text= "操作說明",
    border_color= "#9e4a43", 
    hover_color= "#e06a61",
    fg_color= "#c75d55").pack(pady=12, padx=10)

    

    
    button_1 = customtkinter.CTkButton(text="送出",master=frame_1, command=crawler)
    button_1.pack(pady=12, padx=10)
 
    label_2 = customtkinter.CTkLabel(text="進階篩選     風險指標",master=frame_2).pack(pady=12, padx=10)
    global optionmenu_3,optionmenu_2,select_sort
    optionmenu_3 = customtkinter.CTkOptionMenu(master=frame_2, values=["夏普", "標準差","Beta","Alpha"])
    optionmenu_3.set("選擇風險指標")
    optionmenu_3.pack(pady=12, padx=10)
    optionmenu_2 = customtkinter.CTkOptionMenu(master=frame_2, values=["大到小", "小到大"])
    optionmenu_2.set("風險指標呈現方式")
    optionmenu_2.pack(pady=12, padx=10)
        

    

    app.mainloop()
    
def openweb():
        webbrowser.open(url,new=new)  
def fftt_instruction():
    print("我還不想寫")
    
def crawler ():

    resp = requests.get(url_entry.get())
    global select_type

    data_index_=[]
    data_index_morningstar = [1,4,5,6,7,8,9,10,12,13,14,15]
    data_index_lipper = [1,4,5,6,7,8,9,10,12,13,14,16]
        
    if optionmenu_1.get() == "晨星":
        data_index = data_index_morningstar
        select_type =1
    else:
        data_index = data_index_lipper
        select_type =0

    
    soup = BeautifulSoup(resp.text, 'html.parser')
    rows_even = soup.find_all(class_ = "DTeven")
    rows_odd = soup.find_all(class_ = "DTodd")

    delete_list = []
    #初始化
    even_data=[['\xa0' for count in range(12)] for row in range(len(rows_even))]
    odd_data=[['\xa0' for count in range(12)] for row in range(len(rows_odd))]
    
    #用來存要讀取的資料index 1名字 4三個月 5六個月 6789:1235年,beta

    i = 0
    count = 0
    #讀取偶數欄資料
    for row_even in rows_even:
        count = 0
        for y in range(12):
            even_data[i][y]=row_even.find_all('td')[data_index[count]].text
            if even_data[i][y] == '\xa0':
                delete_list.append(i)
            count+=1
        i+=1

    #刪除空格資料
    even_data = np.delete(even_data,delete_list, axis = 0)
    delete_list.clear()

    i = 0
    count = 0
    #讀取奇數欄資料
    for row_odd in rows_odd:
        count = 0
        for y in range(12):
            odd_data[i][y]=row_odd.find_all('td')[data_index[count]].text
            if odd_data[i][y] == '\xa0':
                delete_list.append(i)
            count+=1
        i+=1

    odd_data = np.delete(odd_data,delete_list, axis = 0)
    #合併資料
    global data
    data = np.vstack((even_data,odd_data)) 
    run(data)

def run(data):
    global data_len
    data_len = len(data)

    num_filter_3 = data_len*0.33
    num_filter_4 = data_len*0.25

    #宣告每個項目之入圍清單
    
    m3_list = [0 for one in range(data_len)] 
    m6_list = [0 for one in range(data_len)]
    y1_list = [0 for one in range(data_len)]
    y2_list = [0 for one in range(data_len)]
    y3_list = [0 for one in range(data_len)]
    y5_list = [0 for one in range(data_len)]
    sty_list = [0 for one in range(data_len)] #今年以來

    #進行每個項目篩選
    fftt(data,m3_list,num_filter_3,data_len,1)
    fftt(data,m6_list,num_filter_3,data_len,2)
    fftt(data,y1_list,num_filter_4,data_len,3)
    fftt(data,y2_list,num_filter_4,data_len,4)
    fftt(data,y3_list,num_filter_4,data_len,5)
    fftt(data,y5_list,num_filter_4,data_len,6)
    fftt(data,sty_list,num_filter_4,data_len,7)

    n=0
    global get_list
    get_list=[]

    space = 0
    #畫圖用
    get_data=[[]]
    get_name=[]
    global name_list
    name_list=[]
    for k in range(data_len):
        if m3_list[n]==1 and m6_list[n]==1 and y1_list[n]==1 and y2_list[n]==1 and y3_list[n]==1 and y5_list[n]==1 and sty_list[n]==1:
            space = 1

            get_list.append(n)
          
            tmp_data = []
            get_name.append(data[n][0])
            #另存資料
            for i in range(6):
                tmp_data.append(float(data[n][i+1]))
            
            get_data.append(tmp_data)
            name_list.append(data[n][0]+'\n')
 
        n+=1
    if(space!=0):
        fftt_result_toplevel()  
    else:
        tk.messagebox.showerror(title=None, message='無符合資料')
def fftt_result_toplevel():
        window = customtkinter.CTkToplevel()
        window.title("4433篩選結果")
        window.geometry("530x400")
        label_2 = customtkinter.CTkLabel(window, text ="以下基金為4433法則後篩選後之結果")
        label_1 = customtkinter.CTkLabel(window, text =''.join(name_list))
        label_1.pack(side="top", fill="both", expand=True, padx=40, pady=40)
        button = customtkinter.CTkButton(text="進階篩選",master=window, command=decide).pack()

def final_result(result_data):
        window = customtkinter.CTkToplevel()
        window.title("進階篩選結果")
        window.geometry("530x400")
        label_1 = customtkinter.CTkLabel(window, text =''.join(result_data))
        label_1.pack(side="top", fill="both", expand=True, padx=40, pady=40)  
    
def decide():
    
    global index_choose
    index_choose =0

    if(optionmenu_3.get()=="夏普"): #夏普
        if(select_type==1):
            index_choose=9
        else:
            index_choose=10
    elif(optionmenu_3.get()=="標準差"):#年化
        index_choose=8    
    elif(optionmenu_3.get()=="Beta"): #beta  
        if(select_type==1):
            index_choose=11
        else:
            index_choose=9
    elif(optionmenu_3.get()=="Alpha"):#阿法
        if(select_type==1):
            index_choose=10
        else:
            index_choose=11

    sorting()
    #elif(var_advancecd_select==5):#特雷諾
        #index_choose= 15
    
def check(input_list):
    compare_list=set(input_list)
    repeat_count = 0
    if len(compare_list) != len(input_list):
        repeat_count+=1
        print("value repeat")
        
             
def sorting():
    copy_data =[]
    result_data=[]
    #tmp = float(index_choose)
    
    #把數據抓出來
    i=0
    for count in range(len(get_list)):
        copy_data.append(float(data[get_list[count]][index_choose]))
        i+=1
    #print("=====================================")
    #print(copy_data)

    #print("=====================================")
    #排序
   
    #revese = true 才是大到小
    print(optionmenu_2.get())
    if(optionmenu_2.get()=="大到小"):
        sorted_copy_data = sorted(copy_data, reverse = True)
    else:
        sorted_copy_data = sorted(copy_data, reverse = False)
    print(sorted_copy_data)
    #=====================bug區=========================
    for count_1 in range(len(get_list)):
        for count_2 in range(len(get_list)):
            if ((float(data[get_list[count_1]][index_choose])) == sorted_copy_data[count_2]):
                result_data.append(data[get_list[count_1]][0]+" "+data[get_list[count_1]][index_choose]+'\n')
                break
    final_result(result_data)
    
    #=====================bug區=========================
    #print(result_data)
    #tk.messagebox.showinfo(title='進階篩選結果', message=''.join(result_data))  
    #result = customtkinter.CTkLabel(text=''.join(result_data),master=advancecd_select).pack(pady=12, padx=10)
    
def fftt(_data,_list,filter,data_len,array_index):

      data_compare=[]
      #把資料轉成float
      for count in range(data_len):
        data_compare.append(float(_data[count][array_index]))

      #進行排序
      data_sorted = sorted(data_compare, reverse = True)
      num = 0

      #執行每一檔資料，並與進行
      for num in range(data_len):
        for x in range(int(filter)):#與排序後前1/3或1/4的資料做比對
          #若資料符合，存入list中
          #已知bug，若數據有兩組一模一樣，會造成誤差。
          if float(_data[num][array_index]) == data_sorted[x]: 
            _list[num] = 1


if __name__ =='__main__':
    gui_inti()
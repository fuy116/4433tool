from msilib import RadioButtonGroup
from ssl import get_default_verify_paths
import tkinter as tk
from typing import Counter
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from tkinter import Toplevel, messagebox
import tkinter.ttk as ttk
def gui_inti():
    win = tk.Tk()
    win.title("基金績效篩選工具")
    win.geometry("645x350")#寬x高
    win.minsize(width=350,height=180) #最小size
    win.maxsize(width=645,height=350)

    label=tk.Label(text="請提供資料來源網址")
    label.pack(side="top")
    label_choose1 = tk.Label(text="請選擇基金網站來源:")
    label_choose1.place(x=5,y=50)
    label_choose2=tk.Label(text="是否以夏普值(Sharpe)進行第二階段篩選")
    label_choose2.place(x=5,y=85)
    label_choose3 = tk.Label(text="是否顯示圖表:")
    label_choose3.place(x=5,y=120)   
    label_i_0 =tk.Label(text="附註：4433法則按以下順序挑選基金")
    label_i_1 =tk.Label(text="「4」：該基金一年期績效排名在同類型的前四分之一")

    label_i_2=tk.Label(text="「4」：該基金兩年、三年、五年以及自今年以來績效排名在同類型的前四分之一")
    label_i_3=tk.Label(text="「3」：該基金六個月期績效排名在同類型的前三分之一\n「3」：該基金三個月期績效排名在同類型的前三分之一\n4433法則是由臺大教授邱顯比、李存修2人設計的。\n主要是用來挑選「中長期」，表現績優的基金。")
    label_source = tk.Label(text="篩選資料來源：中華民國證券投資信託暨顧問商業同業公會官網，統計資料/境外基金各項資料/其他資訊")
    label_source.place(x=50,y=260)
    label_i_0.place(x=5,y=200)
    label_i_1.place(x=5,y=215)
    label_i_2.place(x=5,y=230)
    label_i_3.place(x=5,y=245)
    #input = tk.StringVar()
    global entry 

    entry= tk.Entry(width = 50)
    entry.place(x=70 ,y=0) 
    entry.pack()

    global var,var_1,var_2
    var = tk.IntVar()
    radio1 = tk.Radiobutton(text='晨星',variable=var,value=1)
    radio2 = tk.Radiobutton(text='理柏',variable=var,value=2)
    var_1= tk.IntVar()#sharpe
    radio3 = tk.Radiobutton(text='是',variable=var_1,value=1)
    radio4 = tk.Radiobutton(text='否',variable=var_1,value=0)
    var_2= tk.IntVar()#畫圖
    radio5 = tk.Radiobutton(text='是',variable=var_2,value=1)
    radio6 = tk.Radiobutton(text='否',variable=var_2,value=0)

    radio1.place(x=120,y=50)
    radio2.place(x=170,y=50)
    radio3.place(x=230,y=82)
    radio4.place(x=270,y=82)
    radio5.place(x=90,y=118)
    radio6.place(x=130,y=118)
    
    button = tk.Button(text="送出",command = crawler,padx=40,pady=10)
    button.pack(side="bottom")

    
    win.mainloop()
    
def crawler ():

    resp = requests.get(entry.get())
    global select_type
    select_type = var.get()
    data_index_=[]
    data_index_morningstar = [1,4,5,6,7,8,9,10,12,13,14,15]
    data_index_lipper = [1,4,5,6,7,8,9,10,12,13,14,16]
        
    if select_type == 1:
        data_index = data_index_morningstar
    else:
        data_index = data_index_lipper

    
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
    
        fftt_result = Toplevel()
        fftt_result.title("4433篩選結果")
        fftt_result.geometry("450x300")
        LabelA = tk.Label(fftt_result,text =''.join(name_list)).pack()
        button_select = tk.Button(fftt_result,text="進階篩選",command=advancecd_select,padx=20,pady=10).pack(side="bottom")
        fftt_result.minsize(width=300,height=300) #最小size
        fftt_result.maxsize(width=300,height=300)
       #padx=20,pady=10
        
        #select_button_4 = tk.Radiobutton(text='特雷諾',variable=var,value=2)
        if(var_1.get()==1):
            sharpe(get_list,data)
       # if(var_2.get()==1):
           # draw(get_list,get_name,get_data)
    else:
        tk.messagebox.showerror(title=None, message='無符合資料')
    

def advancecd_select():  
    advancecd_select = Toplevel()
    advancecd_select.title("進階篩選")
    advancecd_select.geometry("400x400")

    #https://www.sitca.org.tw/ROC/Industry/IN2412.aspx?txtYEAR=2022&txtMONTH=05&txtGROUPID=BDEUR
    global var_3,select_sort,select_value_entry
    
    var_3  = tk.IntVar()
    select_sort = tk.IntVar()
    
    title_advselect = tk.Label(advancecd_select,text='風險指標',font=(15)).grid(row=0,column=0)
    #title_selectvalue = tk.Label(advancecd_select,text='篩選數值',font=(15)).grid(row=1,column=0)
    select_button_0 = tk.Radiobutton(advancecd_select,text='夏普',variable=var_3,value=1).grid(row=0,column=1)
    select_button_1 = tk.Radiobutton(advancecd_select,text='標準差',variable=var_3,value=2).grid(row=0,column=2)
    select_button_2 = tk.Radiobutton(advancecd_select,text='Beta',variable=var_3,value=3).grid(row=0,column=3)
    select_button_3 = tk.Radiobutton(advancecd_select,text='Alpha',variable=var_3,value=0).grid(row=0,column=4)
    #大到小or小到大
    
    title_selectsort=tk.Label(advancecd_select,text='呈現方式',font=(15)).grid(row=2,column=0)
   #select_value_entry = tk.Entry(advancecd_select,width=3).grid(row=1,column=1)
    select_button_4 = tk.Radiobutton(advancecd_select,text='大到小',variable=select_sort,value=0).grid(row=2,column=1)
    select_button_5 = tk.Radiobutton(advancecd_select,text='小到大',variable=select_sort,value=1).grid(row=2,column=2)

    decide_button = tk.Button(advancecd_select,text="送出",command = decide).grid(row=8,column=2)
  

def decide():
    #data_index_morningstar = [1,4,5,6,7,8,9,10,12,13,14,15] 11
    #data_index_lipper =      [1,4,5,6,7,8,9,10,12,13,14,16]  
 
    global index_choose
    index_choose =0

    if(var_3.get()==1): #夏普
        if(select_sort.get()==1):
            index_choose=9
        else:
            index_choose=10
    elif(var_3.get()==2):#年化
        index_choose=8    
    elif(var_3.get()==0): #阿法
        if(select_sort.get()==1):
            index_choose=10
        else:
            index_choose=11
    elif(var_3.get()==0): #beta  
        if(select_sort.get()==1):
            index_choose=11
        else:
            index_choose=9
    sorting()
    #elif(var_advancecd_select==5):#特雷諾
        #index_choose= 15
 
# def check(list_a,list_b):#檢查一個list內是否有完全一樣的兩個數據
    # count = 0
    # for x in range(len(list_a)):
        # count=0
        # for y in range(len(list_b)):
            # if(list_a[x]==list_b[y]):
                # count+=1
        # print(count)
        # if(count>=2):
            # return check_true
def sorting():
    copy_data =[]
    result_data=[]
    #tmp = float(index_choose)
 
    #把數據抓出來
    i=0
    for count in range(len(get_list)):
        copy_data.append(float(data[get_list[count]][index_choose]))
        i+=1
    print(copy_data)
    
    #排序
    print(select_sort.get())
    #revese = true 才是大到小???
    
    if(select_sort.get()==0):
        sorted_copy_data = sorted(copy_data, reverse = True)
    else:
        sorted_copy_data = sorted(copy_data, reverse = False)
        
    #交叉比對

    for count_1 in range(len(get_list)):
        for count_2 in range(len(get_list)):
            if ((float(data[get_list[count_2]][index_choose])) == sorted_copy_data[count_1]):

                result_data.append(data[get_list[count_2]][0]+'\n')
             
         
 
    #顯示

    #print(data[get_list[0]][0])
    #print(data[get_list[1]][0])
    #print(sorted_copy_data)
    #print(result_data)
    tk.messagebox.showinfo(title='進階篩選結果', message=''.join(result_data))
       
    
    
def sharpe(get_list,data):
    sharpe_fund =0
    n=0
    best_n=0
    for count in range(len(get_list)):
        if(float(data[get_list[count]][8])>sharpe_fund):
            sharpe_fund=float(data[get_list[n]][8])
            best_n=n
    n+=1
    tk.messagebox.showinfo(title='夏普值篩選',message=data[best_n][0])
     
def s_d(get_list,data,filter_input): #標準差，波動程度。值小波動小，風險小。
    sd_fund = [] 
    get_sdfund=[]
    high_to_low = True
    copy_get_data = []
    filter = len(get_list) * round(filter_input)
    for count in range(get_list):
        copy_get_data.append(float(data[count][12]))
    
    copy_get_data = sorted(copy_get_data, reverse = high_to_low)
    for i in range(filter):
        sd_fund.append()
    
    for x in range(len(get_list)):
        for y in range(len(sd_fund)):
            if(data[get_list[x]][12]==sd_fund[y]):
                get_sdfund.append(get_list[x])
    tk.messagebox.showinfo(title='年度標準差篩選',message=data[get_sdfund][0])        
    print(data[get_sdfund][12])#result
     #算出前X%是多少
    
    #Q:利用for比對陣列改良方法? A???
    
    #先複製一個getlist、算出要前X%、Sort、利用雙for比對(原陣列vs sort後陣列)、把n記錄下來
    #final:printf(data[n][d])       
    
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
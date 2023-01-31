import tkinter as tk
from tkinter import messagebox, ttk, Menu
import sqlite3
import datetime
import os
import ttkbootstrap as boottk
from ttkbootstrap.constants import *
from threading import Thread

# get the current date and time
now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
print(now)
teachers_values = []

#database_path = r"pcs_in_out.db"
#database_BK_path = r"pcs_in_out_BACKUP.db"
database_path = r"\\571158-pc-100\pc_in\pcs_in_out.db"
BK_database_path = r"pcs_in_out_BACKUP.db"

def create_table():
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    try:
        sql = """CREATE TABLE pcs_history(
                Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                PC_Name text,
                teacher text,
                time text,
                in_out text,
                comment text)"""
        with connection:
            cursor.execute(sql)

    except:
        print("Table exist")
    if connection:
        connection.close()


def pc_in():
    answers.delete("1.0", tk.END)
    now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    where = pc_where()
    pc_num = entry01.get()
    entry01.delete(0, tk.END)
    entry03.delete(0, tk.END)
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    if pc_num == "":
        messagebox.showwarning("Error", "Please enter pc number")
    elif where == "no record":
        in_out = "in"
        sql = "INSERT into pcs_history(PC_Name, time, in_out) VALUES(?,?,?)"
        val  = (pc_num, now, "in")
        with connection:
            cursor.execute(sql,val)
        answers.insert(tk.END, f"מחשב מספר {pc_num} נוסף לרשימה")

    elif where[0][4] == "out":
        teacher = where[0][2]
        sql = "INSERT into pcs_history(PC_Name, teacher, time, in_out) VALUES(?,?,?,?)"
        val  = (pc_num, teacher, now, "in")
        with connection:
            cursor.execute(sql,val)
        answers.insert(tk.END, f"pc number {pc_num} back by {teacher}\nComment: {where[0][5]}")
    elif where[0][4] == "in":
        messagebox.showwarning("Error", f"PC {pc_num} is IN not OUT!")




def pc_out():
    answers.delete("1.0", tk.END)
    now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    pc_num = entry01.get()
    where_is_it = pc_where()
    teacher = teachers_combobox.get()
    comment = entry03.get()


    if where_is_it == "no record":
        messagebox.showwarning("We have a problem", f"No record of PC {pc_num} in the database!")
    elif teacher == "":
        messagebox.showwarning("We have a problem", "You must enter teacher name!")
    else:
        in_out = "out"
        where_is_it = pc_where()[0]
        if where_is_it == []:
            answers.insert(tk.END, "no such pc")
        elif where_is_it[4] == "in":
            answers.insert(tk.END, f"database updated. PC {pc_num} given to {teacher}")
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            sql = "INSERT into pcs_history(PC_Name, teacher, time, in_out, comment) VALUES(?,?,?,?,?)"
            val  = (pc_num, teacher, now, "out", comment)
            with connection:
                cursor.execute(sql,val)
        elif where_is_it[4] == "out":
            messagebox.showwarning("We have a problem", f"רשום שהמחשב בחוץ אצל {where_is_it[2]}")
            answers.insert(tk.END, f"המחשב נמצא אצל {where_is_it[2]} מ-{where_is_it[3]}")
        entry01.delete(0, tk.END)

def pc_where():
    answers.delete("1.0", tk.END)
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    pc_num = entry01.get()

    sql = "SELECT * from pcs_history WHERE PC_Name = ? ORDER BY time DESC LIMIT 1"
    var = (pc_num,)
    with connection:
        cursor.execute(sql, var)
        answer01 = cursor.fetchall()
    if answer01 == []:
        return "no record"
    else:
        return answer01


def pc_history():
    answers.delete("1.0", tk.END)
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    pc_num = entry01.get()
    sql = "SELECT * from pcs_history WHERE PC_Name = ? ORDER BY time DESC"
    var = (pc_num,)
    with connection:
        cursor.execute(sql, var)
        answer01 = cursor.fetchall()
    if pc_num == "":
        answers.insert(tk.END, "Error! Please type pc number to search!")
    elif answer01 != []:
        answers.insert(tk.END, f"PC is {answer01[0][4]}\n\nPC Hitory\n------------\n")
        for line in answer01:
            answers.insert(tk.END, f"PCc number:{line[1]}\nTeacher: {line[2]}\nWhere: {line[4]}\nWhen: {line[3]}\n\n")
    else: answers.insert(tk.END, f"no records for {pc_num}")

    if connection:
        connection.close()
    return answer01

def pc_teachers():
    counter = 0
    teacher = teachers_combobox.get()
    answers.delete("1.0", tk.END)
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    sql = "SELECT * from pcs_history WHERE teacher = ? ORDER BY time DESC"
    var = (teacher,)
    with connection:
        cursor.execute(sql, var)
        answer01 = cursor.fetchall()

    if teacher == "":
        answers.insert(tk.END, "Enter teacher name to search.")
    elif answer01 != [] and answer01[0][4] == "out" :
        for line in answer01:
            counter +=1
            answers.insert(tk.END, f"pc number:{line[1]}\nteacher: {line[2]}\nWhere: {line[4]}\nWhen: {line[3]}\nComment: {line[5]}\n\n")
    else:
        answers.insert(tk.END, f"{teacher} holding no pcs right now\n\n")
        if answer01 == []:
            answers.insert(tk.END, f"No history for {teacher}")
        for line in answer01:
            answers.insert(tk.END, f"Teacher History:\nPC number:{line[1]}, Teacher: {line[2]}\nWhere: {line[4]}\nWhen: {line[3]}\nComment: {line[5]}\n-------------------\n")
    if connection:
        connection.close()

    return answer01

def all_pcs_in():
    counter = 0
    pc_in_list = []
    answers.delete("1.0", tk.END)
    pcs_in_out = pcs_in_out_dic()
    for key,value in pcs_in_out.items():
        if value == "in":
            pc_in_list.append(key)
    answers.insert(tk.END, f"{len(pc_in_list)} are IN\n\n")
    for item in pc_in_list:
        answers.insert(tk.END, f"PC Number {item} is in\n")

def all_pcs_out():
    out = ""
    teacher_over_all_pcs = {}

    answers.delete("1.0", tk.END)
    pcs_in_out = pcs_in_out_dic()
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    for key,value in pcs_in_out.items():
        sql = "SELECT DISTINCT PC_Name, in_out, teacher, time, comment from pcs_history WHERE PC_Name = ? order by time DESC limit 1"
        var = (key,)
        with connection:
            cursor.execute(sql, var)
            answer01 = cursor.fetchall()
        if value == "out":
            try:
                teacher_over_all_pcs[answer01[0][2]] = teacher_over_all_pcs[answer01[0][2]] + 1
            except KeyError as e:
                teacher_over_all_pcs[answer01[0][2]] = 1

        if value == "out" and answer01[0][4] == "":
            out = "yes"
            answers.insert(tk.END, f"PC number {answer01[0][0]} with {answer01[0][2]} since {answer01[0][3]}\n")
        elif value == "out" and answer01[0][4] != "":
             out = "yes"
             answers.insert(tk.END, f"PC number {answer01[0][0]} with {answer01[0][2]} since {answer01[0][3]}\nComment: {answer01[0][4]}\n")
    if out != "yes":
        answers.insert(tk.END, "No pc's out there :-)")
    answers.insert(tk.END, f"\n{teacher_over_all_pcs}")

def pcs_in_out_dic():
    pcs_in_out = {}
    answers.delete("1.0", tk.END)
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    #all pcs list
    sql = "SELECT DISTINCT PC_Name from pcs_history order by PC_Name"
    with connection:
        cursor.execute(sql)
        answer01 = cursor.fetchall()

    for line in answer01:

        sql = "SELECT PC_Name, in_out, time from pcs_history where PC_Name = ? order by time DESC limit 1"
        var = (line[0],)
        with connection:
            cursor.execute(sql, var)
            answer01 = cursor.fetchall()

        pcs_in_out[answer01[0][0]] = answer01[0][1]

    return pcs_in_out

def teachers_combo_values(do_it):
    if do_it == "do it":
        with open("teachers.txt", 'r', encoding = 'utf-8-sig') as file:
            for item in file:
                value = item.strip()
                teachers_values.append(value)
    do_it == "dont"
    return teachers_values

def check_input(event):
    value = event.widget.get()
    lst = teachers_combo_values("do_it")

    if value == '':
        teachers_combobox['values'] = lst
    else:
        data = []
        for item in lst:
            if value.lower() in item.lower():
                data.append(item)

        teachers_combobox['values'] = data

def back_up_db():
    src = database_path
    destanation = BK_database_path
    os.system(f"copy {src} {destanation}")

def pc_out_enter(event):
   pc_out()

def on_start():
    print("thread01")
    back_up_db()
    create_table()



def change_theme():
    def close_options():
        frame04.destroy()

    frame04 = boottk.Frame(window)
    frame04.grid(row = 3, column = 0)
    my_themes = window.style.theme_names()  # List of available themes
    my_str = boottk.StringVar(value=window.style.theme_use())  # default selection of theme

    r, c = 0, 0  # row=0 and column =0
    for values in my_themes:  # List of available themes
        b = boottk.Radiobutton(
            frame04, text=values, variable=my_str, value=values, command=lambda: my_upd()
        )  # Radio buttons with themes as values
        b.grid(row=r, column=c, padx=5, pady=20)
        c = c + 1  # increase column by 1
        if c > 4:  # One line complete so change the row and column values
            r, c = r + 1, 0

    button02 = boottk.Button(frame04, text = "close", command = close_options)
    button02.grid(row = r, column=c+1)

    def my_upd():
        window.style.theme_use(my_str.get())
        print(my_str.get())



window = boottk.Window()

#window.geometry("400x600")
window.title("מעקב ניידים")
frame01 = boottk.Frame(window)
frame01.grid(row = 0, column = 0)
frame02 = boottk.Frame(window)
frame02.grid(row = 1, column = 0)
frame03 = boottk.Frame(window)
frame03.grid(row = 2, column = 0)

window.style.theme_use("darkly")

label01 = boottk.Label(frame01, text = "מחשבים ניידים - תיכון המר", font=("Arial", "20"))
label01.grid(row=0, column = 0, columnspan = 2, pady = 10)

label02 = boottk.Label(frame01, text = "מספר מחשב")
label02.grid(row = 1, column =1, pady = 10)
entry01 = boottk.Entry(frame01, width = "29", justify='right')
entry01.grid(row = 1, column = 0, pady = 10)
entry01.bind('<Return>', pc_out_enter)

label03 = boottk.Label(frame01, text = "שם מורה")
label03.grid(row = 2, column =1, pady = 10)
teachers_combobox = boottk.Combobox(frame01, width = "27", justify='right')
teachers_combobox.option_add('Justify', 'right')
lst = teachers_combo_values("do_it")

for value in teachers_combo_values("do it"):
   # Add itmes in combobox through Loop code
   teachers_combobox['values']= tuple(list(teachers_combobox['values']) + [str(value)])
#teachers_combobox['values'] = teachers_combo_values("do it")
teachers_combobox.bind('<KeyRelease>', check_input)
teachers_combobox.bind('<Return>', pc_out_enter)
teachers_combobox.grid(row = 2, column = 0, pady = 10)

label04 = boottk.Label(frame01, text = "הערות")
label04.grid(row = 3, column =1, pady = 10)
entry03 = boottk.Entry(frame01, width = "29", justify='right')
entry03.bind('<Return>', pc_out_enter)
entry03.grid(row = 3, column = 0, pady = 10)

button01 = boottk.Button(frame02, text = "מחשב יצא", width = "20", command = pc_out)
button01.grid(row = 0, column = 0, pady=5, padx=5)
button02 = boottk.Button(frame02, text = "מחשב חזר", width = "20", command = pc_in)
button02.grid(row = 0, column = 1, pady=5, padx=5)
button03 = boottk.Button(frame02, text = "איפה המחשב", width = "20", command = pc_history)
button03.grid(row = 1, column = 0, pady=5, padx=5)
button04 = boottk.Button(frame02, text = "חפש לפי מורה", width = "20", command = pc_teachers)
button04.grid(row = 1, column = 1, pady=5, padx=5)
button05 = boottk.Button(frame02, text = "מה נמצא בארון", width = "20", command = all_pcs_in)
button05.grid(row = 2, column = 0, pady=5, padx=5)
button06 = boottk.Button(frame02, text = "מה בחוץ", width = "20", command = all_pcs_out)
button06.grid(row = 2, column = 1, pady=5, padx=5)

answers = boottk.Text(frame03, width=57,  height=15)
answers.grid(pady=20, padx=20)

menubar = Menu(window)
window.config(menu = menubar)
menubar.add_command(label = 'Choose Theme', command = lambda: change_theme())

thread01 = Thread(target=on_start)
thread01.start()
window.mainloop()

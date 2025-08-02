import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime, date

font = ('Helvetica', 10)
fg = '#FFFFFF'
canvas = 0

def load_database():
    try:
        with open("tracker.json") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("tracker.json", "w") as f:
            json.dump({}, f)
        with open("tracker.json") as f:
            return json.load(f)

def calculate_ymd(start_date, end_date):
    year_diff = end_date.year - start_date.year
    month_diff = end_date.month - start_date.month
    day_diff = end_date.day - start_date.day

    if day_diff < 0:
        month_diff -= 1
        # Borrow days from previous month
        prev_month = end_date.month - 1 if end_date.month > 1 else 12
        prev_year = end_date.year if end_date.month > 1 else end_date.year - 1
        days_in_prev_month = (datetime(prev_year, prev_month + 1, 1) - datetime(prev_year, prev_month, 1)).days
        day_diff += days_in_prev_month

    if month_diff < 0:
        year_diff -= 1
        month_diff += 12

    return year_diff, month_diff, day_diff

def compute_clean_time_text(name, end_date_str, end_time_str):
    end_dt = datetime.strptime(f"{end_date_str} {end_time_str}", "%Y/%m/%d %H:%M")
    now = datetime.now()

    years, months, days = calculate_ymd(end_dt, now)

    # Calculate hours and minutes difference
    hour_diff = now.hour - end_dt.hour
    minute_diff = now.minute - end_dt.minute

    if minute_diff < 0:
        minute_diff += 60
        hour_diff -= 1

    if hour_diff < 0:
        hour_diff += 24
        if days == 0:
            if months == 0:
                years -= 1
                months = 11
            else:
                months -= 1
                if (months == 1) or (months == 3) or (months == 5) or (months == 7) or (months == 8) or (months == 10) or (months == 12):
                    days = 31
                elif months == 2:
                    if ((years % 4 == 0) and not (years % 100 == 0)) or (years % 400 == 0):
                        days = 29
                    else:
                        days = 28
                elif (months == 4) or (months == 6) or (months == 9) or (months == 11):
                    days = 30
        else:
            days -= 1

    return (f"For {name}, you've been clean for {years} year(s), {months} month(s), {days} day(s), "
            f"{hour_diff} hour(s), {minute_diff} minute(s)") # insert meaningful comment

def on_mousewheel(event):
    global canvas
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class Addicts:
    def __init__(self, master, name, end_date, end_time):
        self.name = name
        self.end_date = end_date
        self.end_time = end_time
        self.text = compute_clean_time_text(name, end_date, end_time)

        self.frame = tk.Frame(master, bg='black')
        self.frame.pack(anchor='center', pady=5, expand=True)

        self.label = tk.Label(self.frame, text=self.text, font=font, fg=fg, bg='black')
        self.label.pack(side='left', expand=False, fill='x', padx=5)

        self.button = tk.Button(self.frame, text="Reset", padx=5, command=self.ask, font=font, fg=fg, bg='black')
        self.button.pack(side='left')

    def update_text(self, new_text):
        self.text = new_text
        self.label.config(text=self.text)

    def ask(self):
        if messagebox.askokcancel(master=None, message=f"Are you sure you want to reset {self.name}'s progresses? This cannot be undone! (Unless you edit the save files)"):
            data = load_database()
            data[self.name]["end-date"] = date.today().strftime("%Y/%m/%d")
            data[self.name]["end-time"] = datetime.now().strftime("%H:%M")

            with open("tracker.json", "w") as f:
                json.dump(data, f, indent=2)

            global database
            database = data
            # Update label text immediately
            new_text = compute_clean_time_text(self.name, data[self.name]["end-date"], data[self.name]["end-time"])
            self.update_text(new_text)

def update_all():
    global addictionlist, database, canvas, canvas_window
    database = load_database()
    for addict in addictionlist:
        end_date = database[addict.name]["end-date"]
        end_time = database[addict.name]["end-time"]
        new_text = compute_clean_time_text(addict.name, end_date, end_time)
        addict.update_text(new_text)
    canvas.bind("<Configure>", resize_canvas)
    canvas.config(height=0.5*window.winfo_height())
    window.after(100, update_all)  # why is this comment here you'll never know!

newadddata = {}
newaddadd = {}
entry = 0
date_entry = 0
time_entry = 0
canvas_window = 0

def resize_canvas(event):
    global canvas, canvas_window
    canvas.itemconfig(canvas_window, width=event.width)

def addnewaddc():
    with open("tracker.json") as f:
        data = json.load(f)

    global newaddadd, entry, date_entry, time_entry

    newaddadd = {}
    newaddadd['name'] = entry.get()
    newaddadd['end-date'] = date_entry.get()
    newaddadd['end-time'] = time_entry.get()

    print(newaddadd)

    data[newaddadd['name']] = newaddadd

    with open("tracker.json", "w") as f:
        json.dump(data, f, indent=2)

    addict = Addicts(window, newaddadd["name"], newaddadd["end-date"], newaddadd["end-time"])
    addictionlist.append(addict)

def reset():
    global date_entry, time_entry
    date_entry.delete(0, tk.END)
    time_entry.delete(0, tk.END)
    date_entry.insert(0, date.today().strftime("%Y/%m/%d"))
    time_entry.insert(0, datetime.now().strftime("%H:%M"))

def main():
    global addictionlist, database, entry, date_entry, time_entry, canvas

    window.configure(bg="black")

    title = tk.Label(master=window, pady=10, text="The Addiction Tracker", font=('Helvetica', 25, 'bold'), fg=fg, bg='black')
    title.pack()

    frame = tk.Frame(master=window, bg='black')
    frame.pack(anchor='center', pady=5)

    lab = tk.Label(frame, font=font, fg=fg, bg='black', text='Add new addiction: ')
    lab.pack()

    entry = tk.Entry(frame, font=font, fg=fg, bg='#250000', width=30) # Oh bloody red >:)
    entry.pack(expand=False, fill='x', padx=5)
    entry.insert(0, "Enter new addiction name :(")

    f2 = tk.Frame(master=window, bg='black')
    f2.pack(anchor='center', pady=5)

    tk.Label(f2, text="End Date (YYYY/MM/DD):", fg='white', bg='black').grid(row=1, column=0, sticky='w')
    date_entry = tk.Entry(f2, fg='white', bg='#250000')
    date_entry.grid(row=1, column=1)
    date_entry.insert(0, date.today().strftime("%Y/%m/%d"))

    f3 = tk.Frame(master=window, bg='black')
    f3.pack(anchor='center', pady=5)

    tk.Label(f3, text="End Time (HH:MM):", fg='white', bg='black').grid(row=2, column=0, sticky='w')
    time_entry = tk.Entry(f3, fg='white', bg='#250000')
    time_entry.grid(row=2, column=1)
    time_entry.insert(0, datetime.now().strftime("%H:%M"))

    f4 = tk.Frame(master=window, bg='black')
    f4.pack(anchor='center', pady=5)

    reset_button = tk.Button(f4, text="Reset input time to the current time", padx=10, fg='#FFFFFF', bg='#250000', font=font, command=reset)
    reset_button.grid(row=1, column=1)

    addnew = tk.Button(f4, text="Add", padx=40, command=addnewaddc, font=font, fg=fg, bg='#250000')
    addnew.grid(row=1, column=2, padx=5)

    container = tk.Frame(window, bg='black', width=750)
    container.pack(padx=10)

    canvas = tk.Canvas(container, bg='black', highlightthickness=0, width=750)
    scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)

    scrollable_frame = tk.Frame(canvas, bg='black')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    global canvas_window

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor='n')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', expand=True)
    scrollbar.pack(side='right', fill='y')

    addictionlist = []
    for key in database.keys():
        data = database[key]
        addict = Addicts(scrollable_frame, data["name"], data["end-date"], data["end-time"])
        addictionlist.append(addict)

    update_all()  # start periodic updates

window = tk.Tk()
window.geometry("800x450")
window.title("Addiction Tracker")
window.configure(bg="black")

database = load_database()
addictionlist = []

main()

window.mainloop()

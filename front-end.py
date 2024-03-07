import pickle
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import tkinter as tk
from sys import exit

matplotlib.use("TkAgg")

# Plot graph
def draw_figure(data_df, C, root):
    C.grid_remove()
    C = tk.Canvas(root, height = 250, width = 300)
    C.grid(row = 1, column = 0, columnspan = 2, rowspan = 2)

    x = np.arange(len(data_df))
    bar_width = 0.5
    weeks = []
    fig, ax = plt.subplots()

    ax.grid(axis = 'y')

    ax.bar(x*2, data_df['statuses'].astype(int)/data_df['count'].astype(int), width = bar_width, label = "statuses")
    ax.bar(x*2 + bar_width, data_df['logins'].astype(int)/data_df['count'].astype(int), width = bar_width, label = "logins")
    ax.bar(x*2 + bar_width + bar_width, data_df['registrations'].astype(int)/data_df['count'].astype(int), width = bar_width, label = "registrations")

    weeks = data_df['week']

    ax.set_xticks(x*2 + bar_width)
    ax.legend(loc="right")
    ax.set_xticklabels(weeks, fontsize = 5, rotation = 45)

    figure_canvas_agg = FigureCanvasTkAgg(fig, C)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().grid(row = 1, column = 0, columnspan = 2, rowspan = 2)
    return figure_canvas_agg

def on_closing():
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        exit()

# Create DataFrame
def create_dataframe(data, data_quantity):
    data_df = pd.DataFrame(data)
    data_df = data_df.sort_values(by=['week'], ascending = False)
    data_df = data_df.reset_index()
    data_df = data_df.drop('index', axis=1)
    data_df = data_df.head(data_quantity)
    return data_df

def take_input(data, data_quantity, C, root):
    input_number = T.get("1.0", "end-1c")
    if input_number.strip().isdigit():
        if int(input_number.strip()) <= len(data) - 1:
            data_quantity = int(input_number.strip())
            data_df = create_dataframe(data, data_quantity)
            draw_figure(data_df, C, root)

# Get collected data
file_check = open("data", "a")
file_check.close()
data_file = open("data", "rb")
data = []
try:
    data = pickle.load(data_file)
except:
    pass
data_file.close()

data_df = pd.DataFrame(data)
data_df = data_df.sort_values(by=['week'], ascending = False)
data_df = data_df.reset_index()
data_df = data_df.drop('index', axis=1)
if len(data_df) < 12:
    data_quantity = len(data_df)
else:
    data_quantity = 12

data_df = create_dataframe(data, data_quantity)

root = tk.Tk()
root.title("Charting Mastodon Activity")

root.protocol("WM_DELETE_WINDOW", on_closing)

C = tk.Canvas(root, height = 250, width = 300)
C.grid(row = 2, column = 0, columnspan = 2, rowspan = 2)

input_grid = tk.Canvas(root, height = 250, width = 300)
input_grid.grid(row = 0, column = 0, columnspan = 2)

draw_figure(data_df, C, root)

entries_label = tk.Label(input_grid, text = "Enter number of data entries to plot:", width = 37, anchor="sw")

T = tk.Text(input_grid, height = 1, pady = 5)
Display = tk.Button(input_grid, height = 1, width = 20, text = "Enter", command = lambda:take_input(data, data_quantity, C, root))
entries_label.grid(row = 0, column = 0, sticky = "sw")
T.grid(row = 1, column = 0, sticky = "w")
Display.grid(row = 1, column = 1)

root.grid_columnconfigure(0, weight = 1)
root.grid_rowconfigure(0, weight = 1)
root.grid_rowconfigure(1, weight = 1)

root.mainloop()
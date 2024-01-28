import PySimpleGUI as sg
import pickle
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

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

# Create DataFrame
data_df = pd.DataFrame(data)
data_df = data_df.sort_values(by=['week'], ascending = False)
data_df = data_df.reset_index()
data_df = data_df.drop('index', axis=1)

# Plot graph
x = np.arange(len(data_df))
bar_width = 0.5
weeks = []

fig, ax = plt.subplots(num='Test graph')

ax.grid(axis = 'y')

ax.bar(x*2, data_df['statuses'].astype(int)/data_df['count'].astype(int), width = bar_width, label = "statuses")
ax.bar(x*2 + bar_width, data_df['logins'].astype(int)/data_df['count'].astype(int), width = bar_width, label = "logins")
ax.bar(x*2 + bar_width + bar_width, data_df['registrations'].astype(int)/data_df['count'].astype(int), width = bar_width, label = "registrations")

weeks = data_df['week']

ax.set_xticks(x*2 + bar_width)
ax.legend(loc="right")
ax.set_xticklabels(weeks, fontsize=5, rotation=45)

# Show the graph on the window
layout = [
    [sg.Text("Weekly Activity")],
    [sg.Canvas(key="-CANVAS-")],
    [sg.Button("Close")],
]

window = sg.Window(
    "Matplotlib Single Graph",
    layout,
    location=(0, 0),
    finalize=True,
    element_justification="center",
    font="Helvetica 18",
)

draw_figure(window["-CANVAS-"].TKCanvas, fig)

event, values = window.read()

window.close()
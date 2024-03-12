'''
This program takes the activity data collected by the back-end and displays it
in a graph.

To run this, use: python3 front-end.py
'''

import pickle
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import tkinter as tk
from sys import exit
from datetime import datetime

matplotlib.use('TkAgg')


# Plot the graph.
def draw_figure(data_df, graph_canvas, root, file_name, save):
    # Remove the old graph.
    graph_canvas.grid_remove()
    graph_canvas = tk.Canvas(root, height=250, width=300)
    graph_canvas.grid(row=1, column=0, columnspan=2, rowspan=2)

    # Create the new graph.
    fig, ax = plt.subplots()
    ax.grid()

    # Plot the data on the graph.
    ax.plot(data_df['week'].to_numpy(),
            data_df['statuses'].to_numpy().astype(int) /
            data_df['count'].to_numpy().astype(int),
            label='statuses', marker='x')
    ax.plot(data_df['week'].to_numpy(),
            data_df['logins'].to_numpy().astype(int) /
            data_df['count'].to_numpy().astype(int),
            label='logins', marker='x')
    ax.plot(data_df['week'].to_numpy(),
            data_df['registrations'].to_numpy().astype(int) /
            data_df['count'].to_numpy().astype(int),
            label='registrations', marker='x')

    # Create a graph legend.
    ax.legend(loc='best')

    # Draw the graph in order to get the x-axis labels.
    figure_canvas_agg = FigureCanvasTkAgg(fig, graph_canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().grid(row=1, column=0, columnspan=2,
                                           rowspan=2)

    # Replace the x-axis labels with dates rather than Unix timestamps.
    old_labels = [item.get_position() for item in ax.get_xticklabels()]
    labels = old_labels.copy()
    for label in range(0, len(labels)):
        labels[label] = datetime.fromtimestamp(
                float(labels[label][0])).strftime('%d/%m/%y, %H:%M')
    for x in range(0, len(old_labels)):
        old_labels[x] = float(old_labels[x][0])
    ax.set_xticks(old_labels)
    ax.set_xticklabels(labels, rotation=15)

    # Draw the final graph.
    figure_canvas_agg = FigureCanvasTkAgg(fig, graph_canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().grid(row=1, column=0, columnspan=2,
                                           rowspan=2)
    if save:
        if file_name != '':
            fig.savefig(file_name + '.png')
        else:
            fig.savefig('graph.png')
    return figure_canvas_agg


# Ask for confirmation before closing the program.
def on_closing():
    if tk.messagebox.askokcancel('Quit', 'Do you want to quit?'):
        root.destroy()
        exit()


# Create the DataFrame.
def create_dataframe(data, data_quantity):
    data_df = pd.DataFrame(data)
    data_df = data_df.sort_values(by=['week'], ascending=False)
    data_df = data_df.reset_index()
    data_df = data_df.drop('index', axis=1)
    data_df = data_df.head(data_quantity)
    return data_df


# Get the input from the entries text box.
def take_entries_input(data, data_quantity, graph_canvas, root, save):
    input_number = entries_text_box.get('1.0', 'end-1c')
    file_name = save_text_box.get('1.0', 'end-1c')
    if input_number.strip().isdigit():
        if int(input_number.strip()) <= len(data) - 1 \
                and int(input_number.strip()) > 0:
            data_quantity = int(input_number.strip())
    data_df = create_dataframe(data, data_quantity)
    draw_figure(data_df, graph_canvas, root, file_name, save)


# Get the collected data.
file_check = open('data', 'a')
file_check.close()
data = []
try:
    data_file = open('data', 'rb')
    data = pickle.load(data_file)
    data_file.close()
except Exception:
    pass

# Create a DataFrame to set an initial value for data_quantity.
data_df = pd.DataFrame(data)
data_df = data_df.sort_values(by=['week'], ascending=False)
data_df = data_df.reset_index()
data_df = data_df.drop('index', axis=1)
if len(data_df) < 12:
    data_quantity = len(data_df)
else:
    data_quantity = 12

# Create the inital DataFrame using the data_quantity limit.
data_df = create_dataframe(data, data_quantity)

# Create the window.
root = tk.Tk()
root.title('Charting Mastodon Activity')

# Set the 'x' on the windoiw to call the on_closing function.
root.protocol('WM_DELETE_WINDOW', on_closing)

# Create the initial canvas that the graph will be displayed on.
graph_canvas = tk.Canvas(root, height=250, width=300)
graph_canvas.grid(row=2, column=0, columnspan=2, rowspan=2)

# Create the canvas for getting inputs from the user.
input_grid = tk.Canvas(root, height=250, width=300)
input_grid.grid(row=0, column=0, columnspan=2)

# Create the initial graph.
draw_figure(data_df, graph_canvas, root, '', False)

# Create the elements for the input_grid canvas.
entries_label = tk.Label(input_grid,
                         text='Enter number of data entries to plot:',
                         width=37, anchor='sw')
entries_text_box = tk.Text(input_grid, height=1, pady=5)
entries_button = tk.Button(input_grid, height=1, width=20, text='Enter',
                           command=lambda:
                           take_entries_input(data, data_quantity,
                                              graph_canvas, root, False))

save_label = tk.Label(input_grid,
                      text='Enter the file name you want the gaph to be ' +
                           'saved as:', anchor='sw')
save_text_box = tk.Text(input_grid, height=1, pady=5)
save_button = tk.Button(input_grid, height=1, width=20, text='Save graph',
                        command=lambda:
                        take_entries_input(data, data_quantity,
                                           graph_canvas, root, True))

entries_label.grid(row=0, column=0, sticky='sw')
entries_text_box.grid(row=1, column=0, sticky='w')
entries_button.grid(row=1, column=1)

save_label.grid(row=2, column=0, sticky='sw')
save_text_box.grid(row=3, column=0, sticky='w')
save_button.grid(row=3, column=1)

# Ensure that the elements in the window scale appropriately.
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

root.mainloop()

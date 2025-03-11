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
import time
import tkcalendar
from tkinter import ttk
from os import listdir, mkdir

matplotlib.use('TkAgg')


# Plot the graph.
def draw_figure(data_df_array, frame, file_name, save):
    # Remove the old graph.
    global figure_canvas_agg, selected_instances
    figure_canvas_agg.get_tk_widget().destroy()
    plt.close('all')

    # Create the new graph.
    fig, ax = plt.subplots()
    ax.grid()
    width_value = width_text_box.get('1.0', 'end-1c').strip()
    height_value = height_text_box.get('1.0', 'end-1c').strip()
    if width_value.isdigit():
        fig.set_figwidth(int(width_value))
    if height_value.isdigit():
        fig.set_figheight(int(height_value))

    # Plot the data on the graph.
    for index in range(len(data_df_array)):
        for i in range(len(selected_instances)):
            if selected_instances[i][0] == data_df_array[index][0] and selected_instances[i][1] == 1:
                if show_statuses.get():
                    ax.plot(data_df_array[index][1]['week'].to_numpy(),
                            data_df_array[index][1]['statuses'].to_numpy().astype(int) /
                            data_df_array[index][1]['count'].to_numpy().astype(int),
                            label=data_df_array[index][0] + ' statuses', marker='x')
                if show_logins.get():
                    ax.plot(data_df_array[index][1]['week'].to_numpy(),
                            data_df_array[index][1]['logins'].to_numpy().astype(int) /
                            data_df_array[index][1]['count'].to_numpy().astype(int),
                            label=data_df_array[index][0] + ' logins', marker='x')
                if show_registrations.get():
                    ax.plot(data_df_array[index][1]['week'].to_numpy(),
                            data_df_array[index][1]['registrations'].to_numpy().astype(int) /
                            data_df_array[index][1]['count'].to_numpy().astype(int),
                            label=data_df_array[index][0] + ' registrations', marker='x')
                break

    # Create a graph legend.
    if show_statuses.get() or show_logins.get() or show_registrations.get():
        for i in range(len(selected_instances)):
            if selected_instances[i][1] == 1:
                ax.legend(loc='best')
                break

    # Draw the graph in order to get the x-axis labels.
    figure_canvas_agg = FigureCanvasTkAgg(fig, frame)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().grid(row=2, column=0)

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
    if save:
        try:
            file_check = open('./graphs/' + listdir('./data_files')[0], 'a')
            file_check.close()
        except Exception:
            mkdir('graphs')
        if file_name != '':
            fig.savefig('./graphs/' + file_name + '.png')
        else:
            fig.savefig('./graphs/graph.png')


# Ask for confirmation before closing the program.
def on_closing():
    if tk.messagebox.askokcancel('Quit', 'Do you want to quit?'):
        exit()


# Create the DataFrame.
def create_dataframe(data):
    global selected_instances
    data_df_array = []
    for i in range(len(selected_instances)):
        if selected_instances[i][1] == 1:
            for index in range(len(data)):
                if selected_instances[i][0] == data[index][0]:
                    break
            data_df = pd.DataFrame(data[index][1])
            data_df = data_df.sort_values(by=['week'], ascending=False)
            data_df = data_df.reset_index()
            data_df = data_df.drop('index', axis=1)
            data_df_array.append([selected_instances[i][0], data_df])
    return data_df_array


# Get the inputs from the entries text box.
def get_inputs(data, frame, save):
    # Get the file name.
    file_name = save_text_box.get('1.0', 'end-1c')
    # Create a new DataFrame which only contains the data between midnight of
    # the earlier date and just before the end of the later date.
    data_df_array = create_dataframe(data)
    limit1 = int(time.mktime(time.strptime(date1.get(), '%d/%m/%Y')))
    limit2 = int(time.mktime(time.strptime(date2.get(), '%d/%m/%Y')))
    if limit1 > limit2:
        temp = limit1
        limit1 = limit2
        limit2 = temp
    limit2 += (24 * 60 * 60)
    for index in range(len(data_df_array)):
        data_df_array[index][1] = data_df_array[index][1][data_df_array[index][1]['week'].astype(int) >= limit1]
        data_df_array[index][1] = data_df_array[index][1][data_df_array[index][1]['week'].astype(int) < limit2]
    draw_figure(data_df_array, frame, file_name, save)


# Adjust the region that can be scrolled when the information dislayed on the
# window is changed.
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))


# Resize the canvas to the correct size when the window changes size.
def resize_canvas(event):
    canvas.config(width=frame.winfo_width(), height=frame.winfo_height())


# Track which instances have been selected by updating the selected_instances array.
def instance_changed(event):
    global selected_instances
    for index in range(len(selected_instances)):
        if selected_instances[index][0] == instance_chosen.get():
            if selected_instances[index][1] == 0:
                selected_instances[index][1] = 1
            else:
                selected_instances[index][1] = 0
            break
    get_inputs(data, frame, False)


# Create the window.
root = tk.Tk()
root.title('Charting Mastodon Activity')

# Set the 'x' on the window to call the on_closing function.
root.protocol('WM_DELETE_WINDOW', on_closing)

# Create the canvas for the window.
canvas = tk.Canvas(root, highlightthickness=0)
canvas.grid(row=0, column=0, sticky='n')

# Create the frame for grouping the other widgets together.
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame)

# Create the scroll bars.
vertical_scroll_bar = ttk.Scrollbar(root, orient='vertical',
                                    command=canvas.yview)
vertical_scroll_bar.grid(row=0, column=1, sticky='ns')

horizontal_scroll_bar = ttk.Scrollbar(root, orient='horizontal',
                                      command=canvas.xview)
horizontal_scroll_bar.grid(row=1, column=0, sticky='ew')

# Configure the canvas to allow for scrolling.
canvas.configure(yscrollcommand=vertical_scroll_bar.set,
                 xscrollcommand=horizontal_scroll_bar.set)

frame.bind('<Configure>', on_frame_configure)

# Create the required variables for the checkboxes.
show_statuses = tk.BooleanVar()
show_logins = tk.BooleanVar()
show_registrations = tk.BooleanVar()

# Check if data has been collected.
try:
    file_check = open('./data_files/' + listdir('./data_files')[0], 'a')
    file_check.close()
except Exception:
    raise SystemExit('No data has been collected.')

# Create the array that tracks which instances have been selected.
selected_instances = []
for x in listdir('./data_files'):
    selected_instances.append([x, 0])
selected_instances[0][1] = 1

# Get the collected data.
data = []
for instance in range(len(listdir('./data_files'))):
    try:
        data_file = open('./data_files/' + listdir('./data_files')[instance], 'rb')
        data.append([listdir('./data_files')[instance], pickle.load(data_file)])
        data_file.close()
    except Exception:
        continue

# Create a DataFrame to set a value for how much data to show initially.
data_df = pd.DataFrame(data[0][1])
data_df = data_df.sort_values(by=['week'], ascending=False)
data_df = data_df.reset_index()
data_df = data_df.drop('index', axis=1)
if len(data_df) < 12:
    data_quantity = len(data_df)
else:
    data_quantity = 12

# Create the inital DataFrame using the data_quantity limit.
data_df_array = create_dataframe(data)
data_df = data_df_array[0][1].head(data_quantity)

# Create the frame for getting inputs from the user.
input_grid = tk.Frame(frame, height=250, width=300)
input_grid.grid(row=0, column=0)

# Create the initial graph.
fig, ax = plt.subplots()
ax.grid()

# Plot the data on the graph.
ax.plot(data_df['week'].to_numpy(),
        data_df['statuses'].to_numpy().astype(int) /
        data_df['count'].to_numpy().astype(int),
        label=data_df_array[0][0] + ' statuses', marker='x')
ax.plot(data_df['week'].to_numpy(),
        data_df['logins'].to_numpy().astype(int) /
        data_df['count'].to_numpy().astype(int),
        label=data_df_array[0][0] + ' logins', marker='x')
ax.plot(data_df['week'].to_numpy(),
        data_df['registrations'].to_numpy().astype(int) /
        data_df['count'].to_numpy().astype(int),
        label=data_df_array[0][0] + ' registrations', marker='x')

# Create a graph legend.
ax.legend(loc='best')

# Draw the graph in order to get the x-axis labels.
figure_canvas_agg = FigureCanvasTkAgg(fig, frame)
figure_canvas_agg.draw()
figure_canvas_agg.get_tk_widget().grid(row=2, column=0)

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

# Create the elements for the input_grid frame.
instance_chosen = tk.StringVar()
combobox_label = tk.Label(input_grid, text='Select which instance you want to add/remove:', width=37, anchor='sw')
combobox_label.grid(row=0, column=0, sticky='w')
combobox = ttk.Combobox(input_grid, width = 79, state='readonly', textvariable=instance_chosen)
combobox['values'] = listdir('./data_files')
combobox.grid(row=1, column=0)

entries_label = tk.Label(input_grid,
                         text='Enter the start and end dates for the data:',
                         width=37, anchor='sw')

entries_button = tk.Button(input_grid, height=6, width=20, text='Enter',
                           command=lambda:
                           get_inputs(data, frame, False))

save_label = tk.Label(input_grid,
                      text='\nEnter the file name you want the graph to be ' +
                           'saved as:', anchor='sw')
save_text_box = tk.Text(input_grid, height=1, pady=5)
save_button = tk.Button(input_grid, height=1, width=20, text='Save graph',
                        command=lambda:
                        get_inputs(data, frame, True))

# Create the frame for the start and end date selection.
dates_grid = tk.Frame(input_grid, height=50, width=300)

# Create the frame for the checkboxes.
checkbox_grid = tk.Frame(input_grid, height=50, width=300)

# Create the frames for the width and height inputs.
graph_size_grid = tk.Frame(input_grid, height=50, width=300)

# Add the elements to the input_grid frame.
entries_label.grid(row=2, column=0, sticky='sw')

dates_grid.grid(row=3, column=0, sticky='w')

entries_button.grid(row=3, column=1, rowspan=4)

checkbox_grid.grid(row=4, column=0, sticky='n')

graph_size_grid.grid(row=5, column=0)

save_label.grid(row=7, column=0, sticky='sw')
save_text_box.grid(row=8, column=0, sticky='w')
save_button.grid(row=8, column=1)

# Create the checkboxes that will determine if a metric is shown.
statuses_checkbox = tk.Checkbutton(checkbox_grid, text='Show statuses',
                                   variable=show_statuses, onvalue=True,
                                   offvalue=False)
statuses_checkbox.select()
logins_checkbox = tk.Checkbutton(checkbox_grid, text='Show logins',
                                 variable=show_logins, onvalue=True,
                                 offvalue=False)
logins_checkbox.select()
registrations_checkbox = tk.Checkbutton(checkbox_grid,
                                        text='Show registrations',
                                        variable=show_registrations,
                                        onvalue=True, offvalue=False)
registrations_checkbox.select()

# Add the checkboxes to the checkbox_grid frame.
statuses_checkbox.grid(row=0, column=0)
logins_checkbox.grid(row=0, column=1)
registrations_checkbox.grid(row=0, column=2)

# Create the elements for the graph_size_grid frame.
width_label = tk.Label(graph_size_grid, text='Enter the width of the graph ' +
                       'in inches (optional):')
width_text_box = tk.Text(graph_size_grid, height=1, width=39, pady=5)
height_label = tk.Label(graph_size_grid, text='Enter the height of the graph' +
                        ' in inches (optional):')
height_text_box = tk.Text(graph_size_grid, height=1, width=40, pady=5)

# Add the checkboxes to the graph_size_grid frame.
width_label.grid(row=0, column=0)
width_text_box.grid(row=1, column=0)
height_label.grid(row=0, column=1)
height_text_box.grid(row=1, column=1)

# Create the calendars for the dates_grid frame.
start_date = datetime.fromtimestamp(float(old_labels[0])).strftime('%d/%m/%Y')
date1 = tkcalendar.DateEntry(dates_grid, width=38)
date1.set_date(start_date)

end_date = datetime.fromtimestamp(float(
                                  old_labels[len(
                                    old_labels)-1])).strftime('%d/%m/%Y')
date2 = tkcalendar.DateEntry(dates_grid, width=39)
date2.set_date(end_date)

# Add the calendars to the dates_grid frame.
date1.grid(row=0, column=0)
date2.grid(row=0, column=1)

# Ensure that the elements in the window scale appropriately.
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Set the initial window size.
starting_width = frame.winfo_width()+16
starting_height = frame.winfo_height()+16
root.geometry(f'{starting_width}x{starting_height}')

# Call the resize_canvas function when the window changes size.
root.bind('<Configure>', resize_canvas)

# Call the instance_changed function when a new instance is selected.
combobox.bind('<<ComboboxSelected>>', instance_changed)

root.mainloop()

'''
This program takes the activity data collected by the back-end and displays it
on a graph.

To run this, use: python3 front-end.py
'''

import numpy
from pickle import load
from matplotlib.pyplot import close, subplots
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
from sys import exit
from datetime import datetime
from time import mktime, strptime
from tkcalendar import DateEntry
from tkinter import (Tk, ttk, messagebox, Canvas, Frame, BooleanVar, StringVar,
                     Label, Button, Checkbutton, Text, font, Scale,
                     colorchooser)
from os import listdir, mkdir, path
from pathvalidate import is_valid_filename, sanitize_filename


# Plot the graph.
def draw_figure(data_df_array, frame, file_name, save):
    # Remove the old graph.
    global figure_canvas_agg, selected_instances
    figure_canvas_agg.get_tk_widget().destroy()
    close('all')

    # Create the new graph.
    fig, ax = subplots()
    ax.grid()
    width_value = width_text_box.get('1.0', 'end-1c').strip()
    height_value = height_text_box.get('1.0', 'end-1c').strip()

    if width_value.isdigit() and height_value.isdigit():
        fig.set_figwidth(int(width_value))
        fig.set_figheight(int(height_value))
    elif width_value.isdigit() and height_value == '':
        fig.set_figwidth(int(width_value))
    elif height_value.isdigit() and width_value == '':
        fig.set_figheight(int(height_value))
    elif width_value.isdigit() and height_value != '':
        fig.set_figwidth(int(width_value))
        messagebox.showerror(title='Invalid height', message='The height '
                             + 'entered was invalid.\nThe height has been '
                             + 'reset.')
    elif height_value.isdigit() and width_value != '':
        fig.set_figheight(int(height_value))
        messagebox.showerror(title='Invalid width', message='The width entered'
                             + ' was invalid.\nThe width has been reset.')
    elif width_value != '' and height_value != '':
        messagebox.showerror(title='Invalid dimensions', message='The width '
                             + 'and height values entered were invalid.\nThe '
                             + 'dimensions have been reset.')
    elif width_value != '':
        messagebox.showerror(title='Invalid width', message='The width entered'
                             + ' was invalid.\nThe width has been reset.')
    elif height_value != '':
        messagebox.showerror(title='Invalid height', message='The height '
                             + 'entered was invalid.\nThe height has been '
                             + 'reset.')

    # Plot the data on the graph.
    for index in range(len(data_df_array)):
        for i in range(len(selected_instances)):
            if (selected_instances[i][0] == data_df_array[index][0] and
                    selected_instances[i][1] == 1):
                if show_statuses.get():
                    ax.plot(data_df_array[index][1]['week'].to_numpy(),
                            data_df_array[index][1]['statuses'].to_numpy()
                            .astype(int) / data_df_array[index][1]['count']
                            .to_numpy().astype(int),
                            label=data_df_array[index][0] + ' statuses',
                            marker='x')
                if show_logins.get():
                    ax.plot(data_df_array[index][1]['week'].to_numpy(),
                            data_df_array[index][1]['logins'].to_numpy()
                            .astype(int) / data_df_array[index][1]['count']
                            .to_numpy().astype(int),
                            label=data_df_array[index][0] + ' logins',
                            marker='x')
                if show_registrations.get():
                    ax.plot(data_df_array[index][1]['week'].to_numpy(),
                            data_df_array[index][1]['registrations'].to_numpy()
                            .astype(int) / data_df_array[index][1]['count']
                            .to_numpy().astype(int),
                            label=data_df_array[index][0] + ' registrations',
                            marker='x')
                break

    # Create a graph legend.
    if show_statuses.get() or show_logins.get() or show_registrations.get():
        for i in range(len(selected_instances)):
            if selected_instances[i][1] == 1:
                ax.legend(loc='best')
                break

    # Draw the graph to get the x-axis labels.
    figure_canvas_agg = FigureCanvasTkAgg(fig, frame)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().grid(row=4, column=5)

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
        if not path.exists('./graphs/'):
            mkdir('graphs')
        if file_name != '':
            if (is_valid_filename(file_name)):
                fig.savefig('./graphs/' + file_name)
                messagebox.showinfo(title='Graph saved', message='Graph saved '
                                    + 'as \'' + file_name + '\'.')
            else:
                if sanitize_filename(file_name) != '':
                    messagebox.showerror(title='Invalid file name',
                                         message='The graph was not saved.\n'
                                         + 'Did you mean \''
                                         + sanitize_filename(file_name)
                                         + '\'?')
                else:
                    messagebox.showerror(title='Invalid file name',
                                         message='The graph was not saved.')
        else:
            fig.savefig('./graphs/graph')
            messagebox.showinfo(title='Graph saved', message='Graph saved as '
                                + '\'graph\'.')


# Ask for confirmation before closing the program.
def on_closing():
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
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
            data_df = DataFrame(data[index][1])
            data_df = data_df.sort_values(by=['week'], ascending=False)
            data_df = data_df.reset_index()
            data_df = data_df.drop('index', axis=1)
            data_df_array.append([selected_instances[i][0], data_df])
    return data_df_array


# Get the inputs from the relevant entry elements to provide the required data
# to create the new graph (and save it if required).
def get_inputs(data, frame, save):
    # Get the file name.
    file_name = save_text_box.get('1.0', 'end-1c')
    # Create a new DataFrame which only contains the data between midnight of
    # the earlier date and just before the end of the later date.
    data_df_array = create_dataframe(data)
    limit1 = int(mktime(strptime(date1.get(), '%d/%m/%Y')))
    limit2 = int(mktime(strptime(date2.get(), '%d/%m/%Y')))
    if limit1 > limit2:
        temp = limit1
        limit1 = limit2
        limit2 = temp
    limit2 += (24 * 60 * 60)
    for index in range(len(data_df_array)):
        data_df_array[index][1] = \
            data_df_array[index][1][data_df_array[index][1]['week']
                                    .astype(int) >= limit1]
        data_df_array[index][1] = \
            data_df_array[index][1][data_df_array[index][1]['week']
                                    .astype(int) < limit2]
    draw_figure(data_df_array, frame, file_name, save)


# Adjust the region that can be scrolled when the information displayed on the
# window is changed.
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))


# Resize the canvas to the correct size when the window changes size.
def resize_canvas(event):
    canvas.configure(width=frame.winfo_width(), height=frame.winfo_height())
    separator.configure(height=root.winfo_height()-16)


# Track which instances have been selected by updating the selected_instances
# array.
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


# Change the font when a new font is selected.
def font_changed(event):
    app_font.configure(family=font_chosen.get())
    app_title_font.configure(family=font_chosen.get())


# Change the font size when a new font size is selected, and adjust the widths
# accordingly.
def font_size_changed(event):
    app_font.configure(size=font_size_scale.get())
    app_title_font.configure(size=font_size_scale.get() + 5)
    app_textbox_font.configure(size=font_size_scale.get())
    app_width_1 = int(round((1/font_size_scale.get()) * 420))
    app_width_2 = int(round((1/font_size_scale.get()) * 430))
    app_width_3 = int(round((1/font_size_scale.get()) * 880))
    app_width_4 = int(round((1/font_size_scale.get()) * 300))
    date1.configure(width=app_width_1)
    date2.configure(width=app_width_2)
    width_text_box.configure(width=app_width_2)
    height_text_box.configure(width=app_width_2)
    save_text_box.configure(width=app_width_3)
    font_combobox.configure(width=app_width_4)
    bg_colour_button.configure(width=app_width_4)


# Explicitly change the background colour of every relevant element.
def choose_bg_colour():
    chosen_bg_colour = colorchooser.askcolor(title='Choose colour.')
    root.configure(bg=chosen_bg_colour[1])
    canvas.configure(bg=chosen_bg_colour[1])
    frame.configure(bg=chosen_bg_colour[1])
    input_grid.configure(bg=chosen_bg_colour[1])
    configuration_grid.configure(bg=chosen_bg_colour[1])
    dates_grid.configure(bg=chosen_bg_colour[1])
    window_configuration_label.configure(bg=chosen_bg_colour[1])
    change_font_label.configure(bg=chosen_bg_colour[1])
    change_font_size_label.configure(bg=chosen_bg_colour[1])
    font_size_scale.configure(bg=chosen_bg_colour[1],
                              highlightbackground=chosen_bg_colour[1])
    graph_configuration_label.configure(bg=chosen_bg_colour[1])
    combobox_label.configure(bg=chosen_bg_colour[1])
    entries_label.configure(bg=chosen_bg_colour[1])
    save_label.configure(bg=chosen_bg_colour[1])
    statuses_checkbox.configure(bg=chosen_bg_colour[1],
                                highlightbackground=chosen_bg_colour[1])
    logins_checkbox.configure(bg=chosen_bg_colour[1],
                              highlightbackground=chosen_bg_colour[1])
    registrations_checkbox.configure(bg=chosen_bg_colour[1],
                                     highlightbackground=chosen_bg_colour[1])
    graph_size_grid.configure(bg=chosen_bg_colour[1])
    width_label.configure(bg=chosen_bg_colour[1])
    height_label.configure(bg=chosen_bg_colour[1])
    empty_row_1.configure(bg=chosen_bg_colour[1])
    empty_row_2.configure(bg=chosen_bg_colour[1])
    empty_row_3.configure(bg=chosen_bg_colour[1])
    empty_row_4.configure(bg=chosen_bg_colour[1])
    empty_row_5.configure(bg=chosen_bg_colour[1])
    empty_row_6.configure(bg=chosen_bg_colour[1])
    empty_row_7.configure(bg=chosen_bg_colour[1])
    empty_row_8.configure(bg=chosen_bg_colour[1])
    empty_column_1.configure(bg=chosen_bg_colour[1])
    empty_column_2.configure(bg=chosen_bg_colour[1])
    empty_column_3.configure(bg=chosen_bg_colour[1])
    empty_column_4.configure(bg=chosen_bg_colour[1])
    style.configure('Vertical.TScrollbar', troughcolor=chosen_bg_colour[1],
                    arrowcolor=chosen_bg_colour[1])
    style.configure('Horizontal.TScrollbar', troughcolor=chosen_bg_colour[1],
                    arrowcolor=chosen_bg_colour[1])
    style.configure('TSeparator', background=chosen_bg_colour[1])
    style.configure('TCombobox', arrowcolor=chosen_bg_colour[1])
    width_text_box.configure(highlightbackground=chosen_bg_colour[1])
    height_text_box.configure(highlightbackground=chosen_bg_colour[1])
    save_text_box.configure(highlightbackground=chosen_bg_colour[1])


# Explicitly change the colour of every relevant input element.
def choose_input_colour():
    chosen_input_colour = colorchooser.askcolor(title='Choose colour.')
    style.configure('TCombobox', background=chosen_input_colour[1])
    font_size_scale.configure(troughcolor=chosen_input_colour[1])
    style.configure('DateEntry', fieldbackground=chosen_input_colour[1],
                    background=chosen_input_colour[1])
    width_text_box.configure(bg=chosen_input_colour[1])
    height_text_box.configure(bg=chosen_input_colour[1])
    save_text_box.configure(bg=chosen_input_colour[1])


# Explicitly change the colour of every relevant text element.
def choose_text_colour():
    chosen_text_colour = colorchooser.askcolor(title='Choose colour.')
    window_configuration_label.configure(fg=chosen_text_colour[1])
    change_font_label.configure(fg=chosen_text_colour[1])
    change_font_size_label.configure(fg=chosen_text_colour[1])
    font_size_scale.configure(fg=chosen_text_colour[1])
    text_colour_button.configure(fg=chosen_text_colour[1])
    bg_colour_button.configure(fg=chosen_text_colour[1])
    input_colour_button.configure(fg=chosen_text_colour[1])
    button_colour_button.configure(fg=chosen_text_colour[1])
    highlight_colour_button.configure(fg=chosen_text_colour[1])
    graph_configuration_label.configure(fg=chosen_text_colour[1])
    combobox_label.configure(fg=chosen_text_colour[1])
    entries_label.configure(fg=chosen_text_colour[1])
    entries_button.configure(fg=chosen_text_colour[1])
    save_label.configure(fg=chosen_text_colour[1])
    save_text_box.configure(fg=chosen_text_colour[1])
    save_button.configure(fg=chosen_text_colour[1])
    statuses_checkbox.configure(fg=chosen_text_colour[1])
    logins_checkbox.configure(fg=chosen_text_colour[1])
    registrations_checkbox.configure(fg=chosen_text_colour[1])
    width_label.configure(fg=chosen_text_colour[1])
    width_text_box.configure(fg=chosen_text_colour[1])
    height_label.configure(fg=chosen_text_colour[1])
    height_text_box.configure(fg=chosen_text_colour[1])
    style.configure('DateEntry', foreground=chosen_text_colour[1])


# Explicitly change the colour of every relevant button element.
def choose_button_colour():
    chosen_button_colour = colorchooser.askcolor(title='Choose colour.')
    text_colour_button.configure(bg=chosen_button_colour[1])
    bg_colour_button.configure(bg=chosen_button_colour[1])
    input_colour_button.configure(bg=chosen_button_colour[1])
    button_colour_button.configure(bg=chosen_button_colour[1])
    highlight_colour_button.configure(bg=chosen_button_colour[1])
    entries_button.configure(bg=chosen_button_colour[1])
    save_button.configure(bg=chosen_button_colour[1])


# Explicitly change the highlight colour of every relevant element.
def choose_highlight_colour():
    chosen_highlight_colour = colorchooser.askcolor(title='Choose colour.')
    text_colour_button.configure(
        highlightbackground=chosen_highlight_colour[1])
    bg_colour_button.configure(highlightbackground=chosen_highlight_colour[1])
    input_colour_button.configure(
        highlightbackground=chosen_highlight_colour[1])
    button_colour_button.configure(
        highlightbackground=chosen_highlight_colour[1])
    highlight_colour_button.configure(
        highlightbackground=chosen_highlight_colour[1])
    entries_button.configure(highlightbackground=chosen_highlight_colour[1])
    save_button.configure(highlightbackground=chosen_highlight_colour[1])
    separator.configure(bg=chosen_highlight_colour[1])
    style.configure('Vertical.TScrollbar',
                    background=chosen_highlight_colour[1])
    style.configure('Horizontal.TScrollbar',
                    background=chosen_highlight_colour[1])


# Create the window.
root = Tk()
style = ttk.Style()
style.theme_use('default')
root.title('Charting Mastodon Activity')

# Set the 'x' on the window to call the on_closing function.
root.protocol('WM_DELETE_WINDOW', on_closing)

# Create the canvas for the window.
canvas = Canvas(root, highlightthickness=0)
canvas.grid(row=0, column=0, sticky='n')

# Create the frame for grouping the other elements together.
frame = Frame(canvas)
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
show_statuses = BooleanVar()
show_logins = BooleanVar()
show_registrations = BooleanVar()

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
        data_file = open('./data_files/' + listdir('./data_files')[instance],
                         'rb')
        data.append([listdir('./data_files')[instance], load(data_file)])
        data_file.close()
    except Exception:
        continue

# Create a DataFrame to set the value for how much data to show initially.
data_df = DataFrame(data[0][1])
data_df = data_df.sort_values(by=['week'], ascending=False)
data_df = data_df.reset_index()
data_df = data_df.drop('index', axis=1)
if len(data_df) < 12:
    data_quantity = len(data_df)
else:
    data_quantity = 12

# Create the initial DataFrame using the data_quantity limit.
data_df_array = create_dataframe(data)
data_df = data_df_array[0][1].head(data_quantity)

# Create the frame for getting inputs from the user to configure the window.
configuration_grid = Frame(frame, height=250, width=300)
configuration_grid.grid(row=1, column=1, rowspan=5, sticky='ns')

# Collect all available fonts in an array.
font_options = []
for x in font.families():
    font_options.append(x)
font_options.sort()

# Set the default font.
font_style = StringVar(value='TkDefaultFont')

# Create the font variables.
app_font = font.Font(family=font_style.get(), size=10,
                     weight='normal')
app_title_font = font.Font(family=font_style.get(), size=15, weight='bold',
                           underline=1)
app_textbox_font = font.Font(size=10)

# Create the elements for the configuration_grid frame.
window_configuration_label = Label(configuration_grid,
                                   text='Window Configuration',
                                   anchor='w', wraplength=290,
                                   font=app_title_font)
window_configuration_label.grid(row=0, column=0, sticky='w')

change_font_label = Label(configuration_grid,
                          text='Select font:', anchor='w', wraplength=290,
                          font=app_font)
change_font_label.grid(row=1, column=0, sticky='w')

font_chosen = StringVar()
font_combobox = ttk.Combobox(configuration_grid, width=30, state='readonly',
                             textvariable=font_chosen, font=app_textbox_font)
font_combobox['values'] = font_options
font_combobox.grid(row=2, column=0)

change_font_size_label = Label(configuration_grid,
                               text='Select font size:', anchor='w',
                               wraplength=290, font=app_font)
change_font_size_label.grid(row=3, column=0, sticky='w')

font_size_scale = Scale(configuration_grid, from_=1, to=100,
                        orient='horizontal', font=app_textbox_font)
font_size_scale.set(10)
font_size_scale.grid(row=4, column=0, sticky='ew')

empty_row_1 = Label(configuration_grid, text='')
empty_row_1.grid(row=5, column=0)

text_colour_button = Button(configuration_grid, text='Select text colour',
                            command=choose_text_colour, wraplength=300,
                            font=app_font)
text_colour_button.grid(row=6, column=0, sticky='ew')

empty_row_2 = Label(configuration_grid, text='')
empty_row_2.grid(row=7, column=0)

bg_colour_button = Button(configuration_grid, text='Select background colour',
                          command=choose_bg_colour, wraplength=300,
                          font=app_font)
bg_colour_button.grid(row=8, column=0, sticky='ew')

empty_row_3 = Label(configuration_grid, text='')
empty_row_3.grid(row=9, column=0)

input_colour_button = Button(configuration_grid, text='Select input colour',
                             command=choose_input_colour, wraplength=300,
                             font=app_font)
input_colour_button.grid(row=10, column=0, sticky='ew')

empty_row_4 = Label(configuration_grid, text='')
empty_row_4.grid(row=11, column=0)

button_colour_button = Button(configuration_grid, text='Select button colour',
                              command=choose_button_colour,
                              wraplength=300, font=app_font)
button_colour_button.grid(row=12, column=0, sticky='ew')

empty_row_5 = Label(configuration_grid, text='')
empty_row_5.grid(row=13, column=0)

highlight_colour_button = Button(configuration_grid, text='Select highlight '
                                 + 'colour', command=choose_highlight_colour,
                                 wraplength=300, font=app_font)
highlight_colour_button.grid(row=14, column=0, sticky='ew')

# Add padding around the frames and the separator.
empty_column_1 = Label(frame, text='', width=2)
empty_column_1.grid(row=1, column=0)

empty_column_2 = Label(frame, text='', width=2)
empty_column_2.grid(row=1, column=2)

empty_column_3 = Label(frame, text='', width=2)
empty_column_3.grid(row=1, column=4)

empty_column_4 = Label(frame, text='', width=2)
empty_column_4.grid(row=1, column=6)

empty_row_6 = Label(frame, text='')
empty_row_6.grid(row=0, column=0, columnspan=6)

empty_row_7 = Label(frame, text='')
empty_row_7.grid(row=3, column=5)

empty_row_8 = Label(frame, text='')
empty_row_8.grid(row=5, column=5)

# Create a separator between the configuration_grid frame and the input_grid
# frame.
separator = Frame(frame, width=1, bg='grey', relief='groove')
separator.grid(row=0, column=3, rowspan=6, sticky='ns')

# Create the frame for getting inputs from the user.
input_grid = Frame(frame, height=250, width=300)
input_grid.grid(row=1, column=5)

# Create the initial graph.
fig, ax = subplots()
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

# Draw the graph to get the x-axis labels.
figure_canvas_agg = FigureCanvasTkAgg(fig, frame)
figure_canvas_agg.draw()
figure_canvas_agg.get_tk_widget().grid(row=4, column=5)

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

graph_configuration_label = Label(input_grid, text='Graph Configuration',
                                  anchor='w', wraplength=800,
                                  font=app_title_font)
graph_configuration_label.grid(row=0, column=0, sticky='w')

# Create the elements for the input_grid frame.
instance_chosen = StringVar()
combobox_label = Label(input_grid,
                       text='Select the instance you would like to add or '
                       + 'remove:', anchor='sw', wraplength=800, font=app_font)
combobox_label.grid(row=1, column=0, sticky='w')
combobox = ttk.Combobox(input_grid, state='readonly',
                        textvariable=instance_chosen, font=app_textbox_font)
combobox['values'] = listdir('./data_files')
combobox.grid(row=2, column=0, columnspan=2, sticky='ew')

entries_label = Label(input_grid,
                      text='Enter the start and end dates for the data:',
                      anchor='sw', wraplength=800, font=app_font)

entries_button = Button(input_grid, height=6, width=20, text='Enter',
                        command=lambda: get_inputs(data, frame, False),
                        font=app_font)

save_label = Label(input_grid,
                   text='\nEnter the file name you would like the graph to be '
                   + 'saved as:', anchor='sw', wraplength=800, font=app_font)
save_text_box = Text(input_grid, height=1, width=88, pady=5, padx=2,
                     font=app_textbox_font)
save_button = Button(input_grid, height=1, width=20, text='Save graph',
                     font=app_font, command=lambda: get_inputs(data, frame,
                                                               True))

# Create the frame for the start and end date selection.
dates_grid = Frame(input_grid, height=50, width=300)

# Create the frame for the checkboxes.
checkbox_grid = Frame(input_grid, height=50, width=300)

# Create the frames for the width and height inputs.
graph_size_grid = Frame(input_grid, height=50, width=300)

# Add the elements to the input_grid frame.
entries_label.grid(row=3, column=0, sticky='sw')

dates_grid.grid(row=4, column=0, sticky='ew')

entries_button.grid(row=4, column=1, rowspan=4, sticky='ns')

graph_size_grid.grid(row=5, column=0, sticky='w')

checkbox_grid.grid(row=7, column=0, sticky='nw')

save_label.grid(row=8, column=0, sticky='sw')
save_text_box.grid(row=9, column=0, sticky='w')
save_button.grid(row=9, column=1)

# Create the checkboxes that will determine if a metric is shown.
statuses_checkbox = Checkbutton(checkbox_grid, text='Show statuses',
                                variable=show_statuses, onvalue=True,
                                offvalue=False, wraplength=240, font=app_font)
statuses_checkbox.select()
logins_checkbox = Checkbutton(checkbox_grid, text='Show logins',
                              variable=show_logins, onvalue=True,
                              offvalue=False, wraplength=240, font=app_font)
logins_checkbox.select()
registrations_checkbox = Checkbutton(checkbox_grid, text='Show registrations',
                                     variable=show_registrations, onvalue=True,
                                     offvalue=False, wraplength=240,
                                     font=app_font)
registrations_checkbox.select()

# Add the checkboxes to the checkbox_grid frame.
statuses_checkbox.grid(row=0, column=0)
logins_checkbox.grid(row=0, column=1)
registrations_checkbox.grid(row=0, column=2)

# Create the elements for the graph_size_grid frame.
width_label = Label(graph_size_grid, text='Enter the width of the graph ' +
                    'in inches (optional): ', wraplength=400, font=app_font)
width_text_box = Text(graph_size_grid, height=1, width=43, pady=5, padx=4,
                      font=app_textbox_font)
height_label = Label(graph_size_grid, text='Enter the height of the graph' +
                     ' in inches (optional): ', wraplength=400, font=app_font)
height_text_box = Text(graph_size_grid, height=1, width=43, pady=5, padx=5,
                       font=app_textbox_font)

# Add the elements to the graph_size_grid frame.
width_label.grid(row=0, column=0, sticky='w')
width_text_box.grid(row=1, column=0)
height_label.grid(row=0, column=1, sticky='w')
height_text_box.grid(row=1, column=1)

# Create the calendars for the dates_grid frame.
start_date = datetime.fromtimestamp(float(old_labels[0])).strftime('%d/%m/%Y')
date1 = DateEntry(dates_grid, width=42, font=app_textbox_font)
date1.set_date(start_date)

end_date = datetime.fromtimestamp(float(
                                  old_labels[len(
                                    old_labels)-1])).strftime('%d/%m/%Y')
date2 = DateEntry(dates_grid, width=43, font=app_textbox_font)
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

# Call the font_changed function when a new font is selected.
font_combobox.bind('<<ComboboxSelected>>', font_changed)

# Call the font_size_changed function when a new font size is selected.
font_size_scale.bind('<ButtonRelease-1>', font_size_changed)

root.mainloop()

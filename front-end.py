'''
The front-end takes the activity data collected by the back-end and displays it
on a graph. When connected to a local LLM, it can also provide an AI analysis
of the displayed data.

To run this, use: python3 front-end.py
'''

from tkinter import (Tk, ttk, Canvas, Text, Button, StringVar, Label, Toplevel,
                     BooleanVar, Checkbutton, Frame, font, Scale, colorchooser)
from requests import get, post
from webbrowser import open_new_tab


# Open a URL.
def open_url(URL):
    open_new_tab(URL)


# Hide the pop-up window to allow for it to be used again.
def withdraw_copy_pop_up():
    copy_pop_up.withdraw()


# Copy the command to run the back-end to the clipboard.
def copy_command(root):
    root.clipboard_append('python3 back-end.py')
    copy_pop_up.title('Command copied')
    copy_pop_up_label.configure(text='The command has been copied to your '
                                + 'clipboard.')
    copy_pop_up.geometry('')
    copy_pop_up.deiconify()


# Create a welcome message window.
welcome_window = Tk()
welcome_window.title('Welcome')
welcome_font = font.Font(size=15)

# Create the pop-up for when the command is copied.
copy_pop_up = Toplevel()
copy_pop_up.title('')
copy_pop_up.attributes('-topmost', 1)
copy_pop_up.protocol('WM_DELETE_WINDOW', withdraw_copy_pop_up)
copy_pop_up_label = Label(copy_pop_up, font=welcome_font, text='')
copy_pop_up_close_button = Button(copy_pop_up, text='OK', command=lambda:
                                  withdraw_copy_pop_up(), font=welcome_font)
copy_pop_up_label.pack(padx=50, pady=(25, 0))
copy_pop_up_close_button.pack(pady=25)
copy_pop_up.withdraw()

# Create the elements for the welcome window.
label = Label(welcome_window, font=welcome_font, text='This application takes '
              + 'the activity data of Mastodon instances and displays it on '
              + 'a graph.\nWhen connected to a local LLM, it can also provide '
              + 'an AI analysis of the displayed data.\n\nIf you have not '
              + 'collected any activity data, you can do this using:')
command = Label(welcome_window, fg='blue', font=welcome_font, text='python3 '
                + 'back-end.py')
label_2 = Label(welcome_window, font=welcome_font, text='\nMore information, '
                + 'including how to install the required Python packages, can '
                + 'be found at:')
link = Label(welcome_window, fg='blue', font=welcome_font, text='https://'
             + 'github.com/Ubaydullah-A/Charting-Mastodon-Activity')
label_3 = Label(welcome_window, font=welcome_font, text='')
close_button = Button(welcome_window, text='Close', command=lambda:
                      welcome_window.destroy(), font=welcome_font)
label.pack()
command.pack()
label_2.pack()
link.pack()
label_3.pack()
close_button.pack()

# Set the initial window size.
welcome_window.geometry('1050x350')

# Call the copy_command function when the command text is clicked.
command.bind('<Button-1>', lambda e: copy_command(welcome_window))

# Call the open_url function when the URL text is clicked.
link.bind('<Button-1>', lambda e: open_url('https://github.com/Ubaydullah-A/'
          + 'Charting-Mastodon-Activity'))

welcome_window.mainloop()

try:
    import numpy
    from pickle import load
    from matplotlib.pyplot import close, subplots
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from pandas import DataFrame
    from sys import exit
    from datetime import datetime
    from time import mktime, strptime
    from tkcalendar import DateEntry
    from os import listdir, mkdir, path
    from pathvalidate import is_valid_filename, sanitize_filename
except Exception:
    raise SystemExit('Please install the required Python packages.\nMore '
                     + 'information can be found at: https://github.com/'
                     + 'Ubaydullah-A/Charting-Mastodon-Activity')


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
        pop_up_window.title('Invalid height')
        pop_up_label.configure(text='The height entered was invalid.\nThe '
                               + 'height has been reset.')
        pop_up_window.geometry('')
        pop_up_window.deiconify()
    elif height_value.isdigit() and width_value != '':
        fig.set_figheight(int(height_value))
        pop_up_window.title('Invalid width')
        pop_up_label.configure(text='The width entered was invalid.\nThe width'
                               + ' has been reset.')
        pop_up_window.geometry('')
        pop_up_window.deiconify()
    elif width_value != '' and height_value != '':
        pop_up_window.title('Invalid dimensions')
        pop_up_label.configure(text='The width and height values entered were '
                               + 'invalid.\nThe dimensions have been reset.')
        pop_up_window.geometry('')
        pop_up_window.deiconify()
    elif width_value != '':
        pop_up_window.title('Invalid width')
        pop_up_label.configure(text='The width entered was invalid.\nThe width'
                               + ' has been reset.')
        pop_up_window.geometry('')
        pop_up_window.deiconify()
    elif height_value != '':
        pop_up_window.title('Invalid height')
        pop_up_label.configure(text='The height entered was invalid.\nThe '
                               + 'height has been reset.')
        pop_up_window.geometry('')
        pop_up_window.deiconify()

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
                pop_up_window.title('Graph saved')
                pop_up_label.configure(text='Graph saved as \'' + file_name
                                       + '\'.')
                pop_up_window.geometry('')
                pop_up_window.deiconify()
            else:
                if sanitize_filename(file_name) != '':
                    pop_up_window.title('Invalid file name')
                    pop_up_label.configure(text='The graph was not saved.\nDid'
                                           + ' you mean \''
                                           + sanitize_filename(file_name)
                                           + '\'?')
                    pop_up_window.geometry('')
                    pop_up_window.deiconify()
                else:
                    pop_up_window.title('Invalid file name')
                    pop_up_label.configure(text='The graph was not saved.')
                    pop_up_window.geometry('')
                    pop_up_window.deiconify()
        else:
            fig.savefig('./graphs/graph')
            pop_up_window.title('Graph saved')
            pop_up_label.configure(text='Graph saved as \'graph\'.')
            pop_up_window.geometry('')
            pop_up_window.deiconify()


# Ask for confirmation before closing the program.
def on_closing():
    close_window.deiconify()


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
def get_inputs(data, frame, save, ai_response):
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
    if ai_response:
        # Ensure all inputs are valid.
        llm_input = []
        temp = []
        valid_ai_inputs = False
        server_address_text = server_address_text_box.get('1.0', 'end-1c')
        model_text = model_text_box.get('1.0', 'end-1c')
        max_tokens_text = max_tokens_text_box.get('1.0', 'end-1c')
        temperature_text = temperature_text_box.get('1.0', 'end-1c')
        try:
            response = get(f'{server_address_text}/v1/models')
            if response.status_code == 200:
                if model_text != '':
                    if max_tokens_text != '' and max_tokens_text.isdigit():
                        if temperature_text != '':
                            try:
                                float(temperature_text)
                                valid_ai_inputs = True
                            except ValueError:
                                pop_up_window.title('Invalid temperature')
                                pop_up_label.configure(text='Please enter a '
                                                       + 'valid temperature '
                                                       + 'value.')
                                pop_up_window.geometry('')
                                pop_up_window.deiconify()
                                valid_ai_inputs = False
                        else:
                            pop_up_window.title('Invalid temperature')
                            pop_up_label.configure(text='Please enter a valid '
                                                   + 'temperature value.')
                            pop_up_window.geometry('')
                            pop_up_window.deiconify()
                    else:
                        pop_up_window.title('Invalid token maximum')
                        pop_up_label.configure(text='Please enter a valid '
                                               + 'value for the maximum number'
                                               + ' of tokens.')
                        pop_up_window.geometry('')
                        pop_up_window.deiconify()
                else:
                    pop_up_window.title('Invalid model')
                    pop_up_label.configure(text='Please enter a valid API '
                                           + 'identifier for the model.')
                    pop_up_window.geometry('')
                    pop_up_window.deiconify()
            else:
                pop_up_window.title('Invalid response')
                pop_up_label.configure(text='Unable to get an OK response from'
                                       + ' the LLM.')
                pop_up_window.geometry('')
                pop_up_window.deiconify()
            if valid_ai_inputs:
                # Create the array that will provide the data to the LLM.
                for index in range(len(data_df_array)):
                    for week in range(len(data_df_array[index][1]['week'])):
                        instance = data_df_array[index][0]
                        temp.append('Instance:' + data_df_array[index][0])
                        week_date = datetime.fromtimestamp(
                            float(data_df_array[index][1]['week'][week]))\
                            .strftime('%d/%m/%y')
                        temp.append('Date:' + week_date)
                        if show_statuses.get():
                            statuses = \
                                (int(data_df_array[index][1]['statuses'][week])
                                 / int(data_df_array[index][1]['count'][week]))
                            temp.append('statuses:' + str(statuses))
                        if show_logins.get():
                            logins = \
                                (int(data_df_array[index][1]['logins'][week])
                                 / int(data_df_array[index][1]['count'][week]))
                            temp.append('logins:' + str(logins))
                        if show_registrations.get():
                            registrations = (int(
                                    data_df_array[index][1]
                                    ['registrations'][week])
                                    / int(data_df_array[index][1]
                                          ['count'][week]))
                            temp.append('registrations:' + str(registrations))
                        llm_input.append(temp)
                        temp = []
                get_ai_response(llm_input, max_tokens_text, model_text,
                                temperature_text, server_address_text)
        except Exception:
            pop_up_window.title('Unable to connect to LLM')
            pop_up_label.configure(text='An error occurred when trying to '
                                   + 'connect to the LLM.\nPlease check that '
                                   + 'the LLM is set up correctly and that the'
                                   + ' server address provided is correct.')
            pop_up_window.geometry('')
            pop_up_window.deiconify()

    draw_figure(data_df_array, frame, file_name, save)


# Adjust the region that can be scrolled when the information displayed on the
# window is changed.
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))


# Resize the canvas to the correct size when the window changes size.
def resize_canvas(event):
    canvas.configure(width=frame.winfo_width(), height=frame.winfo_height())
    separator.configure(height=root.winfo_height()-16)


# Resize the output text box to the correct size when the window changes size.
def resize_ai_output(event):
    ai_text_box.configure(state='normal')
    ai_text_box.configure(width=ai_analysis_window.winfo_width(),
                          height=ai_analysis_window.winfo_height())
    ai_text_box.configure(state='disabled')


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
    get_inputs(data, frame, False, False)


# Change the font when a new font is selected.
def font_changed(event):
    app_font.configure(family=font_chosen.get())
    app_title_font.configure(family=font_chosen.get())
    app_pop_up_font.configure(family=font_chosen.get())


# Change the font size when a new font size is selected, and adjust the widths
# accordingly.
def font_size_changed(event):
    app_font.configure(size=font_size_scale.get())
    app_title_font.configure(size=font_size_scale.get() + 5)
    app_pop_up_font.configure(size=font_size_scale.get() + 5)
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
    chosen_bg_colour = colorchooser.askcolor(title='Choose background colour')
    root.configure(bg=chosen_bg_colour[1])
    canvas.configure(bg=chosen_bg_colour[1])
    frame.configure(bg=chosen_bg_colour[1])
    input_grid.configure(bg=chosen_bg_colour[1])
    configuration_grid.configure(bg=chosen_bg_colour[1])
    dates_grid.configure(bg=chosen_bg_colour[1])
    checkbox_grid.configure(bg=chosen_bg_colour[1])
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
    empty_row_9.configure(bg=chosen_bg_colour[1])
    empty_row_10.configure(bg=chosen_bg_colour[1])
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
    pop_up_window.configure(bg=chosen_bg_colour[1])
    pop_up_label.configure(bg=chosen_bg_colour[1])
    close_window.configure(bg=chosen_bg_colour[1])
    close_buttons_grid.configure(bg=chosen_bg_colour[1])
    close_label.configure(bg=chosen_bg_colour[1])
    ai_analysis_window.configure(bg=chosen_bg_colour[1])
    ai_label.configure(bg=chosen_bg_colour[1])
    ai_text_box.configure(highlightbackground=chosen_bg_colour[1])
    ai_analysis_grid.configure(bg=chosen_bg_colour[1])
    server_address_label.configure(bg=chosen_bg_colour[1])
    server_address_text_box.configure(highlightbackground=chosen_bg_colour[1])
    max_tokens_label.configure(bg=chosen_bg_colour[1])
    max_tokens_text_box.configure(highlightbackground=chosen_bg_colour[1])
    model_label.configure(bg=chosen_bg_colour[1])
    model_text_box.configure(highlightbackground=chosen_bg_colour[1])
    temperature_label.configure(bg=chosen_bg_colour[1])
    temperature_text_box.configure(highlightbackground=chosen_bg_colour[1])


# Explicitly change the colour of every relevant input element.
def choose_input_colour():
    chosen_input_colour = colorchooser.askcolor(title='Choose input colour')
    style.configure('TCombobox', background=chosen_input_colour[1])
    font_size_scale.configure(troughcolor=chosen_input_colour[1])
    style.configure('DateEntry', fieldbackground=chosen_input_colour[1],
                    background=chosen_input_colour[1])
    width_text_box.configure(bg=chosen_input_colour[1])
    height_text_box.configure(bg=chosen_input_colour[1])
    save_text_box.configure(bg=chosen_input_colour[1])
    ai_text_box.configure(bg=chosen_input_colour[1])
    server_address_text_box.configure(bg=chosen_input_colour[1])
    max_tokens_text_box.configure(bg=chosen_input_colour[1])
    model_text_box.configure(bg=chosen_input_colour[1])
    temperature_text_box.configure(bg=chosen_input_colour[1])


# Explicitly change the colour of every relevant text element.
def choose_text_colour():
    chosen_text_colour = colorchooser.askcolor(title='Choose text colour')
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
    save_text_box.configure(fg=chosen_text_colour[1],
                            selectforeground=chosen_text_colour[1])
    save_button.configure(fg=chosen_text_colour[1])
    statuses_checkbox.configure(fg=chosen_text_colour[1])
    logins_checkbox.configure(fg=chosen_text_colour[1])
    registrations_checkbox.configure(fg=chosen_text_colour[1])
    width_label.configure(fg=chosen_text_colour[1])
    width_text_box.configure(fg=chosen_text_colour[1],
                             selectforeground=chosen_text_colour[1])
    height_label.configure(fg=chosen_text_colour[1])
    height_text_box.configure(fg=chosen_text_colour[1],
                              selectforeground=chosen_text_colour[1])
    style.configure('DateEntry', foreground=chosen_text_colour[1],
                    selectforeground=chosen_text_colour[1])
    style.configure('TCombobox', foreground=chosen_text_colour[1],
                    selectforeground=chosen_text_colour[1])
    pop_up_label.configure(fg=chosen_text_colour[1])
    pop_up_close_button.configure(fg=chosen_text_colour[1])
    close_label.configure(fg=chosen_text_colour[1])
    close_no_button.configure(fg=chosen_text_colour[1])
    close_yes_button.configure(fg=chosen_text_colour[1])
    ai_label.configure(fg=chosen_text_colour[1])
    ai_text_box.configure(fg=chosen_text_colour[1])
    server_address_label.configure(fg=chosen_text_colour[1])
    server_address_text_box.configure(fg=chosen_text_colour[1])
    max_tokens_label.configure(fg=chosen_text_colour[1])
    max_tokens_text_box.configure(fg=chosen_text_colour[1])
    model_label.configure(fg=chosen_text_colour[1])
    model_text_box.configure(fg=chosen_text_colour[1])
    temperature_label.configure(fg=chosen_text_colour[1])
    temperature_text_box.configure(fg=chosen_text_colour[1])
    ai_analysis_button.configure(fg=chosen_text_colour[1])


# Explicitly change the colour of every relevant button element.
def choose_button_colour():
    chosen_button_colour = colorchooser.askcolor(title='Choose button colour')
    text_colour_button.configure(bg=chosen_button_colour[1])
    bg_colour_button.configure(bg=chosen_button_colour[1])
    input_colour_button.configure(bg=chosen_button_colour[1])
    button_colour_button.configure(bg=chosen_button_colour[1])
    highlight_colour_button.configure(bg=chosen_button_colour[1])
    entries_button.configure(bg=chosen_button_colour[1])
    save_button.configure(bg=chosen_button_colour[1])
    pop_up_close_button.configure(bg=chosen_button_colour[1])
    close_no_button.configure(bg=chosen_button_colour[1])
    close_yes_button.configure(bg=chosen_button_colour[1])
    ai_analysis_button.configure(bg=chosen_button_colour[1])


# Explicitly change the highlight colour of every relevant element.
def choose_highlight_colour():
    chosen_highlight_colour = colorchooser.askcolor(title='Choose highlight '
                                                    + 'colour')
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
    save_text_box.configure(selectbackground=chosen_highlight_colour[1],
                            insertbackground=chosen_highlight_colour[1])
    width_text_box.configure(selectbackground=chosen_highlight_colour[1],
                             insertbackground=chosen_highlight_colour[1])
    height_text_box.configure(selectbackground=chosen_highlight_colour[1],
                              insertbackground=chosen_highlight_colour[1])
    style.configure('Vertical.TScrollbar',
                    background=chosen_highlight_colour[1])
    style.configure('Horizontal.TScrollbar',
                    background=chosen_highlight_colour[1])
    style.configure('DateEntry', selectbackground=chosen_highlight_colour[1])
    style.configure('TCombobox', selectbackground=chosen_highlight_colour[1])
    pop_up_close_button.configure(
        highlightbackground=chosen_highlight_colour[1])
    close_no_button.configure(highlightbackground=chosen_highlight_colour[1])
    close_yes_button.configure(highlightbackground=chosen_highlight_colour[1])
    ai_text_box.configure(selectbackground=chosen_highlight_colour[1],
                          insertbackground=chosen_highlight_colour[1])
    server_address_text_box.configure(
        selectbackground=chosen_highlight_colour[1],
        insertbackground=chosen_highlight_colour[1])
    max_tokens_text_box.configure(selectbackground=chosen_highlight_colour[1],
                                  insertbackground=chosen_highlight_colour[1])
    model_text_box.configure(selectbackground=chosen_highlight_colour[1],
                             insertbackground=chosen_highlight_colour[1])
    temperature_text_box.configure(selectbackground=chosen_highlight_colour[1],
                                   insertbackground=chosen_highlight_colour[1])
    ai_analysis_button.configure(
        highlightbackground=chosen_highlight_colour[1])


# Hide the pop-up windows to allow for them to be used again.
def withdraw_pop_ups():
    pop_up_window.withdraw()
    close_window.withdraw()


def close_windows():
    exit()


# Minimise the AI window to allow for it to be used again.
def iconify_ai_pop_up():
    ai_analysis_window.iconify()


# Interact with the LLM to provide the data and display the response.
def get_ai_response(llm_input, max_tokens, model, temperature, server_address):
    # Define the prompt and parameters
    payload = {
        'model': model,
        'prompt': 'What trends can you find from this data: ' + str(llm_input),
        'max_tokens': max_tokens,
        'temperature': temperature
    }

    # Send the request
    ai_analysis_window.iconify()
    response = post(f'{server_address}/v1/completions', json=payload)

    if response.status_code == 200:
        data = response.json()
        ai_text_box.configure(state='normal')
        ai_text_box.delete('0.0', 'end')
        ai_text_box.insert(1.0, data.get('choices', [{}])[0]
                           .get('text', 'No response'))
        ai_text_box.configure(state='disabled')
    else:
        ai_text_box.configure(state='normal')
        ai_text_box.delete('0.0', 'end')
        ai_text_box.insert(1.0, 'Error: ' + str(response.status_code) + ' - '
                           + response.text)
        ai_text_box.configure(state='disabled')
    ai_analysis_window.deiconify()


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
font_options = list(dict.fromkeys(font_options))
font_options.sort()

# Set the default font.
font_style = StringVar(value='TkDefaultFont')

# Create the font variables.
app_font = font.Font(family=font_style.get(), size=10,
                     weight='normal')
app_title_font = font.Font(family=font_style.get(), size=15, weight='bold',
                           underline=1)
app_textbox_font = font.Font(size=10)
app_pop_up_font = font.Font(family=font_style.get(), size=15, weight='bold')

# Create the template for error and information pop-ups.
pop_up_window = Toplevel()
pop_up_window.title('')
pop_up_window.attributes('-topmost', 1)
pop_up_window.protocol('WM_DELETE_WINDOW', withdraw_pop_ups)
pop_up_label = Label(pop_up_window, font=app_pop_up_font, text='')
pop_up_close_button = Button(pop_up_window, text='OK', command=lambda:
                             withdraw_pop_ups(), font=app_font)
pop_up_label.pack(padx=50, pady=(25, 0))
pop_up_close_button.pack(pady=25)
pop_up_window.withdraw()

# Create the pop-up for closing the main window.
close_window = Toplevel()
close_window.title('Quit')
close_window.attributes('-topmost', 1)
close_window.protocol('WM_DELETE_WINDOW', withdraw_pop_ups)
close_label = Label(close_window, font=app_pop_up_font, text='Do you want to '
                    + 'quit?')
close_buttons_grid = Frame(close_window)
close_no_button = Button(close_buttons_grid, text='No', command=lambda:
                         withdraw_pop_ups(), font=app_font, padx=15)
close_yes_button = Button(close_buttons_grid, text='Yes', command=lambda:
                          close_windows(), font=app_font)
close_label.pack(padx=50, pady=(25, 15))
close_buttons_grid.pack(pady=(0, 25))
close_no_button.grid(row=0, column=0, padx=10)
close_yes_button.grid(row=0, column=1)
close_window.withdraw()

# Create the pop-up for the AI output.
ai_analysis_window = Toplevel()
ai_analysis_window.title('AI analysis')
ai_analysis_window.attributes('-topmost', 1)
ai_analysis_window.protocol('WM_DELETE_WINDOW', iconify_ai_pop_up)
ai_label = Label(ai_analysis_window, font=app_pop_up_font,
                 text='AI analysis response')
ai_text_box = Text(ai_analysis_window, font=app_textbox_font, state='disabled')
ai_label.pack(fill='both', expand=True)
ai_text_box.pack()
ai_analysis_window.geometry('1050x300')
ai_analysis_window.iconify()

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

empty_row_6 = Label(configuration_grid, text='')
empty_row_6.grid(row=15, column=0)

ai_analysis_grid = Frame(configuration_grid)
ai_analysis_grid.grid(row=16, column=0, columnspan=2, sticky='ew')
server_address_label = Label(ai_analysis_grid, text='Enter server address for '
                             + 'the AI model: ', wraplength=400, font=app_font)
server_address_text_box = Text(ai_analysis_grid, height=1, width=30,
                               font=app_textbox_font)
model_label = Label(ai_analysis_grid, text='Enter the model\'s API identifier'
                    + ': ', wraplength=400, font=app_font)
model_text_box = Text(ai_analysis_grid, height=1, width=30,
                      font=app_textbox_font)
max_tokens_label = Label(ai_analysis_grid, text='Enter the maximum number of '
                         + 'tokens: ', wraplength=400, font=app_font)
max_tokens_text_box = Text(ai_analysis_grid, height=1, width=30,
                           font=app_textbox_font)
temperature_label = Label(ai_analysis_grid, text='Enter the temperature value'
                          + ': ', wraplength=400, font=app_font)
temperature_text_box = Text(ai_analysis_grid, height=1, width=30,
                            font=app_textbox_font)
ai_analysis_button = Button(ai_analysis_grid, text='Generate AI analysis\n('
                            + 'window will\nbe temporarily\nunresponsive)',
                            command=lambda:
                                get_inputs(data, frame, False, True),
                                font=app_font, height=4)
empty_row_7 = Label(ai_analysis_grid, text='')
server_address_label.grid(row=0, column=0, sticky='ew')
server_address_text_box.grid(row=1, column=0, sticky='ew')
model_label.grid(row=2, column=0, sticky='ew')
model_text_box.grid(row=3, column=0, sticky='ew')
max_tokens_label.grid(row=4, column=0, sticky='ew')
max_tokens_text_box.grid(row=5, column=0, sticky='ew')
temperature_label.grid(row=6, column=0, sticky='ew')
temperature_text_box.grid(row=7, column=0, sticky='ew')
empty_row_7.grid(row=8, column=0)
ai_analysis_button.grid(row=9, column=0, sticky='ew')

# Add padding around the frames and the separator.
empty_column_1 = Label(frame, text='', width=2)
empty_column_1.grid(row=1, column=0)

empty_column_2 = Label(frame, text='', width=2)
empty_column_2.grid(row=1, column=2)

empty_column_3 = Label(frame, text='', width=2)
empty_column_3.grid(row=1, column=4)

empty_column_4 = Label(frame, text='', width=2)
empty_column_4.grid(row=1, column=6)

empty_row_8 = Label(frame, text='')
empty_row_8.grid(row=0, column=0, columnspan=6)

empty_row_9 = Label(frame, text='')
empty_row_9.grid(row=3, column=5)

empty_row_10 = Label(frame, text='')
empty_row_10.grid(row=5, column=5)

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
                        command=lambda: get_inputs(data, frame, False, False),
                        font=app_font)

save_label = Label(input_grid,
                   text='\nEnter the file name you would like the graph to be '
                   + 'saved as:', anchor='sw', wraplength=800, font=app_font)
save_text_box = Text(input_grid, height=1, width=88, pady=5, padx=2,
                     font=app_textbox_font)
save_button = Button(input_grid, height=1, width=20, text='Save graph',
                     font=app_font, command=lambda: get_inputs(data, frame,
                                                               True, False))

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
date1 = DateEntry(dates_grid, state='readonly', width=42,
                  font=app_textbox_font)
date1.set_date(start_date)

end_date = datetime.fromtimestamp(float(
                                  old_labels[len(
                                    old_labels)-1])).strftime('%d/%m/%Y')
date2 = DateEntry(dates_grid, state='readonly', width=43,
                  font=app_textbox_font)
date2.set_date(end_date)

# Add the calendars to the dates_grid frame.
date1.grid(row=0, column=0)
date2.grid(row=0, column=1)

# Ensure that the elements in the window scale appropriately.
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Set the initial window size.
starting_width = frame.winfo_width()+20
starting_height = frame.winfo_height()+16
root.geometry(f'{starting_width}x{starting_height}')

# Call the resize_ai_output function when the AI analysis window changes size.
ai_analysis_window.bind('<Configure>', resize_ai_output)

# Call the resize_canvas function when the window changes size.
root.bind('<Configure>', resize_canvas)

# Call the instance_changed function when a new instance is selected.
combobox.bind('<<ComboboxSelected>>', instance_changed)

# Call the font_changed function when a new font is selected.
font_combobox.bind('<<ComboboxSelected>>', font_changed)

# Call the font_size_changed function when a new font size is selected.
font_size_scale.bind('<ButtonRelease-1>', font_size_changed)

root.mainloop()

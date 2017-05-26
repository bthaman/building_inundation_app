try:
    import Tkinter as tk
    import ttk
except ImportError:
    # python 3
    import tkinter as tk
    from tkinter import ttk
import ttkcalendar
import datetime
import tkSimpleDialog


class CalendarDialog(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    def body(self, master):
        self.calendar = ttkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.selection


class BasicComboGUI(ttk.LabelFrame):
    def __init__(self, frame_title, date_picker=False):
        self.root = tk.Tk()
        self.root.wm_title(frame_title)
        ttk.LabelFrame.__init__(self, self.root, text=None)
        self.padding = '6, 6, 12, 12'
        self.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.date_picker = date_picker
        self.selected_date_start = tk.StringVar()
        self.selected_date_start.trace('w', self.handle_event)
        self.selected_date_end = tk.StringVar()
        self.selected_date_end.trace('w', self.handle_event)
        self.entered_value = tk.StringVar()
        self.entered_value.trace('w', self.combo_box_select_event)
        self.chk_val = tk.IntVar()
        self.chk_val.trace('w', self.handle_event)
        self.lst_combo_values = []

        # create button and bind it to the envclick function using the command param
        self.btn_env = ttk.Button(self, text='Get Building Workspace', width=25, command=self.envclick)
        self.btn_env.grid(column=2, row=1, sticky='w')
        self.btn_env.configure(state='enabled', cursor='')

        # create combo box
        self.set_combo_box_label(labeltext="Select Building Dataset", row=2, col=1)
        self.combo_box = ttk.Combobox(self, textvariable=self.entered_value, width=12)
        self.combo_box.grid(column=2, row=2, sticky='E')
        self.set_combo_box_width(45)
        self.combo_box['values'] = []

        # create check box
        self.chk_box = ttk.Checkbutton(self, text='placeholder - can be deleted', variable=self.chk_val)
        self.chk_box.grid(column=2, row=3, sticky='W')

        # create button and bind it to the envclick2 function using the command param
        self.btn_env = ttk.Button(self, text='Get Triangles Workspace', width=25, command=self.envclick2)
        self.btn_env.grid(column=2, row=4, sticky='w')
        self.btn_env.configure(state='enabled', cursor='')

        # create list box
        tk.Label(self, text='WSE data').grid(column=1, row=5, sticky='nw')
        self.lstbox = tk.Listbox(self, selectmode='extended', height=10, width=45)

        # function for ListboxSelect event
        def onselect(e):
            # call the event handler
            self.handle_event()

        self.lstbox.bind('<<ListboxSelect>>', onselect)
        self.lstbox.grid(row=5, column=2, sticky='w')

        # create 'OK' button and bind it to the okclick function using the command param
        self.btn_ok = ttk.Button(self, text='OK', width=7, command=self.okclick)
        self.btn_ok.grid(row=6, columnspan=3)
        self.btn_ok.configure(state='disabled', cursor='')

        # since this is a parent window, call the quit method when the window is closed
        # by clicking the 'x' in the upper right
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

        if date_picker:
            self.add_date_controls()

        # put space around the widgets
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def add_date_controls(self):
        self.txt_date = ttk.Entry(self, textvariable=self.selected_date_start, width=15)
        self.btn_choose_date_start = ttk.Button(self, text="Choose start date", command=self.getdatestart, width=18)
        self.btn_choose_date_start.grid(column=1, row=3)
        self.txt_date.grid(column=2, row=3, sticky='W')
        self.txt_date_end = ttk.Entry(self, textvariable=self.selected_date_end, width=15)
        self.btn_choose_date_end = ttk.Button(self, text="Choose end date", command=self.getdateend, width=18)
        self.btn_choose_date_end.grid(column=1, row=4)
        self.txt_date_end.grid(column=2, row=4, sticky='W')

    def getdatestart(self):
        cd = CalendarDialog(self)
        result = cd.result
        if result:
            self.selected_date_start.set(result.strftime("%m/%d/%Y"))

    def getdateend(self):
        cd = CalendarDialog(self)
        result = cd.result
        if result:
            self.selected_date_end.set(result.strftime("%m/%d/%Y"))

    def okclick(self):
        """click event for btn_ok. this should be overridden by any subclass"""
        pass

    def handle_event(self, *args):
        """event enabling/disabling 'OK' button. This should be overridden by any subclass"""
        x = self.selected_date_start.get()
        x2 = self.selected_date_end.get()
        y = self.entered_value.get()

        if self.date_picker and self.chk_val.get():
            self.txt_date.configure(state='disabled')
            self.txt_date_end.configure(state='disabled')
            self.btn_choose_date_start.configure(state='disabled')
            self.btn_choose_date_end.configure(state='disabled')
        elif self.date_picker and not self.chk_val.get():
            self.txt_date.configure(state='normal')
            self.txt_date_end.configure(state='normal')
            self.btn_choose_date_start.configure(state='normal')
            self.btn_choose_date_end.configure(state='normal')

        if self.date_picker:
            if x and x2 and y:
                self.btn_ok.configure(state='normal')
            else:
                self.btn_ok.configure(state='disabled')
        else:
            if y:
                self.btn_ok.configure(state='normal')
            else:
                self.btn_ok.configure(state='disabled')

    def combo_box_select_event(self, *args):
        pass

    def get_durations(self):
        return self.lst_combo_values

    def set_combo_box_label(self, labeltext, col, row):
        ttk.Label(self, text=labeltext).grid(column=col, row=row, sticky='W')

    def set_combo_box_width(self, cb_width):
        self.combo_box.configure(width=cb_width)

    def show_window(self):
        self.root.mainloop()

    def quit(self):
        # if root.quit isn't called, the window will close, but will leave the python.exe process running
        # if there are any child windows (e.g. file/dir dialog that didn't close with root.quit.
        # calling root.destroy() will not kill the process
        self.root.quit()


if __name__ == "__main__":
    gui = BasicComboGUI(frame_title='Change Me', date_picker=False)
    gui.show_window()

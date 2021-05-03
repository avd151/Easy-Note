import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk, messagebox, filedialog, font
from os.path import basename, dirname, realpath, join
from string import whitespace
from webbrowser import open_new

from os.path import basename, dirname, realpath
from datetime import datetime


class File:

    def __init__(self, path):
        self.file_path = path
        self.file_name = basename(path).split(".")[0]
        self.dir_name = dirname(path)
        self.file_ext = basename(path).split(".")[1]
        self.saved = False
        self.modified = False
        self.last_saved = datetime.now()


class CustomDateTime:

    def __init__(self, dt_obj=datetime.now()):
        self.dt_obj = dt_obj
        self.date = str(self.dt_obj.month) + "/" + \
            str(self.dt_obj.day) + "/" + str(self.dt_obj.year)
        self.time = datetime.strftime(datetime.strptime(
            str(self.dt_obj.hour)+":"+str(self.dt_obj.minute), "%H:%M"), "%I:%M %p")

    def __str__(self):
        return self.date + " " + str(self.time)

    def get_date(self):
        return self.date

    def get_time(self):
        return str(self.time)


class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.wm_geometry("800x600")
        self.curr_file = None

        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        self.text = CustomText(self.container)
        self.menu = MenuBar(self)
        self.config(menu=self.menu)

        self.status_bar = StatusBar(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.menu.new_file()

        self.text.bind("<F5>", self.menu.insert_datetime)

        self.text.bind("<Enter>", self.menu.set_button_state)
        self.text.bind("<Leave>", self.menu.set_button_state)
        self.text.bind("<<Modified>>", self.menu.set_button_state)

    def setup(self):
        """
        Currently this only sets the title for the window
        and gives focus to 'text'.
        Planned to do more later.
        """
        self.title("EasyNote - " + self.curr_file.file_name)
        self.text.focus_force()

    def add_scrolledtext(self):
        """
        Adds the scrolledtext box to the container frame.
        """
        if self.text and self.text.winfo_exists():
            self.text.destroy()
        self.text = CustomText(self.container)

        self.text.pack(expand=True, fill="both")


class MenuBar(tk.Menu):

    def __init__(self, master):
        tk.Menu.__init__(self, master)
        self.master = master
        self.wrap_var = tk.StringVar()
        self.wrap_var.set("none")
        self.statusbar_var = tk.BooleanVar()
        self.statusbar_var.set(True)

        self.file_menu = tk.Menu(
            self, tearoff=False)
        self.file_menu.add_command(label="New",
                                   command=self.new_file,
                                   accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open",
                                   command=self.open_file,
                                   accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save",
                                   command=self.save_file,
                                   accelerator="Ctrl+S", state="disabled")
        self.file_menu.add_command(label="Save As...",
                                   command=self.saveas_file)
        self.file_menu.add_separator()
        self.file_menu.add_cascade(label="Quit",
                                   command=master.destroy)
        self.add_cascade(label="File", menu=self.file_menu,
                         font="Times 23 bold")

        self.edit_menu = tk.Menu(self, tearoff=False)
        self.edit_menu.add_command(label="Undo", command=self.undo,
                                   accelerator="Ctrl+Z", state="disabled")
        self.edit_menu.add_command(label="Redo", command=self.redo,
                                   accelerator="Ctrl+Y", state="disabled")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut",
                                   command=self.cut, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy",
                                   command=self.copy, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste",
                                   command=self.paste, accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All",
                                   command=self.select_all,
                                   accelerator="Ctrl+A", state="disabled")
        self.add_cascade(label="Edit", menu=self.edit_menu,
                         font="Times 23 bold")

        self.insert_menu = tk.Menu(self, tearoff=False)
        self.insert_menu.add_command(label="Date & Time",
                                     command=self.insert_datetime, accelerator="F5")
        self.add_cascade(label="Insert", menu=self.insert_menu,
                         font="Times 23 bold")

        self.format_menu = tk.Menu(self, tearoff=False)
        self.format_menu.add_checkbutton(label="Word Wrap",
                                         command=self.toggle_wrap)
        self.format_menu.add_command(label="Font",
                                     command=self.open_font_window)
        self.format_menu.add_command(label="Highlight",
                                     command=self.master.text.highlight)
        self.format_menu.add_command(label="Style",
                                     command=self.master.text.set_style)
        self.add_cascade(label="Format", menu=self.format_menu,
                         font="Times 23 bold")

        self.view_menu = tk.Menu(self, tearoff=False)
        self.view_menu.add_checkbutton(label="Status Bar",
                                       variable=self.statusbar_var,
                                       onvalue=True, offvalue=False,
                                       command=lambda master=master:
                                       self.toggle_statusbar(master))
        self.add_cascade(label="View", menu=self.view_menu,
                         font="Times 23 bold")

        self.list_menu = tk.Menu(self, tearoff=False)
        self.list_menu.add_command(
            label="Make a List", command=self.open_list_window)
        self.add_cascade(label="List", menu=self.list_menu,
                         font="Times 23 bold")

        self.help_menu = tk.Menu(self, tearoff=False)
        self.help_menu.add_command(label="Help")
        self.help_menu.add_command(label="About Application",
                                   command=self.open_about_window)
        self.add_cascade(label="Help", menu=self.help_menu,
                         font="Times 23 bold")
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-v>', self.paste)

    def set_button_state(self, event=None):
        """
        Enables/disables the save, undo, redo, and select
        all menu options based on whether or not they can
        actually be used.
        """
        if self.master.text.edit_modified():
            self.file_menu.entryconfig(2, state="normal")
            self.edit_menu.entryconfig(0, state="normal")
        else:
            self.file_menu.entryconfig(2, state="disabled")
            self.edit_menu.entryconfig(0, state="disabled")

        if len(self.master.text.get("1.0", tk.END)) > 1:
            self.edit_menu.entryconfig(7, state="normal")
        else:
            self.edit_menu.entryconfig(7, state="disabled")

    def new_file(self):
        """
        Creates a new file object.  Then clears container frame and creates a
        new one by calling 'add_scrolledtext'.
        """
        self.master.curr_file = File(join(dirname(realpath(__file__)) +
                                     "\\New File.txt"))
        self.master.add_scrolledtext()
        self.master.setup()

    def open_file(self):
        """
        Destroys container frame and creates a new one by calling
        'add_scrolledtext'.  Inserts the data of that file into
        the newly created scrolledtext box.  Then creates a new File
        object and sets the curr_file to that object.
        """
        file_to_open = filedialog.askopenfilename(defaultextension="txt",
                                                  initialdir=self.master.curr_file.file_path,
                                                  filetypes=(("Text files", "*.txt"),
                                                             ("All files", "*.*"))
                                                  )
        if file_to_open:
            with open(file_to_open, "r") as f:
                data = f.read()
            self.master.curr_file = File(file_to_open)
            self.master.add_scrolledtext()
            self.master.text.insert("1.0", data)
            self.master.text.edit_modified(False)
            self.master.setup()

    def save_file(self):
        """
        Writes text to file and sets saved flag for curr_file to true.
        """
        if self.file_menu.entrycget(2, "state") == "normal":
            with open(self.master.curr_file.file_path, "w+") as f:
                f.write(self.master.text.get("1.0", "end-1c"))
                self.master.curr_file.saved = True
                self.master.text.edit_modified(False)
                self.master.setup()
        else:
            self.saveas_file()

    def saveas_file(self):
        """
        Opens file dialog for user to save new file.
        """
        data = self.master.text.get("1.0", "end-1c")
        save_location = filedialog.asksaveasfilename(defaultextension="txt",
                                                     initialdir=self.master.curr_file.file_path,
                                                     filetypes=(("Text files", "*.txt"),
                                                                ("All files", "*.*"))
                                                     )
        if save_location:
            with open(save_location, "w+") as f:
                f.write(data)
            self.master.curr_file = File(save_location)
            self.master.curr_file.saved = True
            self.master.text.edit_modified(False)
            self.master.setup()

    def undo(self):
        try:
            self.master.text.event_generate("<<Undo>>")
            self.edit_menu.entryconfig(1, state="normal")
        except tk.TclError:
            self.edit_menu.entryconfig(0, state="disabled")

    def redo(self):
        try:
            self.master.text.event_generate("<<Redo>>")
        except tk.TclError:
            self.edit_menu.entryconfig(1, state="disabled")

    def cut(self):
        self.master.text.event_generate("<<Cut>>")

    def copy(self):
        self.master.text.event_generate("<<Copy>>")

    def paste(self):
        self.master.text.event_generate("<<Paste>>")

    def select_all(self, master):
        master.text.tag_add("sel", "1.0", "end")

    def insert_datetime(self, event=None):
        self.curr_date = CustomDateTime()
        self.master.text.insert(self.master.text.index(tk.INSERT),
                                str(self.curr_date))

    def toggle_wrap(self):
        """Turns word wrap on and off for text."""
        if self.wrap_var.get() == "word":
            self.wrap_var.set("none")
        else:
            self.wrap_var.set("word")

        self.master.text.config(wrap=self.wrap_var.get())

    def open_font_window(self):
        """
        Opens a new window which allows the user to change the font
        of the scrolledtext widget.
        """
        self.font_popup = FontWindow(self.master)
        self.font_popup.destroy()

    def toggle_statusbar(self, master):
        """Toggles the status bar at the bottom of the window."""
        if not self.statusbar_var.get():
            master.status_bar.destroy()
        else:
            master.status_bar = StatusBar(master)
            master.status_bar.pack(side=tk.BOTTOm, fill=tk.X)

    def open_list_window(self):
        self.list_window = ListWindow()

    def open_about_window(self):
        """Displays the 'About' window."""
        self.about_popup = AboutWindow()


class FontWindow(tk.Toplevel):

    def __init__(self, master, selected=None):
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.title("Font")
        self.resizable(0, 0)

        self.font_container = tk.Frame(self)
        self.font_container.grid(row=0, column=0)

        self.font_var = tk.StringVar()
        self.style_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.font_var.set("Arial")
        self.style_var.set("normal")
        self.size_var.set("10")

        self.font_frame = tk.Frame(self.font_container)
        tk.Label(self.font_container, text="Font:").grid(row=0, column=0)
        self.selected_font = tk.Entry(self.font_container,
                                      textvariable=self.font_var)
        self.f_scrollbar = tk.Scrollbar(self.font_container,
                                        orient=tk.VERTICAL)
        self.fonts_box = tk.Listbox(self.font_container,
                                    yscrollcommand=self.f_scrollbar.set)
        self.f_scrollbar.config(command=self.fonts_box.yview)
        self.f_scrollbar.grid(row=1, column=1, rowspan=2, sticky="NS")
        for font in sorted(tk.font.families()):
            if not font.startswith("@"):
                self.fonts_box.insert(tk.END, font)
        self.selected_font.grid(row=1, column=0)
        self.fonts_box.grid(row=2, column=0)
        self.font_frame.grid(row=0, column=0)

        styles = ["normal", "bold", "italic", "underline", "overstrike"]

        self.style_frame = tk.Frame(self.font_container)
        tk.Label(self.font_container, text="Font style:").grid(row=0, column=2)
        self.selected_style = tk.Entry(self.font_container,
                                       textvariable=self.style_var)
        self.st_scrollbar = tk.Scrollbar(self.font_container,
                                         orient=tk.VERTICAL)
        self.style_box = tk.Listbox(self.font_container,
                                    yscrollcommand=self.st_scrollbar.set)
        self.st_scrollbar.config(command=self.style_box.yview)
        self.st_scrollbar.grid(row=1, column=3, rowspan=2, sticky="NS")
        for style in styles:
            self.style_box.insert(tk.END, style)
        self.selected_style.grid(row=1, column=2, sticky="WE")
        self.style_box.grid(row=2, column=2)
        self.style_frame.grid(row=0, column=1)

        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]

        self.size_frame = tk.Frame(self.font_container)
        tk.Label(self.font_container, text="Size:").grid(row=0, column=4)
        self.selected_size = tk.Entry(self.font_container,
                                      textvariable=self.size_var)
        self.s_scrollbar = tk.Scrollbar(self.font_container,
                                        orient=tk.VERTICAL)
        self.size_box = tk.Listbox(self.font_container,
                                   yscrollcommand=self.s_scrollbar.set)
        self.s_scrollbar.config(command=self.size_box.yview)
        self.s_scrollbar.grid(row=1, column=5, rowspan=2, sticky="NS")
        for size in sizes:
            self.size_box.insert(tk.END, size)
        self.selected_size.grid(row=1, column=4)
        self.size_box.grid(row=2, column=4)
        self.size_frame.grid(row=0, column=2)

        self.sample_frame = tk.Frame(self.font_container, borderwidth=3,
                                     width=285, height=80, relief="groove")
        self.sample_lbl = tk.Label(self.sample_frame, text="Sample Text",
                                   anchor="center")
        self.sample_lbl.grid(row=0, column=0, sticky="NSEW")
        self.sample_frame.grid(row=3, column=2, columnspan=5, pady=10)
        self.sample_frame.grid_propagate(0)

        self.button_frame = tk.Frame(self.font_container)
        self.confirm_btn = tk.Button(self.button_frame, text="Confirm",
                                     command=lambda master=master:
                                     self.set_font(master))
        self.confirm_btn.grid(row=0, column=0, sticky="WE")
        self.cancel_btn = tk.Button(self.button_frame, text="Cancel",
                                    command=lambda: self.destroy())
        self.cancel_btn.grid(row=0, column=1, sticky="WE")
        self.button_frame.grid(row=4, column=4, padx=5, pady=5)

        self.fonts_box.bind("<<ListboxSelect>>",
                            lambda evt, var=self.font_var:
                            self.onselect(evt, var))
        self.style_box.bind("<<ListboxSelect>>",
                            lambda evt, var=self.style_var:
                            self.onselect(evt, var))
        self.size_box.bind("<<ListboxSelect>>",
                           lambda evt, var=self.size_var:
                           self.onselect(evt, var))

    def onselect(self, evt, var):
        """
        When a listbox item is selected by the user var will be
        set to the selected item.  The sample_lbl will also be
        changed to reflect the new selection.

        :params evt: Event that triggered the call
        :params var: The variable to set
        """
        w = evt.widget
        ndex = int(w.curselection()[0])
        name = w.get(ndex)
        var.set(name)
        self.sample_lbl.config(font=(self.font_var.get(), self.size_var.get(),
                               self.style_var.get()))

    def set_font(self, master, txt=None):
        """
        Sets the font, style, and size of 'txt'.
        """
        if not txt:
            txt = master.text

        txt.config(font=(self.font_var.get(),
                   self.size_var.get(), self.style_var.get()))
        return (self.font_var.get(), self.size_var.get(), self.style_var.get())


class ListWindow(tk.Toplevel):
    def __init__(self, tasks=None):

        super().__init__()

        self.title("Make a List")
        self.geometry("500x500")
        self.backGroundColor_lib = ["palegreen", "mistyrose", "lightcyan",
                                    "wheat", "azure", "paleturquoise", "beige", "lavender"]
        self.fontcolor_lib = ["black"]

        if not tasks:
            self.tasks = []
            task1 = tk.Label(self, text="MAKE A LIST",
                             bg="snow", fg="black", pady=10, font=("Times", 23))
            task1.pack(side=tk.TOP, fill=tk.X)
            self.tasks.append(task1)

        else:
            self.tasks = []
            for i in range(len(tasks)):
                if i == 0:
                    task1 = tk.Label(
                        self, text="MAKE A LIST", bg="snow", fg="black", pady=10, font=("Times", 23))
                    task1.pack(side=tk.TOP, fill=tk.X)
                    self.tasks.append(task1)
                else:
                    self.add(tasks[i])

        self.task_create = tk.Text(self, height=3, bg="white", fg="black")

        self.task_create.pack(side=tk.BOTTOM, fill=tk.X)
        self.task_create.focus_set()

        self.bind('<Return>', self.add_task)

    def add(self, txt, event=None):
        new_task = tk.Label(self, text=txt, pady=20)
        done_button = ttk.Button(
            new_task, text="done", command=lambda: self.removeTask(done_button))

        backGroundIdx = len(self.tasks) % len(self.backGroundColor_lib)
        fontIdx = len(self.tasks) % len(self.fontcolor_lib)

        backGroundColor = self.backGroundColor_lib[backGroundIdx]
        fontColor = self.fontcolor_lib[fontIdx]

        new_task.configure(bg=backGroundColor,
                           fg=fontColor, font=("Times", 20))

        new_task.pack(side=tk.TOP, fill=tk.X)
        done_button.pack(side=tk.RIGHT)

        self.tasks.append(new_task)

    def add_task(self, event=None):
        new_text = self.task_create.get(1.0, tk.END).strip()

        if len(new_text) > 0:
            new_task = tk.Label(self, text=new_text, pady=20)
            done_button = ttk.Button(
                new_task, text="done", command=lambda: self.removeTask(done_button))

            backGroundIdx = len(self.tasks) % len(self.backGroundColor_lib)
            fontIdx = len(self.tasks) % len(self.fontcolor_lib)

            backGroundColor = self.backGroundColor_lib[backGroundIdx]
            fontColor = self.fontcolor_lib[fontIdx]

            new_task.configure(bg=backGroundColor,
                               fg=fontColor, font=("Times", 20))

            new_task.pack(side=tk.TOP, fill=tk.X)
            done_button.pack(side=tk.RIGHT)

            self.tasks.append(new_task)

        self.task_create.delete(1.0, tk.END)

    def removeTask(self, done_button):
        done_button.pack_forget()
        done_button.master.pack_forget()
        self.tasks.remove(done_button.master)

    def on_closing(self):
        writefile = open("data.txt", "w")
        for item in self.tasks:
            print(item.cget("text"), file=writefile)
        writefile.close()
        self.destroy()


class AboutWindow(tk.Toplevel):
    """
    Displays information about the application.
    """

    def __init__(self):
        tk.Toplevel.__init__(self)
        self.title("About Easy Note")
        self.geometry("290x200")
        self.about_frame = tk.Frame(self)
        self.about_frame.grid(column=0, row=0)

        tk.Label(self.about_frame, text="Easy Note", font="bold").grid(column=0,
                                                                       row=0)
        ttk.Separator(self.about_frame).grid(column=0, row=1, columnspan=2,
                                             sticky="ew")
        tk.Label(self.about_frame,
                 text="RPPOOP Mini Project : Easy-Note GUI Application").grid(column=0, row=2)
        ttk.Separator(self.about_frame).grid(column=0, row=3, columnspan=2,
                                             sticky="ew")
        tk.Label(self.about_frame, text="Made by:").grid(column=0, row=4)
        tk.Label(self.about_frame,
                 text="111903020-Apurva Deshpande").grid(column=0, row=5)
        tk.Label(self.about_frame,
                 text="111903026-Sham Targe").grid(column=0, row=6)
        tk.Label(self.about_frame,
                 text="111903030-Chitrang Bhoir").grid(column=0, row=7)


class CustomText(tk.Text):
    def __init__(self, master, *args, **kwargs):
        tk.Text.__init__(self, master, *args, **kwargs)
        self.master = master
        self.hscrollbar = AutoScrollbar(self,
                                        orient=tk.HORIZONTAL)
        self.vscrollbar = AutoScrollbar(self,
                                        orient=tk.VERTICAL)
        self.config(wrap="none", undo=True,
                         xscrollcommand=self.hscrollbar.set,
                         yscrollcommand=self.vscrollbar.set)

    def highlight(self):
        if self.master.master.text.tag_ranges("sel"):
            selected = self.master.master.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if "highlight" in self.master.master.text.tag_names():
                self.master.master.text.tag_delete("highlight")
            self.master.master.text.tag_add(
                "highlight", tk.SEL_FIRST, tk.SEL_LAST)
            self.master.master.text.tag_config(
                "highlight", background="yellow")

    def set_style(self):
        if self.master.master.text.tag_ranges("sel"):
            selected = self.master.master.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.font_window = self.master.master.menu.open_font_window()
            if "styled" in self.master.master.text.tag_names():
                self.master.master.text.tag_delete("styled")
            self.master.master.text.tag_add(
                "styled", tk.SEL_FIRST, tk.SEL_LAST)
            self.master.master.text.tag_config("styled", font=72)


class AutoScrollbar(tk.Scrollbar):
    """Scrollbar that will only display when needed."""

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.pack_forget()
        else:
            if self.cget("orient") == tk.HORIZONTAL:
                self.pack(side=tk.BOTTOM, fill=tk.X)
            else:
                self.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Scrollbar.set(self, lo, hi)


class StatusBar(tk.Frame):
    """
    Status bar for the bottom of the screen that shows
    character count, column number and row (index) of
    cursor.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.columnconfigure(0, weight=1)
        self.status_frame = tk.Frame(self, relief=tk.SUNKEN, bd=1)
        self.status_frame.grid(column=0, row=0, sticky="ew")

        tk.Label(self.status_frame, text="Charcter Count: ",
                 anchor="e").grid(column=1, row=0, sticky="e")
        self.char_count = tk.StringVar()
        self.char_count.set(0)
        tk.Label(self.status_frame,
                 textvariable=self.char_count).grid(column=2, row=0,
                                                    sticky="e")

        tk.Label(self.status_frame, text="Line: ").grid(column=3, row=0,
                                                        sticky="e")
        self.curr_line = tk.StringVar()
        self.curr_line.set(1)
        tk.Label(self.status_frame,
                 textvariable=self.curr_line).grid(column=4, row=0, sticky="e")

        tk.Label(self.status_frame, text="Col: ").grid(column=5, row=0,
                                                       sticky="e")
        self.curr_col = tk.StringVar()
        self.curr_col.set("1")
        tk.Label(self.status_frame,
                 textvariable=self.curr_col).grid(column=6, row=0, sticky="e")

        master.text.bind_all("<Key>", lambda evt,
                             master=master: self.update_status(evt,
                                                               master))

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

    def update_status(self, evt, master):
        """
        Updates the info displayed in the status bar.

        :params evt: Event object.
        :params master: Master window.
        """
        self.position = master.text.index(tk.INSERT).split(".")
        self.char_count.set(len(master.text.get("1.0", tk.END)) - 1)
        self.curr_line.set(self.position[0])
        self.curr_col.set(self.position[1])

import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk, messagebox, filedialog, font
from os.path import basename, dirname, realpath, join
from string import whitespace
from webbrowser import open_new
from tkinter import font
from tkinter.font import Font, families
from tkinter import colorchooser
from tkinter.colorchooser import askcolor
from tkfontchooser import askfont
from os.path import basename, dirname, realpath
from datetime import datetime
import pyttsx3
from PIL import Image, ImageTk

# Flags
IS_SAVED = 0
NIGHT_MODE_IS_ON = 0


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
        self.date = str(self.dt_obj.day) + "/" + \
            str(self.dt_obj.month) + "/" + str(self.dt_obj.year)
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

        self.IS_SAVED = 0

        self.wm_geometry("800x600")
        self.curr_file = None

        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        self.text = CustomText(self.container)
        self.menu = MenuBar(self)
        self.config(menu=self.menu)

        self.status_bar = StatusBar(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.curr_file = File(join(dirname(realpath(__file__)) +
                                   "\\New File.txt"))
        self.add_scrolledtext()
        self.setup()

        self.engine = pyttsx3.init()

        self.engine.setProperty('rate', 110)
        self.engine.setProperty('volume', 1.0)
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[1].id)

        self.text.bind("<F5>", self.menu.insert_datetime)
        self.text.bind("<Enter>", self.menu.set_button_state)
        self.text.bind("<Leave>", self.menu.set_button_state)
        self.text.bind("<<Modified>>", self.menu.set_button_state)
        self.text.bind("<<Modified>>", self.isUnsaved)

        self.bind('<Control-n>', self.menu.ctrlN)
        self.bind('<Control-o>', self.menu.ctrlO)
        self.bind('<Control-s>', self.menu.ctrlS)
        self.bind('<Control-S>', self.menu.ctrlShiftS)
        self.bind('<Control-q>', self.menu.ctrlQ)

        self.speaker = tk.PhotoImage(file="speaker.png")
        self.speaker_btn = tk.Button(
            self.text, image=self.speaker, height=40, width=40, command=self.speak_selected)
        self.speaker_btn.update()
        self.speaker_btn.place(x=self.winfo_width() - 60, y=10)
        self.speaker_btn["bg"] = "white"
        self.speaker_btn["border"] = "0"
        self.speaker_btn.lift()
        self.speaker_btn.update()
        self.bind("<Configure>", self.resizeEvent)

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

    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def speak_selected(self):
        try:
            self.audio = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.speak(self.audio)
        except:
            self.speak("Please select some text.")

    def askToSave(self):
        if not self.IS_SAVED:
            msgbox = messagebox.askyesnocancel(
                title="Save Changes", message="Do you want to save the changes ?")
            if msgbox:
                self.menu.save_file()
                self.destroy()
            elif msgbox is None:
                pass
            else:
                self.destroy()
        else:
            self.destroy()

    def isUnsaved(self, e):
        self.IS_SAVED = 0

    def resizeEvent(self, e):
        self.update()
        self.speaker_btn.place(x=self.winfo_width() - 60, y=10)


class MenuBar(tk.Menu):

    def __init__(self, master):
        tk.Menu.__init__(self, master)
        self.master = master
        self.wrap_var = tk.StringVar()
        self.wrap_var.set("none")
        self.statusbar_var = tk.BooleanVar()
        self.statusbar_var.set(True)

        # File menu
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
                                   command=self.saveas_file,
                                   accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        self.file_menu.add_cascade(label="Quit",
                                   command=master.destroy,
                                   accelerator="Ctrl+Q")
        self.add_cascade(label="File", menu=self.file_menu,
                         font="Times 23 bold")

        # Edit menu
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

        # format menu
        self.Format = tk.Menu(self, tearoff=0)
        self.Format.add_command(label="Bold", command=self.bold_)
        self.Format.add_command(label="Italics", command=self.italics_)
        self.Format.add_command(label="Highlight",
                                command=self.master.text.highlight)
        self.Format.add_separator()
        self.Format.add_command(label="Fonts", command=self.fonts)
        self.Format.add_separator()
        self.Format.add_command(
            label="Selected Text Colour", command=self.colour_)
        self.Format.add_command(label="All Text Colour",
                                command=self.colour_all)
        self.Format.add_command(
            label="Background Colour", command=self.bkg_colour)
        self.Format.add_separator()
        self.Format.add_checkbutton(
            label="Night Mode", command=self.night_mode, variable=NIGHT_MODE_IS_ON)
        self.Format.add_checkbutton(label="Word Wrap",
                                    command=self.toggle_wrap)
        self.add_cascade(label="Format", menu=self.Format,
                         font="Times 23 bold")

        # format menu end

        # View Mwnu
        self.view_menu = tk.Menu(self, tearoff=False)
        self.view_menu.add_checkbutton(label="Status Bar",
                                       variable=self.statusbar_var,
                                       onvalue=True, offvalue=False,
                                       command=lambda master=master:
                                       self.toggle_statusbar(master))
        self.add_cascade(label="View", menu=self.view_menu,
                         font="Times 23 bold")

        # List Menu
        self.list_menu = tk.Menu(self, tearoff=False)
        self.list_menu.add_command(
            label="Make a List", command=self.open_list_window)
        self.add_cascade(label="List", menu=self.list_menu,
                         font="Times 23 bold")

        # Help Menu
        self.help_menu = tk.Menu(self, tearoff=False)
        self.help_menu.add_command(label="Help", command=self.open_help)
        self.help_menu.add_command(label="About Application",
                                   command=self.open_about_window)
        self.add_cascade(label="Help", menu=self.help_menu,
                         font="Times 23 bold")
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-v>', self.paste)

        # Functions
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

    # Format menu functions

    def bold_(self):
        bold_font = font.Font(self.master.text, self.master.text.cget("font"))
        bold_font.configure(weight="bold")
        self.master.text.tag_configure("bold", font=bold_font)
        # def current_tags
        current_tags = self.master.text.tag_names("sel.first")

        # if tag is set then remove else add
        if "bold" in current_tags:
            self.master.text.tag_remove("bold", "sel.first", "sel.last")
        else:
            self.master.text.tag_add("bold", "sel.first", "sel.last")

    def italics_(self):
        italics_font = font.Font(
            self.master.text, self.master.text.cget("font"))
        italics_font.configure(slant="italic")
        self.master.text.tag_configure("italic", font=italics_font)
        # def current_tags
        current_tags = self.master.text.tag_names("sel.first")

        # if tag is set then remove else add
        if "italic" in current_tags:
            self.master.text.tag_remove("italic", "sel.first", "sel.last")
        else:
            self.master.text.tag_add("italic", "sel.first", "sel.last")

    def fonts(self):
        font = askfont(self)
        if font:
            font['family'] = font['family'].replace(' ', '\ ')
            font_str = "%(family)s %(size)i %(weight)s %(slant)s" % font
        if font['underline']:
            font_str += ' underline'
        if font['overstrike']:
            font_str += ' overstrike'
        self.master.text.configure(font=font_str)

    # selected text

    def colour_(self):
        my_colour = colorchooser.askcolor()[1]
        colour_font = font.Font(
            self.master.text, self.master.text.cget("font"))
        # colour_font.configure(slant="italic")
        self.master.text.tag_configure(
            "coloured", font=colour_font, foreground=my_colour)
        # def current_tags
        current_tags = self.master.text.tag_names("sel.first")

        # if tag is set then remove else add
        if "colored" in current_tags:
            self.master.text.tag_remove("coloured", "sel.first", "sel.last")
        else:
            self.master.text.tag_add("coloured", "sel.first", "sel.last")

    # all text
    def colour_all(self):
        my_colour = colorchooser.askcolor()[1]
        if my_colour:
            self.master.text.configure(fg=my_colour)

    # $background colour
    def bkg_colour(self):
        my_colour = colorchooser.askcolor()[1]
        if my_colour:
            self.master.text.configure(fg='#FFFFFF')
            self.master.text.configure(background=my_colour)

    # night mode
    def night_mode(self):
        global NIGHT_MODE_IS_ON
        if not NIGHT_MODE_IS_ON:
            self.master.text.configure(fg='#FFFFFF')
            self.master.text.configure(
                background='#000000', insertbackground='#FFFFFF')
            self.master.speaker_btn["bg"] = '#000000'
            NIGHT_MODE_IS_ON = 1
        else:
            self.master.text.configure(fg='#000000')
            self.master.text.configure(
                background='#FFFFFF', insertbackground='#000000')
            self.master.speaker_btn["bg"] = '#FFFFFF'
            NIGHT_MODE_IS_ON = 0

    # Format menu funstions end

    def new_file(self):
        """
        Creates a new file object.  Then clears container frame and creates a
        new one by calling 'add_scrolledtext'.
        """

        if not self.master.IS_SAVED:
            msgbox = messagebox.askyesnocancel(
                title="Save Changes", message="Do you want to save the changes ?")
            if msgbox:
                self.save_file()
            elif msgbox is None:
                pass
        self.master.curr_file = File(join(dirname(realpath(__file__)) +
                                          "\\New File.txt"))
        self.master.add_scrolledtext()
        self.master.setup()
        self.master.IS_SAVED = 0

    def ctrlN(self, e):
        self.new_file()

    def open_file(self):
        """
        Destroys container frame and creates a new one by calling
        'add_scrolledtext'.  Inserts the data of that file into
        the newly created scrolledtext box.  Then creates a new File
        object and sets the curr_file to that object.
        """
        if not self.master.IS_SAVED:
            msgbox = messagebox.askyesnocancel(
                title="Save Changes", message="Do you want to save the changes ?")
            if msgbox:
                self.save_file()
            elif msgbox is None:
                pass
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
            self.master.IS_SAVED = 1

    def ctrlO(self, e):
        self.open_file()

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
        self.master.IS_SAVED = 1

    def ctrlS(self, e):
        self.save_file()

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
        self.master.IS_SAVED = 1

    def ctrlShiftS(self, e):
        self.saveas_file()

    def ctrlQ(self, e):
        self.master.askToSave()

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

    def select_all(self):
        self.master.text.tag_add("sel", "1.0", "end")

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

    def toggle_statusbar(self, master):
        """Toggles the status bar at the bottom of the window."""
        if not self.statusbar_var.get():
            master.status_bar.destroy()
        else:
            master.status_bar = StatusBar(master)
            master.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_list_window(self):
        self.list_window = ListWindow()

    def open_help(self):
        self.help_popup = HelpWindow()

    def open_about_window(self):
        """Displays the 'About' window."""
        self.about_popup = AboutWindow()


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


class HelpWindow(tk.Toplevel):
    """
    Displays help information.
    """

    def __init__(self):
        tk.Toplevel.__init__(self)
        self.title("Help : Easy-Note")
        self.geometry("800x200")
        self.help_frame = tk.Frame(self)
        self.help_frame.grid(column=0, row=0)
        tk.Label(self.about_frame, text="For Help on Using Easy-Note, Visit",
                 font="bold").grid(column=0, row=1)
        self.link1 = tk.Label(self.help_frame,
                              text="https://github.com/avd151/Easy-Note",
                              fg="blue", cursor="hand2")
        self.link1.grid(column=1, row=2, sticky="w")


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

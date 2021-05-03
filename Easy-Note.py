from gui import Main


if __name__ == "__main__":
    app = Main()
    app.protocol("WM_DELETE_WINDOW", app.askToSave)
    app.mainloop()

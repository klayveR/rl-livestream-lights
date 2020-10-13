from classes.dialog import Dialog
from pywinauto import Desktop

class WindowSelector():
    @staticmethod
    def select():
        print("Fetching list of active windows...")
        windows = Desktop(backend="uia").windows()
        windows_names = []

        for i in range(len(windows)):
            windows_names.append(windows[i].window_text())

        selection = Dialog.ask_for_list_item(windows_names, f"Please select the window the livestream is running in:")

        return windows_names[selection]
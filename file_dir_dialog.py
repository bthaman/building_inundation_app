try:
    # python 3
    import tkinter as tk
    import tkinter.filedialog as fd
except ImportError:
    # python 2
    import Tkinter as tk
    import tkFileDialog as fd
import os


def get_files():
    tk.Tk().withdraw()  # Close the root window
    in_path = fd.askopenfilename(multiple=True, title='Choose file(s)', initialdir=os.getcwd())
    tk.Tk().destroy()
    return in_path if in_path else None


def get_directory(title='Choose directory'):
    tk.Tk().withdraw()  # Close the root window
    in_path = fd.askdirectory(title=title, initialdir=os.getcwd())
    tk.Tk().destroy()
    return in_path if in_path else None


if __name__ == "__main__":
    print(get_directory())
    print(get_files())

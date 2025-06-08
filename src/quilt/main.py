import customtkinter as ctk
import tkinter

import os

from PIL import Image
from tkinter import Menu, filedialog

# Quilt Imports
from src.quilt.utils import *
from src.quilt.workspace import Workspace

from src.quilt.ui.widgets import WorkspaceFileWidget

class QuiltDefault(ctk.CTk):
    def __init__(self):
        super().__init__()        

        # Setting the theme and appearance mode
        ctk.set_default_color_theme('quilt_theme.json')
        ctk.set_appearance_mode("light")

        # Open in center of the screen
        self.eval('tk::PlaceWindow . center')

        # Creating the main window
        self.geometry("400x200")
        self.title(" Quilt")
        self.wm_iconbitmap('assets/quilt.ico')

        # Initialize
        self.load_startup()


    def load_startup(self):
        self.btn_open_ws = ctk.CTkButton(self, text="Open Workspace", 
                                            image=get_ctk_image("folder-open-light"), 
                                            compound="top", 
                                            command=self.open_workspace, 
                                            border_spacing=10,
                                            border_width=2)
        self.btn_open_ws.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)       


    def load_workspace(self, dir):
        self.workspace = Workspace(dir)


    def open_workspace(self):
        dir = filedialog.askdirectory(title=" Select Workspace Directory")
        if dir == '':
            return
        
        # Hide startup widgets
        self.btn_open_ws.place_forget()

        # Load the workspace
        self.load_workspace(dir)

        # Create the workspace UI
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
         # Create navigation pane
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(len(self.workspace.workspace_files) + 1, weight=1)

        self.navigation_title = ctk.CTkLabel(self.navigation_frame, 
                                             text=f" ",
                                             compound="left", 
                                             font=ctk.CTkFont(size=16))
        self.navigation_title.grid(row=0, column=0, padx=0, pady=0)

        file_icon = get_ctk_image("file-pdf-dark", 24)
        for i, workspace_file in enumerate(self.workspace.workspace_files):
            file_widgets = WorkspaceFileWidget(self.navigation_frame,
                                               width=300,
                                               height=32,
                                               text=workspace_file.filename,
                                               image=file_icon)
            file_widgets.grid(row=i + 1, column=0, sticky="ew", padx=10, pady=0)

def run_quilt(default_workspace=None):
    app = QuiltDefault()
    app.after(0, lambda: app.wm_state('zoomed'))
    app.mainloop()
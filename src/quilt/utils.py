import customtkinter as ctk
import os

from PIL import Image

def get_ctk_image(filename, size=32):
    return ctk.CTkImage(Image.open(os.path.join(f'assets', f'{filename}.png')), size=(size, size))  
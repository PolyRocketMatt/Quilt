import io
import os
import re

from cairosvg import svg2png
from PIL import Image
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLabel

from src.quilt.ui.colors import COLORS

SVG_COLOR = '#d9d9d9'
CURRENT_COLOR_NAME = 'dark-gray'
CURRENT_COLOR = COLORS[CURRENT_COLOR_NAME]

def modify_svg_colors(svg_content, color_mapping):
    modified_content = svg_content

    for old_color, new_color in color_mapping.items():
        # Handle different color formats in SVG
        patterns = [
            old_color.lower(),  # #ff0000
            old_color.upper(),  # #FF0000
            old_color.lstrip('#').lower(),  # ff0000
            old_color.lstrip('#').upper(),  # FF0000
        ]
        
        for pattern in patterns:
            # Replace in fill attributes
            modified_content = re.sub(
                rf'fill\s*=\s*["\']#{pattern}["\']',
                f'fill="{new_color}"',
                modified_content,
                flags=re.IGNORECASE
            )
            modified_content = re.sub(
                rf'fill\s*=\s*["\']{pattern}["\']',
                f'fill="{new_color}"',
                modified_content,
                flags=re.IGNORECASE
            )
            
            # Replace in stroke attributes
            modified_content = re.sub(
                rf'stroke\s*=\s*["\']#{pattern}["\']',
                f'stroke="{new_color}"',
                modified_content,
                flags=re.IGNORECASE
            )
            modified_content = re.sub(
                rf'stroke\s*=\s*["\']{pattern}["\']',
                f'stroke="{new_color}"',
                modified_content,
                flags=re.IGNORECASE
            )
            
            # Replace in style attributes
            modified_content = re.sub(
                rf'fill\s*:\s*#{pattern}',
                f'fill:{new_color}',
                modified_content,
                flags=re.IGNORECASE
            )
            modified_content = re.sub(
                rf'stroke\s*:\s*#{pattern}',
                f'stroke:{new_color}',
                modified_content,
                flags=re.IGNORECASE
            )
    
    return modified_content

def make_target_svg(svg_file_name, target_color_name=None):
    if not svg_file_name or not target_color_name:
        return

    svg_file_path = f'assets/icons/{svg_file_name}.svg'
    target_file_path = f'assets/icons/{target_color_name}/{svg_file_name}.svg' if target_color_name else None
    target_directory = f'assets/icons/{target_color_name}' if target_color_name else None

    # Make sure the target directory exists
    if target_directory and not os.path.exists(target_directory):
        os.makedirs(target_directory)

    try:
        # Check if a svg to the target already exists
        if os.path.exists(target_file_path):
            return

        # Read SVG file
        with open(svg_file_path, 'r', encoding='utf-8') as file:
            svg_content = file.read()

        # Apply color modifications if provided
        if target_color_name:
            target_color = COLORS[target_color_name]
            svg_content = modify_svg_colors(svg_content, { "#d9d9d9": target_color })

        # Save the modified SVG to the target path
        with open(target_file_path, 'w', encoding='utf-8') as file:
            file.write(svg_content)
                
    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
        return None


def svg_to_png_data(svg_file_name, target_color_name=None, width=64, height=64):
    if not svg_file_name:
        return None

    svg_file_path = f'assets/icons/{svg_file_name}.svg'

    try:
        # If a target color is specified, create the target SVG
        if target_color_name:
            make_target_svg(svg_file_name, target_color_name)
            svg_file_path = f'assets/icons/{target_color_name}/{svg_file_name}.svg'

        # Read SVG file
        with open(svg_file_path, 'r', encoding='utf-8') as file:
            svg_content = file.read()

        # Convert SVG to PNG
        png_data = svg2png(bytestring=svg_content.encode('utf-8'), output_width=width, output_height=height)
        if not png_data:
            print(f"Failed to convert SVG to PNG for {svg_file_name}")
            return None
        
        # Convert PNG data to bytes
        return png_data
    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
        return None
    
def svg_to_padded_png_data(svg_file_name, target_color_name=None, width=64, height=64, padding=12):
    icon_png_data = svg_to_png_data(svg_file_name, target_color_name, width - padding, height - padding)    
    if not icon_png_data:
        return None
    
    # Load PNG into a Pillow Image
    image = Image.open(io.BytesIO(icon_png_data)).convert("RGBA")

    # Create a new image with padding
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Calculate position to center the icon
    x = (canvas.size[0] - image.size[0]) // 2
    y = (canvas.size[1] - image.size[1]) // 2

    # Paste the icon onto the canvas with padding
    canvas.paste(image, (x, y), image)

    # Save the padded image to a bytes buffer
    output_buffer = io.BytesIO()
    canvas.save(output_buffer, format='PNG')
    output_buffer.seek(0)

    # Return the PNG data as bytes
    return output_buffer.getvalue()

def load_favicon():
    label = QLabel()
    label.setPixmap(QIcon("assets/quilt-nomid.ico").pixmap(16, 16))

    return label

def load_icon(icon_name, width=64, height=64):
    svg_content = svg_to_png_data(icon_name, CURRENT_COLOR_NAME, width, height)
    if not svg_content:
        return QIcon()
        
    pixmap = QPixmap()
    pixmap.loadFromData(svg_content)

    return QIcon(pixmap)

def load_colored_icon(icon_name, color=CURRENT_COLOR_NAME, width=64, height=64):
    svg_content = svg_to_png_data(icon_name, color, width, height)
    if not svg_content:
        return QIcon()
        
    pixmap = QPixmap()
    pixmap.loadFromData(svg_content)

    return QIcon(pixmap)

def load_padded_icon(icon_name, width=64, height=64, padding=0):
    svg_content = svg_to_png_data(icon_name, CURRENT_COLOR_NAME, width, height, padding)
    if not svg_content:
        return QIcon()
        
    pixmap = QPixmap()
    pixmap.loadFromData(svg_content)

    return QIcon(pixmap)

def load_and_save_icon(icon_name, width=32, height=32):
    svg_content = svg_to_png_data(icon_name, CURRENT_COLOR_NAME, width, height)
    if not svg_content:
        return None

    icon_path = f'assets/icons/{CURRENT_COLOR_NAME}/{icon_name}.png'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)

    with open(icon_path, 'wb') as file:
        file.write(svg_content)

    # Return the path to the saved icon
    return icon_path

def load_and_save_padded_icon(icon_name, width=32, height=32, padding=0):
    svg_content = svg_to_padded_png_data(icon_name, CURRENT_COLOR_NAME, width, height, padding)
    if not svg_content:
        return None

    icon_path = f'assets/icons/{CURRENT_COLOR_NAME}/{icon_name}.png'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)

    with open(icon_path, 'wb') as file:
        file.write(svg_content)

    # Return the path to the saved icon
    return icon_path

def load_stylesheet(style_name):
    with open(f'styles/{style_name}.qss', 'r') as file:
        return file.read()
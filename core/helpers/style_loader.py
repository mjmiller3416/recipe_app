"""
StyleLoader class for loading and concatenating QSS stylesheets.

This class is responsible for loading QSS stylesheets from a specified directory,
either a default or a custom one. It provides methods to load specific stylesheets
or all stylesheets in the directory.

Usage:
    style_loader = StyleLoader()
    stylesheet = style_loader.load_styles("button", "label")
    all_stylesheet = style_loader.load_all_styles()
"""


#🔸System Imports
import os

#🔸Local Application Imports
from core.application.config import BASE_DIR


class StyleLoader:
    """
    Loads and concatenates QSS stylesheets from the /styles directory.
    """

    def __init__(self, style_dir=None):
        """
        Initialize StyleLoader with a default relative path to the styles directory.
        """
        if style_dir is None:
            self.style_dir = os.path.join(BASE_DIR, "styles")
        else:
            self.style_dir = style_dir

    def load_styles(self, *files):
        """
        Loads specific .qss files from the style directory.

        Args:
            *files (str): One or more stylesheet filenames (without extension).

        Returns:
            str: Combined QSS content.
        """
        stylesheet = ""
        for file in files:
            path = os.path.join(self.style_dir, f"{file}.qss")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    stylesheet += f.read() + "\n"
            else:
                print(f"[StyleLoader] ⚠️ File not found: {path}")
        return stylesheet

    def load_all_styles(self):
        """
        Loads all .qss files from the style directory.

        Returns:
            str: Combined QSS content.
        """
        stylesheet = ""
        if not os.path.exists(self.style_dir):
            print(f"[StyleLoader] ⚠️ Directory not found: {self.style_dir}")
            return stylesheet

        for filename in os.listdir(self.style_dir):
            if filename.endswith(".qss"):
                path = os.path.join(self.style_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    stylesheet += f.read() + "\n"
        return stylesheet

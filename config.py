# config.py

from PyQt5.QtGui import QFont

# Base Font Configuration
BASE_FONT_FAMILY = "Arial"
BASE_FONT_SIZE = 10

# Specific Font Configurations
BUTTON_FONT_FAMILY = "Arial"
BUTTON_FONT_SIZE = 10

LABEL_FONT_FAMILY = "Arial"
LABEL_FONT_SIZE = 11

PREVIEW_FONT_FAMILY = "Courier New"
PREVIEW_FONT_SIZE = 12

DIALOG_FONT_FAMILY = "Arial"
DIALOG_FONT_SIZE = 11

HELP_BUTTON_FONT_FAMILY = "Arial"
HELP_BUTTON_FONT_SIZE = 10

# Function to get fonts
def get_base_font():
    return QFont(BASE_FONT_FAMILY, BASE_FONT_SIZE)

def get_button_font():
    return QFont(BUTTON_FONT_FAMILY, BUTTON_FONT_SIZE)

def get_label_font():
    return QFont(LABEL_FONT_FAMILY, LABEL_FONT_SIZE)

def get_preview_font():
    return QFont(PREVIEW_FONT_FAMILY, PREVIEW_FONT_SIZE)

def get_dialog_font():
    return QFont(DIALOG_FONT_FAMILY, DIALOG_FONT_SIZE)

def get_help_button_font():
    return QFont(HELP_BUTTON_FONT_FAMILY, HELP_BUTTON_FONT_SIZE)

import os

def copy_to_clipboard(text):
    # Disable clipboard inside Docker
    if os.path.exists("/.dockerenv"):
        return False  # clipboard not supported inside container

    import pyperclip
    pyperclip.copy(text)
    return True

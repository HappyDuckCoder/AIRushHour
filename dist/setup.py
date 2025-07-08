import os
import winshell
from win32com.client import Dispatch

def create_shortcut():
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "Rush Hour Puzzle.lnk")
    target = os.path.join(os.getcwd(), "main.exe")
    working_dir = os.getcwd()
    icon_path = target  # Hoặc thay bằng file .ico riêng nếu có

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = working_dir
    shortcut.IconLocation = icon_path
    shortcut.save()

if __name__ == "__main__":
    create_shortcut()
    print("Shortcut created on Desktop!")

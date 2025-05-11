import os
import win32com.client
import sys

def create_desktop_shortcut():
    # Get the path to the desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut_path = os.path.join(desktop_path, "Resize Images.lnk")
    shortcut = shell.CreateShortCut(shortcut_path)
    
    # Set the shortcut properties
    shortcut.TargetPath = sys.executable
    shortcut.Arguments = f'"{os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_resizer_cli.py")}" "%1" "%2"'
    shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
    shortcut.IconLocation = "imageres.dll, 1"
    shortcut.Description = "Resize images to 1200px width with border"
    
    # Save the shortcut
    shortcut.Save()
    
    print(f"Shortcut created at: {shortcut_path}")
    print("You can now drag and drop folders onto this shortcut to process images.")

if __name__ == "__main__":
    create_desktop_shortcut()

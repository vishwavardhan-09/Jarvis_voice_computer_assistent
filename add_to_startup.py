import os
import shutil

def add_to_startup(file_path):
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    if not os.path.exists(startup_folder):
        print("❌ Startup folder not found.")
        return

    shortcut_path = os.path.join(startup_folder, "Maxi.lnk")

    # Create shortcut using powershell
    powershell_command = f'''
    $WshShell = New-Object -ComObject WScript.Shell;
    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}");
    $Shortcut.TargetPath = "{file_path}";
    $Shortcut.WorkingDirectory = "{os.path.dirname(file_path)}";
    $Shortcut.WindowStyle = 1;
    $Shortcut.Save();
    '''

    os.system(f'powershell -Command "{powershell_command}"')
    print("✅ Maxi has been added to startup!")

if __name__ == "__main__":
    # Path to your maxi.py
    file_path = os.path.abspath("maxi.py")  
    add_to_startup(file_path)

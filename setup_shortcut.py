import os
import sys
import platform
import stat
from PIL import Image, ImageDraw

def create_icon(size=(256, 256)):
    image = Image.new('RGBA', size, color=(0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Scale factors
    w, h = size
    
    # Draw clipboard board
    board_x1, board_y1 = w * 0.15, h * 0.2
    board_x2, board_y2 = w * 0.85, h * 0.95
    dc.rounded_rectangle(
        (board_x1, board_y1, board_x2, board_y2), 
        radius=int(w*0.05), fill=(240, 240, 240), outline=(50, 50, 50), width=int(w*0.03)
    )
    
    # Draw clip top
    clip_x1, clip_y1 = w * 0.3, h * 0.05
    clip_x2, clip_y2 = w * 0.7, h * 0.25
    dc.rounded_rectangle(
        (clip_x1, clip_y1, clip_x2, clip_y2), 
        radius=int(w*0.03), fill=(120, 120, 120), outline=(50, 50, 50), width=int(w*0.02)
    )
    
    # Draw document lines
    line_x1 = w * 0.3
    line_x2 = w * 0.7
    line_w = int(w*0.03)
    dc.line((line_x1, h * 0.4, line_x2, h * 0.4), fill=(150, 150, 150), width=line_w)
    dc.line((line_x1, h * 0.55, line_x2, h * 0.55), fill=(150, 150, 150), width=line_w)
    dc.line((line_x1, h * 0.7, w * 0.5, h * 0.7), fill=(150, 150, 150), width=line_w)
    
    return image

def main():
    print("🛠️  Setting up IoT Smart Clipboard Shortcut...")
    
    # Paths
    project_dir = os.path.abspath(os.path.dirname(__file__))
    icon_png_path = os.path.join(project_dir, "clipboard_icon.png")
    icon_ico_path = os.path.join(project_dir, "clipboard_icon.ico")
    
    # Create icons
    img = create_icon()
    img.save(icon_png_path)
    img.save(icon_ico_path, format="ICO")
    print(f"🖼️  Generated icon at {icon_png_path}")

    app_name = "IoT Smart Clipboard"
    
    system = platform.system()
    if system == "Windows":
        # Try OneDrive Desktop first, fallback to standard Desktop
        onedrive_desktop = os.path.join(os.environ["USERPROFILE"], "OneDrive", "Desktop")
        if os.path.exists(onedrive_desktop):
            desktop_dir = onedrive_desktop
        else:
            desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
            
        shortcut_path = os.path.join(desktop_dir, f"{app_name}.lnk")
        project_shortcut_path = os.path.join(project_dir, f"{app_name}.lnk")
        
        # We use python.exe because pythonw.exe is causing silent crashes on some Windows setups
        python_dir = os.path.dirname(sys.executable)
        pythonw_exe = os.path.join(python_dir, "python.exe")
        
        # Fallback to sys.executable
        if not os.path.exists(pythonw_exe):
            pythonw_exe = sys.executable
            
        target_script = os.path.join(project_dir, "index.py")
        
        # VBScript to create shortcut without needing pywin32
        vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")

' Save to Desktop
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{pythonw_exe}"
oLink.Arguments = """{target_script}"""
oLink.WorkingDirectory = "{project_dir}"
oLink.IconLocation = "{icon_ico_path}"
oLink.WindowStyle = 1
oLink.Description = "Launch {app_name}"
oLink.Save

' Save to Project Folder
sLinkFile2 = "{project_shortcut_path}"
Set oLink2 = oWS.CreateShortcut(sLinkFile2)
oLink2.TargetPath = "{pythonw_exe}"
oLink2.Arguments = """{target_script}"""
oLink2.WorkingDirectory = "{project_dir}"
oLink2.IconLocation = "{icon_ico_path}"
oLink2.WindowStyle = 1
oLink2.Description = "Launch {app_name}"
oLink2.Save
'''
        vbs_path = os.path.join(project_dir, "create_shortcut.vbs")
        with open(vbs_path, "w") as f:
            f.write(vbs_script)
            
        import subprocess
        cscript_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32", "cscript.exe")
        subprocess.run([cscript_path, "//Nologo", vbs_path], check=True)
        os.remove(vbs_path)
        print(f"✅ Created shortcut on Desktop: {shortcut_path}")
        print(f"✅ Created backup shortcut in project folder: {project_shortcut_path}")

        
    elif system == "Linux":
        # Create .desktop on Desktop
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_dir):
            os.makedirs(desktop_dir)
            
        shortcut_path = os.path.join(desktop_dir, f"{app_name}.desktop")
        
        python_exe = sys.executable
        target_script = os.path.join(project_dir, "index.py")
        
        desktop_file_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment=Launch {app_name}
Exec={python_exe} "{target_script}"
Icon={icon_png_path}
Path={project_dir}
Terminal=false
Categories=Utility;
"""
        with open(shortcut_path, "w") as f:
            f.write(desktop_file_content)
            
        # Make it executable
        st = os.stat(shortcut_path)
        os.chmod(shortcut_path, st.st_mode | stat.S_IEXEC)
        
        print(f"✅ Created Linux desktop shortcut at {shortcut_path}")
        
    else:
        print(f"⚠️  Unsupported OS: {system}")
        sys.exit(1)

if __name__ == "__main__":
    main()

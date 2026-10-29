import os
import subprocess
import sys
import time

def setup_and_run():
    print("🚀 Initializing IoT Smart Clipboard (Desktop Edition)...")
    
    # 0. Ensure subjects and specific subject folders exist
    base_subjects = ["FLAT", "JAVA", "OS", "DBMS", "General"]
    if not os.path.exists("subjects"):
        os.makedirs("subjects")
    
    for subject in base_subjects:
        path = os.path.join("subjects", subject)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"📁 Created subject folder: {path}")

    # 1. Check for dependencies
    try:
        import flask
        import easyocr
        import docx
        import pystray # type: ignore
        import webview # type: ignore
        from PIL import Image, ImageDraw
    except ImportError:
        print("📦 Installing required packages (this may take a minute)...")
        # Install new desktop dependencies alongside existing ones
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "flask", "flask-cors", "easyocr", "python-docx", "pillow", "opencv-python", "pystray", "pywebview"
        ])
        print("✅ Installation Complete! Please run the script again to launch.")
        return

    # Helper for silent subprocess execution on Windows
    popen_kwargs = {}
    if os.name == 'nt':
        # CREATE_NO_WINDOW = 0x08000000
        popen_kwargs['creationflags'] = 0x08000000 

    # Get a reliable executable (prefer python.exe over pythonw.exe for subprocesses to avoid IO errors)
    python_exe = sys.executable
    if os.name == 'nt' and python_exe.lower().endswith('pythonw.exe'):
        # keep original case
        python_exe = python_exe[:-11] + "python.exe"

    import socket
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
            
    try:
        if is_port_in_use(5000):
            print("⚡ App is already running in background! Popping open window...")
            with open("desktop_log.txt", "a") as f: f.write("App running. Spawning webview...\n")
            subprocess.Popen(
                [python_exe, "-c", "import webview; webview.create_window('IoT Smart Clipboard', 'http://127.0.0.1:5000', width=1024, height=768); webview.start()"],
                **popen_kwargs
            )
            time.sleep(1) # Give the process a moment to detach before parent exits
            return

        # 2. Start Server Silently in Background
        print("🌐 Starting Backend Server silently...")
        with open("desktop_log.txt", "a") as f: f.write("Starting server...\n")
        server_process = subprocess.Popen([python_exe, "server.py"], **popen_kwargs)
        
        time.sleep(3) # Give server time to start
    except Exception as e:
        with open("desktop_log.txt", "a") as f: f.write(f"ERROR: {str(e)}\n")
        raise

    # 3. Setup System Tray Icon
    from pystray import Icon, Menu, MenuItem # type: ignore
    from PIL import Image, ImageDraw

    def create_clipboard_icon():
        # Generate an image and draw a custom clipboard emoji/icon
        image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw clipboard board (light grey)
        dc.rounded_rectangle((12, 16, 52, 60), radius=4, fill=(240, 240, 240), outline=(50, 50, 50), width=3)
        # Draw clip top (dark grey)
        dc.rounded_rectangle((22, 8, 42, 20), radius=2, fill=(120, 120, 120), outline=(50, 50, 50), width=2)
        # Draw document lines
        dc.line((22, 30, 42, 30), fill=(150, 150, 150), width=3)
        dc.line((22, 40, 42, 40), fill=(150, 150, 150), width=3)
        dc.line((22, 50, 32, 50), fill=(150, 150, 150), width=3)
        
        return image

    webview_process = None

    def open_app(icon, item):
        nonlocal webview_process
        # Only open if not already open
        if webview_process is None or webview_process.poll() is not None:
            # Start pywebview in a separate process to avoid blocking the tray icon event loop
            webview_process = subprocess.Popen(
                [python_exe, "-c", "import webview; webview.create_window('IoT Smart Clipboard', 'http://127.0.0.1:5000', width=1024, height=768); webview.start()"],
                **popen_kwargs
            )

    def quit_app(icon, item):
        nonlocal webview_process
        if webview_process is not None and webview_process.poll() is None:
            webview_process.terminate()
        server_process.terminate()
        icon.stop()

    # Define the right-click menu
    # Setting default=True allows the primary click (usually double-click on Windows) to trigger "Open App"
    menu = Menu(
        MenuItem('Open App', open_app, default=True),
        MenuItem('Quit', quit_app)
    )

    icon = Icon("IoT Smart Clipboard", create_clipboard_icon(), "IoT Smart Clipboard", menu)
    
    print("📋 System Tray Icon activated! Look for the clipboard in your taskbar.")
    print("💡 Click the icon to open the app, or right-click for options.")
    
    # Auto-open the app window slightly after startup to ensure tray and server are ready
    import threading
    def initial_open():
        time.sleep(1.5)
        open_app(None, None)
        
    threading.Thread(target=initial_open, daemon=True).start()
    
    # This blocks the main thread and keeps the tray icon running
    icon.run()

if __name__ == "__main__":
    setup_and_run()

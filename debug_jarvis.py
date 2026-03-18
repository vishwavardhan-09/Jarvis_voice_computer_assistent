import os

# Mock dependencies
def speak(text):
    print(f"SPEAK: {text}")

class MockWhatsapp:
    def send_whatsapp_message(self, phone, msg):
        print(f"WHATSAPP: Sending '{msg}' to {phone}")
        return True

whatsapp_client = MockWhatsapp()

def change_volume(action): pass
def take_screenshot(): return "path.png"
def lock_screen(): pass
def media_control(action): pass
def search_and_open_app(app): pass
def play_youtube(q): return {'status': 'success', 'title': 'video'}

# Copy-paste the relevant parts of execute_command (or import if possible, but importing might trigger init code)
# I will redefine execute_command here to match the file EXACTLY (based on my last edit)

def execute_command(command):
    """Executes a single command and returns (success, response_text)"""
    command_lower = command.lower()
    
    # NLP Pre-processing
    prefixes = [
        "i want to ", "can you ", "please ", "could you ", "maxi ", "hey maxi ", 
        "just ", "asking to ", "would you "
    ]
    
    cleaned_command = command_lower
    for prefix in prefixes:
        if cleaned_command.startswith(prefix):
            cleaned_command = cleaned_command.replace(prefix, "", 1).strip()
            
    command_lower = cleaned_command
    
    response_text = ""
    executed = False

    # ... (other blocks omitted for brevity, focusing on relevant chain)
    # I'll include the ones before WhatsApp to be sure

    if "open youtube" in command_lower:
        print("MATCH: open youtube")
        executed = True

    elif "open google" in command_lower:
        print("MATCH: open google")
        executed = True
        
    # ... Skipping others ...
    
    # WhatsApp Integration
    elif "whatsapp" in command_lower and "send" in command_lower:
        print("MATCH: whatsapp block")
        try:
            CONTACTS = {
                "mom": "+910000000000",
                "dad": "+910000000000",
                "friend": "+910000000000"
            }
            
            recipient = ""
            message = ""
            
            if "send whatsapp to" in command_lower:
                parts = command_lower.replace("send whatsapp to", "").strip()
                if "saying" in parts:
                    recipient_part, message_part = parts.split("saying", 1)
                elif "message" in parts:
                    recipient_part, message_part = parts.split("message", 1)
                else:
                    recipient_part, message_part = parts, ""
                
                recipient = recipient_part.strip()
                message = message_part.strip()
                
            elif " to " in command_lower and (" in whatsapp" in command_lower or " on whatsapp" in command_lower):
                cleaned = command_lower.replace("send ", "", 1).replace(" in whatsapp", "").replace(" on whatsapp", "")
                
                if " to " in cleaned:
                    message_part, recipient_part = cleaned.rsplit(" to ", 1)
                    recipient = recipient_part.strip()
                    message = message_part.strip()
            
            print(f"Parsed: recipient='{recipient}', message='{message}'")

            if recipient in CONTACTS:
                recipient_number = CONTACTS[recipient]
                recipient = recipient_number
            else:
                recipient = recipient.replace(" ", "")
                if recipient.isdigit() and len(recipient) >= 10:
                     if not recipient.startswith("+"):
                        recipient = "+91" + recipient
            
            if recipient and message:
                if recipient == "+910000000000":
                    speak(f"I don't have a number for {recipient} yet.")
                else:
                    speak(f"Sending WhatsApp message to {recipient}")
                    # In real code: success = whatsapp_client.send_whatsapp_message(...)
            else:
                speak("I couldn't understand who to send the message to.")
                
        except Exception as e:
            print(f"❌ WhatsApp Command Error: {e}")
        executed = True

    return executed, response_text

# TEST
cmd = "send hi to chaitan in whatsapp"
print(f"\nTesting command: '{cmd}'")
executed, response = execute_command(cmd)
print(f"Result: executed={executed}, response='{response}'")

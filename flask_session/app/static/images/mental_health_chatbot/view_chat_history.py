from app.database import get_all_messages  # Updated import

def main():
    history = get_all_messages()  # Fetch all messages, no username input
    if not history:
        print("No chat history found.")
        return
    for username, sender, message, timestamp in history:
        print(f"{timestamp} - {username} - {sender}: {message}")

if __name__ == '__main__':
    main()


import json
import os
from collections import deque
from datetime import datetime

class HistoryManager:
    def __init__(self, filepath="history.json", max_size=200):
        self.filepath = filepath
        self.max_size = max_size
        self.history = deque(maxlen=max_size)
        self.load_history()

    def load_history(self):
        """Load history from the JSON file if it exists."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Re-initialize deque with loaded data to respect maxlen
                        self.history = deque(data, maxlen=self.max_size)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading history: {e}. Starting fresh.")
                self.history.clear()

    def save_history(self):
        """Save the current history to the JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(list(self.history), f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"❌ Error saving history: {e}")

    def add_entry(self, user_query, assistant_response):
        """Add a new interaction to the history and save it."""
        if not user_query or not assistant_response:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_query,
            "assistant": assistant_response
        }
        self.history.append(entry)
        self.save_history()

    def get_recent(self, limit=10):
        """Get the most recent interactions."""
        # Convert deque to list and slice the last 'limit' items
        # interactions are appended, so the end of the list is the most recent
        all_items = list(self.history)
        return all_items[-limit:]

    def clear(self):
        """Clear all history."""
        self.history.clear()
        self.save_history()

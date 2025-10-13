# shadow_core/notepad.py
class Notepad:
    def __init__(self, file_path="data/notepad.txt"):
        self.file_path = file_path

    def write_note(self, text):
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        return "Note saved."

    def read_notes(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "No notes found."

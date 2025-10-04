# shadow_core/safety.py
class Safety:
    def __init__(self):
        self.restricted_keywords = ["delete all files", "hack", "crack", "illegal"]

    def check_request(self, user_query):
        for word in self.restricted_keywords:
            if word in user_query.lower():
                return False, "Sorry Salar, I cannot perform this action for safety reasons."
        return True, "Request safe to execute."

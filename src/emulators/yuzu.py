from settings import settings

class Yuzu:
    def __init__(self):
        self.yuzu_user_directory = settings.get("Yuzu:User Directory")
        pass
    def start(self):
        print("starting yuzu")
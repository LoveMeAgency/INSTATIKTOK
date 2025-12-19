import os
import json
import time
import schedule
from datetime import datetime
from instagrapi import Client as InstaClient
from tiktok_uploader.proxy_auth import upload_video
import config

class SocialBot:
    def __init__(self):
        self.history_file = "database/video_history.json"
        self.ensure_dirs()
        self.history = self.load_history()
        self.current_index = self.history.get("current_index", -1)

    def ensure_dirs(self):
        for d in ["database", "session", config.MEDIA_FOLDER]:
            os.makedirs(d, exist_ok=True)

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f: return json.load(f)
            except: return {"current_index": -1}
        return {"current_index": -1}

    def save_history(self):
        with open(self.history_file, 'w') as f: json.dump(self.history, f)

    def get_next_video(self):
        # On accepte maintenant les vidéos ET les images
        valid_exts = ('.mp4', '.mov', '.mkv', '.jpg', '.jpeg', '.png')
        files = sorted([os.path.join(config.MEDIA_FOLDER, f) for f in os.listdir(config.MEDIA_FOLDER) 
                       if f.lower().endswith(valid_exts)])
        
        if not files:
            print(f"⚠️ Aucun média trouvé dans {config.MEDIA_FOLDER}")
            return None
        
        self.current_index = (self.current_index + 1) % len(files)
        self.history["current_index"] = self.current_index
        self.save_history()
        return files[self.current_index]

    def post_insta(self, video_path):
        for acc in config.INSTAGRAM_ACCOUNTS:
            try:
                cl = InstaClient()
                session_path = f"session/insta_{acc['username']}.json"
                if os.path.exists(session_path): cl.load_settings(session_path)
                cl.login(acc["username"], acc["password"])
                cl.dump_settings(session_path)
                cl.clip_upload(video_path, caption=config.DESCRIPTION)
                print(f"✅ Instagram OK")
            except Exception as e: print(f"❌ Erreur Insta : {e}")

    def post_tiktok(self, video_path):
        try:
            upload_video(video_path, description=config.DESCRIPTION, cookies=config.TIKTOK_COOKIES)
            print("✅ TikTok OK")
        except Exception as e: print(f"❌ Erreur TikTok : {e}")

    def run_cycle(self):
        video = self.get_next_video()
        if video:
            print(f"🚀 Publication : {video}")
            self.post_insta(video)
            time.sleep(10)
            self.post_tiktok(video)

    def start(self):
        print("🤖 Bot actif sur VPS.")
        # Publie immédiatement au lancement pour vérifier
        self.run_cycle()
        for t in config.POST_TIMES:
            schedule.every().day.at(t).do(self.run_cycle)
        while True:
            schedule.run_pending()
            time.sleep(30)

if __name__ == "__main__":
    SocialBot().start()
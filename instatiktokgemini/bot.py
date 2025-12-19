import os
import json
import time
import schedule
from datetime import datetime
from instagrapi import Client as InstaClient
from tiktok_uploader.upload import upload_video
import config

class SocialBot:
    def __init__(self):
        # On utilise le nom de fichier que tu as sur ta capture
        self.history_file = "database/post_history.json"
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

    def get_next_media(self):
        # Accepte vidéos et photos
        valid_exts = ('.mp4', '.mov', '.mkv', '.jpg', '.jpeg', '.png')
        files = sorted([os.path.join(config.MEDIA_FOLDER, f) for f in os.listdir(config.MEDIA_FOLDER) 
                       if f.lower().endswith(valid_exts)])
        
        if not files:
            print(f"⚠️ Aucun média dans {config.MEDIA_FOLDER}")
            return None
            
        self.current_index = (self.current_index + 1) % len(files)
        self.history["current_index"] = self.current_index
        self.save_history()
        return files[self.current_index]

    def post_insta(self, media_path):
        for acc in config.INSTAGRAM_ACCOUNTS:
            try:
                cl = InstaClient()
                
                # Application du proxy
                if config.PROXY_URL:
                    cl.set_proxy(config.PROXY_URL)
                
                session_path = f"session/insta_{acc['username']}.json"
                if os.path.exists(session_path):
                    cl.load_settings(session_path)
                
                cl.login(acc["username"], acc["password"])
                cl.dump_settings(session_path)
                
                # Détection automatique : Vidéo ou Photo
                if media_path.lower().endswith(('.mp4', '.mov')):
                    cl.clip_upload(media_path, caption=config.DESCRIPTION)
                else:
                    cl.photo_upload(media_path, caption=config.DESCRIPTION)
                    
                print(f"✅ Instagram OK")
            except Exception as e:
                print(f"❌ Erreur Insta : {e}")

    def post_tiktok(self, video_path):
        if not video_path.lower().endswith(('.mp4', '.mov')):
            print("⏭️ TikTok ignore les photos, passage au suivant.")
            return

        try:
            upload_video(
                video_path, 
                description=config.DESCRIPTION, 
                cookies=config.TIKTOK_COOKIES,
                proxy=config.PROXY_URL
            )
            print("✅ TikTok OK")
        except Exception as e:
            print(f"❌ Erreur TikTok : {e}")

    def run_cycle(self):
        media = self.get_next_media()
        if media:
            print(f"\n🚀 [ {datetime.now().strftime('%H:%M')} ] Envoi de : {media}")
            self.post_insta(media)
            time.sleep(15) # Pause pour éviter le spam
            self.post_tiktok(media)

    def start(self):
        print("🤖 Bot démarré avec Proxy.")
        # Test immédiat au lancement
        self.run_cycle()
        
        for t in config.POST_TIMES:
            schedule.every().day.at(t).do(self.run_cycle)
            
        while True:
            schedule.run_pending()
            time.sleep(30)

if __name__ == "__main__":
    SocialBot().start()

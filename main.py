from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
import threading
import requests
import os

class MobileDownloaderApp(App):
    def build(self):
        self.title = "Media Downloader Pro"
        
        # Layout Utama (Vertical)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Judul
        layout.add_widget(Label(text="⚽ Media Downloader Pro (Android)", font_size=20, size_hint_y=None, height=40))

        # Pilihan Platform
        layout.add_widget(Label(text="Pilih Platform:", size_hint_y=None, height=20))
        self.platform_spinner = Spinner(
            text='TikTok',
            values=('TikTok', 'Instagram'),
            size_hint_y=None, height=40
        )
        layout.add_widget(self.platform_spinner)

        # Input Link (Single atau Massal 1 baris 1 link)
        layout.add_widget(Label(text="Masukkan Link (1 baris 1 link) atau Path File .txt:", size_hint_y=None, height=20))
        self.link_input = TextInput(
            text='',
            hint_text='Tempel link di sini atau ketik path file .txt...',
            size_hint_y=None, height=120,
            multiline=True
        )
        layout.add_widget(self.link_input)

        # Tombol Download Langsung
        self.download_btn = Button(
            text='🚀 Mulai Download Langsung',
            size_hint_y=None, height=48,
            background_color=(0.48, 0.22, 0.93, 1)
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        layout.add_widget(self.download_btn)

        # Progress Bar
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=25)
        layout.add_widget(self.progress_bar)

        # Status / Log Teks
        self.status_label = Label(text="Status: Siap mendownload...", font_size=13, halign='left', valign='top')
        self.status_label.bind(size=self.status_label.setter('text_size'))
        layout.add_widget(self.status_label)

        return layout

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

    def start_download_thread(self, instance):
        raw_text = self.link_input.text.strip()
        if not raw_text:
            self.update_status("⚠️ Peringatan: Masukkan link atau path file .txt terlebih dahulu!")
            return

        # Cek apakah input berupa path file .txt atau langsung link teks
        links = []
        if os.path.isfile(raw_text):
            try:
                with open(raw_text, "r", encoding="utf-8") as f:
                    links = [line.strip() for line in f if line.strip().startswith("http")]
            except Exception as e:
                self.update_status(f"❌ Gagal membaca file .txt: {e}")
                return
        else:
            links = [l.strip() for l in raw_text.split("\n") if l.strip().startswith("http")]

        if not links:
            self.update_status("⚠️ Tidak ditemukan link valid (harus diawali http/https).")
            return

        platform = self.platform_spinner.text
        self.download_btn.disabled = True
        self.progress_bar.value = 0

        threading.Thread(target=self.process_mass_downloads, args=(platform, links)).start()

    def process_mass_downloads(self, platform, links):
        total = len(links)
        self.update_status(f"=== Memulai Download Masal {total} Link {platform} ===")
        
        # Folder penyimpanan internal Android (Folder Download)
        output_dir = "/storage/emulated/0/Download"
        if not os.path.exists(output_dir):
            output_dir = "./"

        success = 0
        for idx, link in enumerate(links, start=1):
            self.update_status(f"[{idx}/{total}] Mendownload langsung...")
            self.progress_bar.value = (idx / total) * 100

            try:
                if platform == 'TikTok':
                    res = requests.post("https://www.tikwm.com/api/", data={"url": link}, timeout=15).json()
                    if res.get("code") == 0:
                        data = res.get("data")
                        vid_url = data.get("play")
                        author = data.get("author", {}).get("unique_id", "tiktok")
                        vid_id = data.get("id", "post")
                        
                        file_path = os.path.join(output_dir, f"{author}_{vid_id}.mp4")
                        vid_res = requests.get(vid_url, stream=True, timeout=30)
                        with open(file_path, "wb") as f:
                            for chunk in vid_res.iter_content(1024):
                                if chunk: f.write(chunk)
                        success += 1
                elif platform == 'Instagram':
                    api_url = "https://api.cobalt.tools/api/json"
                    headers = {"Accept": "application/json", "Content-Type": "application/json"}
                    payload = {"url": link.split("?")[0]}
                    res = requests.post(api_url, json=payload, headers=headers, timeout=20).json()
                    
                    if res.get("status") in ["redirect", "stream"]:
                        media_url = res.get("url")
                        file_path = os.path.join(output_dir, f"IG_media_{idx}.mp4")
                        m_res = requests.get(media_url, stream=True, timeout=30)
                        with open(file_path, "wb") as f:
                            for chunk in m_res.iter_content(1024):
                                if chunk: f.write(chunk)
                        success += 1
            except Exception as e:
                pass

        self.update_status(f"✨ Selesai! Berhasil mengunduh {success}/{total} file.\nTersimpan di folder: Download HP")
        Clock.schedule_once(lambda dt: setattr(self.download_btn, 'disabled', False))

if __name__ == '__main__':
    MobileDownloaderApp().run()
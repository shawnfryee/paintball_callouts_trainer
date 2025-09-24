import asyncio
import random
import threading
import time
import tempfile
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pygame
import edge_tts

# Config
EDGE_TTS_VOICES = [
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-GB-LibbyNeural",
    "en-GB-RyanNeural",
]
MIN_DELAY = 3.2   # seconds between spoken words
MAX_DELAY = 12.2
DEFAULT_MP3_NAME = "background.mp3"
# ----------------------------------------------------

class TTSCache:
    def __init__(self, voice_choices, tmpdir, speaking_volume=0.8):
        self.voice_choices = voice_choices
        self.tmpdir = tmpdir
        self.speaking_volume = speaking_volume
        self.cache = {}
        self.loop = None
        self.loop_thread = None
        self._ensure_loop()

    def _ensure_loop(self):
        if self.loop is not None:
            return
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _gen_file_async(self, voice, word):
        safe_name = f"{voice}_{word}".replace(" ", "_").replace("/", "_")
        out_path = os.path.join(self.tmpdir, safe_name + ".mp3")
        if not os.path.exists(out_path):
            comm = edge_tts.Communicate(word, voice)
            await comm.save(out_path)
        return out_path

    def get_or_make(self, voice, word):
        key = (voice, word)
        if key in self.cache and os.path.exists(self.cache[key]):
            return self.cache[key]

        fut = asyncio.run_coroutine_threadsafe(
            self._gen_file_async(voice, word), self.loop
        )
        out_path = fut.result()
        self.cache[key] = out_path
        return out_path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Callout Trainer")
        self.resizable(False, False)

        # Audio init
        pygame.mixer.init()
        self.music_playing = False

        # State
        self.mp3_path = None
        self.words_path = None
        self.words = []
        self.speaking = False
        self.speak_thread = None

        self.music_vol = tk.DoubleVar(value=80.0)
        self.voice_vol = tk.DoubleVar(value=80.0)

        self.tmpdir = tempfile.mkdtemp(prefix="edge_tts_cache_")
        self.tts_cache = TTSCache(EDGE_TTS_VOICES, self.tmpdir)

        # UI
        pad = {"padx": 8, "pady": 6}
        row = ttk.Frame(self); row.grid(row=0, column=0, sticky="ew", **pad)
        ttk.Button(row, text="Load MP3", command=self.load_mp3).grid(row=0, column=0, **pad)
        self.mp3_label = ttk.Label(row, text="No MP3 loaded", width=34)
        self.mp3_label.grid(row=0, column=1, **pad)

        row2 = ttk.Frame(self); row2.grid(row=1, column=0, sticky="ew", **pad)
        ttk.Button(row2, text="Load Words (.txt)", command=self.load_words).grid(row=0, column=0, **pad)
        self.words_label = ttk.Label(row2, text="No word list loaded", width=34)
        self.words_label.grid(row=0, column=1, **pad)

        row3 = ttk.Frame(self); row3.grid(row=2, column=0, sticky="ew", **pad)
        self.play_btn = ttk.Button(row3, text="Play/Pause Music", command=self.toggle_music, state="disabled")
        self.play_btn.grid(row=0, column=0, **pad)
        ttk.Button(row3, text="Stop Music", command=self.stop_music).grid(row=0, column=1, **pad)

        row4 = ttk.Frame(self); row4.grid(row=3, column=0, sticky="ew", **pad)
        self.speak_btn = ttk.Button(row4, text="Start Speaking", command=self.toggle_speaking, state="disabled")
        self.speak_btn.grid(row=0, column=0, **pad)
        ttk.Button(row4, text="Quit", command=self.safe_quit).grid(row=0, column=1, **pad)

        row5 = ttk.Frame(self); row5.grid(row=4, column=0, sticky="ew", **pad)
        ttk.Label(row5, text="Music Volume").grid(row=0, column=0, sticky="w")
        ttk.Scale(row5, from_=0, to=100, orient="horizontal", variable=self.music_vol,
                  command=lambda _e: self.apply_music_volume()).grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(row5, text="Voice Volume").grid(row=1, column=0, sticky="w")
        ttk.Scale(row5, from_=0, to=100, orient="horizontal", variable=self.voice_vol,
                  command=lambda _e: None).grid(row=1, column=1, sticky="ew", padx=6)  # applied at playback


        self.columnconfigure(0, weight=1); row5.columnconfigure(1, weight=1)

        self.apply_music_volume()
        self.protocol("WM_DELETE_WINDOW", self.safe_quit)

    #  File handling
    def load_mp3(self):
        path = filedialog.askopenfilename(
            title="Select MP3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            pygame.mixer.music.load(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load MP3:\n{e}")
            return
        self.mp3_path = path
        self.mp3_label.config(text=os.path.basename(path))
        self.play_btn.config(state="normal")

    def load_words(self):
        path = filedialog.askopenfilename(
            title="Select word list (.txt, 1 word per line)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f]
            words = [w for w in lines if w]
            if not words:
                raise ValueError("No words found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load word list:\n{e}")
            return
        self.words_path = path
        self.words = words
        self.words_label.config(text=f"{os.path.basename(path)} ({len(words)} words)")
        self.speak_btn.config(state="normal")

    #  Music
    def toggle_music(self):
        if not self.mp3_path:
            return
        if not self.music_playing:
            try:
                pygame.mixer.music.play(loops=-1)
                self.music_playing = True
                self.play_btn.config(text="Pause Music")
            except Exception as e:
                messagebox.showerror("Error", f"Could not play MP3:\n{e}")
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.play_btn.config(text="Resume Music")
            else:
                pygame.mixer.music.unpause()
                self.play_btn.config(text="Pause Music")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False
        self.play_btn.config(text="Play/Pause Music")

    def apply_music_volume(self):
        vol = max(0.0, min(1.0, self.music_vol.get() / 100.0))
        pygame.mixer.music.set_volume(vol)

    # Speaking
    def toggle_speaking(self):
        if not self.words:
            messagebox.showwarning("No words", "Please load a word list first.")
            return

        if self.speaking:
            self.speaking = False
            self.speak_btn.config(text="Start Speaking")
        else:
            self.speaking = True
            self.speak_btn.config(text="Stop Speaking")
            self.speak_thread = threading.Thread(target=self.speak_loop, daemon=True)
            self.speak_thread.start()

    def speak_loop(self):
        prewarm = min(3, len(self.words))
        seen = set()
        for _ in range(prewarm):
            word = random.choice(self.words)
            voice = random.choice(EDGE_TTS_VOICES)
            seen.add((voice, word))
        for voice, word in list(seen):
            try:
                self.tts_cache.get_or_make(voice, word)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("TTS Error", str(e)))
                self.speaking = False
                self.after(0, lambda: self.speak_btn.config(text="Start Speaking"))
                return

        while self.speaking:
            word = random.choice(self.words)
            voice = random.choice(EDGE_TTS_VOICES)
            try:
                mp3_path = self.tts_cache.get_or_make(voice, word)
                # pplay via pygame.Sound for independent volume control
                snd = pygame.mixer.Sound(mp3_path)
                # voice volume
                vol = max(0.0, min(1.0, self.voice_vol.get() / 100.0))
                snd.set_volume(vol)
                ch = snd.play()
                while ch.get_busy() and self.speaking:
                    time.sleep(0.05)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Playback Error", str(e)))
                self.speaking = False
                self.after(0, lambda: self.speak_btn.config(text="Start Speaking"))
                break

            # random delay between words
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            for _ in range(int(delay * 10)):
                if not self.speaking:
                    break
                time.sleep(0.1)


    def safe_quit(self):
        try:
            self.speaking = False
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        finally:
            self.destroy()

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = App()
    app.mainloop()

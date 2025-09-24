# Paintball Callout Trainer — README

Train your awareness: this app plays a looping **background MP3** of paintball markers and randomly **speaks callouts** pulled from a simple `.txt` file (one callout per line). You can adjust **music** and **voice** volumes independently and start/stop whenever you want. For the best training effect, run the app while doing something that demands your full attention—like playing a fast-paced FPS game, solving problems, or reading a book. The idea is to practice picking up and reacting to callouts in the background without breaking focus on your primary task.

---

## Requirements

- **Python 3.10+** must be installed on the PC.
  - Windows: https://www.python.org/downloads/ (check “Add Python to PATH” during install)
  - Linux: usually preinstalled; otherwise install via your package manager.
- Internet connection for natural voices (the app uses **Edge TTS** neural voices).
- This app was **created on Linux** but should also **run on Windows**.

---

## Quick Start

1. **Download the app folder** (contains the Python script and a `background.mp3`).
2. Prepare your **callouts file**:
   - Create a text file like `callouts.txt`.
   - Put **one callout per line**, for example:
     ```
     left snake
     dorito 2
     home bunker
     cross-field
     watch your tape
     ```
3. Install dependencies (from the app folder):
   ```bash
   pip install pygame edge-tts
   ```
   - If you’re on Ubuntu/Debian and Tk isn’t installed:
     ```bash
     sudo apt-get install -y python3-tk
     ```
4. Run the app:
   ```bash
   python word_sayer_packaged.py
   ```

---

## Controls & Features

- **Background audio**: A bundled `background.mp3` auto-loads and can loop continuously.
- **Load Words (.txt)**: Choose your callouts file (must be plain text, one callout per line).
- **Play/Pause Music**: Start/pause the background MP3.
- **Stop Music**: Stops the MP3 loop.
- **Start/Stop Speaking**: Toggles random callout playback using human-like neural voices.
- **Music Volume**: Adjusts background MP3 level.
- **Voice Volume**: Adjusts callout speech level.

> Tip: Keep music slightly lower than voice so callouts are easy to hear.

---

## Editing the Callouts

- Open your `.txt` file in any text editor (Notepad, VS Code, etc.).
- Write **one callout per line**. Blank lines are ignored.
- Save and reload the file from the app if it’s already running.

---

## Packaging (Optional)

If you want a single file/folder to share:

- Install PyInstaller:
  ```bash
  pip install pyinstaller
  ```
- Build (Windows one-file example):
  ```powershell
  pyinstaller --noconfirm --onefile --windowed ^
    --name PaintballCalloutTrainer ^
    --add-data "background.mp3;." ^
    word_sayer_packaged.py
  ```
- Build (Linux one-file example):
  ```bash
  pyinstaller --noconfirm --onefile --windowed \
    --name PaintballCalloutTrainer \
    --add-data "background.mp3:." \
    word_sayer_packaged.py
  ```
Distribute the file in `dist/`. (One-folder builds are also fine and sometimes more stable with antivirus.)

---

## Common Issues

- **“No module named …”**  
  Run:
  ```bash
  pip install pygame edge-tts
  ```
  Make sure you’re using the same Python for both `pip` and `python`:
  ```bash
  python -m pip install pygame edge-tts
  ```

- **No sound / missing GUI on Linux**  
  Install Tk:
  ```bash
  sudo apt-get install -y python3-tk
  ```

- **Voices sound robotic / nothing speaks offline**  
  The app uses **Edge TTS** (neural, online). Ensure you have internet.  
  If you need an offline fallback, ask the maintainer to add `pyttsx3` mode (lower quality, but offline).

- **Antivirus flags the EXE**  
  This can happen with “one-file” builds. Try the **one-folder** build or code-sign the EXE.

---

## Customization

- **Voices**: The app uses a curated set of Microsoft neural voices. More voices can be added by editing the list in the script (look for `EDGE_TTS_VOICES`).
- **Timing**: The pause between callouts is randomized within a small range. This can be adjusted in the script (`MIN_DELAY` / `MAX_DELAY`).

---

## Audio & Licensing Notes

- The bundled `background.mp3` is assumed to be licensed for redistribution by you.  
  **Only distribute audio you have rights to share.**
- Edge TTS voices are provided by Microsoft services; usage requires internet access and is subject to Microsoft’s terms.

---

## Support

- If you hit a packaging or runtime error, share:
  - Your OS (Windows version / Linux distro)
  - Python version (`python --version`)
  - The exact error text (copy/paste)
- Feature requests welcome (e.g., voice picker, min/max delay controls, “no-repeat” mode, hotkeys).

Happy training, and see you on the field! 🟢🔵

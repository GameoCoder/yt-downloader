# PyQt6 YouTube Downloader

A modern, feature-rich GUI application to download videos and audio from YouTube. Built with Python and PyQt6, this tool offers a user-friendly experience for managing downloads, selecting quality, and handling playlists.

> **Note:** This project is a GUI evolution of the CLI tool originally created by [AswinOp](https://github.com/AswinOp/yt-downloader).

## ✨ Features

  * **Modern GUI:** Clean interface built with PyQt6.
  * **Smart Formatting:** Choose between Video (MP4) or Audio (MP3) with a single click.
  * **Playlist Support:** Paste a playlist link to batch download videos.
  * **Advanced Controls:**
      * Select Video Quality (360p, 720p, 1080p, Best).
      * Rate Limiting.
      * Subtitle & Metadata extraction.
  * **Portable Design:** capable of self-extracting necessary dependencies (FFmpeg) on the fly.

## 🛠️ Prerequisites

To run this application from source or build it, you need Python 3.x and the following libraries:

```bash
pip install -r requirements.txt
```

## 🚀 How to Build (Create EXE)

Because GitHub has file size limits, the required FFmpeg archive is hosted externally. Follow these steps to build a standalone `.exe` file that includes FFmpeg.

### 1\. Clone the Repository

```bash
git clone https://github.com/GameoCoder/yt-downloader.git
cd yt-downloader
```

### 2\. Download the FFmpeg Archive

To make the application portable, you must download the compressed FFmpeg archive.

1.  **[Download archive.7z from Google Drive](https://drive.google.com/file/d/14PDvmx0n8QSubWT66a-e3dv4D7keAJGf/view?usp=sharing)**
2.  Place the `archive.7z` file directly into the root folder of the project (where `download_pyqt6.py` is located).

> **Why?** This archive contains `ffmpeg.exe`. The application is programmed to detect if FFmpeg is missing and automatically unzip this archive for the user on the first run.

### 3\. Build with PyInstaller

Run the following command to create the executable. This bundles the script, the UI files, and the 7-Zip archive into a single file.

```bash
pyinstaller --noconfirm --onefile --windowed ^
 --add-data "frame.ui;." ^
 --add-data "advanced.ui;." ^
 --add-data "archive.7z;." ^
 download_pyqt6.py
```

*(Note: If you are on MacOS/Linux, replace the `^` with `\` and `;` with `:` in the command above).*

The final executable will be located in the `dist/` folder.

## 🏃 Running from Source

If you prefer to run the Python script directly without building an EXE:

1.  Ensure you have `ffmpeg` installed on your system **OR** place the `archive.7z` (linked above) in the project folder.
2.  Run the script:
    ```bash
    python download_pyqt6.py
    ```

## 📸 Usage

1.  **Paste URL:** Copy a YouTube video or playlist URL and click "Paste".
2.  **Search:** Click search to validate the link and fetch metadata.
3.  **Download:**
      * For **Single Videos**: Click "Download".
      * For **Playlists**: A table will appear. Select the tracks you want, toggle between Audio/Video for specific tracks, and click "Download Selected".
4.  **Advanced Options:** Click the generic settings icon (Tool Button) to adjust resolution caps, retries, or rate limits.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/GameoCoder/yt-downloader/blob/main/LICENSE) file for details.

## 🤝 Contributing

Feel free to submit issues or pull requests. Special thanks to AswinOp for the original CLI logic.
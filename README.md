
# YouTube Video Downloader

This Python script allows you to download and merge the best quality video and audio from YouTube using `yt-dlp`. It automatically installs `yt-dlp` if it's not already installed on your system.

## Requirements

- Python 3.x
- `ffmpeg` must be installed on your system for merging video and audio streams.

### Installing `ffmpeg`

#### Windows
1. Download `ffmpeg` from [FFmpeg's official site](https://ffmpeg.org/download.html).
2. Extract the ZIP file and add the `bin` directory to your system's PATH environment variable.

#### macOS
Install `ffmpeg` using Homebrew:
```bash
brew install ffmpeg
```

#### Linux
Install `ffmpeg` using your package manager. For example, on Ubuntu:
```bash
sudo apt update
sudo apt install ffmpeg
```

## Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/aswinop/yt-downloader.git
   cd yt-downloader
   ```

2. Run the script:
   ```bash
   python download_video.py
   ```

3. Select the method when prompted:
   ```
   Methods Available:-
     1) Auto Detect
     2) Download Youtube Video
     3) Download Youtube Music
     4) Advanced Options

   Your Choice:
   ```

4. Enter the YouTube video/music URL when prompted:
   ```
   Enter the YouTube video URL: https://www.youtube.com/watch?v=your-video-id
   ```
   OR
   ```
   Enter the Youtube Music URL: https://music.youtube.com/watch?v=your-video-id
   ```

5. The script will download the best available video and audio streams, merge them, and save the file in the current directory.

## For Playlists
   1. Run the script:
      ```
      python download_video.py
      ```
   2. Select the "Auto Detect" method when prompted:
      ```
      Methods Available:-
      1) Auto Detect
      2) Download Youtube Video
      3) Download Youtube Music
      4) Advanced Options

      Your Choice: 1
      ```
   3. Enter the playlist URL, when prompted:
      ```
      Enter the URL: https://music.youtube.com/playlist?list=your-playlist-id
      ```
   4. Enter serial numbers of videos to be downloaded, or "**all**" to download all:
      ```
      Available Music to download:  5

      Select songs to download:
      1. Test Video 1 (https://music.youtube.com/watch?v=test-video-1)
      2. Test Video 2 (https://music.youtube.com/watch?v=test-video-2)
      3. Test Video 3 (https://music.youtube.com/watch?v=test-video-3)
      4. Test Video 4 (https://music.youtube.com/watch?v=test-video-4)
      5. Test Video 5 (https://music.youtube.com/watch?v=test-video-5)

      Enter song numbers (space-separated), or 'all' to download all:  
      ```
   5. Sit back and relax until your selected videos have been downloaded.
      <p>The downloads are multi-threaded, so it would be pretty fast.</p>
> Note: Youtube Music playlist links will ***only*** download files as mp3.


## Example Output

```
yt-dlp is not installed. Installing now...
[yt-dlp] Downloading video...
Title: Example Video Title
Download completed! File saved as Example Video Title.mp4
```

## Contributing

Feel free to submit issues or pull requests to improve the script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
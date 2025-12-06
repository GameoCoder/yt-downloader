import platform
import sys
import subprocess, os, shutil
import wget
import yt_dlp

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def fix_ffmpeg_extracted_path(base_ffmpeg_dir):
    # Step 1: Find the extracted folder
    extracted_folders = [f for f in os.listdir(base_ffmpeg_dir) if os.path.isdir(os.path.join(base_ffmpeg_dir, f))]
    if not extracted_folders:
        raise Exception("No extracted folders found!")
    extracted_path = os.path.join(base_ffmpeg_dir, extracted_folders[0])
    bin_path = os.path.join(extracted_path, "bin")
    if not os.path.exists(bin_path):
        raise Exception("No 'bin' folder inside extracted ffmpeg directory!")
    # Step 2: Move all files from bin/ to ffmpeg/
    for filename in os.listdir(bin_path):
        src = os.path.join(bin_path, filename)
        dst = os.path.join(base_ffmpeg_dir, filename)
        shutil.move(src, dst)
    # Step 3: Delete the extracted folder
    shutil.rmtree(extracted_path)
    print(f"Fixed FFmpeg structure! {extracted_path} removed.")

def extract_7z(archive_path, extract_to):
    seven_zip_path = resource_path(os.path.join("7zip", "7za.exe"))
    if not os.path.exists(seven_zip_path):
        raise FileNotFoundError("7z.exe not found!")
    # Create the destination folder if it doesn't exist
    os.makedirs(extract_to, exist_ok=True)
    # Run 7z.exe command to extract
    subprocess.run([
        seven_zip_path,
        'x', archive_path,
        f'-o{extract_to}',
        '-y'
    ], check=True)

def ensure_ffmpeg_ready():
    required_files = [
        "ffmpeg/ffmpeg.exe",
        "ffmpeg/ffplay.exe",
        "ffmpeg/ffprobe.exe"
    ]
    all_exist = all(os.path.exists(file) for file in required_files)
    if all_exist:
        print("FFmpeg is ready to use!          ✅")
        return
    print("FFmpeg not found or incomplete. Setting up FFmpeg...")
    try:
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z"
        print(f"Downloading {url}")
        file_name = wget.download(url)
        print(f"\nDownloaded {url} to {file_name}")
    except Exception as e:
        print(f"Error occurred {e}")
    file_name = "ffmpeg-git-essentials.7z"
    extract_7z(file_name, "ffmpeg/")
    fix_ffmpeg_extracted_path("./ffmpeg/")
    os.remove(file_name)
    print("FFmpeg setup completed!          🎉")

def download_youtube_video(url):
    try:
        ydl_opts = {
            'ffmpeg_location': './ffmpeg',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            print(f"Title: {info_dict.get('title', 'Unknown Title')}")
            print(f"Download completed! File saved as {info_dict.get('title', 'Unknown Title')}.{info_dict.get('ext', 'mp4')}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__=="__main__":
    print("Program is Alive                 ✅")
    ensure_ffmpeg_ready()
    print("Program Initialized Successfully ✅")
    print("Please Enter Video URL:")
    link = input("URL: ")
    print("Your link is: " + link)
    choice = input("\nIs this correct? Yes/No (Y/N) [Default: Yes]: ").strip().lower()
    if choice in ("y", ""):
        download_youtube_video(link)
    elif choice == "n":
        print("Okay, canceling...")
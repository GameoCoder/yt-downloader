import sys
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QProgressBar, QLabel, QLineEdit, 
    QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout
)
from PyQt6 import uic
from PyQt6.QtGui import QClipboard
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed


URL = "https://music.youtube.com/playlist?list=PLyZ03ihN5GIBiumzB0iyEGCENBidy5I0V"
video_info = {}

class DownloadWorker(QThread):
    progress_update=pyqtSignal(str,int)
    download_complete=pyqtSignal()

    def __init__(self,selected_videos):
        super().__init__()
        self.selected_videos = selected_videos

    def run(self):
        for title,url in self.selected_videos:
            self.download_video_with_progress(title,url)
        self.download_complete.emit()

    def download_video_with_progress(self, title, url):
        ydl_opts = {
            'format': 'best',
            'outtmpl': f"{title}.%(ext)s",
            'progress_hooks': [lambda d: self.update_progress(d,title)]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def update_progress(self, d, title):
        if d['status'] == 'downloading':
            total_size = d.get('total_bytes', None)
            downloaded_size = d.get('downloaded_bytes', 0)

            if total_size:
                percent = (downloaded_size / total_size) * 100
                print(f"Update progress for {title}: {percent}%")
                self.progress_update.emit(title, int(percent))  # Emit signal for progress update

class ResultWindow(QWidget):
    def __init__(self,results):
        super().__init__()
        self.setWindowTitle("Search Results")
        self.setGeometry(100,100,600,400)
        layout=QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Select','Title','Extension','Progress'])
        self.table.setRowCount(len(results))

        self.progress_bars = {} #Dictionary to store Progress Bars
        
        for row, (title, ext) in enumerate(results):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)  # Set checkbox flag
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)  # unchecked by default
            checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, checkbox_item)
            self.table.setItem(row, 1, QTableWidgetItem(title))
            print(f"Title of the video is {title} and {ext}")
            self.table.setItem(row, 2, QTableWidgetItem(ext))
            progress_bar=QProgressBar()
            progress_bar.setValue(0)
            self.table.setCellWidget(row,3,progress_bar)
            self.progress_bars[title]=progress_bar
        self.downloadButtonPlayList = QPushButton("Download Selected")
        self.downloadButtonPlayList.clicked.connect(self.temp)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        layout.addWidget(self.downloadButtonPlayList)
        self.setLayout(layout)

    def temp(self):
        global video_info
        selected_videos=[]
        for row in range(self.table.rowCount()):
            checkbox_item=self.table.item(row,0)
            if checkbox_item and checkbox_item.checkState()==Qt.CheckState.Checked:
                title=self.table.item(row,1).text()
                url=video_info.get(title)
                if url:
                    selected_videos.append((title,url))

        if not selected_videos:
            QMessageBox.warning(self,"Download Error","No Videos selected to Download")
        self.worker=DownloadWorker(selected_videos)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.download_complete.connect(self.on_download_complete)
        self.worker.start()

    def update_progress(self,title,percent):
        if title in self.progress_bars:
            self.progress_bars[title].setValue(percent)
            print(f"Progress bar for {title} set to {percent}%")

    def on_download_complete(self):
        QMessageBox.information(self,"Download Complete", "All Videos have been downloaded")
    def download_selected(self):
        #self.parent().download_videos(self.table)
        global video_info
        selected_videos = []
        for row in range(self.table.rowCount()):
            checkbox_item=self.table.item(row,0)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                title=self.table.item(row,1).text()
                url = video_info.get(title)
                if url:
                    selected_videos.append((title,url))
        
        if not selected_videos:
            QMessageBox.warning(self,"Download Error", "No Videos selected to Download")

        max_workers = 4
        with ThreadPoolExecutor(max_workers=max_workers)as executor:
            future_to_video={executor.submit(self.download_video_with_progress,title,url): title for title,url in selected_videos}

            for future in as_completed(future_to_video):
                title=future_to_video[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error Downloading file {title}: {str(e)}")

    def download_video_with_progress(self,title,url):
        ydl_opts={
            'format':'best',
            'outtmpl':f"{title}.%(ext)s",
            'progress-hooks':[lambda d: self.update_progress(d,title)]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    #def update_progress(self,d,title):
        #if d['status'] == 'downloading':
            #total_size = d.get('total_bytes', None)
            #downloaded_size = d.get('downloaded_bytes', 0)

            #if total_size:
                #percent = (downloaded_size / total_size) * 100
                #self.progress_bars[title].setValue(int(percent))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        uic.loadUi('frame.ui',self)
        self.pasteButton = self.findChild(QPushButton, 'pasteButton')
        self.entry = self.findChild(QLineEdit, 'entry')
        self.downloadText = self.findChild(QLabel, 'downloader')
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.downloadButton = self.findChild(QPushButton, 'downloadButton')
        self.searchButton = self.findChild(QPushButton, 'searchButton')
        self.downloadText.hide()
        self.downloadButton.hide()
        self.progressBar.hide()

        self.pasteButton.clicked.connect(self.paste_from_clipboard)
        self.downloadButton.clicked.connect(self.download_videos)
        self.searchButton.clicked.connect(self.search_video)

    def search_video(self):
        url=self.entry.text()
        if not url:
            QMessageBox.warning(self,"Input Error", "Please Enter a Valid URL.")
            url=URL
        
        ydl_opts = {
            'quiet': True,
            'force-generic-extractor':True,
            'extract_flat': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url,download=False)
                playlist_title=info['title']
                video_titles = [video['title'] for video in info['entries']]
                video_urls = [video['url'] for video in info['entries']]
            
            global video_info
            video_info={title:url for title, url in zip(video_titles,video_urls)}
            results = [(title,"mp3") for title in video_titles]
            self.downloadButton.show()
            self.result_window = ResultWindow(results)
            self.result_window.show()
        except Exception as e:
            print(f"Error Occurred: {e}")

    def paste_from_clipboard(self):
        clipboard=QApplication.clipboard()
        text=clipboard.text()
        self.entry.setText(text)

    def download_videos(self):
        global video_info
        selected_videos = []
        for row in range(self.result_window.table.rowCount()):
            checkbox_item=self.result_window.table.item(row,0)
            if checkbox_item and checkbox_item.CheckState() == Qt.CheckState.Checked:
                title=self.result_window.table.item(row,1).text()
                url = video_info.get(title)
                if url:
                    selected_videos.append((title,url))
        
        if not selected_videos:
            QMessageBox.warning(self,"Download Error", "No Videos selected to Download")

        self.download_progress_window=DownloadProgressWindow(selected_videos)
        self.download_progress_window.show()
        self.result_window.close()

        max_workers = 4
        with ThreadPoolExecutor(max_workers=max_workers)as executor:
            future_to_video={executor.submit(self.download_video_with_progress,title,url): title for title,url in selected_videos}

            for future in as_completed(future_to_video):
                title=future_to_video[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error Downloading file {title}: {str(e)}")

    def download_video_with_progress(self,title,url):
        ydl_opts={
            'format':'best',
            'outtmpl':f"{title}.%(ext)s",
            'progress-hooks':[lambda d: self.update_progress(d,title)]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    def update_progress(self,d,title):
        if d['status'] == 'downloading':
            total_size = d.get('total_bytes', None)
            downloaded_size = d.get('downloaded_bytes', 0)

            if total_size:
                percent = (downloaded_size / total_size) * 100
                progress_bar = self.download_progress_window.progress_bars.get(title)
                if progress_bar:
                    progress_bar.setValue(int(percent))

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec())

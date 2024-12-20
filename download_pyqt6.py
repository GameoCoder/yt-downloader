import sys
import os
import yt_dlp
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QProgressBar, QLabel, QLineEdit, QSlider, QCheckBox, QComboBox, QDoubleSpinBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout, QToolButton, QSpinBox, QGraphicsView, QTextEdit
)
from PyQt6 import uic, QtWidgets
from PyQt6.QtGui import QClipboard, QPixmap, QImage
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from io import BytesIO


## GLOBAL VARIABLES
URL = "https://music.youtube.com/playlist?list=PLyZ03ihN5GIBiumzB0iyEGCENBidy5I0V"  #DEBUG - Remove in production
video_info = {}
extensions = {}
ERROR = False
thumbnail_url = ""

ydl_opts = {
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,
}

def update_options(**kwargs):
    global ydl_opts
    for key, value in kwargs.items():
        if value is None:
            ydl_opts.pop(key, None)
        else:
            ydl_opts[key] = value

class AdvancedWindow(QWidget):
    def __init__(self):
        super().__init__()
        if hasattr(sys,'_MEIPASS'):
            ui_file=os.path.join(sys._MEIPASS, 'advanced.ui')
        else:
            ui_file='advanced.ui'
        uic.loadUi(ui_file,self)
        global ydl_opts
        ydl_opts.clear()
        #Quality Control
        self.qSlider = self.findChild(QSlider, 'qSlider')
        self.qSliderLabel = self.findChild(QLabel, 'qSliderLabel')

        #Checkboxes
        self.checkVerbose = self.findChild(QCheckBox, 'checkVerbose')
        self.checkSubtitle = self.findChild(QCheckBox, 'checkSubtitles')
        self.checkMetadata = self.findChild(QCheckBox, 'checkMetadata')

        #Extension
        self.extensionBox = self.findChild(QComboBox, 'extensionBox')

        #Retry Box
        self.retryBox = self.findChild(QSpinBox, 'retryBox')

        #Rate Limiter
        self.checkRate = self.findChild(QCheckBox, 'checkRate')
        self.rateLimiterBox = self.findChild(QDoubleSpinBox, 'rateLimiterBox')
        self.rateLimiterBox.hide()
        #TODO -> Rate LImiter doesnt work

        #Thumbnail View
        self.graphicsView = self.findChild(QGraphicsView, 'graphicsView')


        #Confirm n Reset
        self.pushConfirm = self.findChild(QPushButton, 'pushConfirm')
        self.pushReset = self.findChild(QPushButton, 'pushReset')
        self.pushConfirm.clicked.connect(self.confirm)

        self.qSlider.valueChanged.connect(self.update_slider_label)

        #Fetch Thumbnail
        global thumbnail_url
        image_data = BytesIO(requests.get(thumbnail_url).content)
        image=QImage()
        image.loadFromData(image_data.getvalue())
        pixmap = QPixmap.fromImage(image)
        view_size = self.graphicsView.size()
        scaled_pixed = pixmap.scaled(view_size,Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        scene=QtWidgets.QGraphicsScene()
        scene.addPixmap(scaled_pixed)
        self.graphicsView.setScene(scene)

    def confirm(self):
        current_quality = self.qSliderLabel.text()
        print(f"Selected Quality: {current_quality}")
        current_retries = self.retryBox.value()
        print(f"Selected number of retries: {current_retries}")
        current_ext = self.extensionBox.currentText()
        print(f"Selected Extension: {current_ext}\n")

    def update_slider_label(self):
        current_value = self.qSlider.value()
        labels = ["Worst", "Good", "Better", "Best"]
        index = current_value // 25
        self.qSliderLabel.setText(labels[index])

class DownloadWorker(QThread):
    progress_update=pyqtSignal(str,int)
    download_complete=pyqtSignal()

    def __init__(self,selected_videos,logger_var=None):
        super().__init__()
        self.selected_videos = selected_videos
        if logger_var != None:
            self.logger_var2 = logger_var

    def run(self):
        global extensions
        try:
            for title,url in self.selected_videos:
                ext="mp4"
                if extensions[title]==False:
                    ext="mp3"
                self.download_video_with_progress(title,url,ext)
            self.download_complete.emit()
        except ValueError:
            for title,url in self.selected_videos.items():
                ext="mp4"
                if extensions[title]==False:
                    ext="mp3"
                self.download_video_with_progress(title,url,ext)
            self.download_complete.emit()

    def download_video_with_progress(self, title, url, ext):
        #ydl_opts = {
        #    'format': 'best',
        #    'outtmpl': f"{title}.{ext}",
        #    'progress_hooks': [lambda d: self.update_progress(d,title)]
        #}
        global ydl_opts
        ydl_opts.clear()
        try:
            update_options(format='best',outtmpl=f'{title}.{ext}',progress_hooks=[lambda d: self.update_progress(d,title)], no_warnings=False, logger=self.logger_var2)
        except Exception:
            update_options(format='best',outtmpl=f'{title}.{ext}',progress_hooks=[lambda d: self.update_progress(d,title)], no_warnings=False)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                print(f"Unable to Download file {title}\nError: {e}")
                self.log_error(e)
                global ERROR
                ERROR = True

    def update_progress(self, d, title):
        if d['status'] == 'downloading':
            total_size = d.get('total_bytes', None)
            downloaded_size = d.get('downloaded_bytes', 0)

            if total_size:
                percent = (downloaded_size / total_size) * 100
                self.progress_update.emit(title, int(percent))
    
    def log_error(self, message):
        logs_directory = "logs"
        if not os.path.exists(logs_directory):
            os.makedirs(logs_directory)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(logs_directory, f"error_{timestamp}.txt")

        with open(log_filename, 'a') as log_file:
            log_file.write(f"{message}\n Timestamp-{datetime.now()}\n")

class Logger(QObject):
    messageSignal=pyqtSignal(str)

    def debug(self,msg):
        self.messageSignal.emit(msg)
    
    def warning(self,msg):
        self.messageSignal.emit(msg)
    
    def error(self,msg):
        self.messageSignal.emit(msg)

class ResultWindow(QWidget):
    def __init__(self,results):
        super().__init__()
        self.setWindowTitle("Search Results")
        self.setGeometry(100,100,600,700)
        layout=QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['','Title','Extension','Progress','Remarks'])
        self.table.setRowCount(len(results))
        self.progress_bars = {}
        self.loggers = {}
        for row, (title, ext) in enumerate(results):
            #CheckBox Item Setup
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            self.table.setItem(row, 0, checkbox_item)
            self.table.item(row, 0).setFlags(self.table.item(row, 0).flags() & ~Qt.ItemFlag.ItemIsEditable)

            #Title Item Setup
            self.table.setItem(row, 1, QTableWidgetItem(title))
            self.table.item(row, 1).setFlags(self.table.item(row, 1).flags() & ~Qt.ItemFlag.ItemIsEditable)

            #Toggle Button Setup
            toggle_button = QPushButton('Video (mp4)')
            toggle_button.setCheckable(True)
            extensions[title]=True
            toggle_button.clicked.connect(lambda checked, btn=toggle_button, r=row: self.toggle_value(btn,r))
            self.table.setCellWidget(row, 2, toggle_button)

            #Progress Bars Setup
            progress_bar=QProgressBar()
            progress_bar.setValue(0)
            self.progress_bars[title]=progress_bar
            self.table.setCellWidget(row, 3, progress_bar)

            #Logger Setup
            logger = QTextEdit()
            logger.setReadOnly(True)
            self.loggers[title]=logger
            self.table.setCellWidget(row, 4, logger)
        self.logger = QTextEdit()
        self.logger.setReadOnly(True)
        self.downloadButtonPlayList = QPushButton("Download Selected")
        self.downloadButtonPlayList.clicked.connect(self.search_and_download)

        #Table Config
        self.table.setAlternatingRowColors(True)
        self.table.setColumnWidth(0,25)
        self.table.setColumnWidth(1,200)
        self.table.setColumnWidth(2,100)
        self.table.setColumnWidth(3,75)
        self.table.setColumnWidth(4,200)
        layout.addWidget(self.table)
        layout.addWidget(self.downloadButtonPlayList)
        layout.addWidget(self.logger)
        self.logger.setFixedHeight(50)
        self.setLayout(layout)

    def toggle_value(self,button,row):
        global video_info
        title=self.table.item(row,1).text()
        if button.isChecked():
            button.setText('Audio (mp3)')
            extensions[title]=False
        else:
            button.setText('Video (mp4)')
            extensions[title]=True

    def search_and_download(self):
        global video_info
        self.selected_videos={}
        for row in range(self.table.rowCount()):
            checkbox_item=self.table.item(row,0)
            if checkbox_item and checkbox_item.checkState()==Qt.CheckState.Checked:
                title=self.table.item(row,1).text()
                url=video_info.get(title)
                if url:
                    self.selected_videos[title]=url
                    self.loggers[title].clear()
                    self.loggers[title].insertPlainText('Waiting To Dowload')

        if not self.selected_videos:
            QMessageBox.warning(self,"Download Error","No Videos selected to Download")
        self.logger_var=Logger()
        self.logger_var.messageSignal.connect(self.logger.append)
        self.worker=DownloadWorker(self.selected_videos,self.logger_var)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.download_complete.connect(self.on_download_complete)
        self.worker.start()

    def update_progress(self,title,percent):
        if title in self.progress_bars:
            self.progress_bars[title].setValue(percent)
            if percent >= 0:
                self.loggers[title].clear()
                self.loggers[title].insertPlainText('Downloading...')

    def on_download_complete(self):
        global ERROR
        if(ERROR == False):
            QMessageBox.information(self,"Download Complete", "All Video/Audio files have been downloaded")
            for title in self.progress_bars:
                if self.selected_videos.get(title) is not None:
                    self.progress_bars[title].setValue(0)
                    self.loggers[title].clear()
                    self.loggers[title].insertPlainText('Downloaded!')
        else:
            QMessageBox.warning(self,"Error","Files not downloaded have some error.\nLogs Created at logs/error______.txt")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        if hasattr(sys,'_MEIPASS'):
            ui_file=os.path.join(sys._MEIPASS, 'frame.ui')
        else:
            ui_file='frame.ui'
        uic.loadUi(ui_file,self)
        self.pasteButton = self.findChild(QPushButton, 'pasteButton')
        self.entry = self.findChild(QLineEdit, 'entry')
        self.downloadText = self.findChild(QLabel, 'downloader')
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.downloadButton = self.findChild(QPushButton, 'downloadButton')
        self.searchButton = self.findChild(QPushButton, 'searchButton')
        self.toolButton = self.findChild(QToolButton, 'toolButton')
        ##TODO - Remove after debug
        self.entry.setText("https://www.youtube.com/watch?v=6rO6uRUrqwY")
        #self.entry.setText(URL)
        self.downloadText.hide()
        self.downloadButton.hide()
        self.progressBar.hide()
        self.toolButton.hide()

        self.toolButton.clicked.connect(self.advanced)
        self.pasteButton.clicked.connect(self.paste_from_clipboard)
        self.downloadButton.clicked.connect(self.download_videos)
        self.searchButton.clicked.connect(self.search_video)

    def advanced(self):
        self.new_window = AdvancedWindow()
        self.new_window.show()

    def search_video(self):
        url=self.entry.text()
        global video_info
        global extensions
        video_info.clear()
        extensions.clear()
        if not url:
            QMessageBox.warning(self,"Input Error", "Please Enter a Valid URL.")
            url=URL
        
        if "playlist" in url or "list" in url:
            global ydl_opts
            ydl_opts.clear()
            update_options(force_generic_extractor=True, extract_flat=True, quiet=True, no_warnings=True)

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url,download=False)
                    playlist_title=info['title']
                    video_titles = [video['title'] for video in info['entries']]
                    video_urls = [video['url'] for video in info['entries']]
                
                video_info.clear()
                video_info={title:url for title, url in zip(video_titles,video_urls)}
                results = [(title,"mp3") for title in video_titles]
                self.result_window = ResultWindow(results)
                self.result_window.show()
            except Exception as e:
                print(f"Error Occurred: {e}")
        else:
            global thumbnail_url
            ydl_opts.clear()
            update_options(quiet=False,force_generic_extractor=True,extract_flat=True)

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info=ydl.extract_info(url,download=False)
                    thumbnail_url = info.get('thumbnail')
                    extensions[info['title']] = "music" not in url
                    video_info={info['title']: info['id']}
                    self.downloadButton.show()
                    self.downloadText.show()
                    self.toolButton.show()
                    self.downloadText.setText("Title - "+info['title'])
            except Exception as e:
                print(f"Error Occurred: {e}")

    def paste_from_clipboard(self):
        clipboard=QApplication.clipboard()
        text=clipboard.text()
        self.entry.setText(text)

    def download_videos(self):
        self.progressBar.show()
        self.progressBar.setValue(0)
        self.downloadText.setText("Downloading...")
        global video_info
        try:
            self.worker=DownloadWorker(video_info)
            self.worker.progress_update.connect(self.update_progress)
            self.worker.download_complete.connect(self.on_download_complete)
            self.worker.start()
        except Exception as e:
            print(f"ERROR: {e}")
    
    def update_progress(self,title,percent):
        self.progressBar.setValue(percent)
    
    def on_download_complete(self):
        global ERROR
        if(ERROR == False):
            QMessageBox.information(self,"Download Complete", "All Videos have been downloaded")
        else:
            QMessageBox.warning(self,"Error","Some error occurred while downloading file/s.\nPlease check logs")

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec())
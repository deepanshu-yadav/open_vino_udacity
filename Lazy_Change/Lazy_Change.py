VERSION = "Change Songs through gesture v0.10"
import sys, time, threading, cv2
import numpy as np
try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel
    from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor
    from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
    from PyQt5.QtCore import QUrl, QDirIterator
    from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QAction, QHBoxLayout, \
        QVBoxLayout, QSlider
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QPoint
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel
    from PyQt4.QtGui import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt4.QtGui import QFont, QPainter, QImage, QTextCursor
try:
    import Queue as Queue
except:
    import queue as Queue

from inference import Inference
from datetime import datetime
IMG_SIZE    = 1280,720         # 640,480 or 1280,720 or 1920,1080
IMG_FORMAT  = QImage.Format_RGB888
DISP_SCALE  = 2                # Scaling factor for display image
DISP_MSEC   = 50                # Delay between display cycles
CAP_API     = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
EXPOSURE    = 0                 # Zero for automatic exposure
TEXT_FONT   = QFont("Courier", 10)

camera_num  = 1                 # Default camera (first in list)
image_queue = Queue.Queue()     # Queue to hold images
capturing   = True              # Flag to indicate capturing

# Grab images from the camera (separate thread)
def grab_images(cam_num, queue):
    cap = cv2.VideoCapture(cam_num-1 + CAP_API)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_SIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_SIZE[1])
    if EXPOSURE:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
    else:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    while capturing:
        if cap.grab():
            retval, image = cap.retrieve(0)
            if image is not None and queue.qsize() < 2:
                queue.put(image)
            else:
                time.sleep(DISP_MSEC / 1000.0)
        else:
            print("Error: can't grab camera image")
            break
    cap.release()

# Image widget
class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()

# Main window
class MyWindow(QMainWindow):
    text_update = pyqtSignal(str)

    # Create main window
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.central = QWidget(self)

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.userAction = -1
        self.inference = Inference()
        self.folder_chosen = False
        self.textbox = QTextEdit(self.central)
        self.textbox.setFont(TEXT_FONT)
        self.textbox.setMinimumSize(300, 100)
        self.text_update.connect(self.append_text)
        sys.stdout = self
        print("Camera number %u" % camera_num)
        print("Image size %u x %u" % IMG_SIZE)
        if DISP_SCALE > 1:
            print("Display scale %u:1" % DISP_SCALE)

        self.vlayout = QVBoxLayout()        # Window layout
        self.displays = QHBoxLayout()
        self.disp = ImageWidget(self)
        self.displays.addWidget(self.disp)
        self.vlayout.addLayout(self.displays)
        self.label = QLabel(self)
        self.vlayout.addWidget(self.label)
        self.vlayout.addWidget(self.textbox)

        # TODO provision for allowing song to play
        self.current_song_start_time = datetime.now()

        volumeslider = QSlider(Qt.Horizontal, self)
        volumeslider.setFocusPolicy(Qt.NoFocus)
        volumeslider.valueChanged[int].connect(self.changeVolume)
        volumeslider.setValue(100)

        playBtn = QPushButton('Play')  # play button
        pauseBtn = QPushButton('Pause')  # pause button
        stopBtn = QPushButton('Stop')  # stop button

        # Add playlist controls
        prevBtn = QPushButton('Prev')
        shuffleBtn = QPushButton('Shuffle')
        nextBtn = QPushButton('Next')

        # Add button layouts
        #controlArea = QVBoxLayout()  # centralWidget
        controls = QHBoxLayout()
        playlistCtrlLayout = QHBoxLayout()

        # Add buttons to song controls layout
        controls.addWidget(playBtn)
        controls.addWidget(pauseBtn)
        controls.addWidget(stopBtn)

        # Add buttons to playlist controls layout
        playlistCtrlLayout.addWidget(prevBtn)
        playlistCtrlLayout.addWidget(shuffleBtn)
        playlistCtrlLayout.addWidget(nextBtn)

        # Add to vertical layout
        self.vlayout.addWidget(volumeslider)
        self.vlayout.addLayout(controls)
        self.vlayout.addLayout(playlistCtrlLayout)

        self.central.setLayout(self.vlayout)

        #self.central.setLayout(controlArea)

        self.setCentralWidget(self.central)

        # Connect each signal to their appropriate function
        playBtn.clicked.connect(self.playhandler)
        pauseBtn.clicked.connect(self.pausehandler)
        stopBtn.clicked.connect(self.stophandler)

        prevBtn.clicked.connect(self.prevSong)
        shuffleBtn.clicked.connect(self.shufflelist)
        nextBtn.clicked.connect(self.nextSong)

        self.statusBar()
        self.playlist.currentMediaChanged.connect(self.songChanged)

        self.mainMenu = self.menuBar()      # Menu bar
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        self.fileMenu = self.mainMenu.addMenu('&File')

        fileAct = QAction('Open File', self)
        folderAct = QAction('Open Folder', self)

        fileAct.setShortcut('Ctrl+O')
        folderAct.setShortcut('Ctrl+D')

        self.fileMenu.addAction(fileAct)
        self.fileMenu.addAction(folderAct)

        fileAct.triggered.connect(self.openFile)
        folderAct.triggered.connect(self.addFiles)

        self.fileMenu.addAction(exitAction)
        #self.addControls()

    # Start image capture & display
    def start(self):
        self.timer = QTimer(self)           # Timer to trigger display
        self.timer.timeout.connect(lambda:
                    self.show_image(image_queue, self.disp, DISP_SCALE))
        self.timer.start(DISP_MSEC)
        self.capture_thread = threading.Thread(target=grab_images,
                    args=(camera_num, image_queue))
        self.capture_thread.start()         # Thread to grab images

    # Fetch camera image from queue, and display it
    def show_image(self, imageq, display, scale):
        if not imageq.empty():
            image = imageq.get()
            if image is not None and len(image) > 0:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                self.display_image(img, display, scale)

    # Display an image, reduce size if required
    def display_image(self, img, display, scale=1):
        disp_size = img.shape[1]//scale, img.shape[0]//scale
        disp_bpl = disp_size[0] * 3
        if scale > 1:
            img = cv2.resize(img, disp_size,
                             interpolation=cv2.INTER_CUBIC)

            self.inference.perform_inference(img)
            if self.inference.network.wait() == 0 :
                result = self.inference.network.extract_output()
                pred = np.argmax(result[0, :])
                print(pred)
                self.handle_inference(  pred  )

        qimg = QImage(img.data, disp_size[0], disp_size[1],
                      disp_bpl, IMG_FORMAT)
        display.setImage(qimg)

    # Handle sys.stdout.write: update text display
    def write(self, text):
        self.text_update.emit(str(text))
    def flush(self):
        pass

    def check_song_is_playing(self):
        if  (datetime.now()  - self.current_song_start_time ).seconds >= 7:
            return False
        else:
            return True
    def handle_inference(self, result):
        result = 4
        if self.folder_chosen == True  and self.check_song_is_playing() == False:
            if result == 0:
                self.pausehandler()
                print('pause')
            elif result == 1:
                self.playhandler()
                print('play')
            elif result == 2:
                self.stophandler()
                print('stop')
            elif result == 3 :
                self.nextSong()
                print('next')
            elif result == 4 :
                self.prevSong()
                print('previous')
            elif result == 5 :
                print('nothing')

    # Append to text display
    def append_text(self, text):
        cur = self.textbox.textCursor()     # Move cursor to end of text
        cur.movePosition(QTextCursor.End)
        s = str(text)
        while s:
            head,sep,s = s.partition("\n")  # Split line at LF
            cur.insertText(head)            # Insert text at cursor
            if sep:                         # New line if LF
                cur.insertBlock()
        self.textbox.setTextCursor(cur)     # Update visible cursor

    # Window is closing: stop video capture
    def closeEvent(self, event):
        global capturing
        capturing = False
        self.capture_thread.join()

    def openFile(self):
        song = QFileDialog.getOpenFileName(self, "Open Song", "~", "Sound Files (*.mp3 *.ogg *.wav *.m4a)")
        if song[0] != '':
            url = QUrl.fromLocalFile(song[0])
            if self.playlist.mediaCount() == 0:
                self.playlist.addMedia(QMediaContent(url))
                self.player.setPlaylist(self.playlist)
                self.player.play()
                self.userAction = 1
            else:
                self.playlist.addMedia(QMediaContent(url))


    def addFiles(self):
        if self.playlist.mediaCount() != 0:
            self.folderIterator()
        else:
            self.folderIterator()
            self.player.setPlaylist(self.playlist)
            self.player.playlist().setCurrentIndex(0)
            self.player.play()
            self.userAction = 1

    def folderIterator(self):
        folderChosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', '~')
        if folderChosen != None:
            it = QDirIterator(folderChosen)
            it.next()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                        self.folder_chosen = True
                it.next()
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

            if it.fileInfo().isDir() == False and it.filePath() != '.':
                fInfo = it.fileInfo()
                if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                    self.folder_chosen = True



    def playhandler(self):
        if self.playlist.mediaCount() == 0:
            self.folder_chosen = False
            self.addFiles()
        elif self.playlist.mediaCount() != 0:
            self.player.play()
            self.current_song_start_time = datetime.now()

            self.userAction = 1


    def pausehandler(self):
        self.userAction = 2
        self.player.pause()

    def stophandler(self):
        self.folder_chosen = False
        self.userAction = 0
        self.player.stop()
        self.playlist.clear()
        self.statusBar().showMessage("Stopped and cleared playlist")

    def changeVolume(self, value):
        self.player.setVolume(value)

    def prevSong(self):
        if self.playlist.mediaCount() == 0:
            self.folder_chosen = False
            self.addFiles()
        elif self.playlist.mediaCount() != 0:
            print(self.playlist.currentIndex(), 'jjlkjlj')
            self.player.playlist().previous()
            self.current_song_start_time = datetime.now()

    def shufflelist(self):
        self.playlist.shuffle()


    def nextSong(self):
        if self.playlist.mediaCount() == 0:
            self.folder_chosen = False
            self.addFiles()

        elif self.playlist.mediaCount() != 0:
            self.player.playlist().next()
            self.current_song_start_time = datetime.now()

    def songChanged(self, media):
        if not media.isNull():
            url = media.canonicalUrl()
            self.statusBar().showMessage(url.fileName())

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            camera_num = int(sys.argv[1])
        except:
            camera_num = 0
    if camera_num < 1:
        print("Invalid camera number '%s'" % sys.argv[1])
    else:
        app = QApplication(sys.argv)
        win = MyWindow()
        win.show()
        win.setWindowTitle(VERSION)
        win.start()
        sys.exit(app.exec_())

#EOF
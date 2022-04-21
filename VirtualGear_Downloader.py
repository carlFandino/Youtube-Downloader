from PyQt5 import QtCore, QtGui, QtWidgets,uic
import threading,time,requests,pytube,sys,pyttsx3,ffmpeg,subprocess,os,ctypes
import webbrowser,random,math
import pafy

FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
millnames = ['', ' Thousand', ' Million', ' Billion', ' Trillion']
def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
    int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
def explore(path):
    # explorer would choke on forward slashes
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


ui = resource_path("youtube_vdownload_designer_beta_1.ui")
splashscreen = resource_path("splash_screen_beta_1.png")

def format_file_size(size, decimals=2, binary_system=True):
    if binary_system:
        units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB']
        largest_unit = 'YiB'
        step = 1024
    else:
        units = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
        largest_unit = 'YB'
        step = 1000
 
    for unit in units:
        if size < step:
            return ('%.' + str(decimals) + 'f %s') % (size, unit)
        size /= step
 
    return ('%.' + str(decimals) + 'f %s') % (size, largest_unit)

#Main Res: 551 321


   



class Youtube_Downloader(QtWidgets.QMainWindow):
	progress_changed = QtCore.pyqtSignal(int)
	def __init__(self):
		super(Youtube_Downloader ,self).__init__()
		uic.loadUi(ui,self)
		self.setSize(551,321)
		self.DOWN_WIDGETS = [self.Download_List,self.Download_Template]
		

		self.__video_formats__ = ["mp4"]
		self.__audio_formats__ = ["mp3"]

		
		self.downloading = False
		self.pauseResume = False
		self.openOneTime = 0
		self.FINAL_AVAILABLE_DOWNLOAD = []
		
		self.__path_to_save__ = ""
		self.__row_count = 0
		self.__downloading_dots = 0
		self.format_picked = ""

		self.Downloading_ConvertAgain.setVisible(False)
		self.Downloading_OpenFile.setVisible(False)
		self.Downloading_Frame.setVisible(False)
		self.Template.setVisible(False)
		self.Download_List.setVisible(False)
		self.Download_Template.setVisible(False)
		self.PutLink_Button.setVisible(False)
		def redirect():
			webbrowser.open("http:/google.com")

		self.ConverterButton.clicked.connect(self.__Convert__)
		self.File_Download_Button.clicked.connect(self.__download__)
		self.PutLink_Button.clicked.connect(lambda : self.Link_Text.setText("https://www.youtube.com/watch?v=oIjQ_hBiZxQ"))
		self.progress_changed.connect(self.Downloading_Indicator.setValue)
		self.Downloading_OpenFile.clicked.connect(self.__open_file__)
		self.Downloading_ConvertAgain.clicked.connect(self.__re_convert__)
		self.Downloading_PauseButton.clicked.connect(self.__pause_and_resume__)
		self.Ad_Image.clicked.connect(redirect)
		self.selected_final_download = ...




		self.__slide_ad__ = False
		self.__ad_visible_seconds__ = 5
		self.__ad_count__ = 0

		self.__ad_anim_1__ = QtCore.QPropertyAnimation(self.Ad_Image,b"pos")
		self.__ad_anim_1__.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
		self.__ad_anim_1__.setEndValue(QtCore.QPoint(360,10))
		self.__ad_anim_1__.setDuration(500)

		self.__ad_anim_2__ = QtCore.QPropertyAnimation(self.Ad_Image,b"pos")
		self.__ad_anim_2__.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
		self.__ad_anim_2__.setEndValue(QtCore.QPoint(10,10))
		self.__ad_anim_2__.setDuration(500)
		self.__ad_random_colors__ = ["red","white","skyblue","orange","violet","lime"]
		self.__ad_random_text__ = ["Ads","Your Ad Here","Ad Space"]



	def __pause_and_resume__(self):
		if self.pauseResume == False and self.downloading == True: #Pause
			self.Downloading_PauseButton.setIcon(QtGui.QIcon("pause.png"))

			
			self.pauseResume = True


		elif self.pauseResume == True and self.downloading == True: #Resume
			self.Downloading_PauseButton.setIcon(QtGui.QIcon("play.png"))
			
			self.pauseResume = False

		

	

	def __re_convert__(self):
		self.Downloading_PauseButton.setVisible(False)
		self.Downloading_Indicator.setValue(0)
		self.Downloading_Frame.setVisible(False)
		self.Template.setVisible(False)
		self.Home_Frame.setVisible(True)
		self.Link_Text.setText("")
		self.__path_to_save__ = ""
		
		for i in self.DOWN_WIDGETS:
			i.setVisible(False)

		self.setSize(551,321)

		


	def __refresher__(self):

		self.timer1 = QtCore.QTimer()
		self.timer1.timeout.connect(self.__refresher__)
		self.timer1.start(500)
		self.ConverterButton.setText(f"Convert To {self.Mode_Selector.currentText().capitalize()}")

		self.__ad_count__ += 0.5
		def __return_ad__():
			self.__ad_anim_2__.start()

		if self.Ad_Image.x() == 360:
			self.Ad_Image.setStyleSheet(f"background-color: {random.choice(self.__ad_random_colors__)};")
			self.Ad_Image.setText(f"{random.choice(self.__ad_random_text__)}")
		
		if self.__ad_count__ == self.__ad_visible_seconds__:

				
			self.__ad_anim_1__.start()
		elif self.__ad_count__ == 7:

			__return_ad__()
			self.__ad_count__ = 0






    #The selected download in QTableWidget.
	def selected_download(self):
		itag = self.Download_List.selectedItems()[3].text()
		for i in self.FINAL_AVAILABLE_DOWNLOAD:

			if i.itag == itag and self.Mode_Selector.currentText() != "mp3":
				self.File_Resolution.setText(f"Resolution: {str(i.quality).split('x')[1]+'p'}")
				self.File_Size.setText(f"File Size: {format_file_size(i.get_filesize(),2,False)}")
				self.File_Type.setText(f"Type: {i.mediatype}")
				self.selected_final_download = i
			elif i.itag == itag and self.Mode_Selector.currentText() == "mp3":
				self.File_Resolution.setText(f"Resolution: {str(i.quality)}")
				self.File_Size.setText(f"File Size: {format_file_size(i.get_filesize(),2,False)}")
				self.File_Type.setText(f"Type: audio")
				self.selected_final_download = i

				

	def setSize(self,y: int,x: int):
		self.resize(y,x)
		self.setFixedSize(y,x)


	def __Convert__(self):
		self.__refresher__()
		if self.Link_Text.text() == "":
			print("No link provided.")
		else:
			self.setSize(920,628)
			self.Template.setVisible(True)
			for i in self.DOWN_WIDGETS:
				i.setVisible(True)
		try:
			self.link = pafy.new(self.Link_Text.text(),basic=True)
			self.audio = pafy.new(self.Link_Text.text())
	
			#Setting Title,views,etc.
			self.Video_Title.setText(f"Title: {self.link.title}")
			self.Video_Views.setText(f"Views: {millify(self.link.viewcount)}")
			self.Video_Length.setText(f"Length: {self.link.length} secs")
			self.Video_Author.setText(f"Author: {self.link.author}")
			self.Video_Watch_URL.setText(f"Watch URL: {self.Link_Text.text()}")
		


			#self.Video_Published_Date.setText(f"Published Date: {self.link.published}")
			
			#If user wants to convert another video then clear the previous streams that came from recent convertion.
			self.Download_List.setRowCount(0)
			self.__row_count = 0
			self.FINAL_AVAILABLE_DOWNLOAD.clear()
	
			#Setting Image
			image = QtGui.QImage()
			image.loadFromData(requests.get(self.link.bigthumbhd).content)
			
			PixmapImage = QtGui.QPixmap(image)
			PixmapImage = PixmapImage.scaled(351,201)

			self.Video_Image.setPixmap(PixmapImage)

			if self.Mode_Selector.currentText() == "mp4":
				self.__get_all_selected_formats__(False,"mp4")
			elif self.Mode_Selector.currentText() == "mp4 (video only)":
				self.__get_all_selected_formats__(True,"mp4")
			elif self.Mode_Selector.currentText() == "mp3":
				self.__get_all_selected_formats__(False,"mp3")
	
		except:
			print("No link")

	def __get_all_selected_formats__(self,isVideoOnly,extension):
		self.Download_List.itemClicked.connect(self.selected_download)
		self.format_picked = extension

		for i in self.link.allstreams:
			if isVideoOnly == False and extension == "mp4":
				if i.extension == "mp4" and i.mediatype == "normal":
					self.__set_table_list__(str(i.quality).split("x")[1]+"p",format_file_size(i.get_filesize(),2,False),"video and audio",i.itag,i)

			elif isVideoOnly == True and extension == "mp4":
				if i.extension == "mp4" and i.mediatype == "video":
					self.__set_table_list__(str(i.quality).split("x")[1]+"p",format_file_size(i.get_filesize(),2,False),i.mediatype + " only",i.itag,i)

			#Convert Mp4 to Mp3
			elif isVideoOnly == False and extension == "mp3":
				if i.extension == "mp4" and i.mediatype == "normal":

					self.__set_table_list__(str(i.quality),format_file_size(i.get_filesize(),2,False),"audio",i.itag,i)






	def __set_table_list__(self,quality,size,mediatype,itag,itemDownloads):
		self.FINAL_AVAILABLE_DOWNLOAD.append(itemDownloads)
		self.__row_count += 1
		self.Download_List.setRowCount(self.__row_count)
		if self.Mode_Selector.currentText().split()[0] in self.__video_formats__:
		    self.Download_List.setItem(self.__row_count-1,0,QtWidgets.QTableWidgetItem(f"{quality}"))
		    self.Download_List.setItem(self.__row_count-1,1,QtWidgets.QTableWidgetItem(f"{size}"))
		    self.Download_List.setItem(self.__row_count-1,2,QtWidgets.QTableWidgetItem(f"{mediatype}"))
		    self.Download_List.setItem(self.__row_count-1,3,QtWidgets.QTableWidgetItem(f"{itag}"))

		elif self.Mode_Selector.currentText().split()[0] in self.__audio_formats__:
			self.Download_List.setItem(self.__row_count-1,0,QtWidgets.QTableWidgetItem(f"{quality}"))
			self.Download_List.setItem(self.__row_count-1,1,QtWidgets.QTableWidgetItem(f"{size}"))
			self.Download_List.setItem(self.__row_count-1,2,QtWidgets.QTableWidgetItem(f"{mediatype}"))
			self.Download_List.setItem(self.__row_count-1,3,QtWidgets.QTableWidgetItem(f"{itag}"))
		


	def __download__(self):
	
		def download(path,filename=self.link.title):
			if os.path.exists(f"{path}/{str(self.link.title).replace(' ','_')}.{self.format_picked}"):
				self.Downloading_Label1.setText("File name already exist.")
				self.Downloading_Indicator.setVisible(False)
				self.Downloading_Rate.setVisible(False)
				self.Downloading_PauseButton.setVisible(False)
				self.Downloading_OpenFile.setVisible(True)
				self.Downloading_ConvertAgain.setVisible(True)
				self.__path_to_save__ = path
				#raise Exception("File already exists.")

			else:
				self.Downloading_PauseButton.setIcon(QtGui.QIcon("play.png"))
				self.Downloading_ConvertAgain.setVisible(False)
				self.Downloading_OpenFile.setVisible(False)
				self.Downloading_PauseButton.setVisible(False)
				self.Downloading_Label1.setVisible(True)
				self.Downloading_Indicator.setVisible(True)
				self.downloading = False
				if self.Mode_Selector.currentText().split()[0] in self.__video_formats__:
					threading.Thread(target=self.selected_final_download.download,kwargs={"filepath":f"{path}/{str(self.link.title).replace(' ','_')}.{self.selected_final_download.extension}","callback":self.__progress_callback__,"quiet":True},daemon=True,name="Download").start()
				elif self.Mode_Selector.currentText().split()[0] in self.__audio_formats__:
					threading.Thread(target=self.selected_final_download.download,kwargs={"filepath":f"{path}/{str(self.link.title).replace(' ','_')}.{self.format_picked}","callback":self.__progress_callback__,"quiet":True},daemon=True,name="Download").start()

			
	
			
		if self.selected_final_download == None:
			print("PLEASE SELECT.")
		else:
			self.Home_Frame.setVisible(False)
			self.Downloading_Frame.setVisible(True)
			self.__path_to_save__ = QtWidgets.QFileDialog.getExistingDirectory(caption="Select where to save")
			download(self.__path_to_save__)

	def __download_done__(self):
		os.system("cls")

		self.Downloading_Label1.setText(" Download Complete! 👍")
		self.Downloading_ConvertAgain.setVisible(True)
		self.Downloading_OpenFile.setVisible(True)


	def __open_file__(self):
		explore(f"{self.__path_to_save__}/{str(self.link.title).replace(' ','_')}.{self.format_picked}")

	def __progress_callback__(self,total,recvd,ratio,rate,eta):

		val = int(ratio * 100)
		ratio *= 500
		self.downloading = True
		self.Downloading_Rate.setVisible(True)
		self.Downloading_Indicator.setVisible(True)
		self.progress_changed.emit(val)
		self.Downloading_Rate.setText(f"Rate: {'%.2f'%rate}KB/s. ETA : {eta} secs. Total: {format_file_size(recvd,2,False)}")
		self.__downloading_dots += 1


	
		if self.__downloading_dots == 1:
			self.Downloading_Label1.setText("Downloading.")
		elif self.__downloading_dots == 2:
			self.Downloading_Label1.setText("Downloading..")
		elif self.__downloading_dots == 3:
			self.Downloading_Label1.setText("Downloading...")
			self.__downloading_dots = 0
		if val == 100:
			self.downloading = False
			self.__download_done__()
			
splashscreen_on_off = True
if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	You_Tube = Youtube_Downloader()
	if splashscreen_on_off == True:
	    picture = QtGui.QPixmap(splashscreen)
	    splash = QtWidgets.QSplashScreen(picture)
	    splash.show()
	    app.processEvents()
	    QtCore.QTimer.singleShot(5000,You_Tube.show)
	    QtCore.QTimer.singleShot(5000,splash.close)
	else:
		You_Tube.show()

	sys.exit(app.exec_())
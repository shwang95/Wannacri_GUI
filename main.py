# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toolbox.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

#import PyQt5
import json
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox
from PyQt5.QtCore import QCoreApplication
from pathlib import Path ,PurePath
from sys import argv , exit
from wannacri_gui import Ui_Main_windows
from convert_option import convert_option
from convert_file import convert_video
from subprocess import Popen ,PIPE , STDOUT

class MyGui(QMainWindow,Ui_Main_windows):

    _translate = QCoreApplication.translate
    ffmpeg_path = Path.joinpath(Path.cwd(),"ffmpeg/ffmpeg.exe")
    ffprobe_path = Path.joinpath(Path.cwd(),"ffmpeg/ffprobe.exe")
    song_bit = 120000
    file_codec = ""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #check ffmpeg
        self.check_ffmpeg()
        #select VP9 by deaful
        self.radioButton_4.setChecked(True)
        self.radioButton_4.setEnabled(False)
        self.radioButton_5.setEnabled(False)
        #setting deaful val
        #crf
        self.spinBox.setValue(16)
        #volmue
        self.doubleSpinBox.setValue(60)
        #bright
        self.doubleSpinBox_2.setValue(100)
        self.toolButton.clicked.connect(self.input_file)
        self.toolButton_2.clicked.connect(self.output_path)
        #H264 warrning
        self.radioButton_5.toggled.connect(self.h264_warning)
        self.pushButton_2.clicked.connect(self.convert_check)
        self.pushButton.clicked.connect(self.GUI_exit)

    def check_ffmpeg(self):
        if Path(self.ffmpeg_path).exists():
            if Path(self.ffprobe_path).exists():
                self.label_9.setStyleSheet("color:#008800")
                self.label_9.setText(self._translate("Main_windows", "FFmpeg check OK!"))
            else:
                self.label_9.setStyleSheet("color:#FF0000")
                self.label_9.setText(self._translate("Main_windows", "Miss FFprobe.exe!"))
        else:
            self.label_9.setStyleSheet("color:#FF0000")
            self.label_9.setText(self._translate("Main_windows", "Miss FFmpeg.exe!"))
    
    def input_file(self):
        input_file_name = QFileDialog.getOpenFileName(self, 'select file......')
        print(input_file_name[0])
        self.lineEdit.setText(input_file_name[0])
        self.check_movie_encode()

    def check_movie_encode(self):
        input_path = self.lineEdit.text()
        if input_path != "":
            #get file info
            
            #old
            #file_info = os.popen(str(self.ffprobe_path) + " -loglevel " + "quiet " + str(input_path) + " -show_streams " + "-of " + "json")
            common_list = [str(self.ffprobe_path),"-loglevel","quiet",str(input_path),"-show_streams","-of","json"]
            p = Popen(common_list, shell=True, stdout=PIPE, stderr=PIPE)
            file_info = p.stdout
            self.radioButton_4.setEnabled(False)
            self.radioButton_5.setEnabled(False)
            self.pushButton_2.setEnabled(True)
            self.spinBox.setEnabled(True)
            self.doubleSpinBox.setEnabled(True)
            self.doubleSpinBox_2.setEnabled(True)
            #use ffprobe get file info
            try:
                with file_info as i:
                    get_info = json.load(i)
                self.file_codec = get_info["streams"][0]["codec_name"]
                self.label_7.setStyleSheet("color:#000000")
                #is video
                if get_info["streams"][0]["codec_type"] == "video":
                    self.radioButton_4.setEnabled(True)
                    self.radioButton_5.setEnabled(True)
                    #get audio bit
                    try:
                        audio_bit_val = int(get_info["streams"][1]["bit_rate"])
                        self.label_7.setText(self._translate("Main_windows", "Video：" + self.file_codec) + "  Audio：" + str(audio_bit_val/1000) + "kb/s")
                    except:
                        try:
                            if get_info["streams"][1]["codec_type"] == "audio":
                                audio_bit_val = 192000
                                self.label_7.setStyleSheet("color:#FF0000")
                                self.label_7.setText(self._translate("Main_windows", "Video：" + self.file_codec + "  Audio：Unknow, set 192kb/s"))
                            else:
                                self.label_7.setText(self._translate("Main_windows", "Video：" + self.file_codec))
                                #disable vol setting
                                self.doubleSpinBox.setEnabled(False)
                        except:
                            self.label_7.setText(self._translate("Main_windows", "Video：" + self.file_codec))
                            #disable vol setting
                            self.doubleSpinBox.setEnabled(False)
                #is audio
                elif get_info["streams"][0]["codec_type"] == "audio":
                    try:
                        #get audio bit
                        audio_bit_val = int(get_info["streams"][0]["bit_rate"])
                        self.label_7.setText(self._translate("Main_windows", "Audio：" + str(audio_bit_val/1000) + "kb/s"))
                    except:
                        audio_bit_val = 192000
                        self.label_7.setStyleSheet("color:#FF0000")
                        self.label_7.setText(self._translate("Main_windows", "Audio：Unknow, will use 192kb/s"))
                    self.spinBox.setEnabled(False)
                    self.doubleSpinBox_2.setEnabled(False)
                #is picture
                else:
                    self.label_7.setStyleSheet("color:#000000")
                    self.label_7.setText(self._translate("Main_windows", "this is a picture file!"))
                    self.pushButton_2.setEnabled(False)
                #set song bit
                if self.doubleSpinBox.isEnabled():
                    self.song_bit = audio_bit_val
            except:
                input_name = PurePath(input_path).parts[-1]
                #usm file
                if input_name.find(".usm") != -1:
                    self.label_7.setStyleSheet("color:#000000")
                    self.label_7.setText(self._translate("Main_windows", "USM File"))
                    #self.pushButton_2.setEnabled(False)
                else:
                    self.label_7.setStyleSheet("color:#FF0000")
                    self.label_7.setText(self._translate("Main_windows", "Unknow file Error!"))
                    self.pushButton_2.setEnabled(False)
                self.spinBox.setEnabled(False)
                self.doubleSpinBox.setEnabled(False)
                self.doubleSpinBox_2.setEnabled(False)

    def output_path(self):
        output_path_name = QFileDialog.getExistingDirectory(self, 'save as......')
        print(output_path_name)
        self.lineEdit_2.setText(output_path_name)

    def h264_warning(self):
            if self.radioButton_5.isChecked():
                really_use_h264_usm = QMessageBox.warning(self,"warning","In 2022.8.29\nLinux system doesn't support H264 USM\nare you sure convert to H264 USM?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
                if really_use_h264_usm == QMessageBox.Yes:
                    self.radioButton_5.setChecked(True)
                elif really_use_h264_usm == QMessageBox.No:
                    self.radioButton_4.setChecked(True)
    
    def GUI_exit(self):
        try:
            os.system("taskkill /f /im ffmpeg.exe")
            os.system("taskkill /f /im ffmpeg.exe")
            exit(0)
        except:
            exit(0)
    
    def convert_check(self):
        input_path = self.lineEdit.text()
        output_path = self.lineEdit_2.text()
        if input_path == "":
            QMessageBox.warning(self,"Input miss","please selece you want to convert file first!",QMessageBox.Yes)
        elif output_path == "":
            QMessageBox.warning(self,"output miss","please selece the path you want to save as!",QMessageBox.Yes)
        else:
            convert_video(MyUi).run()

import sys
app = QApplication(argv)
MyUi = MyGui()
#Nuitka use
os.chdir(sys.path[0])
#Pyinstaller use
#os.chdir(os.path.dirname(sys.executable))
MyUi.show()
print(MyUi.ffmpeg_path)
option_val = convert_option(MyUi)
option_val.run()
MyUi.check_movie_encode()
start_convert = option_val.outpath(argv)
if start_convert:
    print("convert......")
    convert_video(MyUi).run()
    exit(0)
exit(app.exec_())

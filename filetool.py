import sys
import os
import re
import json
# import wi  n32gui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import (QIcon,QKeySequence,QPixmap,QGuiApplication,QPainter,QColor,QTextCharFormat,QBrush,QTextCursor,QFont)
from PyQt5.QtCore import *
import ctypes
import time

print(__file__)
config = {}
workdir = os.path.dirname(os.path.abspath(__file__))
configfile = workdir+"\\config.json"
if os.path.exists(configfile):
    with open(configfile) as f:
         config = json.loads(f.read())
else:
    config["path"] = ""


class Filetool(QWidget):
    def __init__(self):
        super().__init__()
        gb = QGroupBox("文件合并")
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("输入:"))
        self.inputedit = QLineEdit()        
        hbox.addWidget(self.inputedit)
        # self.selectfilebtn = QPushButton("选择文件")  #先不做了
        # self.selectfilebtn.clicked.connect(self.selectfile)
        # hbox.addWidget(self.selectfilebtn)        
        self.selectfolderbtn = QPushButton("选择文件夹")
        self.selectfolderbtn.clicked.connect(self.selectfolder)
        hbox.addWidget(self.selectfolderbtn)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("输出目录:"))
        self.selectfolderbtn2 = QPushButton("选择文件夹")
        self.selectfolderbtn2.clicked.connect(self.selectfolder2)
        self.outputedit = QLineEdit()        
        hbox2.addWidget(self.outputedit)        
        hbox2.addWidget(self.selectfolderbtn2)        
        
        hbox3 = QHBoxLayout()
        hbox3.addWidget(QLabel("文件名:"))
        self.filenameedit = QLineEdit()        
        hbox3.addWidget(self.filenameedit)        
        
        
        self.startbtn = QPushButton("开始合并")
        self.startbtn.clicked.connect(self.startcombine)
        self.openfolderbtn = QPushButton("打开文件夹")
        self.openfolderbtn.clicked.connect(self.openfolder)
        
        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.startbtn)
        hbox4.addWidget(self.openfolderbtn)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        gb.setLayout(vbox)
        
        vbox2 = QVBoxLayout()
        vbox2.addWidget(gb)
        self.tips = QLabel()
        vbox2.addWidget(self.tips)
        self.setLayout(vbox2)
        
        screen = QGuiApplication.primaryScreen()
        rect = screen.geometry()
        x = rect.center().x()-150
        y = rect.center().y()-150

        self.setGeometry(x,y, 500, 120)
        self.setWindowTitle('文件小工具')
        self.show()

    def selectfile(self):
        path = QFileDialog.getOpenFileName(self, "打开文件", ".", "视频文件(*.m3u8)")
        print(path)
        self.inputedit.setText(path[0])
        config["path"] = path[0]
    def selectfolder(self):
        if config["path"] != "":
            curpath = config["path"]
        else:
            curpath = "."
        path = QFileDialog.getExistingDirectory(self, "打开文件夹", curpath)
        print(path)
        if path != "":
            self.inputedit.setText(path)
            self.outputedit.setText(os.path.abspath(path+"\\.."))
            self.filenameedit.setText("文件.mp4")
            config["path"] = path
        
    def selectfolder2(self):
        path = QFileDialog.getExistingDirectory(self, "打开文件夹", ".")
        print(path)
        if path != "":
            self.outputedit.setText(path)
        
    def openfolder(self):
        filename = self.outputedit.text() + "\\" + self.filenameedit.text()
        if os.path.exists(filename):
            cmd = "start explorer /select," + filename
        else:
            # cmd = "start explorer /select,"+self.outputedit.text()
            cmd = "start explorer " + self.outputedit.text()
        print(cmd)
        os.system(cmd)
        
    def startcombine(self):
        inputpath = self.inputedit.text()
        filename = self.filenameedit.text()
        if filename == "":
            filename = "文件.mp4"
            self.filenameedit.setText(filename)
        filepath = self.outputedit.text() + "\\" + filename
        if os.path.exists(filepath):
            QMessageBox.warning(self,"警告","输出文件已存在,请重新指定文件名")
            return
        if os.path.isdir(inputpath):
            files = os.listdir(inputpath)
            print(files)
            def cmpkey(value):
                file = os.path.splitext(value)[0]
                m = re.match(".*?(\d+)$",file)
                if m:
                    v = m.group(1)
                    return int(v)
                else:
                    return 999999999 #其他文件，不应该放在里面
            files.sort(key=cmpkey)
            print(files)

            with open("file.txt","w") as f:
                for file in files:
                    ext = os.path.splitext(file)[1]
                    if ext == ".m3u8" or ext == ".txt":
                        continue
                    tmppath = os.path.realpath(inputpath+"\\"+file)
                    # print(tmppath)
                    f.write("file "+"'"+tmppath+"'\n")

            cmd = f'{workdir}\\ffmpeg.exe -f concat -safe 0 -i {workdir}\\file.txt -c copy {filepath}'
            print(cmd)
            self.tips.setText("开始合并...")
            res = os.system(cmd)
            print("done")                    
            if res == 0:
                QMessageBox.information(self,"提示","合并完成")    
                self.tips.setText("合并完成")
            else:
                QMessageBox.warning(self,"警告","出错,合并未完成")    
                self.tips.setText("出错,合并未完成")


            
    def closeEvent(self,e):
        print("exit")
        self.saveconfig()
        
    def saveconfig(self):
        with open(configfile,"w") as f:
            f.write(json.dumps(config,indent=4))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Filetool()
    sys.exit(app.exec_())
#!/home/puff/App/miniconda3/envs/py310/bin/python
# -*- coding: utf-8 -*-

'''
Date: 2018-07-20
Author: Lin Gang
Email: gang868@gmail.com
Description: Tomato alarm clock
Version: 1.1
'''

import datetime
import os
import sys

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLCDNumber,
    QLabel,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

f = os.path.abspath(__file__)
if os.path.islink(f):
    path = os.readlink(f)
else:
    path = f
BASE_DIR = os.path.dirname(path)


class Tomato(QWidget):
    def __init__(self):
        super().__init__()
        self.work = 25  # 番茄钟时间25分钟
        self.seconds = 60
        self.second_remain = self.work * self.seconds
        self.round = 0
        self.rest = 5  # 休息时间5分钟
        self.round_rest = 30  # 1轮4个番茄钟休息30分钟
        self.current_status = "Work"
        self.show_clock = False
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint  # 窗体总在最前端
            | Qt.FramelessWindowHint
        )
        self.setWindowTitle("Tomato Clock")
        self.setGeometry(0, 0, 350, 250)
        # self.move(2140, 25)
        # 设置番茄图标（程序和托盘）
        self.icon = QIcon(os.path.join(BASE_DIR, 'tomato.svg'))
        self.setWindowIcon(self.icon)
        # 设置托盘功能（显示计时、还原窗体和退出程序）
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray_menu = QMenu()
        self.restoreAction = QAction('Show', self, triggered=self.show)
        self.quitAction = QAction('Quit', self, triggered=app.quit)

        self.tipAction = QAction(
            "%s/%d > %2d:%02d"
            % (
                self.current_status,
                self.round + 1,
                self.second_remain // 60,
                self.second_remain % 60,
            ),
            self,
            triggered=self.show,
        )
        self.tray_menu.addAction(self.tipAction)
        self.tray_menu.addAction(self.restoreAction)
        self.tray_menu.addAction(self.quitAction)
        self.tray.setContextMenu(self.tray_menu)
        # 设置定时器
        self.timer = QTimer()  # 初始化计时器
        self.timer.setInterval(1000)  # 每秒跳1次
        self.timer.timeout.connect(self.onTimer)  # 绑定定时触发事件

        vbox = QVBoxLayout()
        # 提示标签
        self.labelRound = QLabel(self)  # 提示标签
        self.labelRound.setText("Ready")
        self.labelRound.setFixedHeight(50)
        self.labelRound.setAlignment(Qt.AlignCenter)
        self.pe = QPalette()
        self.pe.setColor(QPalette.Window, Qt.darkRed)  # 蓝底白字
        self.pe.setColor(QPalette.WindowText, Qt.white)
        self.labelRound.setAutoFillBackground(True)
        self.labelRound.setPalette(self.pe)
        self.labelRound.setFont(QFont("Courier", 20))

        vbox.addWidget(self.labelRound)
        # 倒计时显示器
        self.clock = QLCDNumber(self)  # 剩余时间显示组件
        self.clock.display(
            "%2d:%02d" % (self.second_remain // 60, self.second_remain % 60)
        )

        vbox.addWidget(self.clock)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        # 功能按钮
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.start)
        hbox.addWidget(self.startButton)

        self.stopButton = QPushButton("Stop")
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stop)
        hbox.addWidget(self.stopButton)

        self.switchButton = QPushButton("Clock")
        self.switchButton.clicked.connect(self.switch_clock)
        hbox.addWidget(self.switchButton)

        self.setLayout(vbox)

        self.tray.show()
        self.show()

    def closeEvent(self, event):
        # 禁止关闭按钮退出程序
        event.ignore()
        # 点击关闭按钮即隐藏主窗体
        self.hide()

    def onTimer(self):
        if self.show_clock:
            self.onTimerClock()
        else:
            self.onTimerWork()

    def onTimerClock(self):
        self.clock.display(datetime.datetime.now().strftime('%H:%M:%S'))

    def onTimerWork(self):
        # 工作状态
        self.second_remain -= 1
        if self.second_remain < 0:
            self.timer.stop()
            if self.current_status == "Work":
                self.current_status = "Rest"
                if (self.round + 1) % 4 == 0:
                    self.second_remain = self.round_rest * self.seconds
                else:
                    self.second_remain = self.rest * self.seconds
            else:
                self.current_status = "Work"
                self.second_remain = self.work * self.seconds
                self.round += 1

            self.timer.start()

        if self.current_status == 'Work':
            self.pe.setColor(QPalette.Window, Qt.darkRed)
        else:
            self.pe.setColor(QPalette.Window, Qt.darkGreen)
        self.labelRound.setPalette(self.pe)
        self.labelRound.setText(
            "Round {0}-{1}".format(self.round + 1, self.current_status)
        )

        self.clock.display(
            "%2d:%02d" % (self.second_remain // 60, self.second_remain % 60)
        )
        self.tipAction.setText(
            "%s/%d > %2d:%02d"
            % (
                self.current_status,
                self.round + 1,
                self.second_remain // 60,
                self.second_remain % 60,
            )
        )

    def start(self):
        # 启动定时器
        if not self.timer.isActive():
            self.timer.start()
        # 设置功能按钮
        # self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.startButton.setText('Pause')
        self.startButton.clicked.disconnect(self.start)
        self.startButton.clicked.connect(self.pause)
        self.onTimerWork()

    def stop(self):
        self.round = 0
        self.second_remain = self.work * self.seconds
        self.current_status = 'Work'
        self.clock.display(
            "%2d:%02d" % (self.second_remain // 60, self.second_remain % 60)
        )
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.timer.stop()

    def pause(self):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.timer.stop()
        self.startButton.setText('Start')
        self.startButton.clicked.disconnect(self.pause)
        self.startButton.clicked.connect(self.start)

    def switch_clock(self):
        if not self.show_clock:  # switch -> clock
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.switchButton.setText('Tomato')
            self.timer.start()
            self.show_clock = True
            self.pe.setColor(QPalette.Window, Qt.darkGreen)
            self.labelRound.setPalette(self.pe)
            self.labelRound.setText('CLOCK')
            self.clock.setDigitCount(8)
            self.clock.display(datetime.datetime.now().strftime('%H:%M:%S'))
        else:
            self.timer.stop()
            self.show_clock = False
            self.switchButton.setText('Clock')
            self.labelRound.setText("TOMATO")
            self.clock.setDigitCount(5)
            self.clock.display(
                "%2d:%02d" % (self.second_remain // 60, self.second_remain % 60)
            )
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.timer.stop()
            self.startButton.setText('Start')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tomato = Tomato()
    sys.exit(app.exec())

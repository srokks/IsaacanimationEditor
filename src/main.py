import math
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import *
from anmParser import AnimatedActor
from pathlib import Path

from animationList import AnimationListWidget
from animationTimeline import AnimationTimeline
from spritesheetList import SpritesheetsList




def window():
	app = QApplication(sys.argv)
	file: AnimatedActor = AnimatedActor(
		'/Users/srokks/PycharmProjects/animationEditor/resources/static/blank_my.anm2')
	widget = QWidget()
	main_lay = QHBoxLayout(widget)
	list_lay = QVBoxLayout()
	list_lay.addWidget(SpritesheetsList(file))
	list_lay.addWidget(AnimationListWidget(file))
	main_lay.addLayout(list_lay)
	main_lay.addWidget(AnimationTimeline())
	widget.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	file: AnimatedActor = AnimatedActor(
		'/Users/srokks/PycharmProjects/animationEditor/resources/static/blank_my.anm2')
	window()

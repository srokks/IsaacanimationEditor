import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt,QStringListModel
from anmParser import AnimatedActor
from designer_widgets.main_window import Ui_MainWindow
from designer_widgets.animList import Ui_animationList
from designer_widgets.spritesheet_edit import Ui_sprite_editor

class SpriteEdit(QtWidgets.QWidget, Ui_sprite_editor):
	def __init__(self):
		super(SpriteEdit, self).__init__()
		self.setupUi(self)

class AnimList(QtWidgets.QWidget, Ui_animationList):
	def __init__(self,list):
		super(AnimList, self).__init__()
		self.setupUi(self)
		self.mod = QStringListModel()
		self.mod .setStringList(list)
		self.listView.setModel(self.mod )


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self,file_path=None):
		super(MainWindow,self).__init__()
		self.setupUi(self)
		self.file_path = file_path
		self.file = AnimatedActor(file_path)
		self.actionOpen.triggered.connect(self.file_open_on_click)
		# print(self.file.path,self.file.get_animation_list())
		self.anim_list = AnimList(self.file.get_animation_list())
		self.main_mdi.addSubWindow(self.anim_list)
	def file_open_on_click(self):
		path = QFileDialog.getOpenFileName(self, 'Open a file', '../resources/static',
		                                   'ANM2 Files (*.anm2)')
		if path != ('', ''):
			self.file_path = path[0]
			self.file = None
			self.file = AnimatedActor(self.file_path)
			self.anim_list.mod.setStringList(self.file.get_animation_list())
		
if __name__ == '__main__':
	from ui_files.convert_all import convert
	convert()
	app = QtWidgets.QApplication(sys.argv)
	path = None
	if "-f" in sys.argv[1:]:
		path = sys.argv[sys.argv.index("-f") + 1]
	window = MainWindow(path)
	window.show()
	app.exec_()

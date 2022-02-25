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


class SpritesheetsModel(QAbstractListModel):
	def __init__(self, file: AnimatedActor):
		super(QAbstractListModel, self).__init__()
		self.file = file

	def rowCount(self, parent=None, *args, **kwargs):
		return len(self.file.spritesheets)

	def data(self, QModelIndex, role=None):
		row = QModelIndex.row()
		if role == Qt.DisplayRole:
			return f'{row}-{self.file.spritesheets[row]}'
		if role == Qt.DecorationRole:
			path = str(file.path.parent.joinpath(Path(self.file.spritesheets[row])))
			pixmap = QPixmap()
			if not pixmap.load(path):  # creates black pixmap if no image file
				pixmap = QPixmap(64, 64)
				pixmap.fill(Qt.black)
			return pixmap.scaledToWidth(64)


class SpritesheetsList(QWidget):
	def __init__(self, file):
		super(QWidget, self).__init__()
		self.file: AnimatedActor = file
		#
		main_lay = QVBoxLayout(self)
		main_lay.setSpacing(0)
		main_lay.setContentsMargins(0, 0, 0, 0)
		main_lay.addWidget(QLabel('Spritesheet list'))
		#
		self.list_view = QListView()
		spritesheet_model = SpritesheetsModel(self.file)
		self.list_view.setModel(spritesheet_model)
		self.list_view.selectionModel().selectionChanged.connect(
			self.selection_changed)
		main_lay.addWidget(self.list_view)
		#
		action_layout = QGridLayout()
		#
		add_btn = QPushButton('Add')
		add_btn.clicked.connect(self.add_clicked)
		#
		save_btn = QPushButton('Save')
		save_btn.clicked.connect(self.on_save)
		#
		remove_unused = QPushButton('Remove unused')
		remove_unused.clicked.connect(self.on_remove_unused)
		#
		self.replace_btn = QPushButton('Replace')
		self.replace_btn.setDisabled(True)
		self.replace_btn.clicked.connect(self.on_replace)
		#
		action_layout.addWidget(add_btn, 0, 0)
		action_layout.addWidget(self.replace_btn, 0, 1)
		action_layout.addWidget(remove_unused, 1, 0)
		action_layout.addWidget(save_btn, 1, 1)
		main_lay.addLayout(action_layout)

	def add_clicked(self):
		path = Path(
			QFileDialog.getOpenFileName(
				self, 'Open a file', str(self.file.path.parent),
				'Png files (*.png)')[0])
		if path.is_file():
			rel_path = '/'.join(path.parts[len(self.file.path.parent.parts):])
			self.file.add_spritesheet(rel_path)
			self.list_view.model().layoutChanged.emit()

	def on_save(self):
		self.file.save_file(self.file.path)

	def on_remove_unused(self):
		self.file.remove_unused_spritesheets()
		self.list_view.model().layoutChanged.emit()

	def on_replace(self):
		path = Path(
			QFileDialog.getOpenFileName(
				self, 'Open a file', str(self.file.path.parent),
				'Png files (*.png)')[0])
		if path.is_file():
			rel_path = '/'.join(path.parts[len(self.file.path.parent.parts):])
			selected_index = self.list_view.selectedIndexes()[0].row()
			self.file.replace_spritesheet(selected_index, rel_path)

	def selection_changed(self):
		if len(self.list_view.selectedIndexes()) > 0:
			self.replace_btn.setDisabled(False)
		else:
			self.replace_btn.setDisabled(True)


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

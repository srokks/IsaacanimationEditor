import math
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import *
from anmParser import AnimatedActor
from pathlib import Path


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


class AnimationModel(QAbstractListModel):
	def __init__(self, file: AnimatedActor):
		super(QAbstractListModel, self).__init__()
		self.animation_list = file.get_animation_list()
		self.file = file

	def rowCount(self, parent=None, *args, **kwargs):
		return len(self.animation_list)

	def data(self, QModelIndex, role=None):
		row = QModelIndex.row()
		if role == Qt.DisplayRole:
			return self.animation_list[row]
		if role == Qt.FontRole:
			if self.animation_list[row] == self.file.default_animation:
				font = QFont()
				font.setBold(13)
				return QVariant(font)


class AnimationListWidget(QWidget):
	def __init__(self, file):
		super(QWidget, self).__init__()
		self.file: AnimatedActor = file
		#
		self.list_view = QListView()
		animation_model = AnimationModel(file)
		self.list_view.setModel(animation_model)
		#
		set_default_btn = QPushButton('Default')
		set_default_btn.clicked.connect(self.on_set_default)
		#
		add_btn = QPushButton('Add')
		add_btn.clicked.connect(self.on_add)
		#
		main_lay = QVBoxLayout(self)
		main_lay.setSpacing(0)
		main_lay.setContentsMargins(0, 0, 0, 0)
		main_lay.addWidget(QPushButton('Animation List'))
		main_lay.addWidget(self.list_view)
		action_layout = QGridLayout()
		action_layout.addWidget(add_btn, 0, 0)
		action_layout.addWidget(QPushButton('Duplicate'), 0, 1)
		action_layout.addWidget(QPushButton('Merge'), 1, 0)
		action_layout.addWidget(QPushButton('Remove'), 1, 1)
		action_layout.addWidget(set_default_btn, 2, 0, 1, 2)
		main_lay.addLayout(action_layout)

	def on_set_default(self):
		sel_index = self.list_view.selectedIndexes()
		if len(sel_index) > 0:
			self.file.set_default_animation(sel_index[0].data())
		self.list_view.model().layoutChanged.emit()

	def on_add(self):
		self.list_view.model().anim_list.append('New animation')
		self.list_view.model().layoutChanged.emit()
		row = self.list_view.model().rowCount()-1
		self.list_view.edit(self.list_view.model().index(row))

class MyTimeline(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		self.setWindowTitle("AnimationLine")
		self.setMouseTracking(True)
		self.current_frame = 0
		lay = QHBoxLayout()
		lay.setAlignment(Qt.AlignLeft)

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setPen(QColor(187, 187, 187))
		qp.setFont(QFont('Times', 8))
		qp.setRenderHint(QPainter.Antialiasing)

		# Draw dash lines
		point = 0
		# qp.drawLine(15,0,15,10)
		# qp.drawLine(15,20,15,30)
		# qp.drawLine(30, 0, 30, 10)
		# qp.drawLine(30, 20, 30, 30)
		# qp.drawRect(0,0,15,30)
		qp.fillRect(0, 0, self.width(), 30, Qt.gray)
		#
		qp.setPen(Qt.black)
		while point <= self.width():
			if (int(point / 10) % 5 == 0) or point == 0:
				qp.fillRect(point, 0, 10, 30, Qt.darkGray)
				qp.drawText(point, 0, 10, 30, Qt.AlignCenter, str(int(point / 10)))
			qp.drawLine(point, 0, point, 10)
			qp.drawLine(point, 20, point, 30)
			point += 10
		qp.drawLine(0, 30, self.width(), 30)
		#
		path = QPainterPath(QPoint(1 + (10 * self.current_frame), 1))
		path.lineTo(QPoint(9 + (10 * self.current_frame), 1))
		path.lineTo(QPoint(9 + (10 * self.current_frame), 10))
		path.lineTo(QPoint(5 + (10 * self.current_frame), 30))
		path.lineTo(QPoint(1 + (10 * self.current_frame), 10))
		line = QLine(
			QPoint(5 + (10 * self.current_frame), 0),
			QPoint(5 + (10 * self.current_frame), self.height()))
		qp.setPen(Qt.darkCyan)
		qp.setBrush(QBrush(Qt.darkCyan))
		# qp.fillRect(1,1,8,15,Qt.darkCyan)
		# qp.fillPath(path,Qt.darkCyan)
		qp.drawPath(path)
		qp.drawLine(line)

	def mousePressEvent(self, e):
		if e.button() == Qt.LeftButton:
			self.current_frame = math.floor(e.pos().x() / 10)
			self.update()


def window():
	app = QApplication(sys.argv)
	file: AnimatedActor = AnimatedActor(
		'/Users/srokks/PycharmProjects/animationEditor/resources/static/blank_my.anm2')
	widget = QWidget()
	lay = QVBoxLayout(widget)
	lay.addWidget(SpritesheetsList(file))
	lay.addWidget(AnimationListWidget(file))
	widget.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	file: AnimatedActor = AnimatedActor(
		'/Users/srokks/PycharmProjects/animationEditor/resources/static/blank_my.anm2')
	window()

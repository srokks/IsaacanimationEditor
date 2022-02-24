import math
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import *
from anmParser import AnimatedActor
from pathlib import Path


class testModel(QAbstractListModel):
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
			pixmap = QPixmap(path)
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
		list_view = QListView()
		self.spritesheet_model = testModel(self.file)
		list_view.setModel(self.spritesheet_model)
		main_lay.addWidget(list_view)
		#
		action_layout = QGridLayout()
		#
		add_btn = QPushButton('Add')
		add_btn.clicked.connect(self.add_clicked)
		#
		save_btn = QPushButton('Save')
		save_btn.clicked.connect(self.on_save)
		#
		action_layout.addWidget(add_btn, 0, 0)
		action_layout.addWidget(QPushButton('Replace'), 0, 1)
		action_layout.addWidget(QPushButton('Select all'), 1, 0)
		action_layout.addWidget(QPushButton('Select none'), 1, 1)
		action_layout.addWidget(QPushButton('Remove unused'), 2, 0)
		action_layout.addWidget(save_btn, 2,1)
		action_layout.setColumnStretch(0, 1)
		action_layout.setColumnStretch(1, 1)
		action_layout.setRowStretch(1, 2)
		main_lay.addLayout(action_layout)

	def add_clicked(self):
		path = Path(
			QFileDialog.getOpenFileName(
				self, 'Open a file', str(self.file.path.parent),
				'Png files (*.png)')[0])
		rel_path = '/'.join(path.parts[len(self.file.path.parent.parts):])
		self.file.add_spritesheet(rel_path)
		self.spritesheet_model.layoutChanged.emit()

	def on_save(self):
		self.file.save_file(self.file.path)

	def on_reload(self):
		self.spritesheet_model.layoutChanged.emit()

class AnimationListWidget(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		main_lay = QVBoxLayout(self)
		main_lay.setSpacing(0)
		main_lay.setContentsMargins(0, 0, 0, 0)
		main_lay.addWidget(QPushButton('Animation List'))
		main_lay.addWidget(QListView())
		action_layout = QGridLayout()
		action_layout.addWidget(QPushButton('Add'), 0, 0)
		action_layout.addWidget(QPushButton('Duplicate'), 0, 1)
		action_layout.addWidget(QPushButton('Merge'), 1, 0)
		action_layout.addWidget(QPushButton('Remove'), 1, 1)
		action_layout.addWidget(QPushButton('Default'), 2, 0, 1, 2)
		main_lay.addLayout(action_layout)


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
	lay.addWidget(AnimationListWidget())
	widget.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	file: AnimatedActor = AnimatedActor(
		'/Users/srokks/PycharmProjects/animationEditor/resources/static/blank_my.anm2')
	window()

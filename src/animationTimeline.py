from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QPoint, QLine, QAbstractTableModel, QSize, pyqtSignal, \
	pyqtSlot, QAbstractListModel, QModelIndex, QRect
import math
from anmParser import *
from spritesheetList import SpritesheetsModel

visible_image = QImage()
visible_image.load("../resources/-visibility_90186.png")


class AddLayerDialog(QDialog):
	def __init__(self):
		super(AddLayerDialog, self).__init__()

		self.setWindowTitle('Layer properties')
		main_lay = QGridLayout()
		main_lay.addWidget(QLabel('Layer name:'), 0, 0)
		main_lay.addWidget(QLineEdit(), 0, 1)
		main_lay.addWidget(QLabel('Spritesheet:'), 1, 0)
		combo = QComboBox()
		mdoel = SpritesheetsModel()
		# combo.setModel()
		main_lay.addWidget(QLineEdit(), 1, 1)
		self.setLayout(main_lay)


class AnimTime(QWidget):
	def __init__(self, file: AnimatedActor, animation_name: str):
		super(AnimTime, self).__init__()
		self.animation = file.get_animation(animation_name)
		self.setMaximumHeight(200)
		main_lay = QVBoxLayout(self)
		main_lay.setSpacing(0)
		main_lay.setContentsMargins(0, 0, 0, 0)
		#
		layer_list_view = QListView()
		model = LayerModel(animation)
		delegate = LayerDelegate()
		layer_list_view.setItemDelegate(delegate)
		layer_list_view.setFixedWidth(150)
		layer_list_view.setModel(model)
		#
		add_btn = QPushButton('Add')
		add_btn.clicked.connect(self.add_btn)
		#
		action__lay = QHBoxLayout()
		action__lay.setContentsMargins(0, 0, 0, 0)
		action__lay.setSpacing(0)
		action__lay.addWidget(add_btn)
		action__lay.addWidget(QPushButton('Remove'))
		#
		main_lay.addWidget(layer_list_view)
		main_lay.addLayout(action__lay)

	def add_btn(self):
		dialog = AddLayerDialog()
		a = dialog.exec_()
		print(a)


class LayerModel(QAbstractListModel):

	def __init__(self, animation: Animation):
		super(QAbstractListModel, self).__init__()
		self.animation = animation
		self.layer_list = animation.get_layer_list()

	def flags(self, index: QModelIndex) -> Qt.ItemFlag:
		return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable

	def rowCount(self, parent: QModelIndex = None) -> int:
		return len(self.layer_list)

	def data(self, index: QModelIndex, role: int = None):
		row = index.row()
		if role == Qt.DisplayRole:
			return self.layer_list[row][1]
		elif role == Qt.SizeHintRole:
			return QSize(120, 30)
		elif role == Qt.UserRole:
			vis = True
			if index.data() != 'Root':
				vis = self.layer_list[row][2]
			return vis

	def setData(self, index: QModelIndex, value, role: int = None) -> bool:
		if role == Qt.UserRole:
			self.animation.change_visibility(index.row() - 1)
			self.update_model()
		return False

	def update_model(self):
		self.layer_list = self.animation.get_layer_list()


class LayerDelegate(QItemDelegate):
	def __init__(self):
		super(QItemDelegate, self).__init__()

	def createEditor(self, parent, option, index):
		return None

	def editorEvent(self, event, model, option, index: QModelIndex):
		if event.type() == 3:
			if event.pos().x() > 120:
				model.setData(index, None, Qt.UserRole)
				return True
		return False

	def paint(self, painter, option, index):
		painter.save()
		# set background color
		painter.setPen(QPen(Qt.NoPen))  # sets not border
		grad = QLinearGradient(
			option.rect.x(), option.rect.y(), option.rect.x(), option.rect.y() + 15)
		if option.state & QStyle.State_Selected:  # sets color if selected
			grad.setColorAt(0, QColor(128, 49, 36))
		else:  # sets color if unselected
			grad.setColorAt(0, QColor(255, 164, 148))
		grad.setColorAt(1, QColor(255, 99, 71))  # main color
		painter.setBrush(grad)
		painter.drawRoundedRect(option.rect, 10, 10)
		#
		visible = index.data(Qt.UserRole)
		# Visible layer trigger draw
		if visible:  # draws eye image as visible layer
			painter.drawImage(
				QRect(option.rect.width() - 30, option.rect.y(), 25, 30),
				visible_image)
		else:  # draws ellipse as hidden layer
			painter.setPen(Qt.lightGray)
			vis_rect = QRect(option.rect.width() - 22, option.rect.y() + 10, 10, 10)
			painter.drawEllipse(vis_rect)
		# set text color
		painter.setPen(QPen(Qt.black))
		rect = QRect(
			option.rect.x(), option.rect.y(), option.rect.width() - 30,
			option.rect.height())
		text = index.data(Qt.DisplayRole)
		painter.drawText(option.rect, Qt.AlignCenter, text)
		painter.restore()


class Frame(QPushButton):
	selected_frame = pyqtSignal(int)

	def __init__(self, pos, name, parent=None):
		super(QPushButton, self).__init__(parent=parent)
		self.setGeometry(pos[0], pos[1], 10, 30)
		selflayer_color = QColor(Qt.red)
		self.clicked = False
		self.name = name

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setPen(QColor(255, 165, 0))
		qp.drawRect(0, 0, self.width(), self.height())
		if self.clicked:
			qp.fillRect(1, 1, self.width() - 2, self.height() - 2, QColor(255, 140, 0))
		else:
			qp.fillRect(1, 1, self.width() - 2, self.height() - 2, QColor(255, 165, 0))
		qp.setPen(Qt.black)
		qp.setBrush(Qt.black)
		qp.drawEllipse(QPoint(5, 15), 2, 2)

	def mousePressEvent(self, e):
		self.selected_frame.emit(self.name)
		self.check_clicked()

	def check_clicked(self):
		self.clicked = True if self.selected_frame == self.name else False
		self.repaint()


class AnimationTimeline(QWidget):

	def __init__(self):
		super(QWidget, self).__init__()
		self.setWindowTitle("AnimationLine")
		self.setMouseTracking(True)
		self.current_frame = 0
		self.setMinimumSize(300, 150)
		self.setMaximumHeight(200)
		layer_frames = [Frame((0 + i * 10, 30), i, self) for i in range(10)]

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setPen(QColor(187, 187, 187))
		qp.setFont(QFont('Times', 8))
		qp.setRenderHint(QPainter.Antialiasing)

		# Draw dash lines
		point = 0
		qp.fillRect(0, 0, self.width(), 30, Qt.gray)
		#
		while point <= self.width():
			qp.setPen(Qt.black)
			if (int(point / 10) % 5 == 0) or point == 0:
				qp.fillRect(point, 0, 10, 30, Qt.darkGray)
				qp.fillRect(point, 30, 10, self.height(), QColor(220, 220, 220))
				qp.drawText(point, 0, 10, 30, Qt.AlignCenter, str(int(point / 10)))
			qp.drawLine(point, 0, point, 10)
			qp.drawLine(point, 20, point, 30)
			# Draws vertical grid
			qp.setPen(QColor(220, 220, 220))
			qp.drawLine(point, 30, point, self.width())
			#
			point += 10
		# draw
		qp.setPen(Qt.black)
		qp.drawLine(0, 30, self.width(), 30)
		# draws horizontal grid
		# Draws vertical grid
		qp.setPen(QColor(220, 220, 220))
		for i in range(1, 5):
			qp.drawLine(0, 30 + i * 30, self.width(), 30 + i * 30)
		# draw pointer
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

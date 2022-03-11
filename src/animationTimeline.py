from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QPoint, QLine, QAbstractTableModel, QSize, pyqtSignal, \
	pyqtSlot
import math

visible_image = QImage()
visible_image.load("../resources/-visibility_90186.png")

class Test2(QWidget):
	"""
	Widget with layer buttons, UGLY
	"""
	a = pyqtSlot(bool)
	selected_layer = None

	def __init__(self, animation=None):
		super(TimelineWi, self).__init__()
		self.setMaximumHeight(150)
		main_lay = QVBoxLayout(self)
		main_lay.setContentsMargins(1, 1, 1, 1)
		main_lay.setSpacing(0)
		btns = []
		for layer in animation.get_layer_list():
			btns.append(LayerButton(layer))
			btns[-1].layer_visible.connect(self.on_change_visibility)
			btns[-1].select.connect(self.on_selection_change)
		for btn in btns:
			main_lay.addWidget(btn)

	def on_change_visibility(self, btn: LayerButton):
		print(btn.text)
		pass

	def on_selection_change(self, btn: LayerButton):
		if self.selected_layer is not None:
			self.selected_layer.setEnabled(False)
		self.selected_layer = btn
		self.selected_layer.setEnabled(True)

class LayerButton(QWidget):
	layer_visible = pyqtSignal(object)
	select = pyqtSignal(object)

	def __init__(self, layer, parent=None):
		super(LayerButton, self).__init__(parent)
		self.setContentsMargins(0, 0, 0, 0)
		self.setFixedSize(QSize(150, 30))
		self.clicked = False
		self.text = layer[1]
		self.triggered = layer[2]

	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		qp.setPen(Qt.red)
		grad = QLinearGradient(0, 0, 0, 15)
		if self.clicked:
			grad.setColorAt(0, QColor(204, 83, 62))
		else:
			grad.setColorAt(0, QColor(255, 100, 80))
		grad.setColorAt(1, QColor(255, 99, 71))

		qp.setBrush(grad)
		rect = QRect(0, 0, self.width(), self.height())
		qp.drawRoundedRect(rect, 10, 10)
		#
		if self.triggered:
			qp.drawImage(QRect(self.width() - 30, 0, 25, 30), visible_image)
		else:
			qp.setPen(Qt.lightGray)
			vis_rect = QRect(self.width() - 22, 10, 10, 10)
			qp.drawEllipse(vis_rect)
		#
		qp.setPen(Qt.black)
		qp.drawText(QRect(0, 0, self.width() - 20, 30), Qt.AlignCenter, self.text)

	def mousePressEvent(self, event: QMouseEvent):
		if event.pos().x() > self.width() - 30:
			self.triggered = False if self.triggered else True
			self.layer_visible.emit(self)
		else:
			self.select.emit(self)
		self.repaint()

	def setEnabled(self, a0: bool) -> None:
		self.clicked = a0
		self.repaint()


class TimelineView(QTableView):
	def __init__(self, parent):
		super(QTableView, self).__init__(parent=parent)
		self.setGridStyle(Qt.DashDotLine)


# def paintEvent(self, event):
# 	pass


class TimeLineModel(QAbstractTableModel):
	def __init__(self):
		super(QAbstractTableModel, self).__init__()

	def columnCount(self, parent=None, *args, **kwargs):
		return 2

	def rowCount(self, parent=None, *args, **kwargs):
		return 4

	def data(self, QModelIndex, role=None):
		row, col = QModelIndex.row(), QModelIndex.column()
		if role == Qt.DisplayRole:
			return '*'
		if role == Qt.SizeHintRole:
			print('s')
			return QSize(4, 4)


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


# self.clicked = False if self.clicked else True


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

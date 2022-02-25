from PyQt5.QtWidgets import QWidget, QHBoxLayout,QTableView
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath,QBrush
from PyQt5.QtCore import Qt, QPoint,QLine
import math

class AnimationTimeline(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		self.setWindowTitle("AnimationLine")
		self.setMouseTracking(True)
		self.current_frame = 0
		lay = QHBoxLayout()
		lay.setAlignment(Qt.AlignLeft)
		self.setMinimumSize(300, 150)
		self.setMaximumHeight(200)
		table_view = QTableView(self)
		table_view.setGeometry(0,30,self.width(),self.height())
		self.repaint()


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

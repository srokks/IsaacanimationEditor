from PyQt5.QtCore import QAbstractListModel,QVariant
from PyQt5.QtWidgets import QWidget, QListView, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.Qt import Qt
from PyQt5.QtGui import QFont
from anmParser import AnimatedActor


class AnimationModel(QAbstractListModel):
	def __init__(self, file: AnimatedActor):
		super(QAbstractListModel, self).__init__()
		self.file = file
		self.anim_list = file.get_animation_list()

	def rowCount(self, parent=None, *args, **kwargs):
		return len(self.anim_list)

	def data(self, QModelIndex, role=None):
		row = QModelIndex.row()
		if role == Qt.DisplayRole:
			return self.anim_list[row]
		if role == Qt.FontRole:
			if self.anim_list[row] == self.file.default_animation:
				font = QFont()
				font.setBold(13)
				return QVariant(font)
		if role == Qt.EditRole:
			return self.anim_list[row]

	def flags(self, index):
		return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

	def setData(self, index, value, role):
		if role == Qt.EditRole:
			# gets animation object from file and change name
			temp_anim = self.file.get_animation(
				self.anim_list[index.row()])
			if temp_anim:
				if temp_anim.name == value:
					print('error')
				temp_anim.name = value
			else:
				self.file.add_animation(value)
			self.update_model()
			self.file.save_file()
			return True

	def update_model(self):
		self.anim_list = self.file.get_animation_list()


class AnimationListWidget(QWidget):
	def __init__(self, file):
		super(QWidget, self).__init__()
		self.file: AnimatedActor = file
		#
		self.list_view = QListView()
		animation_model = AnimationModel(file)
		self.list_view.setModel(animation_model)
		self.list_view.selectionModel().selectionChanged.connect(
			self.selection_changed)
		#
		set_default_btn = QPushButton('Default')
		set_default_btn.clicked.connect(self.on_set_default)
		#
		add_btn = QPushButton('Add')
		add_btn.clicked.connect(self.on_add)
		#
		self.duplicate_btn = QPushButton('Duplicate')
		self.duplicate_btn.setDisabled(True)
		self.duplicate_btn.clicked.connect(self.on_duplicate)
		#
		main_lay = QVBoxLayout(self)
		main_lay.setSpacing(0)
		main_lay.setContentsMargins(0, 0, 0, 0)
		main_lay.addWidget(QPushButton('Animation List'))
		main_lay.addWidget(self.list_view)
		action_layout = QGridLayout()
		action_layout.addWidget(add_btn, 0, 0)
		action_layout.addWidget(self.duplicate_btn, 0, 1)
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
		row = self.list_view.model().rowCount() - 1
		self.list_view.edit(self.list_view.model().index(row))

	def selection_changed(self):
		if len(self.list_view.selectedIndexes()) > 0:
			self.duplicate_btn.setDisabled(False)
		else:
			self.duplicate_btn.setDisabled(True)

	def on_duplicate(self):
		duplicate_anim = self.list_view.selectedIndexes()[0]
		print(self.file.duplicate_animation(duplicate_anim.data()))
		self.list_view.model().update_model()
		self.list_view.model().layoutChanged.emit()
		row = self.list_view.model().rowCount() - 1
		self.list_view.edit(self.list_view.model().index(row))

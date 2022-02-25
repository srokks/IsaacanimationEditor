from lxml import etree, objectify
import dateutil.parser as parser
from datetime import datetime as dt
from pathlib import Path
import copy


class Frame:
	pos_x: int = 0
	pos_y: int = 0
	delay: int = 1
	visible: bool = True
	scale_x: int = 100
	scale_y: int = 100
	tint_red: int = 255
	tint_green: int = 255
	tint_blue: int = 255
	tint_alpha: int = 255
	offset_red: int = 0
	offset_green: int = 0
	offset_blue: int = 0
	rotation: int = 0
	interpolated: bool = False
	# Layer frame specials vars
	pivot_x: int
	pivot_y: int
	width: int
	height: int
	crop_x: int
	crop_y: int

	def __init__(self, frame_tree: etree = None, root=False):
		if frame_tree is not None:
			self.pos_x = int(frame_tree.attrib.get('XPosition'))
			self.pos_y = int(frame_tree.attrib.get('YPosition'))
			self.delay = int(frame_tree.attrib.get('Delay'))
			self.visible = bool(frame_tree.attrib.get('Visible'))
			self.scale_x = int(frame_tree.attrib.get('XScale'))
			self.scale_y = int(frame_tree.attrib.get('YScale'))
			self.tint_red = int(frame_tree.attrib.get('RedTint'))
			self.tint_green = int(frame_tree.attrib.get('GreenTint'))
			self.tint_blue = int(frame_tree.attrib.get('BlueTint'))
			self.tint_alpha = int(frame_tree.attrib.get('AlphaTint'))
			self.offset_red = int(frame_tree.attrib.get('RedOffset'))
			self.offset_green = int(frame_tree.attrib.get('GreenOffset'))
			self.offset_blue = int(frame_tree.attrib.get('BlueOffset'))
			self.rotation = int(frame_tree.attrib.get('Rotation'))
			self.interpolated = bool(frame_tree.attrib.get('Interpolated'))
			# Layer frame specials vars
			if frame_tree.attrib.get('XPivot') is not None:
				self.pivot_x = int(frame_tree.attrib.get('XPivot'))
			if frame_tree.attrib.get('YPivot') is not None:
				self.pivot_y = int(frame_tree.attrib.get('YPivot'))
			if frame_tree.attrib.get('Width') is not None:
				self.width = int(frame_tree.attrib.get('Width'))
			if frame_tree.attrib.get('Height') is not None:
				self.height = int(frame_tree.attrib.get('Height'))
			if frame_tree.attrib.get('XCrop') is not None:
				self.crop_x = int(frame_tree.attrib.get('XCrop'))
			if frame_tree.attrib.get('YCrop') is not None:
				self.crop_y = int(frame_tree.attrib.get('YCrop'))
		else:
			self.pos_x = 0
			self.pos_y = 0
			self.delay = 1
			self.visible = True
			self.scale_x = 100
			self.scale_y = 100
			self.t_red = 255
			self.t_green = 255
			self.t_blue = 255
			self.t_alpha = 255
			self.offset_red = 0
			self.offset_green = 0
			self.offset_blue = 0
			self.rotation = 0
			self.interpolated = False
			# Layer frame specials vars
			if not root:
				self.pivot_x = 0
				self.pivot_y = 0
				self.width = 32
				self.height = 32
				self.crop_x = 0
				self.crop_y = 0


class LayerAnimation:
	def __init__(self, layer_tree: etree = None, layer_id=None, visible: bool = None):
		layer_id: int
		visible: bool
		frames: list
		if layer_tree is None:
			self.layer_id = layer_id
			self.visible = True if visible is None else visible
			self.frames = []
		else:
			self.layer_id = int(layer_tree.attrib.get('LayerId'))
			self.visible = bool(layer_tree.attrib.get('Visible'))
			self.frames = []
			for frame in layer_tree:
				self.frames.append(Frame(frame))


class Animation:
	"""
	trata
	"""

	name: str
	frame_num: int
	loop: bool
	root_animation: list
	layer_animations: list

	def __init__(self, animation_tree: etree = None, name: str = None, ):
		if animation_tree is not None:
			self.name = animation_tree.attrib.get('Name')
			self.frame_num = animation_tree.attrib.get('FrameNum')
			self.loop = animation_tree.attrib.get('Loop')
			self.root_animation = []
			self.layer_animations = []
			for child in animation_tree:
				# ___
				if child.tag == 'RootAnimation':
					for frame in child:
						self.root_animation.append(Frame(frame_tree=frame))
				# ___
				if child.tag == 'LayerAnimations':
					for layer_animation in child:
						self.layer_animations.append(LayerAnimation(layer_animation))
				# ___
				if child.tag == 'NullAnimations':
					# TODO: NullAnimations load
					pass
				# ___
				if child.tag == 'Triggers':
					# TODO: Triggers load
					pass
		else:
			self.name = name
			self.root_animation = [Frame()]
			self.layer_animations = []
			self.frame_num = 1
			self.loop = False


class Layer:
	def __init__(
			self, layer_tree: etree = None, name=None, layer_id=None,
			spritesheet_id=None):
		name: str
		layer_id: int
		spritesheet_id: int
		if layer_tree is None:
			self.name = name
			self.id = layer_id
			self.spritesheet_id = spritesheet_id
		else:
			self.name = layer_tree.get('Name')
			self.id = layer_tree.get('Id')
			self.spritesheet_id = int(layer_tree.get('SpritesheetId'))

	def __str__(self):
		return f'Name: {self.name}|layer_id: {self.id}|spritesheet_id:' \
		       f'{self.spritesheet_id}'


class AnimatedActor:
	def __init__(self, anm_path=None):
		self.created_by: str = 'SrokksAnimEdit'
		self.created_date: 'datetime' = dt.now()
		self.version: int = 1
		self.fps: int = 30
		self.spritesheets: dict = {}
		self.layers: dict = {}
		self.nulls: dict = {}
		self.events: dict = {}
		self.animations: list = []
		self.default_animation: str = ""
		self.path = Path(anm_path)
		if self.path is not None:
			with open(self.path, 'r') as f:
				anm_str = f.read()
			animated_actor = etree.fromstring(anm_str)
			info = animated_actor[0]
			content = animated_actor[1]
			animations = animated_actor[2]
			self.created_by = info.attrib['CreatedBy']
			self.created_date = parser.parse(info.attrib['CreatedOn'])
			self.version = info.attrib['Version']
			self.fps = animated_actor[0].attrib['Fps']
			# _____ Content read
			for child in content:
				# _____ Spritesheet
				if child.tag == 'Spritesheets':
					for sheet in child:
						self.spritesheets.update(
							{int(sheet.get('Id')): sheet.get('Path')})
				# _____ Layers
				if child.tag == 'Layers':
					for layer in child:
						temp_layer = Layer(layer_tree=layer)
						self.layers.update({temp_layer.id: temp_layer})
				# _____ Nulls
				if child.tag == 'Nulls':
					# TODO: nulls load
					pass
				# _____ Events
				if child.tag == 'Events':
					# TODO: event load
					pass
			# _____ Animations read
			self.default_animation = animations.attrib.get('DefaultAnimation')
			for animation in animations:
				self.animations.append(Animation(animation_tree=animation))

	def save_file(self, path=None):
		if path is None:
			path = self.path
		root = etree.Element("AnimatedActor")
		info = etree.SubElement(
			root, 'Info', CreatedBy=self.created_by,
			CreatedOn=self.created_date.strftime(
				'%d/%m/%Y %H:%M:%S'),
			Version=str(self.version), Fps=str(self.fps))
		# _____
		content = etree.SubElement(root, 'Content')
		# _____ Sheets
		spritesheets = etree.SubElement(content, 'Spritesheets')
		for sheet_id, sheet_path in self.spritesheets.items():
			etree.SubElement(
				spritesheets, 'Spritesheet', Id=f'{sheet_id}',
				Path=sheet_path)
		# _____ Layers
		layers = etree.SubElement(content, 'Layers')
		for layer in self.layers.values():
			etree.SubElement(
				layers, 'Layer', Id=str(layer.id), Name=layer.name,
				SpritesheetId=str(layer.spritesheet_id))
		# _____ NULLS
		nulls = etree.SubElement(content, 'Nulls')
		# TODO: nulls save
		# _____ Events
		events = etree.SubElement(content, 'Events')
		# TODO: events save
		# _____
		animations = etree.SubElement(
			root, 'Animations',
			DefaultAnimation=self.default_animation)
		for animation in self.animations:
			anim = etree.SubElement(
				animations, 'Animation', Name=animation.name,
				FrameNum=f'{animation.frame_num}',
				Loop=f'{animation.loop}')
			root_anim = etree.SubElement(anim, 'RootAnimation')
			for frame in animation.root_animation:
				etree.SubElement(
					root_anim, 'Frame', XPosition=f'{frame.pos_x}',
					YPosition=f'{frame.pos_y}',
					Delay=f'{frame.delay}', Visible=f'{frame.visible}',
					XScale=f'{frame.scale_x}',
					YScale=f'{frame.scale_y}', RedTint=f'{frame.tint_red}',
					GreenTint=f'{frame.tint_green}',
					BlueTint=f'{frame.tint_blue}',
					AlphaTint=f'{frame.tint_alpha}',
					RedOffset=f'{frame.offset_red}',
					GreenOffset=f'{frame.offset_green}',
					BlueOffset=f'{frame.offset_blue}',
					Rotation=f'{frame.rotation}',
					Interpolated=f'{frame.interpolated}')
			layers_anim = etree.SubElement(anim, 'LayerAnimations')
			for layer_anim in animation.layer_animations:
				layer = etree.SubElement(
					layers_anim, 'LayerAnimation',
					LayerId=f'{layer_anim.layer_id}',
					Visible=f'{layer_anim.visible}')
				for frame in layer_anim.frames:
					etree.SubElement(
						layer, 'Frame', XPosition=f'{frame.pos_x}',
						YPosition=f'{frame.pos_y}',
						Delay=f'{frame.delay}', Visible=f'{frame.visible}',
						XScale=f'{frame.scale_x}',
						YScale=f'{frame.scale_y}',
						RedTint=f'{frame.tint_red}',
						GreenTint=f'{frame.tint_green}',
						BlueTint=f'{frame.tint_blue}',
						AlphaTint=f'{frame.tint_alpha}',
						RedOffset=f'{frame.offset_red}',
						GreenOffset=f'{frame.offset_green}',
						BlueOffset=f'{frame.offset_blue}',
						Rotation=f'{frame.rotation}',
						Interpolated=f'{frame.interpolated}',
						XPivot=f'{frame.pivot_x}',
						YPivot=f'{frame.pivot_y}', Width=f'{frame.width}',
						Height=f'{frame.height}',
						XCrop=f'{frame.crop_x}', YCrop=f'{frame.crop_y}')
		# _____
		with open(path, 'wb') as f:
			etree.indent(root, space='\t')  # sets indents to tabs
			anm_str = etree.tostring(root, pretty_print=False)
			f.write(anm_str)

	def get_animation_list(self):
		return [anim.name for anim in self.animations]

	def add_spritesheet(self, path: str):
		index = len(self.spritesheets)
		self.spritesheets.update({index: path})
		return index

	def add_animation(self, name):
		self.animations.append(Animation(name=name))
		for layer in self.layers.values():
			self.animations[-1].layer_animations.append(
				LayerAnimation(
					layer_id=layer.id))
		if len(self.animations) == 1:
			self.default_animation = name

	def add_layer(self, name: str, spritesheet_id: int):
		layer_id = len(self.layers)
		self.layers.update(
			{layer_id: Layer(
				name=name, layer_id=layer_id,
				spritesheet_id=spritesheet_id)})
		for anim in self.animations:
			anim.layer_animations.append(LayerAnimation(layer_id=layer_id))

	def add_frame(self, animation_name, layer_id):
		test: LayerAnimation
		for anim in self.animations:
			if anim.name == animation_name:
				for layer_anim in anim.layer_animations:
					if layer_anim.layer_id == layer_id:
						layer_anim.frames.append(Frame())

	def get_layer_by_sprite_id(self, sprite_id):
		for key, layer in self.layers.items():
			if layer.spritesheet_id == sprite_id:
				return self.layers[key]

	def remove_unused_spritesheets(self):
		used_spritesheets = set(layer.spritesheet_id for layer in self.layers.values())
		old_sprites = {key: self.spritesheets[key] for key in used_spritesheets}
		self.spritesheets = {}
		for key, path in old_sprites.items():
			new_index = self.add_spritesheet(path)
			self.get_layer_by_sprite_id(key).spritesheet_id = new_index
		self.save_file(self.path)

	def replace_spritesheet(self, spritesheet_id, path: str):
		self.spritesheets[spritesheet_id] = path

	def set_default_animation(self, name):
		if name in self.get_animation_list():
			self.default_animation = name

	def get_animation(self, name):
		for anim in self.animations:
			if anim.name == name:
				return anim
		else:
			return False

	def duplicate_animation(self, name):
		if name in self.get_animation_list():
			temp_anim = copy.copy(self.get_animation(name))
			self.animations.append(temp_anim)
			self.animations[-1].name = self.animations[-1].name + ' copy'
			return True
		else:
			return False

	def remove_animation(self, name):
		index = self.animations.index(self.get_animation(name))
		self.animations.pop(index)


if __name__ == '__main__':
	anm_path_ = '/Users/srokks/PycharmProjects/animationEditor/resources/static' \
	            '/002_the inner eye.anm2'
	save = '/Users/srokks/PycharmProjects/animationEditor/resources/static/blank_my' \
	       '.anm2'
	file = AnimatedActor(save)
	file.created_by = 'Srokks'
	file.duplicate_animation('Second')
	print(file.get_animation_list())
	file.remove_animation('Second copy')
	print(file.get_animation_list())
	file.save_file()
'''
animation:path
'''

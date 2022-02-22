from lxml import etree, objectify
import dateutil.parser as parser
from datetime import datetime as dt


class Frame:
	def __init__(self, frame, root_anim=False):
		self.pos_x = int(frame.attrib.get('XPosition'))
		self.pos_y = int(frame.attrib.get('YPosition'))
		self.delay = int(frame.attrib.get('Delay'))
		self.visible = bool(frame.attrib.get('Visible'))
		self.scale_x = int(frame.attrib.get('XScale'))
		self.scale_y = int(frame.attrib.get('YScale'))
		self.tint_red = int(frame.attrib.get('RedTint'))
		self.tint_green = int(frame.attrib.get('GreenTint'))
		self.tint_blue = int(frame.attrib.get('BlueTint'))
		self.tint_alpha = int(frame.attrib.get('AlphaTint'))
		self.offset_red = int(frame.attrib.get('RedOffset'))
		self.offset_green = int(frame.attrib.get('GreenOffset'))
		self.offset_blue = int(frame.attrib.get('BlueOffset'))
		self.rotation = int(frame.attrib.get('Rotation'))
		self.interpolated = bool(frame.attrib.get('Interpolated'))
		if not root_anim:
			self.pivot_x = int(frame.attrib.get('XPivot'))
			self.pivot_y = int(frame.attrib.get('YPivot'))
			self.width = int(frame.attrib.get('Width'))
			self.height = int(frame.attrib.get('Height'))
			self.crop_x = int(frame.attrib.get('XCrop'))
			self.crop_y = int(frame.attrib.get('YCrop'))


class LayerAnimation:
	def __init__(self, layer_animation):
		self.layer_id = int(layer_animation.attrib.get('LayerId'))
		self.visible = bool(layer_animation.attrib.get('Visible'))
		self.frames = []
		for frame in layer_animation:
			self.frames.append(Frame(frame))


class Animation:
	def __init__(self, animation):
		print(type(animation))
		self.name = animation.attrib.get('Name')
		self.frame_num = animation.attrib.get('FrameNum')
		self.loop = animation.attrib.get('Loop')
		self.root_animation = []
		self.layer_animations = []
		for child in animation:
			# ___
			if child.tag == 'RootAnimation':
				for frame in child:
					self.root_animation.append(Frame(frame, True))
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


class Layer:
	def __init__(self, layer):
		self.name = layer.get('Name')
		self.id = layer.get('Id')
		self.spritesheet_id = layer.get('SpritesheetId')


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
		self.path = anm_path
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
						temp_layer = Layer(layer)
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
				self.animations.append(Animation(animation))
	
	def save_file(self, path):
		root = etree.Element("AnimatedActor")
		info = etree.SubElement(root, 'Info', CreatedBy=self.created_by,
		                        CreatedOn=self.created_date.strftime(
			                        '%d/%m/%Y %H:%M:%S'),
		                        Version=str(self.version), Fps=str(self.fps))
		# _____
		content = etree.SubElement(root, 'Content')
		# _____ Sheets
		spritesheets = etree.SubElement(content, 'Spritesheets')
		for sheet_id, sheet_path in self.spritesheets.items():
			etree.SubElement(spritesheets, 'Spritesheet', Id=f'{sheet_id}',
			                 Path=sheet_path)
		# _____ Layers
		layers = etree.SubElement(content, 'Layers')
		for layer in self.layers.values():
			etree.SubElement(layers, 'Layer', Id=layer.id, Name=layer.name,
			                 SpritesheetId=layer.spritesheet_id)
		# _____ NULLS
		nulls = etree.SubElement(content, 'Nulls')
		# TODO: nulls save
		# _____ Events
		events = etree.SubElement(content, 'Events')
		# TODO: events save
		# _____
		animations = etree.SubElement(root, 'Animations',
		                              DefaultAnimation=self.default_animation)
		for animation in self.animations:
			anim = etree.SubElement(animations, 'Animation', Name=animation.name,
			                        FrameNum=f'{animation.frame_num}',
			                        Loop=f'{animation.loop}')
			root_anim = etree.SubElement(anim, 'RootAnimation')
			for frame in animation.root_animation:
				etree.SubElement(root_anim, 'Frame', XPosition=f'{frame.pos_x}',
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
				layer = etree.SubElement(layers_anim, 'LayerAnimation',
				                         LayerId=f'{layer_anim.layer_id}',
				                         Visible=f'{layer_anim.visible}')
				for frame in layer_anim.frames:
					etree.SubElement(layer, 'Frame', XPosition=f'{frame.pos_x}',
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
	
	def add_spritesheet(self, path):
		self.spritesheets.update({len(self.spritesheets): path})
		
	def add_animation(self,name):
		pass
	
if __name__ == '__main__':
	anm_path_ = '/Users/srokks/PycharmProjects/animationEditor/resources/static/002_the inner eye.anm2'
	save = '/Users/srokks/PycharmProjects/animationEditor/resources/static/blank_my' \
	       '.anm2'
	file = AnimatedActor(anm_path_)
	file.created_by = 'Srokks'
	file.save_file(save)
'''
animation:path
'''

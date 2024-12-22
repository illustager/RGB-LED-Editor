from ui.mainwindow_ui import Ui_MainWindow
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow

from qfluentwidgets import ColorDialog, FluentIcon, PushButton

import json
from copy import deepcopy

# 将动画转换为 C++ 代码
from convertor import actionsConvert

# 设置按钮颜色
def setPushButtonColor(button: PushButton, color: QColor) -> None:
	button.setStyleSheet(
		button.styleSheet() +
		f'background-color: {color.name()};'
		f'color: {"#FFFFFF" if color.lightness() < 128 else "#000000"};'
	)

class MainWindow(Ui_MainWindow):
	# ==================== 初始化 ====================
	def __init__(self, window: QMainWindow):
		# -------------------- 成员变量 --------------------
		# 常量
		self.defaultColor = QColor('#FFFFFF')
		
		self.defaultSolidAction = {
			'type': 'Solid',
			'colors': [QColor(self.defaultColor) for _ in range(56)],
			'lengthy': 50,
		}
		self.defaultFadingAction = {
			'type': 'Fading',
			'colors': [QColor(self.defaultColor) for _ in range(56)],
			'section': [0, 100, 5],
			'interval': 1,
		}
		self.defaultCycleAction = {
			'type': 'Cycle',
			'colors': [QColor(self.defaultColor) for _ in range(56)],
			'interval': 2,
			'times': 56,
			'isUp': True
		}
		self.defaultFloatingAction = {
			'type': 'Floating',
			'colors': [QColor(self.defaultColor) for _ in range(56)],
			'interval': 2,
			'isUp': True,
		}
		self.defaultGrowingAction = {
			'type': 'Growing',
			'colors': [QColor(self.defaultColor) for _ in range(56)],
			'interval': 1,
			'isUp': True,
		}
		# 变量
		self.painterColor = QColor(self.defaultColor)
		
		self.actions = []
		self.actionIndex = -1 # 当前操作的页面索引，亦即当前的动画索引

		# -------------------- 设置 UI --------------------
		self.setupUi(window)

		# -------------------- 事件绑定 --------------------
		# 导入导出 JSON
		self.menuImport.triggered.connect(self.onImportTriggered)
		self.menuExport.triggered.connect(self.onExportTriggered)
		# 颜色选择
		self.colorButton.clicked.connect(self.onColorButtonClicked)
		self.fillButton.clicked.connect(self.onColorFillButtonClicked)
		self.clearButton.clicked.connect(self.onColorClearButtonClicked)
		# 结果复制
		self.resultButton.clicked.connect(self.onResultButtonClicked)
		# 像素着色
		for i, p in enumerate(self.pixels):
			p.mousePressEvent = lambda _, p=p, i=i: self.onPixelColorChanged(p, i)

	def setupUi(self, window: QMainWindow) -> None:
		super().setupUi(window) # 依照 UI 设计文件设置 UI

		# -------------------- 成员变量 --------------------
		# 像素点
		self.pixels_1 = [
			self.p1_01, self.p1_02, self.p1_03, self.p1_04, self.p1_05, self.p1_06, self.p1_07, self.p1_08,
			self.p1_09, self.p1_10, self.p1_11, self.p1_12, self.p1_13, self.p1_14, self.p1_15, self.p1_16,
			self.p1_17, self.p1_18, self.p1_19, self.p1_20, self.p1_21, self.p1_22, self.p1_23, self.p1_24,
			self.p1_25, self.p1_26, self.p1_27, self.p1_28, self.p1_29, self.p1_30, self.p1_31, self.p1_32,
			self.p1_33, self.p1_34, self.p1_35, self.p1_36, self.p1_37, self.p1_38, self.p1_39, self.p1_40,
			self.p1_41, self.p1_42, self.p1_43, self.p1_44, self.p1_45, self.p1_46, self.p1_47, self.p1_48,
			self.p1_49, self.p1_50, self.p1_51, self.p1_52, self.p1_53, self.p1_54, self.p1_55, self.p1_56
		]
		self.pixels_2 = [
			self.p2_01, self.p2_02, self.p2_03, self.p2_04, self.p2_05, self.p2_06, self.p2_07, self.p2_08,
			self.p2_09, self.p2_10, self.p2_11, self.p2_12, self.p2_13, self.p2_14, self.p2_15, self.p2_16,
			self.p2_17, self.p2_18, self.p2_19, self.p2_20, self.p2_21, self.p2_22, self.p2_23, self.p2_24,
			self.p2_25, self.p2_26, self.p2_27, self.p2_28, self.p2_29, self.p2_30, self.p2_31, self.p2_32,
			self.p2_33, self.p2_34, self.p2_35, self.p2_36, self.p2_37, self.p2_38, self.p2_39, self.p2_40,
			self.p2_41, self.p2_42, self.p2_43, self.p2_44, self.p2_45, self.p2_46, self.p2_47, self.p2_48,
			self.p2_49, self.p2_50, self.p2_51, self.p2_52, self.p2_53, self.p2_54, self.p2_55, self.p2_56
		]
		self.pixels = self.pixels_1 # 仅使用组 1 的像素点
		# -------------------- 设置 UI --------------------
		# 设置窗口属性
		window.setFixedSize(window.size())
		window.setWindowTitle('RGB Editor')
		window.setWindowIcon(FluentIcon.PALETTE.icon())
		# 按钮颜色
		setPushButtonColor(self.colorButton, self.defaultColor)
		# 属性设置 UI
		self.spinBox_colorH.setMaximum(359)
		self.spinBox_colorH.setMinimum(-359)
		self.spinBox_colorH.setValue(0)
		self.spinBox_colorS.setMaximum(255)
		self.spinBox_colorS.setMinimum(-255)
		self.spinBox_colorS.setValue(0)
		self.spinBox_colorV.setMaximum(255)
		self.spinBox_colorV.setMinimum(-255)
		self.spinBox_colorV.setValue(0)

	# ==================== 方法 ====================
	# 获取动画结果，将 QColor 转换为对应字符串
	def actionsOutcome(self) -> list:
		actionsRes = deepcopy(self.actions)

		for i in range(len(actionsRes)):
			actionsRes[i]['colors'] = [c.name() for c in self.actions[i]['colors']]
		
		return actionsRes
	# 画笔颜色渐变
	def colorGradient(self) -> None:
		h, s, v, a = self.painterColor.getHsv()
		h = (h + self.spinBox_colorH.value()) % 360
		s = (s + self.spinBox_colorS.value()) % 256
		v = (v + self.spinBox_colorV.value()) % 256
		self.painterColor.setHsv(h, s, v, a)
		setPushButtonColor(self.colorButton, self.painterColor)

	# ==================== 事件 ====================
	# 选择画笔颜色
	def onColorButtonClicked(self) -> None:
		w = ColorDialog(self.painterColor, 'Choose Painter Color', self.centralwidget, enableAlpha=False)
		w.colorChanged.connect(self.onPainterColorChanged)
		w.exec()
	# 颜色快速填充
	def onColorFillButtonClicked(self) -> None:
		for i in range(len(self.actions[self.actionIndex]['colors'])):
			self.actions[self.actionIndex]['colors'][i] = QColor(self.painterColor)
		self.repaintPage()
	# 清空颜色渐变属性
	def onColorClearButtonClicked(self) -> None:
		self.spinBox_colorH.setValue(0)
		self.spinBox_colorS.setValue(0)
		self.spinBox_colorV.setValue(0)
	# 结果复制, 得到 C++ 代码
	def onResultButtonClicked(self) -> None:
		actionsRes = self.actionsOutcome()
		res = actionsConvert(actionsRes)
		QApplication.clipboard().setText(res)
	# 改变画笔颜色
	def onPainterColorChanged(self, color: QColor) -> None:
		self.painterColor = color
		setPushButtonColor(self.colorButton, color)
	# 像素颜色改变
	def onPixelColorChanged(self, button: PushButton, index: int) -> None:
		setPushButtonColor(button, self.painterColor)
		self.actions[self.actionIndex]['colors'][index] = QColor(self.painterColor)
		self.colorGradient()
	# 导入 JSON
	def onImportTriggered(self) -> None:
		filepath, _ = QFileDialog.getOpenFileName(
			self.centralwidget,
			'Import File',
			'',
			'JSON File (*.json);;All Files (*)'
		)

		if not filepath:
			return
		
		try:
			with open(filepath, 'r') as f:
				import_actions = json.load(f)
			
			for i in range(len(import_actions)):
				import_actions[i]['colors'] = [QColor(c) for c in import_actions[i]['colors']]
				self.addPage(import_actions[i])

			self.repaintPage()
		except Exception as e:
			raise e
	# 导出 JSON
	def onExportTriggered(self) -> None:
		filepath, _ = QFileDialog.getSaveFileName(
			self.centralwidget,
			'Export File',
			'',
			'JSON File (*.json);;All Files (*)'
		)

		if not filepath:
			return

		try:
			with open(filepath, 'w') as f:
				json.dump(self.actionsOutcome(), f, indent=4)
		except Exception as e:
			raise e

from ui.mainwindow_ui import Ui_MainWindow
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow

from qfluentwidgets import ColorDialog, FluentIcon, PushButton

import json
from copy import deepcopy

from serial import Serial
import serial.tools.list_ports as SerialListPorts

# 将动画转换为 C++ 代码
def colorsConvert(colors: list) -> str:
	res = '{'
	for i in range(len(colors)):
		res += f'\"{colors[i].name()}\"'
		if i != len(colors) - 1:
			res += ', '
	res += '}'
	return res

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
		# -------------------- 设置 UI --------------------
		self.setupUi(window)

		# -------------------- 成员变量 --------------------
		# 常量
		self.DEFAULT_COLOR = QColor('#FFFFFF')
		self.PIXEL_NUM = len(self.pixels)
		
		# 变量
		self.painterColor = QColor(self.DEFAULT_COLOR)
		self.colors = [QColor(self.DEFAULT_COLOR) for _ in range(self.PIXEL_NUM)]
		self.serial = None

		# -------------------- 其它设置 --------------------
		self.updatePixelsColor()

		# -------------------- 事件绑定 --------------------
		# 导入导出 JSON
		self.menuImport.triggered.connect(self.onImportTriggered)
		self.menuExport.triggered.connect(self.onExportTriggered)
		# 颜色选择
		self.colorButton.clicked.connect(self.onColorButtonClicked)
		self.fillButton.clicked.connect(self.onColorFillButtonClicked)
		self.clearButton.clicked.connect(self.onColorClearButtonClicked)
		self.reverseButton.clicked.connect(self.onColorReverseButtonClicked)
		# 结果复制
		self.resultButton.clicked.connect(self.onResultButtonClicked)
		# 像素着色
		for i, p in enumerate(self.pixels):
			p.mousePressEvent = lambda _, p=p, i=i: self.onPixelColorChanged(p, i)
		# 串口
		self.comboBox_uart.clicked.connect(self.onUartComboBoxClicked)
		self.pushButton_uart.clicked.connect(self.onUartButtonClicked)

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
		# 串口连接
		self.pushButton_uart.setStyleSheet('background-color: #FF0000; color: #FFFFFF;')

	# ==================== 方法 ====================
	# 画笔颜色渐变
	def colorGradient(self) -> None:
		h, s, v, a = self.painterColor.getHsv()
		h = (h + self.spinBox_colorH.value()) % 360
		s = (s + self.spinBox_colorS.value()) % 256
		v = (v + self.spinBox_colorV.value()) % 256
		self.painterColor.setHsv(h, s, v, a)
		setPushButtonColor(self.colorButton, self.painterColor)
	# 根据 colors 更新像素颜色
	def updatePixelsColor(self) -> None:
		for i in range(self.PIXEL_NUM):
			setPushButtonColor(self.pixels[i], self.colors[i])
	# ==================== 事件 ====================
	# 选择画笔颜色
	def onColorButtonClicked(self) -> None:
		w = ColorDialog(self.painterColor, 'Choose Painter Color', self.centralwidget, enableAlpha=False)
		w.colorChanged.connect(self.onPainterColorChanged)
		w.exec()
	# 颜色快速填充
	def onColorFillButtonClicked(self) -> None:
		for i in range(self.PIXEL_NUM):
			self.colors[i] = self.painterColor
		self.updatePixelsColor()
	# 清空颜色渐变属性
	def onColorClearButtonClicked(self) -> None:
		self.spinBox_colorH.setValue(0)
		self.spinBox_colorS.setValue(0)
		self.spinBox_colorV.setValue(0)
	# 颜色反转
	def onColorReverseButtonClicked(self) -> None:
		self.colors = deepcopy(self.colors[::-1])
		self.updatePixelsColor()
	# 结果复制, 得到 C++ 代码
	def onResultButtonClicked(self) -> None:
		res = colorsConvert(deepcopy(self.colors))
		QApplication.clipboard().setText(res)
	# 改变画笔颜色
	def onPainterColorChanged(self, color: QColor) -> None:
		self.painterColor = color
		setPushButtonColor(self.colorButton, color)
	# 像素颜色改变
	def onPixelColorChanged(self, button: PushButton, index: int) -> None:
		setPushButtonColor(button, self.painterColor)
		self.colors[index] = QColor(self.painterColor)
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
				import_colors = json.load(f)
			
			self.colors = [QColor(c) for c in import_colors['colors']]
			self.updatePixelsColor()
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
		
		res = {'colors': [c.name() for c in self.colors]}

		try:
			with open(filepath, 'w') as f:
				json.dump(res, f, indent=4)
		except Exception as e:
			raise e
	# 串口选择
	def onUartComboBoxClicked(self) -> None:
		ports = SerialListPorts.comports()
		self.comboBox_uart.clear()
		for port in ports:
			self.comboBox_uart.addItem(port.device)
	# 串口连接
	def onUartButtonClicked(self) -> None:
		if self.serial is None:
			port = self.comboBox_uart.currentText()
			try:
				self.serial = Serial(port, 115200)
				self.pushButton_uart.setStyleSheet('background-color: #00FF00; color: #000000;')
			except Exception:
				pass
		else:
			self.serial.close()
			self.serial = None
			self.pushButton_uart.setStyleSheet('background-color: #FF0000; color: #FFFFFF;')

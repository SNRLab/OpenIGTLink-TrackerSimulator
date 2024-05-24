import sys, os, csv, glob
import numpy as np
import PyQt5.QtWidgets as qt
from PyQt5 import QtCore, QtGui
import pyigtl
import qdarkstyle

class MainWindow(qt.QMainWindow):
  def __init__(self):
    super().__init__()

    self.appPath = ""
    if getattr(sys, 'frozen', False):
      self.appPath = os.path.dirname(sys.executable)
    elif __file__:
      self.appPath = os.path.dirname(__file__)

    self.logPaths = []
    self.logData = {}

    self.Server = None

    applicationLayout = qt.QVBoxLayout()
    applicationWidget = qt.QWidget()
    self.setCentralWidget(applicationWidget)
    self.setWindowTitle("Tracker Simulator")
    applicationWidget.setLayout(applicationLayout)

    # --------------------------------- OpenIGTLink Input ----------------------------------
    openIGTLayout = qt.QFormLayout()
    openIGTWidget = qt.QWidget()
    openIGTWidget.setLayout(openIGTLayout)
    applicationLayout.addWidget(openIGTWidget)

    self.toggleServerButton = qt.QPushButton("Start OpenIGTLink Server")
    self.toggleServerButton.setCheckable(True)
    self.toggleServerButton.clicked.connect(self.onToggleServer)
    openIGTLayout.addRow(self.toggleServerButton)

    intValidator = QtGui.QIntValidator()
    self.openIGTPortTextbox = qt.QLineEdit("18934")
    self.openIGTPortTextbox.setValidator(intValidator)
    self.openIGTPortTextbox.setReadOnly(False)
    self.openIGTPortTextbox.setMaximumWidth(75)
    openIGTLayout.addRow("Port: ", self.openIGTPortTextbox)

    openIGTSeperator = qt.QFrame()
    openIGTSeperator.setFrameShape(qt.QFrame.HLine)
    openIGTSeperator.setFrameShadow(qt.QFrame.Sunken)
    applicationLayout.addWidget(openIGTSeperator)

    # --------------------------------- Log Input ----------------------------------
    logInputLayout = qt.QFormLayout()
    logInputWidget = qt.QWidget()
    logInputWidget.setLayout(logInputLayout)
    applicationLayout.addWidget(logInputWidget)

    self.loadLogsButton = qt.QPushButton("Load Logs")
    self.loadLogsButton.clicked.connect(self.onLoadLogs)
    logInputLayout.addRow(self.loadLogsButton)

    self.loadedLogsLabel = qt.QLabel("Loaded Logs:")
    logInputLayout.addRow(self.loadedLogsLabel)

    logInputSeperator = qt.QFrame()
    logInputSeperator.setFrameShape(qt.QFrame.HLine)
    logInputSeperator.setFrameShadow(qt.QFrame.Sunken)
    applicationLayout.addWidget(logInputSeperator)

    # --------------------------------- Playback Input ----------------------------------
    playbackLayout = qt.QFormLayout()
    playbackWidget = qt.QWidget()
    playbackWidget.setLayout(playbackLayout)
    applicationLayout.addWidget(playbackWidget)

    self.togglePlaybackButton = qt.QPushButton("Start Playback")
    self.togglePlaybackButton.setCheckable(True)
    self.togglePlaybackButton.clicked.connect(self.onTogglePlayback)
    playbackLayout.addRow(self.togglePlaybackButton)

    self.playbackLoopCheckbox = qt.QCheckBox("Loop")
    self.playbackLoopCheckbox.setChecked(True)
    playbackLayout.addRow(self.playbackLoopCheckbox)

    self.playbackTimer = QtCore.QTimer()
    self.playbackTimer.timeout.connect(self.onPlaybackTimer)
    self.timerFPSBox = qt.QSpinBox()
    self.timerFPSBox.setSingleStep(1)
    self.timerFPSBox.setMaximum(1000)
    self.timerFPSBox.setMinimum(1)
    self.timerFPSBox.setSuffix(" FPS")
    self.timerFPSBox.setValue(15)
    playbackLayout.addRow("Playback Rate: ", self.timerFPSBox)

    playbackSliderHBoxLayout = qt.QHBoxLayout()
    playbackSliderHBoxWidget = qt.QWidget()
    playbackSliderHBoxWidget.setLayout(playbackSliderHBoxLayout)
    playbackLayout.addWidget(playbackSliderHBoxWidget)

    self.playbackSlider = qt.QSlider(QtCore.Qt.Horizontal)
    self.playbackSlider.setEnabled(False)
    self.playbackSlider.setMinimum(1)
    self.playbackSlider.setMaximum(1)
    self.playbackSlider.valueChanged.connect(self.playbackSliderChanged)
    playbackSliderHBoxLayout.addWidget(self.playbackSlider)

    self.playbackSliderBox = qt.QSpinBox()
    self.playbackSliderBox.setEnabled(False)
    self.playbackSliderBox.setMinimum(1)
    self.playbackSliderBox.setMaximum(1)
    self.playbackSliderBox.setFixedWidth(100)
    self.playbackSliderBox.valueChanged.connect(self.playbackSliderBoxChanged)
    playbackSliderHBoxLayout.addWidget(self.playbackSliderBox)

    self.playbackUpdating = False

    applicationLayout.addStretch()

  def onToggleServer(self):
    if self.toggleServerButton.isChecked():
      self.Server = pyigtl.OpenIGTLinkServer(port=int(self.openIGTPortTextbox.text()))
      self.toggleServerButton.setText("Stop OpenIGTLink Server")
    else:
      self.Server.stop()
      self.Server = None
      self.toggleServerButton.setText("Start OpenIGTLink Server")

  def onLoadLogs(self):
    self.logData = {}
    self.logPaths = glob.glob(os.path.join(f'{self.appPath}/tracker_logs', '*.csv'))
    loadedLogsString = "Loaded Logs:"
    for logPath in self.logPaths:
      csvTransforms = []
      with open(logPath, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
          csvTransforms.append(row)
      self.logData[os.path.splitext(os.path.basename(logPath))[0]] = csvTransforms

      loadedLogsString += f'\n{os.path.basename(logPath)} : {len(csvTransforms)} lines'
      self.loadedLogsLabel.setText(loadedLogsString)

    self.playbackSlider.setEnabled(True)
    self.playbackSliderBox.setEnabled(True)
    self.playbackSlider.setMaximum(max(len(self.logData[key]) for key in self.logData))
    self.playbackSliderBox.setMaximum(max(len(self.logData[key]) for key in self.logData))

  def onTogglePlayback(self):
    if self.togglePlaybackButton.isChecked():
      self.playbackTimer.start(int(1000/int(self.timerFPSBox.value())))
      self.togglePlaybackButton.setText("Stop Playback")
    else:
      self.playbackTimer.stop()
      self.togglePlaybackButton.setText("Start Playback")

  def onPlaybackTimer(self):
    if self.playbackSliderBox.value() >= self.playbackSliderBox.maximum():
      if self.playbackLoopCheckbox.isChecked():
        self.playbackSliderBox.setValue(0)
      else:
        self.togglePlaybackButton.setChecked(False)
        self.onTogglePlayback() 
    else:
      self.playbackSliderBox.setValue(self.playbackSliderBox.value()+1)
  
  def playbackSliderChanged(self, value):
    if not self.playbackUpdating:
      self.playbackUpdating = True
      self.playbackSliderBox.setValue(value)
      self.sendTransformValueByIndex(value)
      self.playbackUpdating = False

  def playbackSliderBoxChanged(self, value):
    if not self.playbackUpdating:
      self.playbackUpdating = True
      self.playbackSlider.setValue(value)
      self.sendTransformValueByIndex(value)
      self.playbackUpdating = False

  def sendTransformValueByIndex(self, index):
    if self.Server.is_connected():
      transformMessages = []
      for logName, logValues in self.logData.items():
        if index >= len(logValues):
          continue
        matrix = np.eye(4)
        matrix[0] = logValues[index-1][0:4]
        matrix[1] = logValues[index-1][4:8]
        matrix[2] = logValues[index-1][8:12]
        transformMessages.append(pyigtl.TransformMessage(matrix, device_name=logName))
      for transformMessage in transformMessages:
        self.Server.send_message(transformMessage)

if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MainWindow()
    window.resize(600, 200)
    window.show()
    sys.exit(app.exec_())
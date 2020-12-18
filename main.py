from PyQt5 import QtCore, QtGui, QtWidgets
from Materials import Materials
from ScrollLabel import ScrollLabel
import pyqtgraph as pg
import numpy as np
import sys

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

####################################################
##  Langų dydžiai
global mainWindowX
global mainWindowY
global errorWindowX
global errorWindowY
global materialInfoWindowX
global materialInfoWindowY
global aboutWindowX
global aboutWindowY
mainWindowX = 1118
mainWindowY = 680
errorWindowX = 500
errorWindowY = 120
materialInfoWindowX = 700
materialInfoWindowY = 400
aboutWindowX = 350
aboutWindowY = 200

####################################################
##  Pagrindinio lango klasė
class Ui_Dialog(object):

    ####################################################
    ## Kintamųjų aprašymas
    length1_initValue = 1000
    length1_minValue = 10
    length1_maxValue = 2000

    length2_initValue = 1100
    length2_minValue = 10
    length2_maxValue = 2000

    temp1_initValue = 30
    temp1_minValue = 0
    temp1_maxValue = 300

    temp2_initValue = 70
    temp2_minValue = 0
    temp2_maxValue = 300

    timerInterval = 100
    
    ####################################################
    ##  Šriftų aprašymas
    labelFont = QtGui.QFont()
    labelFont.setPointSize(12)

    valueFont = QtGui.QFont()
    valueFont.setPointSize(16)

    ####################################################
    ##  'Go' mygtuko paspaudimo metodas
    def doGo(self):
        ilgis_pr = self.length1Slider.value()
        ilgis_ga = self.length2Slider.value()
        temp_pr = self.temp1Slider.value()
        temp_ga = self.temp2Slider.value()

        if (temp_pr == temp_ga):
            errorUI.showErrorMsg("Galutinė temperatūra turi skirtis nuo pradinės!")
            return
        if (ilgis_pr > ilgis_ga and temp_pr < temp_ga and self.selectAlpha.isChecked()):
            errorUI.showErrorMsg("Sąlyga `Pradinis ilgis` > `Galutinis ilgis` kai\n`Pradinė temperatūra` < `Galutinė temperatūra` neįmanoma!")
            return
        if (ilgis_pr < ilgis_ga and temp_pr > temp_ga and self.selectAlpha.isChecked()):
            errorUI.showErrorMsg("Sąlyga `Pradinis ilgis` < `Galutinis ilgis` kai\n`Pradinė temperatūra` > `Galutinė temperatūra` neįmanoma!")
            return
        if (ilgis_pr == ilgis_ga and temp_pr != temp_ga and self.selectAlpha.isChecked()):
            errorUI.showErrorMsg("Sąlyga `Pradinis ilgis` = `Galutinis ilgis` kai\n`Pradinė temperatūra` =/= `Galutinė temperatūra` neįmanoma!")
            return

        self.calcDirection = True
        if (temp_pr > temp_ga):
            self.calcDirection = False

        coef = Materials.getCoef(Materials, self.materialComboBox.currentIndex())
        self.results.setValue(0)
        result = None

        print("----------------------------------------")
        print("Medžiaga             : ", self.materialComboBox.currentText())
        print("Pradinis ilgis  (mm) : ", ilgis_pr)
        if (self.selectAlpha.isChecked()):
            print("Galutinis ilgis (mm) : ", ilgis_ga)
        print("Pradinė temp.   (°C) : ", temp_pr)
        print("Galutinė temp.  (°C) : ", temp_ga)
        self.materialComboBox.setEnabled(False)
        self.length1Slider.setEnabled(False)
        self.length2Slider.setEnabled(False)
        self.length1Value.setEnabled(False)
        self.length2Value.setEnabled(False)
        self.temp1Slider.setEnabled(False)
        self.temp2Slider.setEnabled(False)
        self.temp1Value.setEnabled(False)
        self.temp2Value.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.radioGroup.setEnabled(False)
        self.plotView.clear()

        ####################################################
        ## Rezultato apskaičiavimas
        if (self.selectAlpha.isChecked()):
            ilgis_pr = ilgis_pr / 1000
            ilgis_ga = ilgis_ga / 1000
            result = (ilgis_ga - ilgis_pr) / (ilgis_pr * (temp_ga - temp_pr))
        else:
            ilgis_pr = ilgis_pr / 1000
            ilgis_ga = ilgis_pr + (ilgis_pr * coef * (temp_ga - temp_pr))

        ####################################################
        ## Funkcijos apskaičiavimas
        ilgis_pr = ilgis_pr * 1000
        ilgis_ga = ilgis_ga * 1000
        self.ilgioFunkcija = [[], []]
        k = (ilgis_ga - ilgis_pr) / (temp_ga - temp_pr)
        if (temp_pr > temp_ga):
            rangex = range(temp_pr, temp_ga - 1, -1)
        else:
            rangex = range(temp_pr, temp_ga + 1)

        self.ilgioFunkcija[0] = list(rangex)
        for x in rangex:
            self.ilgioFunkcija[1].append(k * (x - temp_pr) + ilgis_pr)
            
        ####################################################
        ## Funkcijos braižymas
        plt = self.plotView
        self.plotView.setXRange(temp_pr, temp_ga)
        self.plotView.setYRange(ilgis_pr, ilgis_ga)
        self.plotView.centralLayout
        self.data = [[], []]
        self.curve = plt.plot()
        self.curve.setData()
        self.i = temp_pr
        self.line = plt.addLine(x=self.i, pen=pg.mkPen('b', width=1))
        self.iteration = 0

        def update():
            self.data[0].append(self.ilgioFunkcija[0][self.iteration])
            self.data[1].append(self.ilgioFunkcija[1][self.iteration])
            self.curve.setData(x=self.data[0], y=self.data[1], pen=pg.mkPen('r', width=3))
            self.line.setValue(self.i)
            if (self.calcDirection):
                self.i = (self.i+1)
            else:
                self.i = (self.i-1)
            self.iteration += 1

            if (self.iteration == abs(temp_ga - temp_pr) + 1):
                self.timer.stop()
                self.enableControls()
                plt.removeItem(self.line)
                if (self.selectAlpha.isChecked()):
                    self.results.setDecimals(6)
                    self.results.setValue(result)
                    print("           α (m/m°C) : ", result)
                else:
                    self.results.setDecimals(3)
                    self.results.setValue(ilgis_ga)
                    print("              L (mm) : ", ilgis_ga)

        self.update = update
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.timerInterval)

    ####################################################
    ##  'Reset' mygtuko paspaudimo metodas
    def doReset(self):
        self.length1Slider.setValue(self.length1_initValue)
        self.length2Slider.setValue(self.length2_initValue)
        self.length1Value.setValue(self.length1_initValue)
        self.length2Value.setValue(self.length2_initValue)
        self.temp1Slider.setValue(self.temp1_initValue)
        self.temp2Slider.setValue(self.temp2_initValue)
        self.temp1Value.setValue(self.temp1_initValue)
        self.temp2Value.setValue(self.temp2_initValue)
        self.results.setValue(0)
        self.enableControls()
        self.plotView.clear()
    ####################################################

    def showMaterialInfo(self):
        materialInfoUI.showMaterialInfo(Materials.getInfo(Materials, self.materialComboBox.currentIndex()))

    ####################################################
    ##  Įvedamų reikšmių pasikeitimo valdymo metodai
    def onLength1SliderChange(self):
        self.length1Value.setValue(self.length1Slider.value())
    def onTemp1SliderChange(self):
        self.temp1Value.setValue(self.temp1Slider.value())
    def onLength2SliderChange(self):
        self.length2Value.setValue(self.length2Slider.value())
    def onTemp2SliderChange(self):
        self.temp2Value.setValue(self.temp2Slider.value())
    def onLength1ValueChange(self):
        self.length1Slider.setValue(self.length1Value.value())
    def onTemp1ValueChange(self):
        self.temp1Slider.setValue(self.temp1Value.value())
    def onLength2ValueChange(self):
        self.length2Slider.setValue(self.length2Value.value())
    def onTemp2ValueChange(self):
        self.temp2Slider.setValue(self.temp2Value.value())
    def onRadioGroupChange(self):
        self.results.setValue(0)
        if (self.selectAlpha.isChecked()):
            self.materialGroup.setEnabled(False)
            self.length2Group.setEnabled(True)
            self.materialInfoButton.setEnabled(False)
            self.resultsLabel2.setText("α, m/m°C")
        else:
            self.materialGroup.setEnabled(True)
            self.length2Group.setEnabled(False)
            self.materialInfoButton.setEnabled(True)
            self.resultsLabel2.setText("L, mm")
    def enableControls(self):
        self.materialComboBox.setEnabled(True)
        self.length1Slider.setEnabled(True)
        self.length2Slider.setEnabled(True)
        self.length1Value.setEnabled(True)
        self.length2Value.setEnabled(True)
        self.temp1Slider.setEnabled(True)
        self.temp2Slider.setEnabled(True)
        self.temp1Value.setEnabled(True)
        self.temp2Value.setEnabled(True)
        self.pushButton.setEnabled(True)
        self.radioGroup.setEnabled(True)

    ####################################################
    ##  Grafinės sąsajos aprašymas ir inicializavimas
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")

        self.lengthGroup1 = QtWidgets.QGroupBox(Dialog)
        self.lengthGroup1.setGeometry(QtCore.QRect(920, 20, 181, 111))
        self.lengthGroup1.setTitle("")
        self.lengthGroup1.setObjectName("lengthGroup1")

        self.length1Slider = QtWidgets.QSlider(self.lengthGroup1)
        self.length1Slider.setGeometry(QtCore.QRect(10, 40, 160, 21))
        self.length1Slider.setOrientation(QtCore.Qt.Horizontal)
        self.length1Slider.setObjectName("length1Slider")
        self.length1Slider.setMinimum(self.length1_minValue)
        self.length1Slider.setMaximum(self.length1_maxValue)
        self.length1Slider.setValue(self.length1_initValue)
        self.length1Slider.valueChanged.connect(self.onLength1SliderChange)
        self.length1Slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.length1Slider.setTickInterval(100)

        self.length1Label = QtWidgets.QLabel(self.lengthGroup1)
        self.length1Label.setGeometry(QtCore.QRect(10, 10, 161, 21))
        self.length1Label.setFont(self.labelFont)
        self.length1Label.setObjectName("length1Label")

        self.length1Value = QtWidgets.QSpinBox(self.lengthGroup1)
        self.length1Value.setGeometry(QtCore.QRect(10, 70, 161, 31))
        self.length1Value.setObjectName("length1Value")
        self.length1Value.setMinimum(self.length1_minValue)
        self.length1Value.setMaximum(self.length1_maxValue)
        self.length1Value.setValue(self.length1_initValue)
        self.length1Value.valueChanged.connect(self.onLength1ValueChange)
        self.length1Value.setFont(self.valueFont)

        self.temp1Group = QtWidgets.QGroupBox(Dialog)
        self.temp1Group.setGeometry(QtCore.QRect(920, 240, 181, 111))
        self.temp1Group.setTitle("")
        self.temp1Group.setObjectName("temp1Group")

        self.temp1Slider = QtWidgets.QSlider(self.temp1Group)
        self.temp1Slider.setGeometry(QtCore.QRect(10, 40, 160, 21))
        self.temp1Slider.setOrientation(QtCore.Qt.Horizontal)
        self.temp1Slider.setObjectName("temp1Slider")
        self.temp1Slider.setMinimum(self.temp1_minValue)
        self.temp1Slider.setMaximum(self.temp1_maxValue)
        self.temp1Slider.setValue(self.temp1_initValue)
        self.temp1Slider.valueChanged.connect(self.onTemp1SliderChange)
        self.temp1Slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.temp1Slider.setTickInterval(10)

        self.temp1Label = QtWidgets.QLabel(self.temp1Group)
        self.temp1Label.setGeometry(QtCore.QRect(10, 10, 161, 21))
        self.temp1Label.setFont(self.labelFont)
        self.temp1Label.setObjectName("temp1Label")

        self.temp1Value = QtWidgets.QSpinBox(self.temp1Group)
        self.temp1Value.setGeometry(QtCore.QRect(10, 70, 161, 31))
        self.temp1Value.setObjectName("temp1Value")
        self.temp1Value.setMinimum(self.temp1_minValue)
        self.temp1Value.setMaximum(self.temp1_maxValue)
        self.temp1Value.setValue(self.temp1_initValue)
        self.temp1Value.valueChanged.connect(self.onTemp1ValueChange)
        self.temp1Value.setFont(self.valueFont)
        
        self.materialGroup = QtWidgets.QGroupBox(Dialog)
        self.materialGroup.setGeometry(QtCore.QRect(920, 460, 181, 71))
        self.materialGroup.setTitle("")
        self.materialGroup.setObjectName("materialGroup")
        self.materialGroup.setEnabled(False)

        self.materialComboBox = QtWidgets.QComboBox(self.materialGroup)
        self.materialComboBox.setGeometry(QtCore.QRect(10, 40, 161, 22))
        self.materialComboBox.setFont(self.labelFont)
        self.materialComboBox.setObjectName("materialComboBox")
        for x in range(len(Materials.items)):
            self.materialComboBox.addItem("")

        self.materialLabel = QtWidgets.QLabel(self.materialGroup)
        self.materialLabel.setGeometry(QtCore.QRect(10, 10, 101, 21))
        self.materialLabel.setFont(self.labelFont)
        self.materialLabel.setObjectName("materialLabel")

        self.plotView = pg.PlotWidget(Dialog)
        self.plotView.setXRange(0, 300)
        self.plotView.setYRange(1000, 2000)
        self.plotView.setGeometry(QtCore.QRect(10, 20, 891, 500))
        self.plotView.setObjectName("plotView")
        self.plotView.showButtons()
        self.plotView.setBackground('w')
        self.plotView.setTitle("Kietojo kūno pailgėjimo priklausomybė nuo temperatūros pokyčio grafikas", color='#000000',
                                size="15pt")
        self.plotView.setLabel('left', "<span style=\"color:black;font-size:20px\">L, mm</span>")
        self.plotView.setLabel('bottom', "<span style=\"color:black;font-size:20px\">Temperatūra, °C</span>")
        self.plotView.addLegend()
        self.plotView.showGrid(x=True, y=True)

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(920, mainWindowY - 51, 81, 41))
        self.pushButton.setFont(self.labelFont)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.doGo)

        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(1020, mainWindowY - 51, 81, 41))
        self.pushButton_2.setFont(self.labelFont)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.doReset)

        self.temp2Group = QtWidgets.QGroupBox(Dialog)
        self.temp2Group.setGeometry(QtCore.QRect(920, 350, 181, 111))
        self.temp2Group.setTitle("")
        self.temp2Group.setObjectName("temp2Group")

        self.temp2Slider = QtWidgets.QSlider(self.temp2Group)
        self.temp2Slider.setGeometry(QtCore.QRect(10, 40, 160, 21))
        self.temp2Slider.setOrientation(QtCore.Qt.Horizontal)
        self.temp2Slider.setObjectName("temp2Slider")
        self.temp2Slider.setMinimum(self.temp2_minValue)
        self.temp2Slider.setMaximum(self.temp2_maxValue)
        self.temp2Slider.setValue(self.temp2_initValue)
        self.temp2Slider.valueChanged.connect(self.onTemp2SliderChange)
        self.temp2Slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.temp2Slider.setTickInterval(10)
        
        self.temp2Label = QtWidgets.QLabel(self.temp2Group)
        self.temp2Label.setGeometry(QtCore.QRect(10, 10, 161, 21))
        self.temp2Label.setFont(self.labelFont)
        self.temp2Label.setObjectName("temp2Label")

        self.temp2Value = QtWidgets.QSpinBox(self.temp2Group)
        self.temp2Value.setGeometry(QtCore.QRect(10, 70, 161, 31))
        self.temp2Value.setObjectName("temp2Value")
        self.temp2Value.setMinimum(self.temp2_minValue)
        self.temp2Value.setMaximum(self.temp2_maxValue)
        self.temp2Value.setValue(self.temp2_initValue)
        self.temp2Value.valueChanged.connect(self.onTemp2ValueChange)
        self.temp2Value.setFont(self.valueFont)

        self.length2Group = QtWidgets.QGroupBox(Dialog)
        self.length2Group.setGeometry(QtCore.QRect(920, 130, 181, 111))
        self.length2Group.setTitle("")
        self.length2Group.setObjectName("length2Group")

        self.length2Slider = QtWidgets.QSlider(self.length2Group)
        self.length2Slider.setGeometry(QtCore.QRect(10, 40, 160, 21))
        self.length2Slider.setOrientation(QtCore.Qt.Horizontal)
        self.length2Slider.setObjectName("length2Slider")
        self.length2Slider.setMinimum(self.length2_minValue)
        self.length2Slider.setMaximum(self.length2_maxValue)
        self.length2Slider.setValue(self.length2_initValue)
        self.length2Slider.valueChanged.connect(self.onLength2SliderChange)
        self.length2Slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.length2Slider.setTickInterval(100)

        self.length2Label = QtWidgets.QLabel(self.length2Group)
        self.length2Label.setGeometry(QtCore.QRect(10, 10, 161, 21))
        self.length2Label.setFont(self.labelFont)
        self.length2Label.setObjectName("length2Label")

        self.length2Value = QtWidgets.QSpinBox(self.length2Group)
        self.length2Value.setGeometry(QtCore.QRect(10, 70, 161, 31))
        self.length2Value.setObjectName("length2Value")
        self.length2Value.setMinimum(self.length2_minValue)
        self.length2Value.setMaximum(self.length2_maxValue)
        self.length2Value.setValue(self.length2_initValue)
        self.length2Value.valueChanged.connect(self.onLength2ValueChange)
        self.length2Value.setFont(self.valueFont)

        self.radioGroup = QtWidgets.QGroupBox(Dialog)
        self.radioGroup.setGeometry(QtCore.QRect(920, 530, 181, 91))
        self.radioGroup.setTitle("")
        self.radioGroup.setObjectName("radioGroup")

        self.radioLabel = QtWidgets.QLabel(self.radioGroup)
        self.radioLabel.setGeometry(QtCore.QRect(10, 10, 161, 21))
        self.radioLabel.setFont(self.labelFont)
        self.radioLabel.setObjectName("radioLabel")

        self.alphaLabel = QtWidgets.QLabel(self.radioGroup)
        self.alphaLabel.setGeometry(QtCore.QRect(15, 40, 161, 21))
        self.alphaLabel.setFont(self.labelFont)
        self.alphaLabel.setObjectName("alphaLabel")

        self.selectAlpha = QtWidgets.QRadioButton(self.radioGroup)
        self.selectAlpha.setGeometry(QtCore.QRect(43, 65, 161, 21))
        self.selectAlpha.setChecked(True)
        self.selectAlpha.clicked.connect(self.onRadioGroupChange)

        self.selectLengthLabel = QtWidgets.QLabel(self.radioGroup)
        self.selectLengthLabel.setGeometry(QtCore.QRect(117, 40, 161, 21))
        self.selectLengthLabel.setFont(self.labelFont)
        self.selectLengthLabel.setObjectName("selectLengthLabel")

        self.selectLength = QtWidgets.QRadioButton(self.radioGroup)
        self.selectLength.setGeometry(QtCore.QRect(127, 65, 161, 21))
        self.selectLength.clicked.connect(self.onRadioGroupChange)

        self.resultsGroup = QtWidgets.QGroupBox(Dialog)
        self.resultsGroup.setGeometry(QtCore.QRect(10, 550, 181, 120))
        self.resultsGroup.setTitle("")
        self.resultsGroup.setObjectName("resultsGroup")

        self.materialInfoButton = QtWidgets.QPushButton(Dialog)
        self.materialInfoButton.setGeometry(QtCore.QRect(201, 550, 200, 55))
        self.materialInfoButton.setFont(self.labelFont)
        self.materialInfoButton.setObjectName("materialInfoButton")
        self.materialInfoButton.setEnabled(False)
        self.materialInfoButton.clicked.connect(self.showMaterialInfo)

        self.aboutButton = QtWidgets.QPushButton(Dialog)
        self.aboutButton.setGeometry(QtCore.QRect(201, 615, 200, 55))
        self.aboutButton.setFont(self.labelFont)
        self.aboutButton.setObjectName("aboutButton")
        self.aboutButton.clicked.connect(About_Dialog.showAbout)

        self.resultsLabel1 = QtWidgets.QLabel(self.resultsGroup)
        self.resultsLabel1.setGeometry(QtCore.QRect(10, 10, 161, 21))
        self.resultsLabel1.setFont(self.labelFont)
        self.resultsLabel1.setObjectName("resultsLabel1")
        
        self.resultsLabel2 = QtWidgets.QLabel(self.resultsGroup)
        self.resultsLabel2.setGeometry(QtCore.QRect(10, 45, 161, 21))
        self.resultsLabel2.setFont(self.labelFont)
        self.resultsLabel2.setObjectName("resultsLabel2")

        self.results = QtWidgets.QDoubleSpinBox(self.resultsGroup)
        self.results.setGeometry(QtCore.QRect(10, 70, 161, 31))
        self.results.setMinimum(sys.float_info.min)
        self.results.setMaximum(sys.float_info.max)
        self.results.setFont(self.valueFont)
        self.results.setReadOnly(True)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    ####################################################
    ##  Grafinės sąsajos elementų antraščių ir reikšmių aprašymai
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Kietojo kūno temperatūrinio ilgėjimo koeficiento nustatymas"))
        self.length1Label.setText(_translate("Dialog", "Pradinis ilgis, mm"))
        self.temp1Label.setText(_translate("Dialog", "Pradinė temp., °C"))
        self.materialLabel.setText(_translate("Dialog", "Medžiaga"))
        self.pushButton.setText(_translate("Dialog", "Go"))
        self.pushButton_2.setText(_translate("Dialog", "Reset"))
        self.temp2Label.setText(_translate("Dialog", "Galutinė temp., °C"))
        self.length2Label.setText(_translate("Dialog", "Galutinis ilgis, mm"))
        self.alphaLabel.setText(_translate("Dialog", "α, m/m°C"))
        self.selectLengthLabel.setText(_translate("Dialog", "L, mm"))
        self.resultsLabel1.setText(_translate("Dialog", "Rezultatai"))
        self.resultsLabel2.setText(_translate("Dialog", "α, m/m°C"))
        self.materialInfoButton.setText(_translate("Dialog", "Informacija apie medžiagą"))
        self.aboutButton.setText(_translate("Dialog", "Apie autorius"))
        self.radioLabel.setText(_translate("Dialog", "Skaičiuoti"))

        for material in Materials.items:
            self.materialComboBox.setItemText(material.id, _translate("Dialog", material.name))

####################################################
##  Klaidos lango klasė
class Error_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("errorDialog")
        Dialog.setWindowTitle("Klaida!")

        labelFont = QtGui.QFont()
        labelFont.setPointSize(12)

        self.errorMsg = QtWidgets.QLabel(Dialog)
        self.errorMsg.setGeometry(QtCore.QRect(20, 10, errorWindowX - 40, errorWindowY - 70))#20, 10, 470, 50))
        self.errorMsg.wordWrap = True
        self.errorMsg.setFont(labelFont)
        self.errorMsg.setObjectName("errorMsg")

        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(errorWindowX - 100, errorWindowY - 50, 80, 30))
        self.okButton.setFont(labelFont)
        self.okButton.setObjectName("okButton")
        self.okButton.setText("OK")
        self.okButton.clicked.connect(self.closeDialog)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def showErrorMsg(self, errorMsgText):
        self.errorMsg.setText(errorMsgText)
        errorDialog.show()
        errorDialog.raise_()
        window.setEnabled(False)

    def closeDialog(self):
        errorDialog.close()

    def onExit(self):
        window.setEnabled(True)

####################################################
##  Medžiagos informacijos lango klasė
class MaterialInfo_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("materialInfoDialog")
        Dialog.setWindowTitle("Informacija apie medžiagą")

        labelFont = QtGui.QFont()
        labelFont.setPointSize(12)

        self.materialInfoText = ScrollLabel(Dialog)
        self.materialInfoText.setGeometry(QtCore.QRect(20, 10, materialInfoWindowX - 40, materialInfoWindowY - 70))
        self.materialInfoText.wordWrap = True
        self.materialInfoText.setFont(labelFont)
        self.materialInfoText.setObjectName("materialInfoText")

        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(materialInfoWindowX - 100, materialInfoWindowY - 50, 80, 30))
        self.okButton.setFont(labelFont)
        self.okButton.setObjectName("okButton")
        self.okButton.setText("OK")
        self.okButton.clicked.connect(self.closeDialog)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def showMaterialInfo(self, materialInfo):
        self.materialInfoText.setText(materialInfo)
        materialInfoDialog.show()
        materialInfoDialog.raise_()
        window.setEnabled(False)

    def closeDialog(self):
        materialInfoDialog.close()

    def onExit(self):
        window.setEnabled(True)

####################################################
##  Autorių informacijos lango klasė
class About_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("aboutDialog")
        Dialog.setWindowTitle("Apie autorius")

        labelFont = QtGui.QFont()
        labelFont.setPointSize(12)

        self.aboutText = QtWidgets.QLabel(Dialog)
        self.aboutText.setGeometry(QtCore.QRect(20, 10, aboutWindowX - 40, aboutWindowY - 70))
        self.aboutText.wordWrap = True
        self.aboutText.setFont(labelFont)
        self.aboutText.setObjectName("aboutText")
        self.aboutText.setText("Programą sukūrė:\nLukas Sparnauskas IFC-7\nJuozas Venckus IFB-7\nMarius Pupelis IFB-7\nRaminta Šniaukštaitė IFB-7\nAugustinas Juškevičius IFB-7\nTautvydas Banelis IFS-8")

        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(aboutWindowX - 100, aboutWindowY - 50, 80, 30))
        self.okButton.setFont(labelFont)
        self.okButton.setObjectName("okButton")
        self.okButton.setText("OK")
        self.okButton.clicked.connect(self.closeDialog)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def showAbout(self):
        aboutDialog.show()
        aboutDialog.raise_()
        window.setEnabled(False)

    def closeDialog(self):
        aboutDialog.close()

    def onExit(self):
        window.setEnabled(True)

####################################################
##  Programos paleidimas
def main():    
    global app
    global window
    global errorDialog
    global errorUI
    global materialInfoDialog
    global materialInfoUI
    global aboutDialog

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QDialog()
    window.setFixedSize(mainWindowX, mainWindowY)
    ui = Ui_Dialog()
    ui.setupUi(window)
    window.show()
    window.raise_()

    errorDialog = QtWidgets.QDialog()
    errorDialog.setFixedSize(errorWindowX, errorWindowY)
    errorUI = Error_Dialog()
    errorUI.setupUi(errorDialog)
    errorDialog.closeEvent = Error_Dialog.onExit

    materialInfoDialog = QtWidgets.QDialog()
    materialInfoDialog.setFixedSize(materialInfoWindowX, materialInfoWindowY)
    materialInfoUI = MaterialInfo_Dialog()
    materialInfoUI.setupUi(materialInfoDialog)
    materialInfoDialog.closeEvent = MaterialInfo_Dialog.onExit

    aboutDialog = QtWidgets.QDialog()
    aboutDialog.setFixedSize(aboutWindowX, aboutWindowY)
    aboutUI = About_Dialog()
    aboutUI.setupUi(aboutDialog)
    aboutDialog.closeEvent = About_Dialog.onExit

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
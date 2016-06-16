import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, qApp, QTabWidget, 
    QHBoxLayout, QVBoxLayout, QLabel, QToolBar, QToolButton, QTextEdit,
    QScrollArea)

class MainWindow(QMainWindow):

    def __init__(self):

        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Fanns - Finance Analysis Neural-Nets System')
        self.setMinimumSize(800, 600)
        self.initToolBar()
        self.initMenuBar()
        self.initMainBoard()

        self.show()

    def initMainBoard(self):

        self.mainBoard = QWidget()
        self.setCentralWidget(self.mainBoard)
        self.pagesStatus = [0]*5
        self.pages = [QWidget(self.mainBoard) for i in self.pagesStatus]

        self.mainBoard.setStyleSheet("padding:10px")

    def initToolBar(self):

        self.toolBar = QToolBar("Tools")
        self.toolBar.setMovable(False)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)
        self.toolBar.setIconSize(QSize(20, 20))
        self.setStyleSheet(
            "QToolBar {" +
                "background-color: #a1afc9;" +
                "border-right: 1px solid #065279;" + 
                "padding: 5px}" +
            "QToolBar > QToolButton:hover {" +
                "background-color: #f0f0f4;" +
                "border-radius:3px}")

        configButton = QToolButton()
        configButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        configButton.setIcon(QIcon("Image/Icon/file.png"))
        configButton.setText("Configure")
        configButton.setFixedSize(120, 30)
        envAnaButton = QToolButton()
        envAnaButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        envAnaButton.setIcon(QIcon("Image/Icon/file.png"))
        envAnaButton.setText("Environment")
        envAnaButton.setFixedSize(120, 30)
        stoHisButton = QToolButton()
        stoHisButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        stoHisButton.setIcon(QIcon("Image/Icon/file.png"))
        stoHisButton.setText("Stock History")
        stoHisButton.setFixedSize(120, 30)
        stoAnaButton = QToolButton()
        stoAnaButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        stoAnaButton.setIcon(QIcon("Image/Icon/file.png"))
        stoAnaButton.setText("Stocks Analysis")
        stoAnaButton.setFixedSize(120, 30)
        autoTrButton = QToolButton()
        autoTrButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        autoTrButton.setIcon(QIcon("Image/Icon/file.png"))
        autoTrButton.setText("Auto Trading")
        autoTrButton.setFixedSize(120, 30)

        configButton.clicked.connect(self.configPage)
        envAnaButton.clicked.connect(self.envAnaPage)
        stoHisButton.clicked.connect(self.stoHisPage)
        stoAnaButton.clicked.connect(self.stoAnaPage)
        autoTrButton.clicked.connect(self.autoTrPage)

        self.toolBar.addWidget(configButton)
        self.toolBar.addWidget(envAnaButton)
        self.toolBar.addWidget(stoHisButton)
        self.toolBar.addWidget(stoAnaButton)
        self.toolBar.addWidget(autoTrButton)

    def initMenuBar(self):

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        launchAction = QAction('&Launch', self)
        launchAction.setShortcut('Ctrl+L')
        launchAction.triggered.connect(self.execute)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fannsMenu = menubar.addMenu('&App')
        fannsMenu.addAction(exitAction)
        editMenu = menubar.addMenu('&Func')
        editMenu.addAction(launchAction)

    def execute(self):

        print 'have a lunch!'

    def configPage(self):

        print "in config page"
        ci = 0
        page = self.pages[ci]

        if self.pagesStatus[ci] == 0:

            self.label = QLabel("This is configure page.", page)
            self.label.show()
            self.pagesStatus[ci] = 1

        for pi in range(0,len(self.pages)): self.pages[pi].hide()
        page.show()

    def envAnaPage(self):

        print "in environment page"
        ci = 1
        page = self.pages[ci]

        if self.pagesStatus[ci] == 0:

            self.label = QLabel("This is environment page.", page)
            self.label.show()
            self.pagesStatus[ci] = 1

        for pi in range(0,len(self.pages)): self.pages[pi].hide()
        page.show()

    def stoHisPage(self):

        print "in stock history page"
        ci = 2
        page = self.pages[ci]

        if self.pagesStatus[ci] == 0:

            self.label = QLabel("This is stock history page.", page)
            self.label.show()
            self.pagesStatus[ci] = 1

        for pi in range(0,len(self.pages)): self.pages[pi].hide()
        page.show()

    def stoAnaPage(self):

        print "in stock analysis page"
        ci = 3
        page = self.pages[ci]

        if self.pagesStatus[ci] == 0:

            self.label = QLabel("This is stock analysis page.", page)
            self.label.show()
            self.pagesStatus[ci] = 1

        for pi in range(0,len(self.pages)): self.pages[pi].hide()
        page.show()

    def autoTrPage(self):

        print "in auto trading page"
        ci = 4
        page = self.pages[ci]

        if self.pagesStatus[ci] == 0:

            self.label = QLabel("This is auto trading page.", page)
            self.label.show()
            self.pagesStatus[ci] = 1

        for pi in range(0,len(self.pages)): self.pages[pi].hide()
        page.show()

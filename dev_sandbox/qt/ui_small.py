# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'small.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                               QSizePolicy, QWidget)


class Ui_Frame(object):
    def setupUi(self, Frame):
        if not Frame.objectName():
            Frame.setObjectName(u"Frame")
        Frame.resize(280, 100)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Frame.sizePolicy().hasHeightForWidth())
        Frame.setSizePolicy(sizePolicy)
        Frame.setStyleSheet(u"/* \ud83d\udd32 QGridLayout containers */\n"
"QWidget[layoutType=\"grid\"] {\n"
"    border: 2px dashed #E57373; /* soft red */\n"
"    background-color: rgba(229, 115, 115, 0.05); /* super subtle red fill */\n"
"}\n"
"\n"
"/* \ud83d\udd3d QVBoxLayout containers */\n"
"QWidget[layoutType=\"vbox\"] {\n"
"    border: 2px dashed #64B5F6; /* soft blue */\n"
"    background-color: rgba(100, 181, 246, 0.05);\n"
"}\n"
"\n"
"/* \ud83d\udd3c QHBoxLayout containers */\n"
"QWidget[layoutType=\"hbox\"] {\n"
"    border: 2px dashed #81C784; /* soft green */\n"
"    background-color: rgba(129, 199, 132, 0.05);\n"
"}\n"
"\n"
"/* \ud83d\udd39 All layout-bearing widgets \u2013 catch-alls */\n"
"QWidget:has(*:layout) {\n"
"    margin: 4px;\n"
"    padding: 2px;\n"
"}")
        self.horizontalLayout = QHBoxLayout(Frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lbl_image = QLabel(Frame)
        self.lbl_image.setObjectName(u"lbl_image")
        sizePolicy.setHeightForWidth(self.lbl_image.sizePolicy().hasHeightForWidth())
        self.lbl_image.setSizePolicy(sizePolicy)
        self.lbl_image.setMinimumSize(QSize(100, 100))
        self.lbl_image.setMaximumSize(QSize(100, 100))

        self.horizontalLayout.addWidget(self.lbl_image)

        self.lbl_name = QLabel(Frame)
        self.lbl_name.setObjectName(u"lbl_name")

        self.horizontalLayout.addWidget(self.lbl_name, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.retranslateUi(Frame)

        QMetaObject.connectSlotsByName(Frame)
    # setupUi

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QCoreApplication.translate("Frame", u"Frame", None))
        self.lbl_image.setText("")
        self.lbl_name.setText("")
    # retranslateUi


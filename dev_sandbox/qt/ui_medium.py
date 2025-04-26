# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'medium.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QSizePolicy, QSpacerItem, QWidget)


class Ui_MediumLayout(object):
    def setupUi(self, MediumLayout):
        if not MediumLayout.objectName():
            MediumLayout.setObjectName(u"MediumLayout")
        MediumLayout.resize(298, 420)
        MediumLayout.setStyleSheet(u"/* \ud83d\udd32 QGridLayout containers */\n"
"QFrame {\n"
"	color: black;\n"
"}\n"
"\n"
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
        self.grid = QGridLayout(MediumLayout)
        self.grid.setObjectName(u"grid")
        self.lbl_image = QLabel(MediumLayout)
        self.lbl_image.setObjectName(u"lbl_image")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_image.sizePolicy().hasHeightForWidth())
        self.lbl_image.setSizePolicy(sizePolicy)
        self.lbl_image.setMinimumSize(QSize(280, 280))
        self.lbl_image.setMaximumSize(QSize(280, 280))
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.grid.addWidget(self.lbl_image, 0, 0, 1, 4)

        self.lbl_name = QLabel(MediumLayout)
        self.lbl_name.setObjectName(u"lbl_name")
        font = QFont()
        font.setPointSize(16)
        font.setWeight(QFont.Medium)
        self.lbl_name.setFont(font)

        self.grid.addWidget(self.lbl_name, 1, 2, 1, 2)

        self.lyt_headings = QHBoxLayout()
        self.lyt_headings.setObjectName(u"lyt_headings")
        self.lbl_servings_heading = QLabel(MediumLayout)
        self.lbl_servings_heading.setObjectName(u"lbl_servings_heading")
        font1 = QFont()
        font1.setPointSize(12)
        self.lbl_servings_heading.setFont(font1)

        self.lyt_headings.addWidget(self.lbl_servings_heading)

        self.lbl_time_heading = QLabel(MediumLayout)
        self.lbl_time_heading.setObjectName(u"lbl_time_heading")
        self.lbl_time_heading.setFont(font1)
        self.lbl_time_heading.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.lyt_headings.addWidget(self.lbl_time_heading)


        self.grid.addLayout(self.lyt_headings, 2, 0, 2, 4)

        self.lyt_servings = QHBoxLayout()
        self.lyt_servings.setSpacing(10)
        self.lyt_servings.setObjectName(u"lyt_servings")
        self.lbl_icon = QLabel(MediumLayout)
        self.lbl_icon.setObjectName(u"lbl_icon")
        font2 = QFont()
        font2.setPointSize(30)
        self.lbl_icon.setFont(font2)

        self.lyt_servings.addWidget(self.lbl_icon)

        self.lbl_servings = QLabel(MediumLayout)
        self.lbl_servings.setObjectName(u"lbl_servings")
        font3 = QFont()
        font3.setPointSize(16)
        self.lbl_servings.setFont(font3)

        self.lyt_servings.addWidget(self.lbl_servings, 0, Qt.AlignmentFlag.AlignBottom)


        self.grid.addLayout(self.lyt_servings, 3, 1, 2, 1)

        self.horizontalSpacer = QSpacerItem(129, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.grid.addItem(self.horizontalSpacer, 4, 2, 1, 1)

        self.lyt_time = QHBoxLayout()
        self.lyt_time.setObjectName(u"lyt_time")
        self.lbl_time = QLabel(MediumLayout)
        self.lbl_time.setObjectName(u"lbl_time")
        font4 = QFont()
        font4.setPointSize(20)
        self.lbl_time.setFont(font4)

        self.lyt_time.addWidget(self.lbl_time)

        self.lbl_time_suffix = QLabel(MediumLayout)
        self.lbl_time_suffix.setObjectName(u"lbl_time_suffix")
        font5 = QFont()
        font5.setPointSize(14)
        self.lbl_time_suffix.setFont(font5)

        self.lyt_time.addWidget(self.lbl_time_suffix)


        self.grid.addLayout(self.lyt_time, 4, 3, 1, 1)


        self.retranslateUi(MediumLayout)

        QMetaObject.connectSlotsByName(MediumLayout)
    # setupUi

    def retranslateUi(self, MediumLayout):
        MediumLayout.setWindowTitle(QCoreApplication.translate("MediumLayout", u"Frame", None))
        self.lbl_image.setText(QCoreApplication.translate("MediumLayout", u"Recipe Image", None))
        self.lbl_name.setText(QCoreApplication.translate("MediumLayout", u"Recipe Name", None))
        self.lbl_servings_heading.setText(QCoreApplication.translate("MediumLayout", u"Servings", None))
        self.lbl_time_heading.setText(QCoreApplication.translate("MediumLayout", u"Time", None))
        self.lbl_icon.setText(QCoreApplication.translate("MediumLayout", u"&", None))
        self.lbl_servings.setText(QCoreApplication.translate("MediumLayout", u"4", None))
        self.lbl_time.setText(QCoreApplication.translate("MediumLayout", u"30", None))
        self.lbl_time_suffix.setText(QCoreApplication.translate("MediumLayout", u"min.", None))
    # retranslateUi


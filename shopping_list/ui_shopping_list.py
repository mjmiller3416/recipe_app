# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shopping_list.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ShoppingList(object):
    def setupUi(self, ShoppingList):
        if not ShoppingList.objectName():
            ShoppingList.setObjectName(u"ShoppingList")
        ShoppingList.resize(852, 813)
        self.verticalLayout_2 = QVBoxLayout(ShoppingList)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(ShoppingList)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(27)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame = QFrame(ShoppingList)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_2.addWidget(self.frame)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_2 = QFrame(ShoppingList)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(ShoppingList)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.frame_3)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 12)

        self.retranslateUi(ShoppingList)

        QMetaObject.connectSlotsByName(ShoppingList)
    # setupUi

    def retranslateUi(self, ShoppingList):
        ShoppingList.setWindowTitle(QCoreApplication.translate("ShoppingList", u"Form", None))
        self.label.setText(QCoreApplication.translate("ShoppingList", u"SHOPPING LIST", None))
    # retranslateUi


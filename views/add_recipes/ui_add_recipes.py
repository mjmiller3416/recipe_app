# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_recipes.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QScrollArea,
                               QSizePolicy, QTextEdit, QVBoxLayout, QWidget)

from ui.components.inputs import CustomComboBox


class Ui_AddRecipes(object):
    def setupUi(self, AddRecipes):
        if not AddRecipes.objectName():
            AddRecipes.setObjectName(u"AddRecipes")
        AddRecipes.resize(1063, 805)
        self.gridLayout = QGridLayout(AddRecipes)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.lyt_ingredients = QVBoxLayout()
        self.lyt_ingredients.setObjectName(u"lyt_ingredients")
        self.lbl_ingredients = QLabel(AddRecipes)
        self.lbl_ingredients.setObjectName(u"lbl_ingredients")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_ingredients.sizePolicy().hasHeightForWidth())
        self.lbl_ingredients.setSizePolicy(sizePolicy)
        self.lbl_ingredients.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.lyt_ingredients.addWidget(self.lbl_ingredients)

        self.sa_ingredients = QScrollArea(AddRecipes)
        self.sa_ingredients.setObjectName(u"sa_ingredients")
        self.sa_ingredients.setWidgetResizable(True)
        self.ingredients_container = QWidget()
        self.ingredients_container.setObjectName(u"ingredients_container")
        self.ingredients_container.setGeometry(QRect(0, 0, 505, 669))
        self.sa_ingredients.setWidget(self.ingredients_container)

        self.lyt_ingredients.addWidget(self.sa_ingredients)


        self.gridLayout.addLayout(self.lyt_ingredients, 2, 0, 1, 1)

        self.lyt_recipe_input = QWidget(AddRecipes)
        self.lyt_recipe_input.setObjectName(u"lyt_recipe_input")
        self.horizontalLayout_6 = QHBoxLayout(self.lyt_recipe_input)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 6)
        self.lyt_recipe_name = QHBoxLayout()
        self.lyt_recipe_name.setObjectName(u"lyt_recipe_name")
        self.lbl_recipe_name = QLabel(self.lyt_recipe_input)
        self.lbl_recipe_name.setObjectName(u"lbl_recipe_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbl_recipe_name.sizePolicy().hasHeightForWidth())
        self.lbl_recipe_name.setSizePolicy(sizePolicy1)

        self.lyt_recipe_name.addWidget(self.lbl_recipe_name)

        self.le_recipe_name = QLineEdit(self.lyt_recipe_input)
        self.le_recipe_name.setObjectName(u"le_recipe_name")
        sizePolicy.setHeightForWidth(self.le_recipe_name.sizePolicy().hasHeightForWidth())
        self.le_recipe_name.setSizePolicy(sizePolicy)

        self.lyt_recipe_name.addWidget(self.le_recipe_name)


        self.horizontalLayout_6.addLayout(self.lyt_recipe_name)

        self.lyt_category = QHBoxLayout()
        self.lyt_category.setObjectName(u"lyt_category")
        self.lbl_category = QLabel(self.lyt_recipe_input)
        self.lbl_category.setObjectName(u"lbl_category")
        sizePolicy1.setHeightForWidth(self.lbl_category.sizePolicy().hasHeightForWidth())
        self.lbl_category.setSizePolicy(sizePolicy1)

        self.lyt_category.addWidget(self.lbl_category)

        self.cb_recipie_category = CustomComboBox(self.lyt_recipe_input)
        self.cb_recipie_category.setObjectName(u"cb_recipie_category")
        sizePolicy.setHeightForWidth(self.cb_recipie_category.sizePolicy().hasHeightForWidth())
        self.cb_recipie_category.setSizePolicy(sizePolicy)

        self.lyt_category.addWidget(self.cb_recipie_category)


        self.horizontalLayout_6.addLayout(self.lyt_category)

        self.lyt_total_time = QHBoxLayout()
        self.lyt_total_time.setObjectName(u"lyt_total_time")
        self.lbl_total_time = QLabel(self.lyt_recipe_input)
        self.lbl_total_time.setObjectName(u"lbl_total_time")
        sizePolicy1.setHeightForWidth(self.lbl_total_time.sizePolicy().hasHeightForWidth())
        self.lbl_total_time.setSizePolicy(sizePolicy1)

        self.lyt_total_time.addWidget(self.lbl_total_time)

        self.le_total_time = QLineEdit(self.lyt_recipe_input)
        self.le_total_time.setObjectName(u"le_total_time")
        sizePolicy.setHeightForWidth(self.le_total_time.sizePolicy().hasHeightForWidth())
        self.le_total_time.setSizePolicy(sizePolicy)

        self.lyt_total_time.addWidget(self.le_total_time)


        self.horizontalLayout_6.addLayout(self.lyt_total_time)

        self.lyt_servings = QHBoxLayout()
        self.lyt_servings.setObjectName(u"lyt_servings")
        self.lbl_servings = QLabel(self.lyt_recipe_input)
        self.lbl_servings.setObjectName(u"lbl_servings")
        sizePolicy1.setHeightForWidth(self.lbl_servings.sizePolicy().hasHeightForWidth())
        self.lbl_servings.setSizePolicy(sizePolicy1)

        self.lyt_servings.addWidget(self.lbl_servings)

        self.le_servings = QLineEdit(self.lyt_recipe_input)
        self.le_servings.setObjectName(u"le_servings")
        sizePolicy.setHeightForWidth(self.le_servings.sizePolicy().hasHeightForWidth())
        self.le_servings.setSizePolicy(sizePolicy)

        self.lyt_servings.addWidget(self.le_servings)


        self.horizontalLayout_6.addLayout(self.lyt_servings)

        self.lyt_image = QHBoxLayout()
        self.lyt_image.setObjectName(u"lyt_image")
        self.lbl_image_path = QLabel(self.lyt_recipe_input)
        self.lbl_image_path.setObjectName(u"lbl_image_path")
        sizePolicy1.setHeightForWidth(self.lbl_image_path.sizePolicy().hasHeightForWidth())
        self.lbl_image_path.setSizePolicy(sizePolicy1)

        self.lyt_image.addWidget(self.lbl_image_path)

        self.btn_image_path = QPushButton(self.lyt_recipe_input)
        self.btn_image_path.setObjectName(u"btn_image_path")
        sizePolicy1.setHeightForWidth(self.btn_image_path.sizePolicy().hasHeightForWidth())
        self.btn_image_path.setSizePolicy(sizePolicy1)
        self.btn_image_path.setMinimumSize(QSize(0, 0))
        self.btn_image_path.setMaximumSize(QSize(75, 16777215))

        self.lyt_image.addWidget(self.btn_image_path)


        self.horizontalLayout_6.addLayout(self.lyt_image)

        self.horizontalLayout_6.setStretch(0, 5)
        self.horizontalLayout_6.setStretch(2, 1)
        self.horizontalLayout_6.setStretch(3, 1)
        self.horizontalLayout_6.setStretch(4, 1)

        self.gridLayout.addWidget(self.lyt_recipe_input, 1, 0, 1, 2)

        self.lyt_directions = QVBoxLayout()
        self.lyt_directions.setObjectName(u"lyt_directions")
        self.lbl_directions = QLabel(AddRecipes)
        self.lbl_directions.setObjectName(u"lbl_directions")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lbl_directions.sizePolicy().hasHeightForWidth())
        self.lbl_directions.setSizePolicy(sizePolicy2)
        self.lbl_directions.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.lyt_directions.addWidget(self.lbl_directions)

        self.te_directions = QTextEdit(AddRecipes)
        self.te_directions.setObjectName(u"te_directions")

        self.lyt_directions.addWidget(self.te_directions)


        self.gridLayout.addLayout(self.lyt_directions, 2, 1, 1, 1)

        self.lyt_header = QHBoxLayout()
        self.lyt_header.setSpacing(6)
        self.lyt_header.setObjectName(u"lyt_header")
        self.lbl_add_recipes = QLabel(AddRecipes)
        self.lbl_add_recipes.setObjectName(u"lbl_add_recipes")

        self.lyt_header.addWidget(self.lbl_add_recipes)

        self.btn_save_recipes = QPushButton(AddRecipes)
        self.btn_save_recipes.setObjectName(u"btn_save_recipes")
        sizePolicy1.setHeightForWidth(self.btn_save_recipes.sizePolicy().hasHeightForWidth())
        self.btn_save_recipes.setSizePolicy(sizePolicy1)
        self.btn_save_recipes.setMinimumSize(QSize(0, 0))

        self.lyt_header.addWidget(self.btn_save_recipes)


        self.gridLayout.addLayout(self.lyt_header, 0, 0, 1, 2)


        self.retranslateUi(AddRecipes)

        QMetaObject.connectSlotsByName(AddRecipes)
    # setupUi

    def retranslateUi(self, AddRecipes):
        AddRecipes.setWindowTitle(QCoreApplication.translate("AddRecipes", u"Form", None))
        self.lbl_ingredients.setText(QCoreApplication.translate("AddRecipes", u"Ingredients:", None))
        self.lbl_recipe_name.setText(QCoreApplication.translate("AddRecipes", u"Recipe Name:", None))
        self.le_recipe_name.setPlaceholderText(QCoreApplication.translate("AddRecipes", u"Enter recipe name", None))
        self.lbl_category.setText(QCoreApplication.translate("AddRecipes", u"Category:", None))
        self.cb_recipie_category.setPlaceholderText(QCoreApplication.translate("AddRecipes", u"Meal Type", None))
        self.lbl_total_time.setText(QCoreApplication.translate("AddRecipes", u"Total Time:", None))
        self.le_total_time.setPlaceholderText(QCoreApplication.translate("AddRecipes", u"e.g., 45", None))
        self.lbl_servings.setText(QCoreApplication.translate("AddRecipes", u"Servings:", None))
        self.le_servings.setPlaceholderText(QCoreApplication.translate("AddRecipes", u"e.g., 4", None))
        self.lbl_image_path.setText(QCoreApplication.translate("AddRecipes", u"Image Path:", None))
        self.btn_image_path.setText(QCoreApplication.translate("AddRecipes", u"Browse", None))
        self.lbl_directions.setText(QCoreApplication.translate("AddRecipes", u"Directions:", None))
        self.lbl_add_recipes.setText(QCoreApplication.translate("AddRecipes", u"Recipe Details", None))
        self.btn_save_recipes.setText(QCoreApplication.translate("AddRecipes", u"Save Recipe", None))
    # retranslateUi


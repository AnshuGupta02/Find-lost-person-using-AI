import sys
import io
import base64
import requests
import json

import numpy as np

from PIL import Image

from PyQt5.QtGui import QFont, QIcon, QStandardItemModel, QStandardItem, QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QMessageBox, QListView
from PyQt5.QtCore import Qt, QSize

from new_case import NewCase
from train_model import train
from match_faces import  match


class AppWindow(QMainWindow):

    def __init__(self, user):
        super(AppWindow, self).__init__()
        self.URL = "http://localhost:8000"
        self.icon_path = "../resources/icon.png"
        self.width = 820
        self.height = 600
        self.user = user

        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowTitle("Application")
        self.setFixedSize(self.width, self.height)

        # UserName Display
        username = QLabel("Hello " + self.user.title()  + ":)", self)
        username.setFont(QFont("Times", 15))
        username.setMinimumWidth(self.width-15)
        username.setMinimumHeight(60)
        username.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # button display
        new_case_btn =  QPushButton("+ New Case", self)
        new_case_btn.setFont(QFont("Times", 13))
        new_case_btn.resize(150, 50)
        new_case_btn.move(20, 5)
        new_case_btn.clicked.connect(self.new_case)

        bar = QLabel("|", self)
        bar.setFont(QFont("Times", 13))
        bar.move(173, 5)
        bar.setFixedHeight(50)

        refresh_btn = QPushButton("Refresh", self)
        refresh_btn.setFont(QFont("Times", 13))
        refresh_btn.resize(100, 50)
        refresh_btn.move(184, 5)
        refresh_btn.clicked.connect(self.refresh_model)

        match_btn = QPushButton("Match", self)
        match_btn.setFont(QFont("Times", 13))
        match_btn.resize(100, 50)
        match_btn.move(284, 5)
        match_btn.clicked.connect(self.match_from_submitted)

        bar = QLabel("|", self)
        bar.setFont(QFont("Times", 13))
        bar.move(387, 5)
        bar.setFixedHeight(50)

        submitted_case_btn = QPushButton("View Cases", self)
        submitted_case_btn.setFont(QFont("Times", 13))
        submitted_case_btn.resize(150, 50)
        submitted_case_btn.move(398, 5)
        submitted_case_btn.clicked.connect(self.view_submitted_cases)

        # confirmed_case_btn = QPushButton("Confirmed Cases", self)
        # confirmed_case_btn.setFont(QFont("Times", 13))
        # confirmed_case_btn.resize(200, 50)
        # confirmed_case_btn.move(598, 30)
        # confirmed_case_btn.clicked.connect(self.view_confirmed_cases)



        self.show()

    def new_case(self):
        self.newcase = NewCase(self.user)

    def refresh_model(self):
        out = train(self.user)
        if out["status"]:
            QMessageBox.about(self, "Success!", out["message"])
        else:
            QMessageBox.about(self, "Error", out["message"])

    def match_from_submitted(self):
        out = match()
        if out["status"]:
            self.view_cases(out["result"])
        else:
            QMessageBox.about(self, "Error", out["message"])

    def view_submitted_cases(self):
        URL = "http://localhost:8000/get_submitted_cases?submitted_by=" + self.user
        try:
            cases = json.loads(requests.get(URL).text)
            if cases == []:
                QMessageBox.about(
                    self, "No cases Found", "No cases have been submitted by you"
                )
            else:
                self.view_submitted_cases_ui(cases)
        except requests.ConnectionError as e:
            QMessageBox.about(self, "Something went wrong", str(e))

    def view_confirmed_cases(self):
        URL = "http://localhost:8000/get_confirmed_cases?submitted_by=" + self.user
        try:
            cases = json.loads(requests.get(URL).text)
            if cases == []:
                QMessageBox.about(
                    self, "No cases Found", "No cases have been confirmed by you"
                )
            else:
                self.view_submitted_cases_ui(cases)
        except requests.ConnectionError as e:
            QMessageBox.about(self, "Something went wrong", str(e))

    def view_submitted_cases_ui(self, result):
        list_ = QListView(self)
        list_.setIconSize(QSize(96, 96))
        list_.setMinimumSize(400, 380)
        list_.move(40, 95)
        model = QStandardItemModel(list_)
        model.setHorizontalHeaderLabels(['Submitted Cases'])

        for case_detail in result:
            image = self.decode_base64(case_detail[7])
            item = QStandardItem(
                " Name: "
                + case_detail[2]
                + "\n Father's Name: "
                + case_detail[3]
                + "\n Age: "
                + str(case_detail[4])
                + "\n Mobile: "
                + str(case_detail[5])
                + "\n Status: "
                + list(
                    map(
                        lambda x: "Not Found" if x == "NF" else "Found",
                        [case_detail[10]],
                    )
                )[0]
                + "\n Submission Date: "
                + case_detail[8]
            )
            image = QImage(
                image,
                image.shape[1],
                image.shape[0],
                image.shape[1] * 3,
                QImage.Format_RGB888,
            )
            icon = QPixmap(image)
            item.setIcon(QIcon(icon))
            model.appendRow(item)

        list_.setModel(model)
        list_.show()

    def change_confirmation_Status(self, case_id):
        requests.get(f"http://localhost:8000/change_found_status?case_id='{case_id}'")

    def view_cases(self, result):
        list_ = QListView(self)
        list_.setIconSize(QSize(96, 96))
        list_.setMinimumSize(400, 380)
        list_.move(40, 95)
        list_.viewMode()
        model = QStandardItemModel(list_)
        item = QStandardItem("Matched")
        model.appendRow(item)

        for case_id, submission_list in result.items():
            # Change status of Matched Case
            # requests.get(
            #     f"http://localhost:8000/change_found_status?case_id='{case_id}'"
            # )
            case_details = self.get_details(case_id, "case")
            for submission_id in submission_list:
                submission_details = self.get_details(submission_id, "public_submission")
                image = self.decode_base64(case_details[0][2])
                item = QStandardItem(
                    " Name: "
                    + case_details[0][0]
                    + "\n Father's Name: "
                    + case_details[0][1]
                    + "\n Age: "
                    + str(case_details[0][4])
                    + "\n Mobile: "
                    + str(case_details[0][3])
                    + "\n Found at: "
                    + submission_details[0][0]
                    + "\nUser Name & Contact Number: "
                    + submission_details[0][3]
                    + " & "
                    + str(submission_details[0][4])
                    +"\n Matched Date" + str(submission_details[0][1])
                )
                image = QImage(
                    image,
                    image.shape[1],
                    image.shape[0],
                    image.shape[1] * 3,
                    QImage.Format_RGB888,
                )
                icon = QPixmap(image)
                item.setIcon(QIcon(icon))
                model.appendRow(item)

        list_.setModel(model)
        list_.show()

    def get_details(self, case_id, type):
        if type == "public_submission":
            URL = f"http://localhost:8000/get_user_details?case_id='{case_id}'"
        else:
            URL = f"http://localhost:8000/get_case_details?case_id='{case_id}'"
        try:
            result = requests.get(URL)
            if result.status_code == 200:
                return json.loads(result.text)
            else:
                pass
        except Exception as e:
            raise e

    def decode_base64(self, img):
        img = np.array(Image.open(io.BytesIO(base64.b64decode(img))))
        return img


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AppWindow("admin")
    sys.exit(app.exec())


'''
import requests
import json
import base64
import io

from PIL import Image
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QListView,
    QBoxLayout,
)
from PyQt5.QtWidgets import QMessageBox, QListWidget, QLabel, QLineEdit

from new_case import NewCase
from train_model import train
from match_faces import match


class AppWindow(QMainWindow):
    def __init__(self, user):
        super(AppWindow, self).__init__()
        self.title = "Application"
        self.width = 800
        self.height = 600
        self.user = user

        self.initialize()

    def initialize(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)

        button_upload = QPushButton("New Case", self)
        button_upload.move(570, 50)
        button_upload.resize(150, 50)
        button_upload.clicked.connect(self.new_case)

        button_refresh_model = QPushButton("Refresh", self)
        button_refresh_model.resize(150, 50)
        button_refresh_model.move(570, 150)
        button_refresh_model.clicked.connect(self.refresh_model)

        button_match = QPushButton("Match", self)
        button_match.resize(150, 50)
        button_match.move(570, 250)
        button_match.clicked.connect(self.match_from_submitted)

        submitted_case_button = QPushButton("View submitted cases", self)
        submitted_case_button.resize(150, 50)
        submitted_case_button.move(570, 350)
        submitted_case_button.clicked.connect(self.view_submitted_cases)

        confirmed_case_button = QPushButton("Confirmed", self)
        confirmed_case_button.resize(150, 50)
        confirmed_case_button.move(570, 450)
        confirmed_case_button.clicked.connect(self.view_confirmed_cases)

        self.show()

    def new_case(self):
        self.new_case = NewCase(self.user)

    def refresh_model(self):
        output = train(self.user)
        if output["status"]:
            QMessageBox.about(self, "Success", output["message"])
        else:
            QMessageBox.about(self, "Error", output["message"])

    def match_from_submitted(self):
        output = match()
        if output["status"]:
            result = output["result"]
            self.view_cases(result)
        else:
            QMessageBox.about(self, "Error", output["message"])

    def view_confirmed_cases(self):
        URL = "http://localhost:8000/get_confirmed_cases?submitted_by=" + self.user
        try:
            cases = json.loads(requests.get(URL).text)
            if cases == []:
                QMessageBox.about(
                    self, "No cases Found", "No cases have been confirmed by you"
                )
            else:
                self.view_submitted_cases_ui(cases)
        except requests.ConnectionError as e:
            QMessageBox.about(self, "Something went wrong", str(e))

    def view_submitted_cases(self):
        URL = "http://localhost:8000/get_submitted_cases?submitted_by=" + self.user
        try:
            cases = json.loads(requests.get(URL).text)
            if cases == []:
                QMessageBox.about(
                    self, "No cases Found", "No cases have been submitted by you"
                )
            else:
                self.view_submitted_cases_ui(cases)
        except requests.ConnectionError as e:
            QMessageBox.about(self, "Something went wrong", str(e))

    def view_submitted_cases_ui(self, result):
        list_ = QListView(self)
        list_.setIconSize(QSize(96, 96))
        list_.setMinimumSize(400, 380)
        list_.move(40, 40)
        model = QStandardItemModel(list_)
        # model.setHorizontalHeaderLabels(['Submitted Cases'])

        for case_detail in result:
            image = self.decode_base64(case_detail[7])
            item = QStandardItem(
                " Name: "
                + case_detail[2]
                + "\n Father's Name: "
                + case_detail[3]
                + "\n Age: "
                + str(case_detail[4])
                + "\n Mobile: "
                + str(case_detail[5])
                + "\n Status: "
                + list(
                    map(
                        lambda x: "Not Found" if x == "NF" else "Found",
                        [case_detail[10]],
                    )
                )[0]
                + "\n Submission Date: "
                + case_detail[8]
            )
            image = QtGui.QImage(
                image,
                image.shape[1],
                image.shape[0],
                image.shape[1] * 3,
                QtGui.QImage.Format_RGB888,
            )
            icon = QPixmap(image)
            item.setIcon(QIcon(icon))
            model.appendRow(item)

        list_.setModel(model)
        list_.show()

    def view_cases(self, result):
        list_ = QListView(self)
        list_.setIconSize(QSize(96, 96))
        list_.setMinimumSize(400, 380)
        list_.move(40, 40)
        model = QStandardItemModel(list_)
        item = QStandardItem("Matched")
        model.appendRow(item)

        for case_id, submission_list in result.items():
            # Change status of Matched Case
            requests.get(
                f"http://localhost:8000/change_found_status?case_id='{case_id}'"
            )
            case_details = self.get_details(case_id, "case")
            for submission_id in submission_list:
                submission_details = self.get_details(
                    submission_id, "public_submission"
                )
                image = self.decode_base64(case_details[0][2])

                item = QStandardItem(
                    " Name: "
                    + case_details[0][0]
                    + "\n Father's Name: "
                    + case_details[0][1]
                    + "\n Age: "
                    + str(case_details[0][4])
                    + "\n Mobile: "
                    + str(case_details[0][3])
                    + "\n Location: "
                    + submission_details[0][0]
                    # "\n Matched Date" + submission_details[0][1]
                )
                image = QtGui.QImage(
                    image,
                    image.shape[1],
                    image.shape[0],
                    image.shape[1] * 3,
                    QtGui.QImage.Format_RGB888,
                )
                icon = QPixmap(image)
                item.setIcon(QIcon(icon))
                model.appendRow(item)

        list_.setModel(model)
        list_.show()

    def get_details(self, case_id: str, type: str):
        if type == "public_submission":
            URL = f"http://localhost:8000/get_user_details?case_id='{case_id}'"
        else:
            URL = f"http://localhost:8000/get_case_details?case_id='{case_id}'"
        try:
            result = requests.get(URL)
            if result.status_code == 200:
                return json.loads(result.text)
            else:
                pass
        except Exception as e:
            raise e

    def decode_base64(self, img: str):
        """
        Image is converted ot numpy array.
        """
        img = np.array(Image.open(io.BytesIO(base64.b64decode(img))))
        return img
'''
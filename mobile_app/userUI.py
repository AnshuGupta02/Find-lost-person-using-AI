import sys
import requests
import json
import base64
import uuid

from PyQt5.QtWidgets import QApplication, QGroupBox, QFormLayout, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QFont, QIntValidator, QRegularExpressionValidator, QPixmap
from PyQt5.QtCore import QRegularExpression, Qt


class MobileApp(QDialog):

    def __init__(self):
        super(MobileApp, self).__init__()

        self.key_points = None

        self.db_URL = "http://localhost:8000"
        self.face_encoding_URL = "http://localhost:8002"
        self.icon_path = "../resources/icon.png"

        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowTitle("Found Lost Person")
        self.font_size = 13
        self.setFixedSize(400, 700)

        self.formGroupBox = QGroupBox("Your Details")
        self.formGroupBox.setFont(QFont("Times", self.font_size))
        self.formGroupBox.setFixedWidth(375)
        self.setFixedHeight(650)

        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setFont(QFont("Times", self.font_size))
        self.upload_btn.clicked.connect(self.openFileNameDialog)

        self.name_edit = QLineEdit()

        self.mob_edit = QLineEdit()
        int_mob = QRegularExpressionValidator()
        int_mob.setRegularExpression(QRegularExpression("^[0-9]{10}$"))
        self.mob_edit.setValidator(int_mob)

        self.location_edit = QLineEdit()

        self.save_btn = QPushButton("Save")
        self.save_btn.setFont(QFont("Times", self.font_size))
        self.save_btn.clicked.connect(self.save)

        self.create_form()

        self.image_edit = QLabel(self)
        pixmap = QPixmap("../resources/Unknown_person.jpg")
        pixmap = pixmap.scaled(220, 250)
        self.image_edit.setPixmap(pixmap)
        self.image_edit.setAlignment(Qt.AlignCenter)
        self.image_edit.show()

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.image_edit)
        mainLay.addSpacing(20)
        mainLay.addWidget(self.formGroupBox)

        self.setLayout(mainLay)

        self.show()

    def create_form(self):
        layout = QFormLayout()
        layout.addRow(self.upload_btn)
        layout.addRow(QLabel("Name"), self.name_edit)
        layout.addRow(QLabel("Contact No."), self.mob_edit)
        layout.addRow(QLabel("Location"), self.location_edit)
        layout.addRow(self.save_btn)
        layout.setFormAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        self.formGroupBox.setLayout(layout)

    def save(self):
        # register case
        entries = self.get_entries()
        if entries:
            entries["face_encoding"] = self.key_points
            entries["sub_id"] = self.generate_uuid()
            self.save_to_db(entries)
        else:
            QMessageBox.about(self, "Uh no!", "Please fill all the entries.")

    def save_to_db(self, entries):
        new_url = self.db_URL + "/user_submission"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        byte_content = open(self.fileName, "rb").read()
        base64_bytes = base64.b64encode(byte_content)
        base64_string = base64_bytes.decode("utf-8")

        entries["image"] = base64_string
        try:
            res = requests.post(new_url, json.dumps(entries), headers=headers)
            if res.status_code == 200:
                QMessageBox.about(self, "Voila!", "Saved successfully")
                self.name_edit.clear()
                self.location_edit.clear()
                self.mob_edit.clear()
                pixmap = QPixmap("../resources/Unknown_person.jpg")
                pixmap = pixmap.scaled(220, 250)
                self.image_edit.setPixmap(pixmap)
                self.image_edit.setAlignment(Qt.AlignCenter)
                self.image_edit.show()

            else:
                QMessageBox.about(self, "Uh oh!", "Something went wrong while saving")
        except:
            QMessageBox.about(self, "Error", "Couldn't connect to database")

    def generate_uuid(self):
        return str(uuid.uuid4())

    def get_entries(self):
        entries = {}
        if self.name_edit.text() and self.mob_edit.text() and self.location_edit.text():
            entries["name"] = self.name_edit.text()
            entries["location"] = self.location_edit.text()
            entries["mobile"] = self.mob_edit.text()
        return entries

    def openFileNameDialog(self):
        # upload image function
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "jpg file (*.jpg)",
            options=options,
        )
        if self.fileName:
            self.key_points = self.get_facial_points(self.fileName)
            if self.key_points:
                pixmap = QPixmap(self.fileName)
                pixmap = pixmap.scaled(220, 250)
                self.image_edit.setPixmap(pixmap)
                self.image_edit.show()

    def get_facial_points(self, image_url):
        """
                This method passes the base64 form image to get facial key points.
                Returns: list
        """
        new_url = self.face_encoding_URL + "/image"
        f = [("image", open(image_url, "rb"))]
        try:
            result = requests.post(new_url, files=f)
            if result.status_code == 200:
                return json.loads(result.text)["encoding"]
            else:
                QMessageBox.about(self, "Oops!", "Couldn't find face in Image")
        except:
            QMessageBox.about(self, "Error", "Couldn't connect to face encoding API")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MobileApp()
    sys.exit(app.exec())


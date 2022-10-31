import sys
import requests
import json
import base64

from utils import generate_uuid

from PyQt5.QtWidgets import QApplication, QGroupBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QFont, QIntValidator, QRegularExpressionValidator, QPixmap
from PyQt5.QtCore import QRegularExpression


class NewCase(QDialog):

    def __init__(self, user):
        super(NewCase, self).__init__()

        self.key_points = None
        self.user = user

        self.db_URL = "http://localhost:8000"
        self.face_encoding_URL = "http://localhost:8002"
        self.icon_path = "../resources/icon.png"

        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowTitle("Registration")

        self.formGroupBox = QGroupBox("Register New Case")
        self.formGroupBox.setFont(QFont("Times", 15))
        self.formGroupBox.setFixedWidth(400)

        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setFont(QFont("Times", 15))
        self.upload_btn.clicked.connect(self.openFileNameDialog)

        self.name_edit = QLineEdit()

        self.age_edit = QLineEdit()
        int_age = QIntValidator()
        int_age.setRange(0, 200)
        self.age_edit.setValidator(int_age)

        self.father_edit = QLineEdit()

        self.mob_edit = QLineEdit()
        int_mob = QRegularExpressionValidator()
        int_mob.setRegularExpression(QRegularExpression("^[0-9]{10}$"))
        self.mob_edit.setValidator(int_mob)

        self.save_btn = QPushButton("Save")
        self.save_btn.setFont(QFont("Times", 15))
        self.save_btn.clicked.connect(self.save)

        self.create_form()

        self.image_edit = QLabel(self)
        pixmap = QPixmap("../resources/Unknown_person.jpg")
        pixmap = pixmap.scaled(220, 250)
        self.image_edit.setPixmap(pixmap)
        self.image_edit.show()

        mainLay = QHBoxLayout()
        mainLay.addWidget(self.formGroupBox)
        mainLay.addSpacing(20)
        mainLay.addWidget(self.image_edit)
        mainLay.addSpacing(10)

        self.setLayout(mainLay)

        self.show()

    def create_form(self):
        layout = QFormLayout()
        layout.addRow(self.upload_btn)
        layout.addRow(QLabel("Name"), self.name_edit)
        layout.addRow(QLabel("Age"), self.age_edit)
        layout.addRow(QLabel("Father's Name"), self.father_edit)
        layout.addRow(QLabel("Mobile No."), self.mob_edit)
        layout.addRow(self.save_btn)
        self.formGroupBox.setLayout(layout)

    def save(self):
        # register case
        entries = self.get_entries()
        if entries:
            entries["face_encoding"] = self.key_points
            entries["submitted_by"] = self.user
            entries["case_id"] = generate_uuid()
            self.save_to_db(entries)
        else:
            QMessageBox.about(self, "Uh no!", "Please fill all the entries.")

    def save_to_db(self, entries):
        new_url = self.db_URL + "/new_case"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        byte_content = open(self.fileName, "rb").read()
        base64_bytes = base64.b64encode(byte_content)
        base64_string = base64_bytes.decode("utf-8")

        entries["image"] = base64_string
        try:
            res = requests.post(new_url, json.dumps(entries), headers=headers)
            if res.status_code == 200:
                QMessageBox.about(self, "Voila!", "Saved successfully")
                self.close()
            else:
                QMessageBox.about(self, "Uh oh!", "Something went wrong while saving")
        except:
            QMessageBox.about(self, "Error", "Couldn't connect to database")

    def get_entries(self):
        entries = {}
        if self.name_edit.text() and self.age_edit.text() and self.father_edit.text() and self.mob_edit.text():
            entries["age"] = self.age_edit.text()
            entries["name"] = self.name_edit.text()
            entries["father_name"] = self.father_edit.text()
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
    w = NewCase("admin")
    sys.exit(app.exec())

# import sys
# import requests
# import base64
# import json
#
# from PIL import Image
# from PyQt5.QtGui import QPixmap, QImage, QImageReader
# from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication
# from PyQt5.QtWidgets import QInputDialog, QLabel, QLineEdit, QMessageBox
#
# from utils import generate_uuid
#
#
# class NewCase(QMainWindow):
#     """
#     This class is a subpart of main window.
#     The purpose of this class is to register a new case and
#     save it in Firebase Database.
#
#     After selecting the image you'll see in left side of window.
#     If you are able to see image that means algo is able to find
#     facial points in image. Otherwise you'll get error.
#
#     If you encounter any error while saving the image, check the logs
#     which are being printed.
#     """
#
#     def __init__(self, user: str):
#         """
#         We are initializing few things we would need.
#             name -> Name of person whose case has to be registered.
#             age -> Age of the person
#             mob -> Mobile number that will be contacted after the person is found.
#             father_name -> Father's name of the person
#             image -> image of the person
#
#         Args:
#             user: str
#                 The logged in user
#         """
#         super().__init__()
#         self.title = "Register New Case"
#         self.name = None
#         self.age = None
#         self.mob = None
#         self.father_name = None
#         self.image = None
#         self.encoded_image = None
#         self.key_points = None
#         self.user = user
#         self._x_axis = 500
#         self.initialize()
#
#     def initialize(self):
#         """
#         This method contains button to select the image and
#         also register the case.
#
#         The select image button is connected to openFileNameDialog method.
#
#         The save button is connected to save method (within the class).
#
#         -> If you are changing the window size make sure to align the buttons
#             correctly.
#         """
#         self.setFixedSize(800, 600)
#         self.setWindowTitle(self.title)
#
#         upload_image_button = QPushButton("Upload Image", self)
#         upload_image_button.resize(150, 50)
#         upload_image_button.move(self._x_axis, 20)
#         upload_image_button.clicked.connect(self.openFileNameDialog)
#
#         save_button = QPushButton("Save", self)
#         save_button.resize(150, 50)
#         save_button.move(self._x_axis, 350)
#         save_button.clicked.connect(self.save)
#
#         self.get_name()
#         self.get_age()
#         self.get_fname()
#         self.get_mob()
#         self.show()
#
#     def get_name(self):
#         """
#         This method reads the input name from text field in GUI.
#         """
#         self.name_label = QLabel(self)
#         self.name_label.setText("Name:")
#         self.name_label.move(self._x_axis, 100)
#         self.name = QLineEdit(self)
#         self.name.move(self._x_axis + 50, 100)
#
#     def get_age(self):
#         """
#         This method reads the age from text field in GUI.
#         """
#         self.age_label = QLabel(self)
#         self.age_label.setText("Age:")
#         self.age_label.move(self._x_axis, 150)
#
#         self.age = QLineEdit(self)
#         self.age.move(self._x_axis + 50, 150)
#
#     def get_fname(self):
#         """
#         This method reads Father's name from text field in GUI.
#         """
#         self.fname_label = QLabel(self)
#         self.fname_label.setText("Father's\n Name:")
#         self.fname_label.move(self._x_axis, 200)
#
#         self.father_name = QLineEdit(self)
#         self.father_name.move(self._x_axis + 50, 200)
#
#     def get_mob(self):
#         """
#         This method reads mob number from text field in GUI.
#         """
#         self.mob_label = QLabel(self)
#         self.mob_label.setText("Mobile:")
#         self.mob_label.move(self._x_axis, 250)
#
#         self.mob = QLineEdit(self)
#         self.mob.move(self._x_axis + 50, 250)
#
#     def get_facial_points(self, image_url) -> list:
#         """
#         This method passes the base64 form iamge to get facialkey points.
#
#         Returns
#         -------
#          list
#         """
#         URL = "http://localhost:8002/image"
#         f = [("image", open(image_url, "rb"))]
#         try:
#             result = requests.post(URL, files=f)
#             if result.status_code == 200:
#                 return json.loads(result.text)["encoding"]
#             else:
#                 QMessageBox.about(self, "Error", "Couldn't find face in Image")
#                 return None
#         except Exception as e:
#             QMessageBox.about(self, "Error", "Couldn't connect to face encoding API")
#             return None
#
#     def openFileNameDialog(self):
#         """
#         This method is triggered on button click to select image.
#
#         When an image is selected its local URL is captured.
#         After which it is passed through read_image method.
#         Then it is converted to base64 format and facial keypoints are
#         generated for it.
#
#         If keypoints are not found in the image then you'll get a dialogbox.
#         """
#         options = QFileDialog.Options()
#         self.fileName, _ = QFileDialog.getOpenFileName(
#             self,
#             "QFileDialog.getOpenFileName()",
#             "",
#             "jpg file (*.jpg)",
#             options=options,
#         )
#
#         if self.fileName:
#             self.key_points = self.get_facial_points(self.fileName)
#             if self.key_points:
#                 label = QLabel(self)
#                 pixmap = QPixmap(self.fileName)
#                 pixmap = pixmap.scaled(320, 350)
#                 label.setPixmap(pixmap)
#                 label.resize(310, 350)
#                 label.move(50, 50)
#                 label.show()
#
#     def get_entries(self):
#         """
#         A check to make sure empty fields are not saved.
#         A case will be uniquely identified by these fields.
#         """
#         entries = {}
#         if (
#             self.age.text() != ""
#             and self.mob.text() != ""
#             and self.name != ""
#             and self.father_name != ""
#         ):
#             entries["age"] = self.age.text()
#             entries["name"] = self.name.text()
#             entries["father_name"] = self.father_name.text()
#             entries["mobile"] = self.mob.text()
#             return entries
#         else:
#             return None
#
#     def save_to_db(self, entries):
#         URL = "http://localhost:8000/new_case"
#         headers = {"Content-Type": "application/json", "Accept": "application/json"}
#
#         byte_content = open(self.fileName, "rb").read()
#         base64_bytes = base64.b64encode(byte_content)
#         base64_string = base64_bytes.decode("utf-8")
#
#         entries["image"] = base64_string
#         try:
#             res = requests.post(URL, json.dumps(entries), headers=headers)
#             if res.status_code == 200:
#                 QMessageBox.about(self, "Success", "Saved successfully")
#             else:
#                 QMessageBox.about(self, "Error", "Something went wrong while saving")
#         except Exception as e:
#             QMessageBox.about(self, "Error", "Couldn't connect to database")
#
#     def save(self):
#         """
#         Save method is triggered with save button on GUI.
#
#         All the parameters are passed to a db methods whose task is to save
#         them in db.
#
#         If the save operation is successful then you'll get True as output and
#         a dialog message will be displayed other False will be returned and
#         you'll get appropriate message.
#
#         """
#         entries = self.get_entries()
#         if entries:
#             entries["face_encoding"] = self.key_points
#             entries["submitted_by"] = self.user
#             entries["case_id"] = generate_uuid()
#             self.save_to_db(entries)
#         else:
#             QMessageBox.about(self, "Error", "Please fill all entries")
#
#
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import seaborn as sns
import traceback, sys
import pickle
import sys
from PyQt5 import QtCore
import scraper2

import csv
import sys
import numpy as np
import numpy.linalg as LNG
from bokeh.plotting import gmap
from bokeh.models import GMapOptions
from bokeh.io import show, output_file

import gmaps
import gmaps.datasets
import requests


import math
from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, QPushButton, QVBoxLayout,QMainWindow
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

from PyQt5.QtCore import pyqtSlot
import time
from os.path import isfile, join, dirname, realpath

from pandas import ExcelWriter
import pandas as pd
from shutil import copyfile


import numpy as np
import time

class BackEnd(QtCore.QThread):
    # CLass for BACKEND processes
    ask_location_trigger = QtCore.pyqtSignal()
    display_trigger = QtCore.pyqtSignal(str,object)
    update_journey = QtCore.pyqtSignal()

    top_words_trigger = QtCore.pyqtSignal(list,list,object)
    predictions_trigger = QtCore.pyqtSignal()
    counter = QtCore.pyqtSignal(int)
    trigger = QtCore.pyqtSignal(str)
    top_label_init = QtCore.pyqtSignal(dict)
    plot = QtCore.pyqtSignal()
    plot_trigger = QtCore.pyqtSignal(dict)
    search_results_trigger = QtCore.pyqtSignal(object,object)
    update_table_trigger = QtCore.pyqtSignal()
    sort_trigger = QtCore.pyqtSignal(object,object)

    API = '' #Insert API here
    google_api = "https://maps.googleapis.com/maps/api/directions/json?"




    def __init__(self):
        QtCore.QThread.__init__(self)

        #self.update_table = False
        self.returned = False


    def find_place(self,name):
        modified_name = name.replace(',', '')
        modified_name = '+'.join(modified_name.split(sep=' '))
        modified_name += "hong+kong"

        response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={modified_name}&key={self.API}')
        resp_json_payload = response.json()
        lat = resp_json_payload['results'][0]['geometry']['location']['lat']
        lng = resp_json_payload['results'][0]['geometry']['location']['lng']

        return lat, lng


    def safest_route(self,start, finish):

        with open('secondary_data.csv',encoding='utf-8') as fnew:
            secondary_data = {}
            reader_new = csv.reader(fnew)
            for row in reader_new:
                secondary_data[row[0]] = {'lat': row[1], 'lng': row[2], 'cases': row[3]}

        startlat, startlng = self.find_place(start)
        endlat, endlng = self.find_place(finish)

        response = requests.get(
            self.google_api + f'origin={startlat},{startlng}&destination={endlat},{endlng}&key={self.API}&mode=walking&alternatives=true')
        resp_json_payload = response.json()

        all_coords = []

        for i in range(len(resp_json_payload['routes'])):
            path_coords = []
            for dot in resp_json_payload['routes'][i]['legs'][0]['steps']:
                lat_end = dot['end_location']['lat']
                lng_end = dot['end_location']['lng']
                lat_start = dot['start_location']['lat']
                lng_start = dot['start_location']['lng']
                path_coords.append((lat_end, lng_end))
                path_coords.append((lat_start, lng_start))

            all_coords.append(path_coords)

        lim = 0.0009 / 2
        l = lim * np.sqrt(2)

        path_scores = []
        # max_covid_cases = sum([])
        path_option = 0
        for coords in all_coords:
            total_score = 0
            for point in coords:
                lat_min = point[0] - lim
                lat_max = point[0] + lim
                lng_min = point[1] - lim
                lng_max = point[1] + lim

                for key, item in secondary_data.items():
                    if lat_min < item['lat'] < lat_max and lng_min < item['lng'] < lng_max:
                        lat_diff = abs(item['lat'] - point[0])
                        lng_diff = abs(item['lng'] - point[1])
                        d = LNG.norm([lat_diff, lng_diff])
                        score = (l - d) / l
                        # print(f'cases = {item["cases"]}')
                        score *= item['cases']
                        # print(f'scores ={score}')
                        total_score += score

            path_option += 1
            print(
                f'Path {path_option}: On Average you might encounter, {round(total_score, 2)} cases while walking from {start} to {finish}')
            path_scores.append(total_score)

        safest_path = np.argmin(path_scores) + 1

        print('Safest path is path', safest_path)
        return all_coords

    def plot_options(self,all_coords, zoom=15, map_type='roadmap'):
        bokeh_width, bokeh_height = 500, 400

        all_lats = []
        all_lngs = []

        for coords in all_coords:
            lats = []
            lngs = []

            for lat, lng in coords:
                lats.append(lat)
                lngs.append(lng)

            all_lats.append(lat)
            all_lngs.append(lng)

        gmap_options = GMapOptions(lat=lats[0], lng=lngs[0], map_type=map_type, zoom=zoom)

        p = gmap(self.API, gmap_options, title='Route Map', width=bokeh_width, height=bokeh_height)
        colour_code = ['red', 'yellow', 'blue', 'green', 'orange']

        for i in range(len(all_coords)):
            for lat, lng in all_coords[i]:
                p.circle([lng], [lat], size=10, alpha=0.5, color=colour_code[i])
            # p.line(lng,lat, line_color=colour_code[i])

        output_file('legend2.html')

        show(p)
        return all_coords



    def get_map(self,start='hysan place',end='pacific place'):
        self.plot_options(self.safest_route(start,end))



    def run(self):

        self.ask_location_trigger.emit()
        print('hello')
        while not self.returned:
            time.sleep(0.5)
        self.returned = False
        location = self.data['location']
        headings_sent = scraper2.return_df()
        print(headings_sent)

        self.display_trigger.emit(location,headings_sent)
        while not self.returned:
            time.sleep(0.5)
        self.returned = False
        string = self.data
        string = string.split(',')
        start = string[0]
        end = string[1]
        self.get_map(start,end)
        self.update_journey.emit()



class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(1200, 700)
        self.showMaximized()
        self.setStyleSheet("MainWindow {background-color: #F0F8FF ;color: white;padding-left: 4px;border: 1px solid #6c6c6c;"
                           "spacing: 3px; }")

        self.image_path = 'map.PNG'

        self.data_dict = {}

        # self.setFixedSize(1200,700)
        self.setWindowIcon(QtGui.QIcon('algomo.png'))
        self.info = QLabel('Info...', self)
        self.info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.info.setStyleSheet(
            "QLabel {background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d7801a, stop:0.5 #b56c17 stop:1 #ffa02f); font-size:25px;  font-family: 'Open Sans', sans-serif; text-align:center;}")

        self.layout = QVBoxLayout()

        self.setWindowTitle('COVID Feed')
        self.title = QLabel('COVID Updates ', self)
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.title.setAlignment(Qt.AlignHCenter)

        self.title.setStyleSheet(
            "QLabel {background-color: #F0F8FF ;color:darkBlue; font-family: Avantgarde; text-align:center;font-size:30px; font-weight:bold;}")

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.title)

        self.setLayout(self.layout)
        self.run_backend()

    def deleteWidget(self, layout, widget):
        layout.removeWidget(widget)
        widget.deleteLater()
        widget = None

    def update_map(self):
        self.journey_map = QWebView()
        self.journey_map.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.journey_map.load(QUrl.fromLocalFile(QDir.current().absoluteFilePath('legend2.html')))
        self.tabs_widget.tab2.layout.addWidget(self.journey_map)


    def display(self,location,headings_df,num_articles = 10):
        print(headings_df)
        self.map_image = QLabel()

        pixmap = QtGui.QPixmap(self.image_path)
        self.map_image.setPixmap(pixmap)
        self.location_box = TextBox('Enter your postcode', self)
        self.location_box.clicked.connect(self.location_box.selectAll)
        self.location_box.returnPressed.connect(self.set_location)
        #self.layout.addWidget(self.map_image, 0, Qt.AlignCenter)

        self.tabs_widget = MyTableWidget(self)
        self.tabs_widget.setStyleSheet("QWidget {background-color: #e6f0ff}")


        self.layout.addWidget(self.tabs_widget)
        self.maps_tabs = MapsWidget(self)
        #self.maps_tabs.setStyleSheet("QWidget {background-color:#b8dbff}")
        self.maps_tabs.setStyleSheet("QWidget {background-color:white;} ")
        self.maps_tabs.setFixedSize(1400,700)
        self.map = QWebView()

        self.map.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.map.load(QUrl.fromLocalFile(QDir.current().absoluteFilePath('export.html')))

        self.maps_tabs.tab1.layout.addWidget(self.map,0,Qt.AlignHCenter)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.maps_tabs)
        #self.h_layout.addWidget(QLabel('test'))

        self.journey_map = QWebView()
        self.journey_map.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.journey_map.load(QUrl.fromLocalFile(QDir.current().absoluteFilePath('legend.html')))

        self.location_box = TextBox('Enter start and end location, seperated by comma',self)
        self.location_box.clicked.connect(self.location_box.selectAll)
        self.location_box.returnPressed.connect(self.update_location)



        self.articles_table = QTableWidget(num_articles, 2)
        self.map.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.articles_table.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.map.setFixedSize(1400,800)
        header = self.articles_table.horizontalHeader()
        #header.setStretchLastSection(True)
        #self.articles_table.verticalHeader().setStretchLastSection(True)
        self.articles_table.setFixedSize(400,700)
        #self.map.resize(700,500)
        #self.articles_table.resize(400,500)



        for i,headings_sent in enumerate(zip(headings_df.Heading,headings_df.Sentiment)):
            heading, sentiment = headings_sent
            print(heading,sentiment)
            self.articles_table.setItem(i,0,QTableWidgetItem(heading))
            self.articles_table.setItem(i, 1, QTableWidgetItem(str(sentiment)))

        header = self.articles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        #header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        #self.articles_table.resizeColumnsToContents()
        self.articles_table.resizeRowsToContents()
        self.articles_table.setColumnWidth(1,80)

        self.articles_table.setAutoScroll(False)
        #self.articles_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.articles_table.setHorizontalHeaderLabels(('Title', 'Sentiment'))
        self.articles_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        articles_layout = QVBoxLayout()
        table_title= QLabel('Latest Headlines')
        table_title.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        table_title.setStyleSheet("QLabel {background-color:#e6f0ff; font-size:25px;font-weight:bold;  font-family: 'Open Sans', sans-serif; text-align:center;}")
        articles_layout.addWidget(table_title)
        articles_layout.addWidget(self.articles_table)
        self.articles_table.setFrameStyle(QFrame.NoFrame)
        self.h_layout.addLayout(articles_layout)

        self.tabs_widget.tab1.layout.addLayout(self.h_layout)
        self.tabs_widget.tab2.layout.addWidget(self.journey_map)
        self.tabs_widget.tab2.layout.addWidget(self.location_box)

        self.map.setStyleSheet(
            "QWebEngineView { background-color: #F0F8FF;padding: 1px; border-style: solid; border: 1px solid #1e1e1e;border-radius: 5; }")

        self.articles_table.setStyleSheet("QTableWidget { background-color: #F0F8FF;padding: 1px; border-style: solid; border: 1px solid #1e1e1e;border-radius: 5; }")


        #self.tabs_widget.tab1.layout.addWidget(self.map)
        self.layout.addWidget(self.location_box)

    def update_location(self):
        self.back_end.data = str(self.location_box.text())
        print('3')
        self.deleteWidget(self.layout,self.journey_map)



        print('3')
        self.back_end.returned = True

    def set_location(self):
        self.data_dict['location'] = str(self.location_box.text())
        print('3')
        self.deleteWidget(self.layout,self.location_box)
        self.back_end.data = self.data_dict
        print('3')
        self.back_end.returned = True

    def ask_location(self):
        self.location_box = TextBox('Enter your postcode', self)
        self.location_box.clicked.connect(self.location_box.selectAll)
        self.location_box.returnPressed.connect(self.set_location)
        self.layout.addWidget(self.location_box, 0, Qt.AlignCenter)



    def run_backend(self):
        self.threads = []

        self.back_end = BackEnd()
        self.threads.append(self.back_end)
        self.back_end.ask_location_trigger.connect(self.ask_location)
        self.back_end.display_trigger.connect(self.display)
        self.back_end.update_journey.connect(self.update_map)
        self.back_end.start()

class TextBox(QLineEdit):
    clicked = pyqtSignal()
    def __init__(self,name, parent):
        super().__init__(name,parent)


    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()

class MapsWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(600, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "By COVID Cases")
        self.tabs.addTab(self.tab2, "By Overall Risk")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.layout = QVBoxLayout(self)
        self.tab2.setLayout(self.tab2.layout)


        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "Hong Kong Heatmap")
        self.tabs.addTab(self.tab2, "Journey Safety")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.layout = QVBoxLayout(self)
        self.tab2.setLayout(self.tab2.layout)


        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())



app = QApplication(sys.argv)
window = MainWindow()
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook
#window.showMaximized()
try:
    app.exec_()
except Exception as e:
    print(e)


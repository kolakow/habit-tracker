style = '''
    QLineEdit {
        padding: 10 10px;
    }

    QPushButton {
        background-color: white;
        height: 25%;
    }

    QPushButton#edit {
        max-width: 100%
    }

    QPushButton#remove {
        max-width: 50%
    }

    QCheckBox#check {
        font-size: 18px;
        spacing: 10px;
    }

    QCheckBox::indicator#check {
    }

    '''

import sys
import time
import datetime
from PyQt5 import QtWidgets, QtGui, QtCore #
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QSettings

settings = QSettings('habitApp', 'App') #Used to store/restore settings (window, habits, and date)
habits_list = settings.value('habits') #Load habits from previous use

class setupWindow(QWidget): #Used to setup/edit habits
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        settings.setValue('window', 'setup_window') #Update state for future use
        self.init_ui() #Initialize widget
    
    def init_ui(self): #Initialize UI
        QWidget.__init__(self) #Create blank widget 
        self.showMaximized() #Maximize window
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet(style) #Set CSS style

        width = self.width()
        height = self.height()

        self.vlayout = QVBoxLayout()

        print('Habits in setup...', settings.value('habits'))

        self.text = QLineEdit() #Habit name
        # reg_ex = QtCore.QRegExp("[A-Za-z.-2 0-9]{0,30}") #Restrict input to numbers, letters, and spaces
        # validate = QtGui.QRegExpValidator(reg_ex, self.text)
        # self.text.setValidator(validate)
        self.vlayout.addWidget(self.text)

        self.hlayout = QHBoxLayout()

        self.save = QPushButton('Save', self) #Saves all habits and goes to new habitsWindow()
        self.save.clicked.connect(self.saveHabits)

        self.add = QPushButton('Add Habit', self) #Adds habit to vlayout
        self.add.clicked.connect(self.addCheckbox)

        self.hlayout.addWidget(self.save) 
        self.hlayout.addWidget(self.add)

        self.vlayout.addLayout(self.hlayout)
        self.vlayout.addStretch(1)

        if(settings.value('habits') != None): #Restore habits from previous session
            print('Restoring saved habits...')

            for habit in settings.value('habits'):
                self.checkBox = QCheckBox(habit)
                self.checkBox.setObjectName('check')
                self.removeBox = QPushButton("X", self)
                self.removeBox.setObjectName('remove')
                self.hlayout = QHBoxLayout()
                self.hlayout.addWidget(self.checkBox)
                self.hlayout.addWidget(self.removeBox)

                self.removeBox.clicked.connect(self.checkBox.deleteLater)
                self.removeBox.clicked.connect(self.removeBox.deleteLater)
                self.removeBox.clicked.connect(self.hlayout.deleteLater)

                self.vlayout.addLayout(self.hlayout)


        self.vlayout.setContentsMargins(width * .25, height * .25, width * .25, height * .25)
        # self.vlayout.setAlignment(Qt.AlignTop)
        self.vlayout.addStretch(20)
        self.setLayout(self.vlayout)
        self.text.setFocus()

    def addCheckbox(self): #Adds new habit with checkbox and button for deletion
        if(self.text.text() == ""): #If empty, return error
            message = QMessageBox()
            message.setWindowFlags(QtCore.Qt.Popup)
            message.setText("Unnamed habits cannot be added.")
            message.exec_()
            return
        elif(self.text.text() in habits_list): #If duplicate, return error
            message = QMessageBox()
            message.setWindowFlags(QtCore.Qt.Popup)
            message.setText("Duplicate habits cannot be added.")
            message.exec_()
            return
        elif((len(self.vlayout.findChildren(QHBoxLayout)) + 2) > 12):
            message = QMessageBox()
            message.setWindowFlags(QtCore.Qt.Popup)
            message.setText("Only 10 habits can be added at a time.")
            message.exec_()
            return

        self.checkBox = QCheckBox(self.text.text()) #Habit checkbox
        self.checkBox.setObjectName('check')

        self.removeBox = QPushButton("X", self) #Delete button
        self.removeBox.setObjectName('remove')

        self.text.clear() #Clear text input

        self.hlayout = QHBoxLayout() #Add widgets to hbox
        self.hlayout.addWidget(self.checkBox)
        self.hlayout.addWidget(self.removeBox)

        self.removeBox.clicked.connect(self.checkBox.deleteLater) #Delete widgets and hbox upon press of delete button
        self.removeBox.clicked.connect(self.removeBox.deleteLater)
        self.removeBox.clicked.connect(self.hlayout.deleteLater)

        position = len(self.vlayout.findChildren(QHBoxLayout)) + 2 #Grab all hboxes
        self.vlayout.insertLayout(position, self.hlayout) #Insert new hbox below them

    def saveHabits(self): #Saves habits to settings and opens habits window
        widgets = []

        for i in self.vlayout.children(): #Store all widgets
            widgets.append(i)

        if(len(widgets) > 1 or widgets == None):
            habitList = self.findChildren(QtWidgets.QCheckBox) #Grab all habits
            habits_list = []

            for habit in habitList: #Save habits into a list
                if(habit.text() not in habits_list):
                    habits_list.append(habit.text())

            settings.setValue('habits', habits_list) #Save habit_list for future use
            settings.setValue('window', 'habit_window')

            self.close() #Close setup window, and open habits window
            self.window = habitsWindow()
            self.window.show()
        else: #Else, print error
            message = QMessageBox()
            message.setWindowFlags(QtCore.Qt.Popup)
            message.setText("Cannot save! Please add a habit before saving.")
            message.exec_()

class habitsWindow(QWidget): #Used to complete habits and reset on a new day
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self) #Create blank widget

        if(settings.value('window') == 'complete_window' and settings.value('date') == datetime.date.today()): #If habits are completed and day hasn't changed, keep waiting
            self.waiting()

        self.init_ui()

    def init_ui(self): #Initialize UI
        self.showMaximized() #Maximize window
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet(style) #Set CSS style

        width = self.width()
        height = self.height()

        print('Habits window...', settings.value('habits'))
        
        habits_list = settings.value('habits') #Import saved habits

        self.vlayout = QVBoxLayout()

        self.done = QPushButton('Done', self) #Sets window to completed if all habits are done
        self.done.clicked.connect(self.habitsDone)

        self.edit = QPushButton('Edit', self) #Goes back to setup_window to edit habits
        self.edit.setObjectName('edit')
        self.edit.clicked.connect(self.editHabits)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.done)
        self.hlayout.addWidget(self.edit)

        self.vlayout.addLayout(self.hlayout)

        for habit in habits_list: #Import habits as checkboxes
            self.checkBox = QCheckBox(habit)
            self.checkBox.setObjectName('check')
            self.vlayout.addWidget(self.checkBox)

        self.vlayout.setContentsMargins(width * .25, height * .25, width * .25, height * .25)

        self.setLayout(self.vlayout)
        self.vlayout.addStretch(20)

    def editHabits(self, event): #Close habitsWindow() and open setupWindow() for habit modification
        self.close()
        self.window = setupWindow()
        self.window.show()

    def habitsDone(self, event): #Check if all habits are done
        check = self.findChildren(QtWidgets.QCheckBox) #Grab all checkboxes
        checked = [] #Save checked boxes
        unchecked = [] #Save unchecked boxes

        for checkbox in check: #If checked add to checked, otherwise add to unchecked
            if(checkbox.isChecked()):
                checked.append(checkbox)
            else:
                unchecked.append(checkbox)

        if(len(check) == len(checked)): #Confirm all habits are checked
            message = QMessageBox()
            message.setWindowFlags(QtCore.Qt.Popup)
            message.setText("Good job! See you tomorrow.")
            message.exec_()

            settings.setValue('date', datetime.date.today()) #Save today's date
            settings.setValue('window', 'complete_window') #Change state to complete

            for checkbox in check: #Uncheck all boxes
                checkbox.setCheckState(False)

            self.showMinimized() #Minimize window
            self.close()
            self.waiting() #Wait for a new day

        else: #If not, show which aren't checked off
            unfinished_habits = ["\n"]

            for checkbox in unchecked: #Grab all unfinished habits
                unfinished_habits.append(checkbox.text())

            message = QMessageBox() #Show which habits need to be completed
            messageText = "The following habits need to be completed: " + '\n- '.join(unfinished_habits) 
            message.setWindowFlags(QtCore.Qt.Popup)
            message.setText(messageText)
            message.exec_()

    def waiting(self): #Waits for the day to change to restore habits window
        self.close() #Close prior window

        while True: #Check every minute if the day has changed
            time.sleep(60) 
            current_time = datetime.date.today()
        
            if(settings.value('date') != current_time): #Once the date has changed, set window back to habit_window
                settings.setValue('window', 'habit_window')
                self.window = habitsWindow()
                self.window.show()
                break

def main():
    application = QApplication(sys.argv) #Create app

    #Restore window from previous session
    if(settings.value('window') == 'setup_window'):
        w = setupWindow()
        w.show()
    elif(settings.value('window') == 'habit_window' or settings.value('window') == 'complete_window'):
        w = habitsWindow()
        w.show()

    sys.exit(application.exec_()) #Run app

if __name__ == '__main__':
    main()

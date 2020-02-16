#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from GUI import App
from camera import camera_loop
from threading import Thread

from PyQt5.QtWidgets import QApplication
if __name__ == '__main__':

    config_dict = {}
    config_dict['source'] = 0



    camera_processing_thread = Thread(target=camera_loop,
                                      name='Camera Processing Thread',
                                      kwargs=config_dict)
    camera_processing_thread.start()

    app = QApplication(sys.argv)

    ex = App()

    sys.exit(app.exec_())

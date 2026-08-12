import cv2
import numpy as np
import filters
import os

from tkinter import Tk
from tkinter import filedialog

from managers import WindowManager, CaptureManager
from storage import StorageManager


class Cameo(object):

    def __init__(self):
        self._windowManager = WindowManager(
            'Cameo',
            self.onKeypress
        )

        self._storageManager = StorageManager()

        self._captureManager = CaptureManager(
            cv2.VideoCapture(0),
            self._windowManager,
            False
        )

        self._curveFilter = filters.BGRPortraCurveFilter()

        self._currentMode = 1
        self._settingsOpen = False
        self._buttonAreas = {}

        self._modeNames = {
            1: 'Original',
            2: 'Stroke Edges',
            3: 'Portra Filter',
            4: 'Canny Edges',
            5: 'Contours',
            6: 'Circle Detection',
            7: 'Canny + Contours',
            8: 'All Effects'
        }

        self._windowManager.createWindow()

        cv2.setMouseCallback(
            'Cameo',
            self._onMouse
        )

    def run(self):
        while self._windowManager.isWindowCreated:

            self._captureManager.enterFrame()

            frame = self._captureManager.frame

            if frame is not None:

                self._applyCurrentMode(frame)

                if self._settingsOpen:
                    self._drawSettings(frame)
                else:
                    self._drawMainUI(frame)

            self._captureManager.exitFrame()

            self._windowManager.processEvents()

        if self._captureManager.isWritingVideo:
            self._captureManager.stopWritingVideo()

        self._captureManager._capture.release()

        cv2.destroyAllWindows()

    def _applyCurrentMode(self, frame):

        if self._currentMode == 1:
            return

        elif self._currentMode == 2:
            filters.strokeEdges(
                frame,
                frame
            )

        elif self._currentMode == 3:
            self._curveFilter.apply(
                frame,
                frame
            )

        elif self._currentMode == 4:

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            edges = cv2.Canny(
                gray,
                50,
                150
            )

            frame[:] = cv2.cvtColor(
                edges,
                cv2.COLOR_GRAY2BGR
            )

        elif self._currentMode == 5:
            self._drawContours(frame)

        elif self._currentMode == 6:
            self._detectCircles(frame)

        elif self._currentMode == 7:
            self._drawContours(frame)

        elif self._currentMode == 8:

            filters.strokeEdges(
                frame,
                frame
            )

            self._curveFilter.apply(
                frame,
                frame
            )

            self._drawContours(frame)

            self._detectCircles(frame)

    def _drawContours(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        edges = cv2.Canny(
            blurred,
            50,
            150
        )

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            if area > 100:

                cv2.drawContours(
                    frame,
                    [contour],
                    -1,
                    (0, 255, 0),
                    2
                )

    def _detectCircles(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        blurred = cv2.GaussianBlur(
            gray,
            (9, 9),
            2
        )

        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=30,
            param1=100,
            param2=35,
            minRadius=10,
            maxRadius=250
        )

        if circles is not None:

            circles = np.round(
                circles[0, :]
            ).astype(int)

            for x, y, radius in circles:

                cv2.circle(
                    frame,
                    (x, y),
                    radius,
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    frame,
                    (x, y),
                    3,
                    (0, 0, 255),
                    -1
                )

    def _drawButton(
            self,
            frame,
            name,
            x1,
            y1,
            x2,
            y2):

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (45, 45, 45),
            -1
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (180, 180, 180),
            1
        )

        textSize = cv2.getTextSize(
            name,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            1
        )[0]

        textX = (
            x1
            + ((x2 - x1 - textSize[0]) // 2)
        )

        textY = (
            y1
            + ((y2 - y1 + textSize[1]) // 2)
        )

        cv2.putText(
            frame,
            name,
            (textX, textY),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    def _drawMainUI(self, frame):

        height, width = frame.shape[:2]

        cv2.rectangle(
            frame,
            (0, 0),
            (width, 38),
            (0, 0, 0),
            -1
        )

        modeText = (
            'Mode: '
            + self._modeNames[self._currentMode]
        )

        cv2.putText(
            frame,
            modeText,
            (10, 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

        if self._captureManager.isWritingVideo:

            cv2.circle(
                frame,
                (width - 145, 19),
                6,
                (0, 0, 255),
                -1
            )

            cv2.putText(
                frame,
                'RECORDING',
                (width - 130, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )

        buttonHeight = 45
        buttonY1 = height - buttonHeight
        buttonY2 = height - 5

        self._buttonAreas.clear()

        self._buttonAreas['settings'] = (
            10,
            buttonY1,
            130,
            buttonY2
        )

        self._buttonAreas['screenshot'] = (
            140,
            buttonY1,
            280,
            buttonY2
        )

        self._buttonAreas['record'] = (
            290,
            buttonY1,
            450,
            buttonY2
        )

        self._drawButton(
            frame,
            'Settings',
            *self._buttonAreas['settings']
        )

        self._drawButton(
            frame,
            'Screenshot',
            *self._buttonAreas['screenshot']
        )

        recordText = 'Start Recording'

        if self._captureManager.isWritingVideo:
            recordText = 'Stop Recording'

        self._drawButton(
            frame,
            recordText,
            *self._buttonAreas['record']
        )

    def _drawSettings(self, frame):

        height, width = frame.shape[:2]

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (0, 0),
            (width, height),
            (20, 20, 20),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.92,
            frame,
            0.08,
            0,
            frame
        )

        cv2.putText(
            frame,
            'CAMEO SETTINGS',
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            'FILTERS',
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2,
            cv2.LINE_AA
        )

        self._buttonAreas.clear()

        x1 = 30
        x2 = 280
        y = 100

        for number, name in self._modeNames.items():

            y1 = y
            y2 = y + 32

            buttonName = (
                str(number)
                + ' - '
                + name
            )

            if number == self._currentMode:
                buttonName += ' [CURRENT]'

            self._buttonAreas[
                'filter_' + str(number)
            ] = (
                x1,
                y1,
                x2,
                y2
            )

            self._drawButton(
                frame,
                buttonName,
                x1,
                y1,
                x2,
                y2
            )

            y += 38

        cv2.putText(
            frame,
            'SAVING',
            (340, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2,
            cv2.LINE_AA
        )

        location = (
            self._storageManager.outputFolder
        )

        cv2.putText(
            frame,
            'Save Location:',
            (340, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

        locationDisplay = location

        if len(locationDisplay) > 45:
            locationDisplay = (
                '...'
                + locationDisplay[-42:]
            )

        cv2.putText(
            frame,
            locationDisplay,
            (340, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (190, 190, 190),
            1,
            cv2.LINE_AA
        )

        self._buttonAreas['change_location'] = (
            340,
            165,
            580,
            205
        )

        self._drawButton(
            frame,
            'Change Location',
            340,
            165,
            580,
            205
        )

        self._buttonAreas['open_screenshots'] = (
            340,
            220,
            580,
            260
        )

        self._drawButton(
            frame,
            'Open Screenshots',
            340,
            220,
            580,
            260
        )

        self._buttonAreas['open_videos'] = (
            340,
            275,
            580,
            315
        )

        self._drawButton(
            frame,
            'Open Videos',
            340,
            275,
            580,
            315
        )

        self._buttonAreas['close_settings'] = (
            340,
            350,
            580,
            395
        )

        self._drawButton(
            frame,
            'Close Settings',
            340,
            350,
            580,
            395
        )

        cv2.putText(
            frame,
            'ESC - Open / Close Settings',
            (30, height - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (150, 150, 150),
            1,
            cv2.LINE_AA
        )

    def _isInside(
            self,
            x,
            y,
            area):

        x1, y1, x2, y2 = area

        return (
            x1 <= x <= x2
            and y1 <= y <= y2
        )

    def _onMouse(
            self,
            event,
            x,
            y,
            flags,
            param):

        if event != cv2.EVENT_LBUTTONUP:
            return

        if self._settingsOpen:

            for number in self._modeNames:

                key = (
                    'filter_'
                    + str(number)
                )

                if self._isInside(
                    x,
                    y,
                    self._buttonAreas.get(
                        key,
                        (-1, -1, -1, -1)
                    )
                ):

                    self._currentMode = number
                    return

            if self._isInside(
                x,
                y,
                self._buttonAreas.get(
                    'change_location',
                    (-1, -1, -1, -1)
                )
            ):

                self._changeOutputFolder()
                return

            if self._isInside(
                x,
                y,
                self._buttonAreas.get(
                    'open_screenshots',
                    (-1, -1, -1, -1)
                )
            ):

                self._openFolder(
                    self._storageManager.screenshotFolder
                )
                return

            if self._isInside(
                x,
                y,
                self._buttonAreas.get(
                    'open_videos',
                    (-1, -1, -1, -1)
                )
            ):

                self._openFolder(
                    self._storageManager.videoFolder
                )
                return

            if self._isInside(
                x,
                y,
                self._buttonAreas.get(
                    'close_settings',
                    (-1, -1, -1, -1)
                )
            ):

                self._settingsOpen = False
                return

        else:

            if self._isInside(
                x,
                y,
                self._buttonAreas.get(
                    'settings',
                    (-1, -1, -1, -1)
                )
            ):

                self._settingsOpen = True
                return

            if self._isInside(
                x,
                y,
                self._buttonAreas.get(
                    'screenshot',
                    (-1, -1, -1, -1)
                )
            ):

                self._takeScreenshot()
                return

            if self._isInside(
                x,
                y,
                self._buttonAreas.get(
                    'record',
                    (-1, -1, -1, -1)
                )
            ):

                self._toggleRecording()
                return

    def _takeScreenshot(self):

        filename = (
            self._storageManager
            .getScreenshotFilename()
        )

        self._captureManager.writeImage(
            filename
        )

        print(
            'Screenshot:',
            filename
        )

    def _toggleRecording(self):

        if self._captureManager.isWritingVideo:

            self._captureManager.stopWritingVideo()

        else:

            filename = (
                self._storageManager
                .getVideoFilename()
            )

            self._captureManager.startWritingVideo(
                filename
            )

    def _changeOutputFolder(self):

        root = Tk()

        root.withdraw()

        root.attributes(
            '-topmost',
            True
        )

        folder = filedialog.askdirectory(
            title='Choose Cameo Save Location'
        )

        root.destroy()

        if folder:

            self._storageManager.setOutputFolder(
                folder
            )

            print(
                'Save location changed to:',
                folder
            )

    def _openFolder(self, folder):

        if not os.path.exists(folder):

            os.makedirs(
                folder,
                exist_ok=True
            )

        try:

            os.startfile(folder)

        except Exception as error:

            print(
                'Could not open folder:',
                error
            )

    def onKeypress(self, keycode):

        if keycode == 32:

            self._takeScreenshot()

        elif keycode == ord('r'):

            self._toggleRecording()

        elif keycode == 27:

            self._settingsOpen = (
                not self._settingsOpen
            )


if __name__ == '__main__':
    Cameo().run()
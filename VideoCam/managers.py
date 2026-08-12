import cv2
import numpy
import time


class CaptureManager(object):

    def __init__(
            self,
            capture,
            previewWindowManager=None,
            shouldMirrorPreview=False):

        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview
        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None

        self._imageFilename = None

        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

        self._startTime = None
        self._framesElapsed = 0
        self._fpsEstimate = None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):

        if self._channel != value:

            self._channel = value
            self._frame = None

    @property
    def frame(self):

        if self._enteredFrame and self._frame is None:

            _, self._frame = (
                self._capture.retrieve()
            )

        return self._frame

    @property
    def isWritingImage(self):

        return self._imageFilename is not None

    @property
    def isWritingVideo(self):

        return self._videoFilename is not None

    def enterFrame(self):

        assert not self._enteredFrame, (
            'previous enterFrame() had no matching '
            'exitFrame()'
        )

        if self._capture is not None:

            self._enteredFrame = (
                self._capture.grab()
            )

    def exitFrame(self):

        if self.frame is None:

            self._enteredFrame = False
            return

        if self._framesElapsed == 0:

            self._startTime = time.time()

        else:

            timeElapsed = (
                time.time()
                - self._startTime
            )

            if timeElapsed > 0:

                self._fpsEstimate = (
                    self._framesElapsed
                    / timeElapsed
                )

        self._framesElapsed += 1

        if self.previewWindowManager is not None:

            if self.shouldMirrorPreview:

                mirroredFrame = numpy.fliplr(
                    self._frame
                ).copy()

                self.previewWindowManager.show(
                    mirroredFrame
                )

            else:

                self.previewWindowManager.show(
                    self._frame
                )

        if self.isWritingImage:

            success = cv2.imwrite(
                self._imageFilename,
                self._frame
            )

            if success:

                print(
                    'Screenshot saved:',
                    self._imageFilename
                )

            else:

                print(
                    'Failed to save screenshot:',
                    self._imageFilename
                )

            self._imageFilename = None

        self._writeVideoFrame()

        self._frame = None
        self._enteredFrame = False

    def writeImage(self, filename):

        self._imageFilename = filename

    def startWritingVideo(
            self,
            filename,
            encoding=None):

        if self.isWritingVideo:
            return

        self._videoFilename = filename

        if encoding is None:

            encoding = cv2.VideoWriter_fourcc(
                'X',
                'V',
                'I',
                'D'
            )

        self._videoEncoding = encoding

        self._videoWriter = None

        self._startTime = time.time()
        self._framesElapsed = 0

        print(
            'Recording started:',
            filename
        )

    def stopWritingVideo(self):

        if self._videoWriter is not None:

            self._videoWriter.release()

            self._videoWriter = None

        if self._videoFilename is not None:

            print(
                'Recording stopped:',
                self._videoFilename
            )

        self._videoFilename = None
        self._videoEncoding = None

    def _writeVideoFrame(self):

        if not self.isWritingVideo:
            return

        if self._videoWriter is None:

            fps = self._capture.get(
                cv2.CAP_PROP_FPS
            )

            if fps is None or fps <= 0:

                fps = 30.0

            width = int(
                self._capture.get(
                    cv2.CAP_PROP_FRAME_WIDTH
                )
            )

            height = int(
                self._capture.get(
                    cv2.CAP_PROP_FRAME_HEIGHT
                )
            )

            if width <= 0 or height <= 0:

                height, width = (
                    self._frame.shape[:2]
                )

            self._videoWriter = cv2.VideoWriter(
                self._videoFilename,
                self._videoEncoding,
                fps,
                (width, height)
            )

            if not self._videoWriter.isOpened():

                print(
                    'Could not open video writer.'
                )

                self._videoWriter = None
                self._videoFilename = None
                self._videoEncoding = None

                return

        self._videoWriter.write(
            self._frame
        )


class WindowManager(object):

    def __init__(
            self,
            windowName,
            keypressCallback=None):

        self.keypressCallback = keypressCallback
        self._windowName = windowName
        self._isWindowCreated = False

    @property
    def isWindowCreated(self):

        return self._isWindowCreated

    def createWindow(self):

        cv2.namedWindow(
            self._windowName
        )

        self._isWindowCreated = True

    def show(self, frame):

        cv2.imshow(
            self._windowName,
            frame
        )

    def destroyWindow(self):

        if self._isWindowCreated:

            cv2.destroyWindow(
                self._windowName
            )

            self._isWindowCreated = False

    def processEvents(self):

        keycode = cv2.waitKey(1)

        try:

            windowVisible = cv2.getWindowProperty(
                self._windowName,
                cv2.WND_PROP_VISIBLE
            )

            if windowVisible < 1:

                self._isWindowCreated = False

                cv2.destroyAllWindows()

                return

        except cv2.error:

            self._isWindowCreated = False

            return

        if (
            self.keypressCallback is not None
            and keycode != -1
        ):

            keycode &= 0xFF

            self.keypressCallback(
                keycode
            )
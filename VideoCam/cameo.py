import cv2
import numpy as np
import filters

from managers import WindowManager, CaptureManager


class Cameo(object):

    def __init__(self):

        # Create the window manager.
        self._windowManager = WindowManager(
            'Cameo',
            self.onKeypress
        )

        # Create the capture manager.
        self._captureManager = CaptureManager(
            cv2.VideoCapture(0),
            self._windowManager,
            True
        )

        # Create the filter.
        self._curveFilter = filters.BGRPortraCurveFilter()

    def run(self):
        """Run the main loop."""

        # Create the camera window.
        self._windowManager.createWindow()

        # Keep running while the window is open.
        while self._windowManager.isWindowCreated:

            # Capture a frame.
            self._captureManager.enterFrame()

            # Get the current frame.
            frame = self._captureManager.frame

            if frame is not None:

                # Apply edge filter.
                filters.strokeEdges(frame, frame)

                # Apply the BGR Portra curve filter.
                self._curveFilter.apply(frame, frame)

                # Convert the frame to grayscale.
                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

                # Detect edges using Canny.
                edges = cv2.Canny(
                    gray,
                    100,
                    200
                )

                # Find contours from the edges.
                contours, hierarchy = cv2.findContours(
                    edges,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                # Draw the detected contours.
                cv2.drawContours(
                    frame,
                    contours,
                    -1,
                    (0, 255, 0),
                    2
                )

                # Blur the grayscale image to reduce noise.
                blurred = cv2.GaussianBlur(
                    gray,
                    (9, 9),
                    2
                )

                # Detect circles using Hough Circle Transform.
                circles = cv2.HoughCircles(
                    blurred,
                    cv2.HOUGH_GRADIENT,
                    dp=1,
                    minDist=50,
                    param1=100,
                    param2=50,
                    minRadius=10,
                    maxRadius=300
                )

                # Check if circles were detected.
                if circles is not None:

                    # Convert circle values to integers.
                    circles = np.round(
                        circles[0, :]
                    ).astype("int")

                    # Draw each detected circle.
                    for (x, y, r) in circles:

                        # Draw the outside of the circle.
                        cv2.circle(
                            frame,
                            (x, y),
                            r,
                            (0, 255, 0),
                            2
                        )

                        # Draw the center of the circle.
                        cv2.circle(
                            frame,
                            (x, y),
                            2,
                            (0, 0, 255),
                            3
                        )

            # Display/save the frame.
            self._captureManager.exitFrame()

            # Check for keyboard input.
            self._windowManager.processEvents()


    def onKeypress(self, keycode):
        """Handle keyboard input."""

        # SPACE = Take screenshot.
        if keycode == 32:

            self._captureManager.writeImage(
                'screenshot.png'
            )

        # TAB = Start/stop video recording.
        elif keycode == 9:

            if not self._captureManager.isWritingVideo:

                self._captureManager.startWritingVideo(
                    'screencast.avi'
                )

            else:

                self._captureManager.stopWritingVideo()

        # ESC = Quit the program.
        elif keycode == 27:

            self._windowManager.destroyWindow()


if __name__ == '__main__':
    Cameo().run()
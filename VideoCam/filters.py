import cv2
import numpy as np


def strokeEdges(src, dst, blurKsize=7, edgeKsize=5):
    """
    Detect edges in an image and blend the edges with the original image.

    This is one of the filters used by cameo.py.
    """

    if blurKsize >= 3:
        blurredSrc = cv2.GaussianBlur(
            src,
            (blurKsize, blurKsize),
            0
        )
    else:
        blurredSrc = src

    graySrc = cv2.cvtColor(
        blurredSrc,
        cv2.COLOR_BGR2GRAY
    )

    graySrc = cv2.Laplacian(
        graySrc,
        cv2.CV_8U,
        ksize=edgeKsize
    )

    normalizedInverseAlpha = (1.0 / 255.0) * (
        255 - graySrc
    )

    channels = cv2.split(src)

    for channel in channels:
        channel[:] = channel * normalizedInverseAlpha

    cv2.merge(channels, dst)


class BGRPortraCurveFilter(object):
    """
    A simple photographic curve filter inspired by the
    BGR Portra-style filter used in the Cameo activity.

    The filter uses lookup tables to adjust the blue,
    green, and red channels.
    """

    def __init__(self):
        self._bLUT = self._createLUT(
            [0, 64, 128, 192, 255],
            [0, 70, 135, 195, 255]
        )

        self._gLUT = self._createLUT(
            [0, 64, 128, 192, 255],
            [0, 70, 135, 195, 255]
        )

        self._rLUT = self._createLUT(
            [0, 64, 128, 192, 255],
            [0, 65, 135, 205, 255]
        )

        self._bgrLUT = self._createLUT(
            [0, 64, 128, 192, 255],
            [0, 70, 140, 200, 255]
        )

    @staticmethod
    def _createLUT(x, y):
        """
        Create a 256-value lookup table from control points.
        """

        x = np.array(x, dtype=np.float32)
        y = np.array(y, dtype=np.float32)

        return np.interp(
            np.arange(256),
            x,
            y
        ).astype(np.uint8)

    def apply(self, src, dst):
        """
        Apply the BGR curve filter to the source image
        and place the result in dst.
        """

        # Apply separate curves to the B, G, and R channels.
        b, g, r = cv2.split(src)

        b = cv2.LUT(b, self._bLUT)
        g = cv2.LUT(g, self._gLUT)
        r = cv2.LUT(r, self._rLUT)

        # Merge the adjusted channels.
        cv2.merge(
            (b, g, r),
            dst
        )

        # Apply an additional overall curve.
        dst[:] = cv2.LUT(
            dst,
            self._bgrLUT
        )

        return dst

def grayscale(src, dst):
    """Convert a color image to grayscale."""

    gray = cv2.cvtColor(
        src,
        cv2.COLOR_BGR2GRAY
    )

    if len(dst.shape) == 2:
        dst[:] = gray
    else:
        dst[:] = cv2.cvtColor(
            gray,
            cv2.COLOR_GRAY2BGR
        )

    return dst


def blur(src, dst, ksize=5):
    """Apply Gaussian blur."""

    result = cv2.GaussianBlur(
        src,
        (ksize, ksize),
        0
    )

    dst[:] = result

    return dst


def canny(src, dst, threshold1=100, threshold2=200):
    """Apply Canny edge detection."""

    gray = cv2.cvtColor(
        src,
        cv2.COLOR_BGR2GRAY
    )

    result = cv2.Canny(
        gray,
        threshold1,
        threshold2
    )

    if len(dst.shape) == 2:
        dst[:] = result
    else:
        dst[:] = cv2.cvtColor(
            result,
            cv2.COLOR_GRAY2BGR
        )

    return dst
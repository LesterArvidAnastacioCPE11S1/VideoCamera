import os
import json


class StorageManager:

    def __init__(self):
        self.configFile = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'cameo_config.json'
        )

        self.outputFolder = self._loadOutputFolder()

        self.cameoFolder = os.path.join(
            self.outputFolder,
            'Cameo'
        )

        self.screenshotFolder = os.path.join(
            self.cameoFolder,
            'Screenshots'
        )

        self.videoFolder = os.path.join(
            self.cameoFolder,
            'Videos'
        )

        self.createFolders()

    def _loadOutputFolder(self):

        defaultFolder = os.path.join(
            os.path.expanduser('~'),
            'Pictures'
        )

        if not os.path.exists(self.configFile):
            return defaultFolder

        try:

            with open(
                self.configFile,
                'r'
            ) as file:

                data = json.load(file)

                folder = data.get(
                    'outputFolder',
                    defaultFolder
                )

                if os.path.exists(folder):
                    return folder

        except:
            pass

        return defaultFolder

    def _saveOutputFolder(self):

        data = {
            'outputFolder': self.outputFolder
        }

        try:

            with open(
                self.configFile,
                'w'
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4
                )

        except:
            pass

    def createFolders(self):

        os.makedirs(
            self.screenshotFolder,
            exist_ok=True
        )

        os.makedirs(
            self.videoFolder,
            exist_ok=True
        )

    def setOutputFolder(self, outputFolder):

        self.outputFolder = outputFolder

        self.cameoFolder = os.path.join(
            self.outputFolder,
            'Cameo'
        )

        self.screenshotFolder = os.path.join(
            self.cameoFolder,
            'Screenshots'
        )

        self.videoFolder = os.path.join(
            self.cameoFolder,
            'Videos'
        )

        self.createFolders()
        self._saveOutputFolder()

    def getScreenshotFilename(self):

        return self._getNextFilename(
            self.screenshotFolder,
            'Screenshot',
            '.png'
        )

    def getVideoFilename(self):

        return self._getNextFilename(
            self.videoFolder,
            'Video',
            '.avi'
        )

    def _getNextFilename(
            self,
            folder,
            prefix,
            extension):

        number = 1

        while True:

            filename = os.path.join(
                folder,
                f'{prefix}_{number:03d}{extension}'
            )

            if not os.path.exists(filename):
                return filename

            number += 1
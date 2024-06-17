class MKVmergeError(Exception):
    """
    Exception raised when MKVmerge identify or remux fails.

    This exception is raised when the MKVmerge command line tool encounters an error during the identification or remuxing of a media file.

    Attributes:
        message (str): The error message.

    """

    ERROR_MESSAGE = "An error occurred running the mkvmerge command."

    def __init__(self, message):
        self.message = message
        super().__init__(self.ERROR_MESSAGE)

    def __str__(self):
        return self.message

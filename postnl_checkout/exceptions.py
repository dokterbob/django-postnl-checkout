class PostNLException(Exception):
    """ Exception class for use with PostNLCheckout. """
    pass


class PostNLResponseException(PostNLException):
    """ Exceptions due to values in the response. """
    pass

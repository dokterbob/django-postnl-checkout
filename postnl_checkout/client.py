import logging
logger = logging.getLogger(__name__)

import hashlib
import datetime

import requests

import suds.client
import suds.wsse

import suds_requests


class PostNLCheckoutClient(object):
    """
    Client exposing the PostNL checkout client.

    This part should not depend on Django in any way and might be separated
    from the rest of the module later.
    """

    SANDBOX_ENDPOINT_URL = (
        'https://testservice.postnl.com/CIF_SB/'
        'WebshopCheckoutWebService/2_2/WebshopCheckoutService.svc?wsdl'
    )

    PRODUCTION_ENDPOINT_URL = (
        'https://service.postnl.com/CIF/'
        'WebshopCheckoutWebService/2_2/WebshopCheckoutService.svc?wsdl'
    )

    datetime_format = '%d-%m-%Y %H:%M:%S'

    def __init__(
        self, username, password, webshop_id, environment,
        timeout=None, cache=None
    ):
        """
        Initialize, setting required attributes and instantiate web service.
        """
        self.webshop_id = webshop_id

        # Setup Requests session
        session = self._get_session(timeout)

        # Instantiate web service.
        self.suds_client = self._get_client(
            environment, session, username, password, cache
        )

        self.service = self.suds_client.service

    @classmethod
    def _get_session(cls, timeout=None):
        """ Setup requests session. """
        session = requests.Session()
        session.verify = True

        if timeout:
            session.timeout = timeout

        return session

    @classmethod
    def _get_client(
        cls, environment, session, username, password, cache=None
    ):
        """ Return webservice from SOAP client (suds). """

        # Endpoint URL depending on environment
        assert environment in ('sandbox', 'production'), 'Unknown environment'

        if environment == 'production':
            webservice_url = cls.PRODUCTION_ENDPOINT_URL
        else:
            webservice_url = cls.SANDBOX_ENDPOINT_URL

        # Setup authentication
        sha1 = hashlib.sha1()
        sha1.update(password)

        security = suds.wsse.Security()
        token = suds.wsse.UsernameToken(username, sha1.hexdigest())
        security.tokens.append(token)

        # Instantiate client
        client = suds.client.Client(
            webservice_url,
            transport=suds_requests.RequestsTransport(session),
            cachingpolicy=1, cache=cache,
            wsse=security
        )

        return client

    @classmethod
    def parse_datetime(cls, value):
        """ Parse datetime in PostNL format. """

        return datetime.datetime.strptime(value, cls.datetime_format)

    @classmethod
    def format_datetime(cls, value):
        """ Format datetime in PostNL format. """

        return datetime.datetime.strftime(value, cls.datetime_format)

    @classmethod
    def _assert_required_attributes(cls, kwargs, required):
        """ Assert whether all required attributes are present. """

        for key in required:
            assert key in kwargs, 'Required argument %s not present.' % key

    def _add_webshop(self, kwargs):
        """ Add webshop to argument dictionary. """

        assert 'Webshop' not in kwargs
        kwargs['Webshop'] = {
            'IntRef': self.webshop_id
        }

    def prepare_order(self, **kwargs):
        """ Wrapper around PrepareOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Order')
            )

        # Execute API call
        result = self.service.PrepareOrder(**kwargs)

        # Return the result
        return result

    def read_order(self, **kwargs):
        """ Wrapper around ReadOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Checkout')
            )

        # Execute API call
        result = self.service.ReadOrder(**kwargs)

        # Return the result
        return result

    def confirm_order(self, **kwargs):
        """ Wrapper around ConfirmOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Checkout', 'Order')
            )

        # Execute API call
        result = self.service.ConfirmOrder(**kwargs)

        # Return the result
        return result

    def update_order(self, **kwargs):
        """ Wrapper around UpdateOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Order')
            )

        # Execute API call
        result = self.service.UpdateOrder(**kwargs)

        # Return the result
        assert result in ('true', 'false')

        return result == 'true'

    def ping_status(self, **kwargs):
        """
        Wrapper around PingStatus API call.

        Returns True if service OK, False for not OK.
        """

        result = self.service.PingStatus()

        assert result in ('OK', 'NOK')

        return result == 'OK'

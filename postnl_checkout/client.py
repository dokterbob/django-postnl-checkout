import logging
logger = logging.getLogger(__name__)

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
        'WebshopCheckoutWebService/2_2/WebshopCheckoutService.svc'
    )

    PRODUCTION_ENDPOINT_URL = (
        'https://service.postnl.com/CIF/'
        'WebshopCheckoutWebService/2_2/WebshopCheckoutService.svc'
    )

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
        self.webservice = self._get_webservice(
            environment, session, username, password, cache
        )

    @classmethod
    def _get_session(cls, timeout=None):
        """ Setup requests session. """
        session = requests.Session()
        session.verify = True

        if timeout:
            session.timeout = timeout

        return session

    @classmethod
    def _get_webservice(
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
        security = suds.wsse.Security()
        token = suds.wsse.UsernameToken('username', 'password')
        security.tokens.append(token)

        client = suds.client.Client(
            webservice_url,
            transport=suds_requests.RequestsTransport(session),
            cachingpolicy=1, cache=cache,
            wsse=security
        )

        return client.service

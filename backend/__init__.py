""" Module initializer
"""


import celery
import logging
import pyramid
import pyramid_raml
import zope


LOG = logging.getLogger(__name__)


#@pyramid.events.subscriber(pyramid.events.NewRequest)
def log_request(event):
    """ Log new incoming requests.
    """
    LOG.error("{} {}".format(event.request.method, event.request.path_qs))
    return None


#@pyramid.events.subscriber(pyramid.events.NewRequest)
def log_routes(event):
    intrs = event.request.registry.introspector.get_category('routes', [])
    names = [intr['introspectable']['name'] for intr in intrs]
    LOG.error("routes {}".format(names))
    return None


@pyramid.events.subscriber(pyramid.events.NewRequest)
def add_cors_headers_callback(event):
    """ Add response callback for CORS headers.
    """
    def cors_headers(request, response):
        """ Add CORS headers to HTTP response.
        """
        headers = ', '.join([
#            'Origin',
            'Content-Type',
#            'Accept',
#            'Authorization',
        ])
#        methods = ', '.join([
#            'DELETE',
#            'GET',
#            'HEAD',
#            'OPTIONS',
#            'POST',
#            'PUT',
#            'TRACE'
#        ])
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
#            'Access-Control-Allow-Methods': methods,
            'Access-Control-Allow-Headers': headers,
#            'Access-Control-Allow-Credentials': 'true',
#            'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)


@pyramid_raml.api_service('/foo')
class ThisIsNotFoo(object):

    def __init__(self, request):
        self.request = request
        return None

    @pyramid_raml.api_method('get')
    def rest_foo_get(self):
        async_result_uid = self.request.params['uid']
        celery_app = self.request.registry.queryUtility(ICeleryApp)
        async_result = celery.result.AsyncResult(async_result_uid, app=celery_app)
        return {
            'uid': async_result_uid,
            'result': async_result.get(),
        }

    @pyramid_raml.api_method('post')
    def rest_foo_post(self):
        arg = self.request.json_body['arg']
        subtask = celery.signature('business.tasks.foo', args=(arg,))
        callback = celery.signature('business.tasks.foo_callback')
        async_result = subtask.apply_async(link=callback)
        async_result_uid = getattr(async_result, 'id')
        return {
            'async_result': async_result_uid,
        }


@pyramid_raml.api_service('/allfoos')
class WhateverFoos(object):

    def __init__(self, request):
        self.request = request
        return None

    @pyramid_raml.api_method('post')
    def rest_foos_post(self):
        status = []
        async_result_uids = self.request.json_body

        celery_app = self.request.registry.queryUtility(ICeleryApp)
        for async_result_uid in async_result_uids:
            async_result = celery.result.AsyncResult(async_result_uid, app=celery_app)
            status.append({
                'uid': async_result_uid,
                'status': async_result.status,
            })

        return {
            'status': status,
        }


class ICeleryApp(zope.interface.Interface):
    pass


def main(dummy_global_config, **settings):
    """ Make the Pyramid WSGI application.
    """

    config = pyramid.config.Configurator(
        settings=settings,
    )

    config.include('pyramid_raml')

    celery_app = celery.Celery('business.tasks', backend='redis://redis')
    config.registry.registerUtility(celery_app, ICeleryApp)

    config.scan()
    return config.make_wsgi_app()


# EOF

import urllib2
import httputil
import pdb
import time

requests = httputil.get_requests_session()

class PyBingException(Exception):
    pass

class PyBingSearch(object):

    #QUERY_URL = 'https://api.datamarket.azure.com/Bing/Search/v1/Composite' \
    #             + '?Sources={}&Query={}&$top={}&$skip={}&$format={}'
    QUERY_URL = 'https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web' \
                 + '?Query={}&$top={}&$skip={}&$format={}&Adult=%27Off%27'

    IMAGE_URL = 'https://api.datamarket.azure.com/Bing/Search/v1/Image' \
                + '?Query={}&$top={}&$skip={}&$format={}&Adult=%27Off%27'

    def __init__(self, api_key, safe=False):
        self.api_key = api_key
        self.safe = safe

    def search(self, query, limit=50, offset=0, format='json', timeout=5, source='Web'):
        return self._search(query, limit, offset, format, timeout=timeout, source=source)

    def search_all(self, query, limit=50, format='json'):
        results = self._search(query, limit, 0, format)
        while results.total > len(results) and len(results) < limit:
            max = limit - len(results)
            more_results = self._search(query, max, len(results), format)
            results += more_results
        return results

    def _search(self, query, limit, offset, format, timeout=5, source='Web'):
        '''
        Returns a list of result objects, with the url for the next page bing search url.
        '''
        url = self.QUERY_URL.format(urllib2.quote("'{}'".format(query)), limit, offset, format)
        if source.lower() == "image":
            url = self.IMAGE_URL.format(urllib2.quote("'{}'".format(query)), limit, offset, format)
        r = requests.get(url, auth=("", self.api_key), timeout=timeout)
        try:
            json_results = r.json()
        except ValueError as vE:
            if not self.safe:
                raise PyBingException("Request returned with code %s, error msg: %s" % (r.status_code, r.text))
            else:
                print "[ERROR] Request returned with code %s, error msg: %s. \nContinuing in 5 seconds." % (r.status_code, r.text)
                time.slee(5)
        try:
            next_link = json_results['d']['__next']
        except KeyError as kE:
            print "Couldn't extract next_link: KeyError: %s" % kE
            next_link = ''
        return [Result(single_result_json, source) for single_result_json in json_results['d']['results']], next_link

class Result(object):
    '''
    The class represents a SINGLE search result.
    Each result will come with the following:

    #For the actual results#
    title: title of the result
    url: the url of the result
    description: description for the result
    id: bing id for the page

    #Meta info#:
    meta.uri: the search uri for bing
    meta.type: for the most part WebResult
    '''

    class _Meta(object):
        '''
        Holds the meta info for the result.
        '''
        def __init__(self, meta):
            self.type = meta['type']
            self.uri = meta['uri']

    def __init__(self, result, source='Web'):
        self.url = result.get('Url')
        if source.lower() == 'image':
            self.url = result.get('MediaUrl')
        self.title = result['Title']
        self.description = result.get('Description')
        self.height = result.get('Height')
        self.width = result.get('Width')
        self.source = source
        self.size = result.get('Size')
        self.content_type = result.get('ContentType')
        self.id = result['ID']

        self.meta = self._Meta(result['__metadata'])

# import cStringIO
import io
# import httplib
import http.client
import re
import pycurl

class HTTPResponse:
    def __init__(self, status, reason, data):
        self.status = status
        self.reason = reason
        self.data = data

class HTTPApi:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.debuglvl = 0

    ############################################################################
    # Issues a HTTP GET request to the RESTful API using Python httplib module
    # Note: httplib module has known issues on certain versions of Python.
    # It may specifically have issues related to certificates used in ssl.
    # If you face such issues sample code based on Pycurl can be used.
    ############################################################################
    def get_use_httplib(self, uri):
        method = "GET"
        # connection = httplib.HTTPSConnection(self.host, self.port)
        connection = http.client.HTTPSConnection(self.host, self.port)
        connection.set_debuglevel(self.debuglvl)
        connection.putrequest(method, uri)
        connection.putheader('Content-type', 'text/json')
        connection.putheader('username', self.username)
        connection.putheader('password', self.password)
        connection.endheaders()

        response = connection.getresponse()
        if response.status == 200:
            return HTTPResponse(response.status, response.reason, response.read())
        else:
            return HTTPResponse(response.status, response.reason, None)

    def post_use_httplib(self, uri, data):
        method = "POST"
        # connection = httplib.HTTPSConnection(self.host, self.port)
        connection = http.client.HTTPSConnection(self.host, self.port)
        connection.set_debuglevel(self.debuglvl)
        headers = {"Content-type": "text/json", "username": self.username, "password": self.password}
        connection.request(method, uri, data, headers)

        response = connection.getresponse()
        if response.status == 200:
            return HTTPResponse(response.status, response.reason, response.read())
        else:
            return HTTPResponse(response.status, response.reason, None)

    #############################################################################
    # Issues a HTTP GET request to the RESTful API using pycurl
    #############################################################################
    def get_use_pycurl(self, uri):
        c = pycurl.Curl()
        # buf = cStringIO.StringIO()
        # hdrbuf = cStringIO.StringIO()
        buf = io.StringIO()
        hdrbuf = io.StringIO()
        url = "https://" + self.host + ":" + self.port + "/" + uri
        headers = ['Content-type: text/json', 'username: ' + self.username, 'password: ' + self.password]
        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.setopt(c.HEADERFUNCTION, hdrbuf.write)
        c.setopt(c.SSL_VERIFYPEER, 0)
        c.setopt(c.SSL_VERIFYHOST, 0)
        # c.setopt(c.VERBOSE, True)
        c.perform()
        response = buf.getvalue()

        status = c.getinfo(pycurl.HTTP_CODE)
        reason = None
        data = None
        status_line = hdrbuf.getvalue().splitlines()[0]
        m = re.match(r'HTTP\/\S*\s*\d+\s*(.*?)\s*$', status_line)
        if m:
            reason = m.groups(1)
        if status == 200:
            data = buf.getvalue()

        buf.close()
        hdrbuf.close()

        return HTTPResponse(status, reason, data)

    #############################################################################
    # Issues a HTTP POST request to the RESTful API using pycurl
    #############################################################################
    def post_use_pycurl(self, uri, data):
        c = pycurl.Curl()
        # readbuf = cStringIO.StringIO()
        readbuf = io.StringIO()
        wrtbuf = None
        # hdrbuf = cStringIO.StringIO()
        hdrbuf = io.StringIO()
        url = "https://" + self.host + ":" + self.port + uri
        headers = ['Content-type: text/json', 'username: ' + self.username, 'password: ' +
                   self.password]

        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.WRITEFUNCTION, readbuf.write)
        c.setopt(c.POST, 1)
        if data:
            # wrtbuf = cStringIO.StringIO(data)
            wrtbuf = io.StringIO(data)
            c.setopt(c.POSTFIELDSIZE, len(data))
            c.setopt(c.READFUNCTION, wrtbuf.getvalue)
        else:
            c.setopt(c.POSTFIELDSIZE, 0)

        c.setopt(c.HEADERFUNCTION, hdrbuf.write)
        c.setopt(c.SSL_VERIFYPEER, 0)
        c.setopt(c.SSL_VERIFYHOST, 0)
        c.setopt(c.VERBOSE, True)
        c.perform()
        status = c.getinfo(pycurl.HTTP_CODE)
        reason = None
        data = None

        status_line = hdrbuf.getvalue().splitlines()[0]
        m = re.match(r'HTTP\/\S*\s*\d+\s*(.*?)\s*$', status_line)
        if m:
            reason = m.groups(1)
        if status == 200:
            data = readbuf.getvalue()
        readbuf.close()
        if wrtbuf:
            wrtbuf.close()
        hdrbuf.close()
        return HTTPResponse(status, reason, data)

    def get(self, uri):
        return self.get_use_pycurl(uri)

    def post(self, uri, data):
        return self.post_use_pycurl(uri, data)

import logging

from flask import Flask, Response, request
from flask_classful import FlaskView, route

from .packet_handler import PacketHandler
from .http_helper import B64SCCrypto
from ..log_handler.log_handler import LogHandler

http_logging = LogHandler('http_server', 'network.log', level=logging.DEBUG).get_logger()
gts_logging = LogHandler('gts_server', 'network.log', level=logging.DEBUG).get_logger()

werkzeug_logging = logging.getLogger('werkzeug')
werkzeug_logging.setLevel(logging.ERROR)

AUTH_TOKEN = 'c9KcX1Cry3QKS2Ai7yxL6QiQGeBGeQKR'

class GTSResponse(Response):
    def __init__(self, response=None, status=None, headers=None, content_type=None, **kwargs):
        default_headers = {
            "Server": "Microsoft-IIS/6.0",
            "P3P": "CP='NOI ADMa OUR STP'",
            "cluster-server": "aphexweb3",
            "X-Server-Name": "AW4",
            "X-Powered-By": "ASP.NET",
            "Content-Type": "text/html",
            "Set-Cookie": "ASPSESSIONIDQCDBDDQS=JFDOAMPAGACBDMLNLFBCCNCI; path=/",
            "Cache-control": "private"
        }

        if headers:
            headers.update(default_headers)
        else:
            headers = default_headers

        super().__init__(response, status, headers, content_type, **kwargs)

app = Flask(__name__)
packet_handler = PacketHandler(config_path="/home/server/config.yaml")

@app.before_request
def handle_request():
    if request.url_rule is None:
        http_logging.warning(f"No route found for {request.url}")
        return GTSResponse(b'\x01\x00')
    gts_logging.info(f"Incoming Request: {request.url} {request.args.to_dict()}")
    if len(request.args.to_dict()) == 1:
        return GTSResponse(AUTH_TOKEN)

class GTSServer(FlaskView):
    route_base = '/pokemondpds'

    def __init__(self):
        self.b64sc = B64SCCrypto()

    @route('/worldexchange/info.asp', methods=['GET'])
    def info(self):
        gts_logging.info('Connection Established.')
        packet_handler.reset()
        return GTSResponse(b'\x01\x00')

    @route('/worldexchange/common/setProfile.asp', methods=['GET'])
    def set_profile(self):
        return GTSResponse(b'\x00' * 8)

    @route('/common/setProfile.asp', methods=['GET'])
    def set_profile_plat(self):
        return GTSResponse(b'\x00' * 8)

    @route('/worldexchange/post.asp', methods=['GET'])
    def post(self):
        data = self.b64sc.decrypt(request.args.get('data'))
        gts_logging.info(f"POST data: {data.hex()}")
        packet_handler.handle_post(data)
        return GTSResponse(b'\x0c\x00')

    @route('/worldexchange/search.asp', methods=['GET'])
    def search(self):
        data = self.b64sc.decrypt(request.args.get('data'))
        gts_logging.info(f"POST data: {data.hex()}")
        count = int(data.hex()[-2:], 16)
        payload = packet_handler.get_payload(count=count)
        return GTSResponse(payload)

    @route('/worldexchange/result.asp', methods=['GET'])
    def result(self):
        data = self.b64sc.decrypt(request.args.get('data'))
        gts_logging.info(f"POST data: {data.hex()}")
        payload = packet_handler.get_payload(count=1)
        return GTSResponse(payload)

    @route('/worldexchange/delete.asp', methods=['GET'])
    def delete(self):
        return GTSResponse(b'\x01\x00')

GTSServer.register(app)

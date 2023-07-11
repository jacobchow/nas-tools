from app.utils import ExceptionUtils
from app.utils.types import IndexerType
from config import Config
from app.indexer.client._base import _IIndexClient
from app.utils import RequestUtils
from app.helper import IndexerConf


class Prowlarr(_IIndexClient):
    # 索引器ID
    client_id = "prowlarr"
    # 索引器类型
    client_type = IndexerType.PROWLARR
    # 索引器名称
    client_name = IndexerType.PROWLARR.value


    _client_config = {}
    _api_key = ""
    _host = ""

    def __init__(self, config=None):
        super().__init__()
        if config:
            self._client_config = config
        else:
            self._client_config = Config().get_config('prowlarr')
        self.init_config()

    def init_config(self):
        if self._client_config:
            self._api_key = self._client_config.get('api_key')
            self._host = self._client_config.get('host')
            if self._host:
                if not self._host.startswith('http'):
                    self._host = "http://" + self._host
                if not self._host.endswith('/'):
                    self._host = self._host + "/"

    @classmethod
    def match(cls, ctype):
        return True if ctype in [cls.client_id, cls.client_type, cls.client_name] else False

    def get_status(self):
        """
        检查连通性
        :return: True、False
        """
        if not self._api_key or not self._host:
            return False
        return True if self.get_indexers() else False

    def get_indexers(self):
        """
        获取配置的prowlarr indexer
        :return: indexer 信息 [(indexerId, indexerName, url)]
        """
        indexer_query_url = f"{self._host}api/v1/indexerstats?apikey={self._api_key}"
        try:
            ret = RequestUtils().get_res(indexer_query_url)
        except Exception as e2:
            ExceptionUtils.exception_traceback(e2)
            return []
        if not ret:
            return []
        indexers = ret.json().get("indexers", [])
        return [IndexerConf({"id": v["indexerId"],
                             "name": v["indexerName"],
                             "domain": f'{self._host}{v["indexerId"]}/api',
                             "builtin": False})
                for v in indexers]

    def search(self, *kwargs):
        return super().search(*kwargs)

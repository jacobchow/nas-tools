import requests

from app.utils import RequestUtils
from app.helper import IndexerConf
from app.utils import ExceptionUtils

from app.plugins import EventHandler
from app.utils.types import EventType
from app.plugins.modules._base import _IPluginModule

class Jackett(_IPluginModule):
    # 插件名称
    module_name = "Jackett"
    # 插件描述
    module_desc = "功能开发中..."
    # 插件图标
    module_icon = "jackett.png"
    # 主题色
    module_color = "#C90425"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "mattoid"
    # 作者主页
    author_url = "https://github.com/Mattoids"
    # 插件配置项ID前缀
    module_config_prefix = "jackett_"
    # 加载顺序
    module_order = 15
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enable = False
    _host = ""
    _api_key = ""
    _password = ""

    @staticmethod
    def get_fields():
        return [
            # 同一板块
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'title': 'Jackett地址',
                            'required': "required",
                            'tooltip': 'Jackett访问地址和端口，如为https需加https://前缀。注意需要先在Jackett中添加indexer，才能正常测试通过和使用',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'host',
                                    'placeholder': 'http://127.0.0.1:9117',
                                }
                            ]
                        },
                        {
                            'title': 'Api Key',
                            'required': "required",
                            'tooltip': 'Jackett管理界面右上角复制API Key',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'api_key',
                                    'placeholder': '',
                                }
                            ]
                        }
                    ],
                    [
                        {
                            'title': '密码',
                            'required': "required",
                            'tooltip': 'Jackett管理界面中配置的Admin password，如未配置可为空',
                            'type': 'password',
                            'content': [
                                {
                                    'id': 'password',
                                    'placeholder': '',
                                }
                            ]
                        }
                    ]
                ]
            }
        ]

    # def get_page(self):
    #     """
    #     插件的额外页面，返回页面标题和页面内容
    #     :return: 标题，页面内容，确定按钮响应函数
    #     """
    #     return "测试", None, None

    def get_status(self):
        """
        检查连通性
        :return: True、False
        """
        if not self._api_key or not self._host:
            return False
        self.user.plugin.jackett = self.get_indexers()
        return True if self.get_indexers() else False

    def get_indexers(self):
        """
        获取配置的jackett indexer
        :return: indexer 信息 [(indexerId, indexerName, url)]
        """
        # 获取Cookie
        cookie = None
        session = requests.session()
        res = RequestUtils(session=session).post_res(url=f"{self._host}UI/Dashboard",
                                                     params={"password": self._password})
        if res and session.cookies:
            cookie = session.cookies.get_dict()
        indexer_query_url = f"{self._host}api/v2.0/indexers?configured=true"
        try:
            ret = RequestUtils(cookies=cookie).get_res(indexer_query_url)
            if not ret or not ret.json():
                return []
            return [IndexerConf({"id": v["id"],
                                 "name": v["name"],
                                 "domain": f'{self._host}api/v2.0/indexers/{v["id"]}/results/torznab/',
                                 "public": True if v['type'] == 'public' else False,
                                 "builtin": False,
                                 "proxy": True})
                    for v in ret.json()]
        except Exception as e2:
            ExceptionUtils.exception_traceback(e2)
            return []

    def init_config(self, config=None):
        self.info(f"初始化配置{config}")

        if not config:
            return

        if config:
            self._host = config.get("host")
            self._api_key = config.get("api_key")
            self._password = config.get("password")
            res = self.get_status()
            self.info(f"检测结果：{res}")

    @EventHandler.register(EventType.SearchStart)
    def search_start(self, event):
        """
        监听搜索事件
        :param event:
        :return:
        """
        self.info(f"监听搜索事件{event}")

    @EventHandler.register(EventType.SubscribeAdd)
    def subscribe_add(self, event):
        """
        监听新增订阅
        :param event:
        :return:
        """
        self.info(f"监听订阅事件{event}")


    @EventHandler.register(EventType.SubscribeFinished)
    def subscribe_finished(self, event):
        """
        监听订阅完成
        :param event:
        :return:
        """
        self.info(f"监听订阅事件{event}")

    def get_state(self):
        return self._enable

    def stop_service(self):
        """
        退出插件
        """
        pass
import modules.IxLib as IxLib
import autobot.test as test
import autobot.helpers as helpers


class Ixia(object):
    def __init__(self):
        pass

    def ixia_initialize(self, node):
        t = test.Test()
        tg = t.traffic_generator(node)

        helpers.log("tcl_server_ip: %s" % tg.tcl_server_ip())
        helpers.log("chassis_ip: %s" % tg.chassis_ip())
        helpers.log("ports: %s" % tg.ports())

        self._ixia = IxLib.Ixia(tcl_server_ip=tg.tcl_server_ip(),
                                chassis_ip=tg.chassis_ip(),
                                port_map_list=tg.ports())
        self._ixia.ix_connect()

    def ixia_l2_add(self, **kwargs):
        return self._ixia.ixia_l2_add(**kwargs)

    def ixia_start_l2_traffic(self, stream=None):
        return self._ixia.ix_start_traffic_ethernet(stream)

    def ixia_stop_l2_traffic(self, stream=None):
        return self._ixia.ix_stop_traffic(stream)

    def ixia_fetch_port_stats(self):
        result = self._ixia.ix_fetch_port_stats()
        helpers.log('result:\n%s' % helpers.prettify(result))

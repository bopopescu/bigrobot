import modules.IxLib as IxLib
import autobot.test as test
import autobot.helpers as helpers


class Ixia(object):
    '''
        The Main IXIA TCL API IXIA Keywords that leverage from modules/Ixlib.py
    '''
    def __init__(self):
        pass

    def ixia_initialize(self, node, init=False):
        t = test.Test()
        tg = t.traffic_generator(node)
        if init:
            helpers.log("Re-Initializing Ixia...")
            helpers.log("tcl_server_ip: %s" % tg.tcl_server_ip())
            helpers.log("chassis_ip: %s" % tg.chassis_ip())
            helpers.log("ports: %s" % tg.ports())

            tg._ixia = IxLib.Ixia(tcl_server_ip=tg.tcl_server_ip(),
                                    chassis_ip=tg.chassis_ip(),
                                    port_map_list=tg.ports())
            tg._ixia.ix_connect()
        else:
            helpers.log("tcl_server_ip: %s" % tg.tcl_server_ip())
            helpers.log("chassis_ip: %s" % tg.chassis_ip())
            helpers.log("ports: %s" % tg.ports())

            self._ixia = IxLib.Ixia(tcl_server_ip=tg.tcl_server_ip(),
                                    chassis_ip=tg.chassis_ip(),
                                    port_map_list=tg.ports())
            self._ixia.ix_connect()

    def l2_add(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_l2_add(**kwargs)

    def l3_add(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_l3_add(**kwargs)

    def raw_stream_add(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_raw_add(**kwargs)

    def l3_add_host(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_l3_add_hosts(**kwargs)

    def l3_start_hosts(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_start_hosts(**kwargs)

    def l3_stop_hosts(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_stop_hosts(**kwargs)

    def l3_chk_gw_arp(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_chk_arp(**kwargs)

    def start_traffic(self, stream=None, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_start_traffic_ethernet(stream)

    def apply_traffic(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_apply_traffic()
#     def stop_l3_traffic(self, stream=None, **kwargs):
#         t = test.Test()
#         if 'node' not in kwargs:
#             node = 'tg1'
#         else:
#             node = kwargs['node']
#             del kwargs['node']
#         tg_handle = t.traffic_generator(node).handle()
#         return tg_handle._ixia.ix_stop_traffic(stream)
#
    def stop_traffic(self, stream=None, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_stop_traffic(stream)

    def fetch_port_stats(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()

        result = tg_handle.ix_fetch_port_stats(**kwargs)
        helpers.log('result:\n%s' % helpers.prettify(result))
        return result

    def clear_stats(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_clear_stats()

    def delete_traffic(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_delete_traffic()

    def simulate_port_state(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_simulate_port_state(**kwargs)
    def get_port_state(self, **kwargs):
        t = test.Test()
        if 'node' not in kwargs:
            node = 'tg1'
        else:
            node = kwargs['node']
            del kwargs['node']
        tg_handle = t.traffic_generator(node).handle()
        return tg_handle.ix_get_port_state(**kwargs)


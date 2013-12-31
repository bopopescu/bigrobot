import autobot.helpers as helpers
import autobot.test as test


class Mininet(object):

    def __init__(self):
        pass
        
    def mininet_dump(self):
        t = test.Test()
        mn = t.mininet()
        mn.cli('dump')
        helpers.log(mn.cli_response())

    def mininet_pingall(self):
        t = test.Test()
        mn = t.mininet()
        mn.cli('pingall')
        out = mn.cli_response()
        helpers.log("Cli response: %s" % out)
        
        drop = helpers.any_match(out, r'Results: (\d+)% dropped')
        helpers.log("drop: %s" % drop)
        if int(drop[0]) > 0:
            helpers.test_failure(drop[0] + "% packet drop")
    
    def mininet_ping(self, src, dst, count=5):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ping %s -c %s' % (src, dst, count))
        out = mn.cli_response()
        helpers.log("Cli response: %s" % out)

        loss = helpers.any_match(out, r', (\d+)% packet loss')
        helpers.log("packet loss: %s" % loss)
        if int(loss[0]) > 0:
            helpers.test_failure(loss[0] + "% packet loss")

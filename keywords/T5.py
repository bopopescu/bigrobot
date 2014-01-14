import autobot.helpers as helpers
import autobot.test as test


class T5(object):

    def __init__(self):
        pass

    def rest_create_tenant(self, tenant):
        t = test.Test()
        c = t.controller()

        helpers.log("Input arguments: tenant = %s" % tenant )
                
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % tenant
        c.rest.put(url, {"name": tenant})

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
        
    def _rest_show_tenant(self, tenant=None, negative=False):
        t = test.Test()
        c = t.controller()

        if tenant:
            # Show a specific tenant
            url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % tenant
        else:
            # Show all tenants
            url = '/api/v1/data/controller/applications/bvs/tenant'
            
        c.rest.get(url)
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        data = c.rest.content()

        # If showing all tenants, then we don't need to check further
        if tenant is None:
            return data
        
        # Search list of tenants to find a match
        for t in data:
            actual_tenant = t['name']
            if actual_tenant == tenant:
                helpers.log("Match: Actual tenant '%s' == expected tenant '%s'"
                            % (actual_tenant, tenant))
                
                if negative:
                    helpers.test_failure("Unexpected match: Actual tenant '%s' == expected tenant '%s'"
                                         % (actual_tenant, tenant))
                else:
                    return data
            else:
                helpers.log("No match: Actual tenant '%s' != expected tenant '%s'"
                            % (actual_tenant, tenant))
        
        # If we reach here, then we didn't find a matching tenant.
        if negative:
            helpers.log("Expected No match: For tenant '%s'" % tenant)
            return data
        else:
            helpers.test_failure("No match: For tenant '%s'." % tenant)

    def rest_show_tenant(self, tenant=None):
        helpers.log("Input arguments: tenant = %s" % tenant )
        return self._rest_show_tenant(tenant)
        
    def rest_show_tenant_gone(self, tenant=None):
        helpers.log("Input arguments: tenant = %s" % tenant )
        return self._rest_show_tenant(tenant, negative=True)
        
    def rest_delete_tenant(self, tenant=None):
        t = test.Test()
        c = t.controller()

        helpers.log("Input arguments: tenant = %s" % tenant )
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % tenant

        c.rest.delete(url, {"name": tenant})

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()

    def test_args(self, arg1, arg2, arg3):
        helpers.log("Input arguments: arg1 = %s" % arg1 )
        helpers.log("Input arguments: arg2 = %s" % arg2 )
        helpers.log("Input arguments: arg3 = %s" % arg3 )

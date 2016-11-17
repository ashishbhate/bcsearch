class LoadBalancer(object):
    """
    Client side load balancer for fetching from remote resources.
    WIP!
    """
    def __init__(self):
        # object, times between calls and weight
        self._items = []

    def add_resource(self, resource, hold_off, weight):
        # silently adds a last_returned
        last_called = None
        resource = [resource, hold_off, weight, last_called]
        return resource, hold_off, weight

    def update_resource(self, resource, hold_off=None, weight=None):
        pass

    def remove_resource(self, resource):
        for item in self._items:
            pass
        pass

    def get_resource(blocking=True):
        # returns first available resource with highest weight, and its weight.
        # If blocking is True it sleeps till a resource is available, otherwise
        # returns immediate with None and None
        pass

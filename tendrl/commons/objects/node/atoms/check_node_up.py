import os
from tendrl.commons import objects


class CheckNodeUp(objects.BaseObject):
    def run(self):
        fqdn = self.parameters.get("fqdn")
        response = os.system("ping -c 1 " + fqdn)
        # and then check the response...
        if response == 0:
            return True
        else:
            return False

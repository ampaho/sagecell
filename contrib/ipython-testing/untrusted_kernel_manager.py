from forking_kernel_manager import ForkingKernelManager
import logging

class UntrustedMultiKernelManager(object):
    def __init__(self):
        self.fkm = ForkingKernelManager()
        self._kernels = set()
        self.setup_sage()

    def setup_sage(self):
        try:
            logging.debug('initializing sage')
            import StringIO
            import sage
            import sage.all
            # The first plot takes about 2 seconds to generate (presumably
            # because lots of things, like matplotlib, are imported).  We plot
            # something here so that worker processes don't have this overhead
            logging.debug('plotting')
            try:
                sage.all.plot(lambda x: x, (0,1)).save(StringIO.StringIO())
            except Exception as e:
                logging.debug('plotting exception: %s'%e)
            # effectively do import *
            #self.sage_dict = dict([(n,getattr(sage.all, n)) for n in dir(sage.all) if not n.startswith("_")])
            self.sage_dict = {'sage': sage}
            sage_code = """
from sage.all import *
from sage.calculus.predefined import x
from sage.misc.html import html
from sage.server.support import help
from sagenb.misc.support import automatic_names
"""
            exec sage_code in self.sage_dict
            
            logging.debug('set up sage') 
        except ImportError as e:
            self.sage_dict = {}
    
    def start_kernel(self):
        x = self.fkm.start_kernel(self.sage_dict)
        self._kernels.add(x["kernel_id"])
        return x

    def kill_kernel(self, kernel_id):
        return self.fkm.kill_kernel(kernel_id)

    def interrupt_kernel(self, kernel_id):
        return self.fkm.interrupt_kernel(kernel_id)

    def restart_kernel(self, kernel_id, *args, **kwargs):
        return self.fkm.restart_kernel(self.sage_dict, kernel_id)
        

if __name__ == "__main__":
    x = UntrustedMultiKernelManager()
    y = x.start_kernel()
    print y
    from time import sleep 
    sleep(2)
    print x.restart_kernel(y["kernel_id"])
    sleep(2)
    x.kill_kernel(y["kernel_id"])

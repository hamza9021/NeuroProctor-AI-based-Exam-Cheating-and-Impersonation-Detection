# Site customization to fix sixdrepnet utils import conflict
import sys
import importlib.util

class UtilsImportFinder:
    """Custom import finder that redirects 'utils' to 'sixdrepnet.utils'"""
    
    def find_module(self, fullname, path=None):
        if fullname == 'utils':
            return self
        return None
    
    def load_module(self, fullname):
        # Load sixdrepnet.utils
        try:
            sixdrepnet_utils = importlib.import_module('sixdrepnet.utils')
            return sixdrepnet_utils
        except ImportError:
            # If sixdrepnet is not available, let normal import proceed
            return None

# Install the import hook before any other imports
utils_finder = UtilsImportFinder()
sys.meta_path.insert(0, utils_finder)


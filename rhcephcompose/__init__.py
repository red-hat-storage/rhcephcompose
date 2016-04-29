import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger('rhcephcompose')

from .build import Build
from .comps import Comps
from .variants import Variants

__all__ = ['Build', 'Comps', 'Variants']

__version__ = '1.0.1'

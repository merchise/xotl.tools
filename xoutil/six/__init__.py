from __future__ import absolute_import as _
import warnings

warnings.warn('xoutil.six is deprecated, use six directly.', stacklevel=2)

from six import *
from six import moves

moves = sys.modules[__name__ + ".moves"] = moves

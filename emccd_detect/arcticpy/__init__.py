from autoarray.instruments import acs
import pyximport
pyximport.install()
import Cython
from emccd_detect.arcticpy.main import add_cti, remove_cti, model_for_HST_ACS
from emccd_detect.arcticpy.roe import (
    ROE,
    ROEChargeInjection,
    ROETrapPumping,
)
from emccd_detect.arcticpy.ccd import CCD, CCDPhase
from emccd_detect.arcticpy.traps import (
    Trap,
    TrapInstantCapture,
    TrapLifetimeContinuumAbstract,
    TrapLogNormalLifetimeContinuum,
)
from emccd_detect.arcticpy.trap_managers import (
    AllTrapManager,
    TrapManager,
    TrapManagerTrackTime,
    TrapManagerInstantCapture,
)

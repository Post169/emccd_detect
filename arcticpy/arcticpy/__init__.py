from autoarray.instruments import acs

from arcticpy.arcticpy.main import add_cti, remove_cti, model_for_HST_ACS
from arcticpy.arcticpy.roe import (
    ROE,
    ROEChargeInjection,
    ROETrapPumping,
)
from arcticpy.arcticpy.ccd import CCD, CCDPhase
from arcticpy.arcticpy.traps import (
    Trap,
    TrapInstantCapture,
    TrapLifetimeContinuumAbstract,
    TrapLogNormalLifetimeContinuum,
)
from arcticpy.arcticpy.trap_managers import (
    AllTrapManager,
    TrapManager,
    TrapManagerTrackTime,
    TrapManagerInstantCapture,
)

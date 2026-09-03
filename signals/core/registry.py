from ..indicators.absolute_strength import ABSOLUTE_STRENGTH
from ..indicators.aroon import AROON
from ..indicators.atr import ATR
from ..indicators.ichimoku_cross import ICHIMOKU_CROSS
from ..indicators.ichimoku_cloud import ICHIMOKU_CLOUD
from ..indicators.kijunsen import KIJUNSEN
from ..indicators.ssl import SSL
from ..indicators.wae import WAE


SIGNALS = {
    "absolute_strength": ABSOLUTE_STRENGTH,
    "aroon": AROON,
    "atr": ATR,
    "ichimoku_cross": ICHIMOKU_CROSS,
    "ichimoku_cloud": ICHIMOKU_CLOUD,
    "kijunsen": KIJUNSEN,
    "ssl": SSL,
    "wae": WAE,
}


def get_signal(name):
    if name not in SIGNALS:
        raise ValueError(
            f"Signal '{name}' is not registered. "
            f"Available: {list(SIGNALS)}"
        )
    return SIGNALS[name]


def validate_signals(names):
    invalid = [name for name in names if name not in SIGNALS]

    if invalid:
        raise ValueError(
            f"Unknown signal(s): {invalid}. "
            f"Available: {list(SIGNALS)}"
        )
"""Dip-buy BTC bot for make.fun btc-race-24h-20261123-0511.

Long only, one position at a time, full size. Buys a 30-minute dip once the
last 5 minutes turn positive, then exits at a fixed +1.2% take-profit or a
fixed -1.2% stop-loss. Integer arithmetic only; no floats, no clock, no
network, no files, no randomness.
"""

# Strategy parameters (all integer bps; 10000 bps = 100%):
#   DIP_BPS 80        -- enter when the 30-min return is below -0.80%.
#   BOUNCE_BARS 5     -- the last 5-min return must be positive.
#   TAKE_PROFIT 120 / STOP_LOSS 120 -- exit at +1.2% / -1.2% vs the entry bar's close.
#   LOSS_LIMIT $15    -- stop opening new positions once realized losses reach $15.
# Why the bounce confirmation: a 30-min dip alone keeps falling more often than
# it reverses, so the bot only buys once the last 5 minutes have turned up --
# that turn is the first sign the dip is a bounce rather than the start of a slide.
# The 30-min dip is measured bar-to-bar on closes; the entry bar's close is the
# anchor for both exit levels, so the levels never move once a position is open.

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
BPS = 10000
DIP_BPS = 80
BOUNCE_BARS = 5
HISTORY_BARS = 30
TAKE_PROFIT_BPS = 120
STOP_LOSS_BPS = 120
MAX_SLIPPAGE_BPS = 100
MIN_NOTIONAL_UNITS = 1000000
LOSS_LIMIT_UNITS = 15000000
INITIAL_CAPITAL_UNITS = 1000000000

closes = []
entry_close = None


def on_batch(state, batch):
    global entry_close
    close = state.close(SYMBOL)
    if close is None:
        return []
    closes.append(close)
    if len(closes) > HISTORY_BARS + 1:
        del closes[: -(HISTORY_BARS + 1)]
    if state.warming_up:
        return []
    holding = state.positions.get(SYMBOL)
    if holding is not None and holding.qty > 0:
        if entry_close is not None:
            if close * BPS >= entry_close * (BPS + TAKE_PROFIT_BPS):
                return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty, "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            if close * BPS <= entry_close * (BPS - STOP_LOSS_BPS):
                return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty, "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []
    if len(closes) < HISTORY_BARS + 1:
        return []
    close_30 = closes[-(HISTORY_BARS + 1)]
    close_5 = closes[-(BOUNCE_BARS + 1)]
    if close * BPS >= close_30 * (BPS - DIP_BPS):
        return []
    if close <= close_5:
        return []
    if state.cash <= INITIAL_CAPITAL_UNITS - LOSS_LIMIT_UNITS:
        return []
    amount = state.cash
    room = state.weight_room(SYMBOL)
    if room < amount:
        amount = room
    if amount < MIN_NOTIONAL_UNITS:
        return []
    entry_close = close
    return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": amount, "max_slippage_bps": MAX_SLIPPAGE_BPS}]


makefun_bars.run(on_batch)

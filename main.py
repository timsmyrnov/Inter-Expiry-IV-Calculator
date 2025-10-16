import math
import pandas as pd
import yfinance as yf

DAY_BASIS = 365

def get_ivs(symbol, targets_days) -> dict:
    ticker = yf.Ticker(symbol)
    spot = float(ticker.history(period="1d")["Close"].iloc[-1])
    today = pd.Timestamp.today().normalize()

    listed = []
    for e in ticker.options:
        d = (pd.to_datetime(e) - today).days
        if d > 0:
            listed.append((d, e))
    if not listed:
        return {}

    listed.sort()
    exp_ivs = {}

    for target in targets_days:
        d, e = next(((dd, ee) for dd, ee in listed if dd >= target), listed[-1])
        chain = ticker.option_chain(e)
        df = pd.concat(
            [
                chain.calls[["strike", "impliedVolatility"]],
                chain.puts[["strike", "impliedVolatility"]],
            ],
            ignore_index=True,
        )
        if df.empty:
            continue
        df = df[df["impliedVolatility"].notna()]
        df = df.sort_values(by="strike", key=lambda x: (x - spot).abs())
        iv = df["impliedVolatility"].iloc[0]

        if pd.isna(iv):
            continue
        exp_ivs[d] = float(iv)

    return exp_ivs

def inter_iv_calc(expiry_atm_vols: dict, day_basis: int = DAY_BASIS) -> dict:
    keys = sorted(expiry_atm_vols.keys())
    if len(keys) < 2:
        return {}

    variances = {k: (expiry_atm_vols[k] ** 2) * (k / day_basis) for k in keys}
    inter_ivs = {}

    for i in range(len(keys) - 1):
        t1, t2 = keys[i], keys[i + 1]
        T_interval = (t2 - t1) / day_basis
        var_interval = variances[t2] - variances[t1]

        if var_interval < 0:
            var_interval = 0.0

        inter_iv = math.sqrt(var_interval / T_interval) if T_interval > 0 else float("nan")
        inter_ivs[(t1, t2)] = inter_iv

    return inter_ivs

if __name__ == "__main__":
    expiries = [1, 8, 15, 22]
    ivs = get_ivs("UBER", expiries)
    print("ATMs by actual listed days:", ivs)
    print("Interval IVs:", inter_iv_calc(ivs))
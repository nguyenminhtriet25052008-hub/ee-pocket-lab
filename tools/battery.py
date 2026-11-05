#!/usr/bin/env python3
"""battery - IoT / embedded device battery life estimator (Active + Deep Sleep duty cycle).

Usage:
    python battery.py --mah 2000 --i-active 80 --t-active 2 --i-sleep 0.05 --t-sleep 58
    python battery.py --mah 500 --i-active 12 --derate 0.8
"""
import argparse


def estimate_life(capacity_mah, i_active_ma, t_active_s=1.0, i_sleep_ma=0.0, t_sleep_s=0.0, derate=0.85):
    """Return average current (mA), duty cycle (%), and estimated runtime (hours, days)."""
    cycle_s = t_active_s + t_sleep_s
    if cycle_s <= 0 or capacity_mah <= 0:
        raise ValueError("capacity and cycle time must be > 0")
    duty_pct = (t_active_s / cycle_s) * 100.0
    i_avg_ma = (i_active_ma * t_active_s + i_sleep_ma * t_sleep_s) / cycle_s
    usable_mah = capacity_mah * derate
    hours = usable_mah / i_avg_ma
    return {
        "duty_pct": duty_pct,
        "i_avg_ma": i_avg_ma,
        "usable_mah": usable_mah,
        "hours": hours,
        "days": hours / 24.0,
        "years": hours / (24.0 * 365.25),
    }


def main():
    ap = argparse.ArgumentParser(description="Embedded / IoT battery life calculator.")
    ap.add_argument("--mah", type=float, required=True, help="nominal battery capacity (mAh)")
    ap.add_argument("--i-active", type=float, required=True, help="active current (mA)")
    ap.add_argument("--t-active", type=float, default=1.0, help="active duration per cycle (s, default 1)")
    ap.add_argument("--i-sleep", type=float, default=0.0, help="sleep current (mA, e.g. 0.02 for 20 uA)")
    ap.add_argument("--t-sleep", type=float, default=0.0, help="sleep duration per cycle (s, default 0)")
    ap.add_argument("--derate", type=float, default=0.85, help="usable capacity factor 0..1 (default 0.85)")
    args = ap.parse_args()

    res = estimate_life(args.mah, args.i_active, args.t_active, args.i_sleep, args.t_sleep, args.derate)
    print(f"Battery: {args.mah:g} mAh (usable {res['usable_mah']:.0f} mAh at {args.derate * 100:.0f}% derating)")
    print(f"Active : {args.i_active:g} mA for {args.t_active:g}s  |  Sleep: {args.i_sleep:g} mA for {args.t_sleep:g}s")
    print(f"Duty   : {res['duty_pct']:.3f}%  |  Average Current = {res['i_avg_ma']:.4f} mA ({res['i_avg_ma'] * 1e3:.1f} uA)")
    print(f"Runtime: {res['hours']:.1f} hours  (~{res['days']:.1f} days / {res['years']:.2f} years)")


if __name__ == "__main__":
    main()

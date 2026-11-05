#!/usr/bin/env python3
"""pcbtrace - IPC-2221 PCB copper trace width, resistance & voltage drop calculator.

Usage:
    python pcbtrace.py --amps 2.5                       # 2.5A, 1 oz/ft^2, +10 C rise
    python pcbtrace.py --amps 5 --oz 2 --rise 20 --len 50 --inner
"""
import argparse

MM_PER_MIL = 0.0254
RHO_CU = 1.724e-8  # Ohm*m at 20 C
ALPHA_CU = 0.00393  # temp coeff 1/C


def ipc2221_width_mm(current_a, temp_rise_c=10.0, copper_oz=1.0, internal=False):
    """Return minimum trace width in mm per IPC-2221 formula."""
    k = 0.024 if internal else 0.048
    area_mils2 = (current_a / (k * (temp_rise_c ** 0.44))) ** (1.0 / 0.725)
    thickness_mils = copper_oz * 1.378
    width_mils = area_mils2 / thickness_mils
    return width_mils * MM_PER_MIL


def trace_drop(current_a, width_mm, length_mm, copper_oz=1.0, temp_c=25.0):
    """Return (resistance_ohm, voltage_drop_v, power_mw) for a copper trace."""
    thickness_m = (copper_oz * 1.378 * MM_PER_MIL) * 1e-3
    area_m2 = (width_mm * 1e-3) * thickness_m
    length_m = length_mm * 1e-3
    r_ohm = (RHO_CU * (1.0 + ALPHA_CU * (temp_c - 20.0)) * length_m) / area_m2
    v_drop = current_a * r_ohm
    return r_ohm, v_drop, current_a * v_drop * 1000.0


def main():
    ap = argparse.ArgumentParser(description="IPC-2221 PCB trace width & voltage drop calculator.")
    ap.add_argument("--amps", type=float, required=True, help="trace current (A)")
    ap.add_argument("--oz", type=float, default=1.0, help="copper weight in oz/ft^2 (default 1.0)")
    ap.add_argument("--rise", type=float, default=10.0, help="allowed temperature rise in C (default 10)")
    ap.add_argument("--len", type=float, default=25.0, help="trace length in mm (default 25)")
    ap.add_argument("--inner", action="store_true", help="internal layer (default: external layer)")
    args = ap.parse_args()

    w_mm = ipc2221_width_mm(args.amps, args.rise, args.oz, args.inner)
    w_mil = w_mm / MM_PER_MIL
    r_ohm, v_drop, p_mw = trace_drop(args.amps, w_mm, args.len, args.oz, 25.0 + args.rise)
    layer = "Internal" if args.inner else "External"
    print(f"IPC-2221 ({layer}, {args.oz:g} oz Cu, +{args.rise:g} C rise) for {args.amps:g} A:")
    print(f"  Min Trace Width : {w_mm:.3f} mm  ({w_mil:.1f} mil)")
    print(f"  Over {args.len:g} mm len : R = {r_ohm * 1e3:.2f} mOhm  |  V_drop = {v_drop * 1e3:.2f} mV  |  P = {p_mw:.1f} mW")


if __name__ == "__main__":
    main()

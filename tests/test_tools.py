"""Unit tests for ee-pocket-lab (stdlib unittest only). Run: python -m unittest discover -s tests -v"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import adc  # noqa: E402
import battery  # noqa: E402
import crc  # noqa: E402
import divider  # noqa: E402
import ledcalc  # noqa: E402
import ne555  # noqa: E402
import numbase  # noqa: E402
import opamp  # noqa: E402
import pcbtrace  # noqa: E402
import rcfilter  # noqa: E402


class TestDivider(unittest.TestCase):
    def test_calc_vout(self):
        vout, i_ma = divider.calc_vout(10.0, 1000.0, 1000.0)
        self.assertAlmostEqual(vout, 5.0)
        self.assertAlmostEqual(i_ma, 5.0)

    def test_best_pairs(self):
        pairs = divider.best_pairs(5.0, 3.3, "E24", top=3)
        self.assertEqual(len(pairs), 3)
        _, _, vo, err = pairs[0]
        self.assertLess(abs(err), 1.5)
        self.assertAlmostEqual(vo, 3.3, delta=0.05)


class TestRcFilter(unittest.TestCase):
    def test_rc_cutoff(self):
        fc = rcfilter.rc_cutoff(1000.0, 100e-9)
        self.assertAlmostEqual(fc, 1591.5494, places=3)

    def test_response_at_cutoff(self):
        mag, db, phase = rcfilter.response(1000.0, 1000.0, "lp")
        self.assertAlmostEqual(mag, 1.0 / math.sqrt(2.0), places=5)
        self.assertAlmostEqual(db, -3.0103, places=3)
        self.assertAlmostEqual(phase, -45.0, places=3)

    def test_lc_resonance(self):
        f0 = rcfilter.lc_resonance(1e-3, 1e-6)
        self.assertAlmostEqual(f0, 5032.921, places=2)


class TestLedCalc(unittest.TestCase):
    def test_solve_led(self):
        res = ledcalc.solve_led(5.0, 2.0, 20.0, count=1)
        self.assertAlmostEqual(res["r_exact"], 150.0)
        self.assertEqual(res["r_std"], 150.0)
        self.assertEqual(res["rating"], "1/8 W")

    def test_invalid_supply(self):
        with self.assertRaises(ValueError):
            ledcalc.solve_led(3.0, 2.0, 20.0, count=2)


class TestNe555(unittest.TestCase):
    def test_astable(self):
        res = ne555.astable(1000.0, 10000.0, 100e-9)
        self.assertAlmostEqual(res["freq"], 687.0, delta=0.1)
        self.assertTrue(50.0 < res["duty"] < 100.0)

    def test_monostable(self):
        t = ne555.monostable(100e3, 10e-6)
        self.assertAlmostEqual(t, math.log(3.0), places=4)


class TestPcbTrace(unittest.TestCase):
    def test_ipc2221(self):
        w_ext = pcbtrace.ipc2221_width_mm(2.0, 10.0, 1.0, internal=False)
        w_int = pcbtrace.ipc2221_width_mm(2.0, 10.0, 1.0, internal=True)
        self.assertGreater(w_int, w_ext)
        self.assertGreater(w_ext, 0.5)

    def test_trace_drop(self):
        r, v, p = pcbtrace.trace_drop(2.0, 1.0, 50.0, 1.0)
        self.assertGreater(r, 0.0)
        self.assertAlmostEqual(v, 2.0 * r)
        self.assertAlmostEqual(p, 2.0 * v * 1000.0)


class TestOpAmp(unittest.TestCase):
    def test_gains(self):
        av_ni, _ = opamp.calc_gain("noninv", 9000.0, 1000.0)
        av_in, _ = opamp.calc_gain("inv", 10000.0, 2000.0)
        self.assertAlmostEqual(av_ni, 10.0)
        self.assertAlmostEqual(av_in, -5.0)

    def test_find_pairs(self):
        pairs = opamp.find_pairs("noninv", 11.0)
        self.assertAlmostEqual(pairs[0][2], 11.0, places=3)


class TestBattery(unittest.TestCase):
    def test_estimate_life(self):
        res = battery.estimate_life(1000.0, 100.0, 1.0, 0.0, 9.0, derate=1.0)
        self.assertAlmostEqual(res["i_avg_ma"], 10.0)
        self.assertAlmostEqual(res["hours"], 100.0)


class TestNumbase(unittest.TestCase):
    def test_convert_signed_8bit(self):
        r = numbase.convert(0xFF, width=8)
        self.assertEqual(r["unsigned"], 255)
        self.assertEqual(r["signed"], -1)
        self.assertEqual(len(r["set_bits"]), 8)


class TestCrc(unittest.TestCase):
    def test_standard_check_vector(self):
        res = crc.compute_all(b"123456789")
        self.assertEqual(res["crc8"], 0xF4)
        self.assertEqual(res["crc16_ccitt"], 0x29B1)
        self.assertEqual(res["crc16_modbus"], 0x4B37)
        self.assertEqual(res["crc32"], 0xCBF43926)


class TestAdc(unittest.TestCase):
    def test_quantize_midpoint(self):
        r = adc.analyze_adc(12, 3.3, vin=1.65)
        self.assertIn(r["code"], (2047, 2048))
        self.assertLess(abs(r["q_err_mv"]), 1.0)


if __name__ == "__main__":
    unittest.main()

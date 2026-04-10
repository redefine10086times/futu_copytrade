"""Tests that exercise the real trading logic via mocks."""

import sys
import types
import unittest
from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo


def _install_fake_dependencies():
    """Provide lightweight stand-ins so tests can import production modules."""
    if "moomoo" not in sys.modules:
        fake_moomoo = types.ModuleType("moomoo")
        fake_moomoo.OpenSecTradeContext = object
        fake_moomoo.TrdEnv = types.SimpleNamespace(SIMULATE="SIMULATE", REAL="REAL")
        fake_moomoo.TrdMarket = types.SimpleNamespace(US="US", HK="HK")
        fake_moomoo.TrdSide = types.SimpleNamespace(BUY="BUY", SELL="SELL")
        fake_moomoo.OrderType = types.SimpleNamespace(
            MARKET="MARKET",
            NORMAL="NORMAL",
            STOP_LIMIT="STOP_LIMIT",
            TRAILING_STOP="TRAILING_STOP",
        )
        fake_moomoo.OrderStatus = types.SimpleNamespace(
            FILLED_ALL="FILLED_ALL",
            CANCELLED_ALL="CANCELLED_ALL",
            FAILED="FAILED",
            DISABLED="DISABLED",
            DELETED="DELETED",
        )
        fake_moomoo.ModifyOrderOp = types.SimpleNamespace(NORMAL="NORMAL", CANCEL="CANCEL")
        fake_moomoo.SecurityFirm = types.SimpleNamespace(FUTUINC="FUTUINC")
        fake_moomoo.TrailType = types.SimpleNamespace(RATIO="RATIO", AMOUNT="AMOUNT")
        fake_moomoo.RET_OK = 0
        sys.modules["moomoo"] = fake_moomoo

    if "yfinance" not in sys.modules:
        fake_yfinance = types.ModuleType("yfinance")
        fake_yfinance.Ticker = object
        sys.modules["yfinance"] = fake_yfinance

    if "requests" not in sys.modules:
        fake_requests = types.ModuleType("requests")
        fake_requests.get = mock.Mock()
        sys.modules["requests"] = fake_requests


_install_fake_dependencies()

import trader  # noqa: E402
import main  # noqa: E402


ET = ZoneInfo("America/New_York")


class _FakeDateTime:
    current = None

    @classmethod
    def now(cls, tz=None):
        return cls.current


class _FakeSeries:
    def __init__(self, value):
        self.iloc = [value]


class _FakeFrame(dict):
    def __getitem__(self, key):
        return _FakeSeries(super().__getitem__(key))


class TradableHoursTests(unittest.TestCase):
    def _assert_tradable(self, dt, expected):
        with mock.patch.object(trader, "datetime", _FakeDateTime):
            _FakeDateTime.current = dt
            self.assertEqual(trader._is_tradable_hours(), expected)

    def test_weekday_night_is_tradable(self):
        self._assert_tradable(datetime(2026, 4, 8, 22, 0, tzinfo=ET), True)

    def test_friday_after_20_is_not_tradable(self):
        self._assert_tradable(datetime(2026, 4, 10, 20, 0, tzinfo=ET), False)

    def test_sunday_before_16_is_not_tradable(self):
        self._assert_tradable(datetime(2026, 4, 12, 15, 59, tzinfo=ET), False)

    def test_sunday_16_is_tradable(self):
        self._assert_tradable(datetime(2026, 4, 12, 16, 0, tzinfo=ET), True)


class TraderPriceTests(unittest.TestCase):
    def setUp(self):
        self.trader = trader.Trader()
        self.trader._trd_ctx = mock.Mock()

    def test_place_order_buy_limit_uses_discounted_price(self):
        self.trader._trd_ctx.place_order.return_value = (
            trader.RET_OK,
            _FakeFrame(order_id="OID-1"),
        )
        with mock.patch.object(self.trader, "get_price", return_value=100.0):
            order_id = self.trader.place_order("US.AAPL", 10, trader.TrdSide.BUY, False)

        self.assertEqual(order_id, "OID-1")
        self.assertEqual(self.trader._trd_ctx.place_order.call_args.kwargs["price"], 99.90)

    def test_place_order_sell_limit_uses_discounted_price(self):
        self.trader._trd_ctx.place_order.return_value = (
            trader.RET_OK,
            _FakeFrame(order_id="OID-2"),
        )
        with mock.patch.object(self.trader, "get_price", return_value=100.0):
            order_id = self.trader.place_order("US.AAPL", 10, trader.TrdSide.SELL, False)

        self.assertEqual(order_id, "OID-2")
        self.assertEqual(self.trader._trd_ctx.place_order.call_args.kwargs["price"], 99.90)

    def test_modify_order_price_buy_reprices_upward(self):
        self.trader._trd_ctx.modify_order.return_value = (trader.RET_OK, {})
        with mock.patch.object(self.trader, "get_price", return_value=100.0):
            self.trader.modify_order_price("OID-3", "US.AAPL", 10, trader.TrdSide.BUY, 1)
            first_price = self.trader._trd_ctx.modify_order.call_args.kwargs["price"]
            self.trader.modify_order_price("OID-3", "US.AAPL", 10, trader.TrdSide.BUY, 2)
            second_price = self.trader._trd_ctx.modify_order.call_args.kwargs["price"]

        self.assertEqual(first_price, 100.00)
        self.assertEqual(second_price, 100.10)

    def test_modify_order_price_sell_reprices_downward(self):
        self.trader._trd_ctx.modify_order.return_value = (trader.RET_OK, {})
        with mock.patch.object(self.trader, "get_price", return_value=100.0):
            self.trader.modify_order_price("OID-4", "US.AAPL", 10, trader.TrdSide.SELL, 1)
            first_price = self.trader._trd_ctx.modify_order.call_args.kwargs["price"]
            self.trader.modify_order_price("OID-4", "US.AAPL", 10, trader.TrdSide.SELL, 2)
            second_price = self.trader._trd_ctx.modify_order.call_args.kwargs["price"]

        self.assertEqual(first_price, 99.80)
        self.assertEqual(second_price, 99.70)


class RunOnceFlowTests(unittest.TestCase):
    def setUp(self):
        main._overnight_notified = None

    def test_run_once_executes_diff_in_tradable_extended_hours(self):
        dt = datetime(2026, 4, 12, 16, 0, tzinfo=ET)
        diff = {
            "added": [{"code": "US.AAPL", "name": "Apple", "weight": 0.2}],
            "removed": [],
            "changed": [],
        }
        trader_instance = mock.Mock()

        with mock.patch.object(trader, "datetime", _FakeDateTime), \
             mock.patch.object(main, "fetch_portfolio", return_value=[{"code": "US.AAPL"}]), \
             mock.patch.object(main, "load_snapshot", return_value=[]), \
             mock.patch.object(main, "diff_positions", return_value=diff), \
             mock.patch.object(main, "has_changes", return_value=True), \
             mock.patch.object(main, "_load_pending_buys", return_value=[]), \
             mock.patch.object(main, "_load_overnight_account", return_value=None), \
             mock.patch.object(main, "_clear_overnight_account"), \
             mock.patch.object(main, "notify_changes"), \
             mock.patch.object(main, "save_snapshot"), \
             mock.patch.object(main, "Trader", return_value=trader_instance):
            _FakeDateTime.current = dt
            main.run_once(dry_run=False)

        trader_instance.execute_diff.assert_called_once_with(
            diff,
            use_market_order=False,
            skip_sells=False,
        )

    def test_run_once_skips_trading_when_market_closed(self):
        dt = datetime(2026, 4, 12, 10, 0, tzinfo=ET)
        diff = {
            "added": [{"code": "US.AAPL", "name": "Apple", "weight": 0.2}],
            "removed": [],
            "changed": [],
        }
        overnight_file = mock.Mock()
        overnight_file.exists.return_value = True

        with mock.patch.object(trader, "datetime", _FakeDateTime), \
             mock.patch.object(main, "fetch_portfolio", return_value=[{"code": "US.AAPL"}]), \
             mock.patch.object(main, "load_snapshot", return_value=[]), \
             mock.patch.object(main, "diff_positions", return_value=diff), \
             mock.patch.object(main, "has_changes", return_value=True), \
             mock.patch.object(main, "notify_overnight_change"), \
             mock.patch.object(main, "_snapshot_account_positions"), \
             mock.patch.object(main, "_save_overnight_account"), \
             mock.patch.object(main, "Trader") as trader_cls, \
             mock.patch.object(main, "OVERNIGHT_ACCT_FILE", overnight_file):
            _FakeDateTime.current = dt
            main.run_once(dry_run=False)

        trader_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()

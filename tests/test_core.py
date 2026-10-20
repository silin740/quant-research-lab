import copy
import tempfile
import unittest
from pathlib import Path
from quantlab.core import backtest, signals, load_bars
from quantlab.cli import run

def bars(prices):
    return [dict(date=f'2024-01-{i+1:02d}',open=p,high=p+1,low=p-1,close=p,volume=100) for i,p in enumerate(prices)]

class QuantTests(unittest.TestCase):
    def test_next_open_execution(self):
        r=backtest(bars([100,110,120]),[1,0,0],fee_bps=0,slippage_bps=0)
        self.assertEqual([x['date'] for x in r['fills']],['2024-01-02','2024-01-03'])
        self.assertAlmostEqual(r['equity'][-1]['equity'],10000*120/110)
        self.assertEqual(r['equity'][0]['shares'],0)
    def test_cost_accounting(self):
        r=backtest(bars([100,100,100]),[1,0,0],fee_bps=10,slippage_bps=20)
        quantity=10000/(100*1.002*1.001)
        self.assertAlmostEqual(r['equity'][-1]['equity'],quantity*100*0.998*0.999)
    def test_drawdown(self):
        r=backtest(bars([100,100,80,90]),[1,1,1,1],fee_bps=0,slippage_bps=0)
        self.assertAlmostEqual(r['metrics']['max_drawdown'],-0.2)
    def test_cash_metrics(self):
        r=backtest(bars([100,100,100]),[0,0,0])
        self.assertIsNone(r['metrics']['sharpe'])
        self.assertEqual(r['metrics']['total_return'],0)
    def test_last_signal_cannot_trade(self):
        self.assertEqual(backtest(bars([100,110]),[0,1])['fills'],[])
    def test_invalid_configuration(self):
        for kw in ({'fee_bps':-1},{'slippage_bps':10000},{'initial_cash':0}):
            with self.assertRaises(ValueError): backtest(bars([100,100]),[1,0],**kw)
        with self.assertRaises(ValueError): backtest(bars([100,100]),[1])
    def test_breakout(self):
        self.assertEqual(signals(bars([100,100,103,99,97]),'breakout',2),[0,0,1,1,0])
    def test_vwap(self):
        self.assertEqual(signals(bars([100,100,90,110]),'vwap',2,0.02),[0,0,1,0])
    def test_future_independence(self):
        data=bars([100,101,105,99,98,110,80,120])
        changed=copy.deepcopy(data)
        changed[-1].update(open=1000,high=1001,low=999,close=1000)
        for strategy in ('breakout','vwap'):
            self.assertEqual(signals(data,strategy,2)[:-1],signals(changed,strategy,2)[:-1])
            self.assertEqual(signals(data[:5],strategy,2),signals(data,strategy,2)[:5])
    def test_data_validation(self):
        for row in ('2024-01-01,100,101,99,100,10','2024-01-02,100,101,99,nan,10','2024-01-02,100,90,99,100,10','2024-01-02,100,101,99,100,0'):
            with tempfile.TemporaryDirectory() as directory:
                p=Path(directory)/'bad.csv'
                p.write_text('date,open,high,low,close,volume\n2024-01-01,100,101,99,100,10\n'+row+'\n')
                with self.assertRaises(ValueError): load_bars(p)
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as directory:
            r=run('data/synthetic_daily.csv',directory)
            self.assertEqual(r['bars'],756)
            self.assertEqual(len(r['results']),3)
            self.assertTrue((Path(directory)/'summary.json').exists())
            self.assertEqual(len(list(Path(directory).glob('*.csv'))),6)

if __name__=='__main__': unittest.main()

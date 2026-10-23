# Differential test report

## Oracle 1: statsmodels GofChisquarePower (a-priori)

- Vectors: **799** (w x alpha x power x df grid)
- N exact match vs ceil(statsmodels N): **799/799** (100.0%)
- actual_power within 1e-6 of statsmodels power at our N: **799/799**

statsmodels returns a fractional N (e.g. 219.4); a sample size must be an
integer that *reaches* the target power, so the engine reports the smallest
integer N with power >= target, i.e. ceil(). See LEDGER.md for the rounding rule.

- Skipped (statsmodels solver returned NaN, all very large w): **1**

## Oracle 2: G*Power 3.1.9.7 GUI (oracle/gpower_gui_vectors.csv)

_No G*Power GUI values recorded yet. Fill the exp_* columns from the GUI._

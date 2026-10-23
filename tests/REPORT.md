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

- Vectors with recorded G*Power values: **44**
- Full match: **42/44** (95.5%)
- Deliberate differences (contract range wins over G*Power): g25 (n_total = 1), g38 (w = 0)
- Unexplained mismatches: **0** 

| id | match | expected | got |
|---|---|---|---|
| g01 | yes | `{'n_total': '220', 'ncp': '19.8000000', 'critical_chi2': '11.0704977', 'actual_power': '0.9502155'}` | `{'ncp': 19.8, 'critical_chi2': 11.070497693516355, 'n_total': 220, 'actual_power': 0.9502155018970162}` |
| g02 | yes | `{'n_total': '88', 'ncp': '7.9200000', 'critical_chi2': '3.8414588', 'actual_power': '0.8035275'}` | `{'ncp': 7.92, 'critical_chi2': 3.8414588206941285, 'n_total': 88, 'actual_power': 0.8035274844561174}` |
| g03 | yes | `{'n_total': '785', 'ncp': '7.8500000', 'critical_chi2': '3.8414588', 'actual_power': '0.8000569'}` | `{'ncp': 7.850000000000001, 'critical_chi2': 3.8414588206941285, 'n_total': 785, 'actual_power': 0.8000569268798245}` |
| g04 | yes | `{'n_total': '32', 'ncp': '8.0000000', 'critical_chi2': '3.8414588', 'actual_power': '0.8074304'}` | `{'ncp': 8.0, 'critical_chi2': 3.8414588206941285, 'n_total': 32, 'actual_power': 0.8074304194325567}` |
| g05 | yes | `{'n_total': '129948', 'ncp': '12.9948000', 'critical_chi2': '3.8414588', 'actual_power': '0.9500013'}` | `{'ncp': 12.994800000000001, 'critical_chi2': 3.8414588206941285, 'n_total': 129948, 'actual_power': 0.9500013004068691}` |
| g06 | yes | `{'n_total': '7848861', 'ncp': '7.8488610', 'critical_chi2': '3.8414588', 'actual_power': '0.8000000'}` | `{'ncp': 7.848860999999999, 'critical_chi2': 3.8414588206941285, 'n_total': 7848861, 'actual_power': 0.8000000245161561}` |
| g07 | yes | `{'n_total': '2', 'ncp': '8.0000000', 'critical_chi2': '3.8414588', 'actual_power': '0.8074304'}` | `{'ncp': 8.0, 'critical_chi2': 3.8414588206941285, 'n_total': 2, 'actual_power': 0.8074304194325567}` |
| g08 | yes | `{'n_total': '1', 'ncp': '25.0000000', 'critical_chi2': '3.8414588', 'actual_power': '0.9988173'}` | `{'ncp': 25.0, 'critical_chi2': 3.8414588206941285, 'n_total': 1, 'actual_power': 0.9988172507035041}` |
| g09 | yes | `{'n_total': '1', 'ncp': '0.0900000', 'critical_chi2': '11.0704977', 'actual_power': '0.0539009'}` | `{'ncp': 0.09, 'critical_chi2': 11.070497693516355, 'n_total': 1, 'actual_power': 0.053900899738176425}` |
| g10 | yes | `{'error_text': 'Power must be greater than or equal to alpha.'}` | `{'error': 'Power must be greater than or equal to alpha', 'code': 'INCONSISTENT', 'field': 'power'}` |
| g11 | yes | `{'n_total': '1', 'ncp': '0.0900000', 'critical_chi2': '11.0704977', 'actual_power': '0.0539009'}` | `{'ncp': 0.09, 'critical_chi2': 11.070497693516355, 'n_total': 1, 'actual_power': 0.053900899738176425}` |
| g12 | yes | `{'n_total': '445', 'ncp': '40.0500000', 'critical_chi2': '23.2092512', 'actual_power': '0.9900571'}` | `{'ncp': 40.05, 'critical_chi2': 23.20925115895436, 'n_total': 445, 'actual_power': 0.9900571081146358}` |
| g13 | yes | `{'n_total': '289', 'ncp': '26.0100000', 'critical_chi2': '16.2662362', 'actual_power': '0.9012598'}` | `{'ncp': 26.009999999999998, 'critical_chi2': 16.26623619623813, 'n_total': 289, 'actual_power': 0.9012597691193169}` |
| g14 | yes | `{'n_total': '262', 'ncp': '10.4800000', 'critical_chi2': '4.6051702', 'actual_power': '0.9005778'}` | `{'ncp': 10.480000000000002, 'critical_chi2': 4.605170185988092, 'n_total': 262, 'actual_power': 0.9005777569674721}` |
| g15 | yes | `{'n_total': '203', 'ncp': '12.6875000', 'critical_chi2': '5.9914645', 'actual_power': '0.9008030'}` | `{'ncp': 12.6875, 'critical_chi2': 5.991464547107983, 'n_total': 203, 'actual_power': 0.9008029804771022}` |
| g16 | yes | `{'n_total': '2705', 'ncp': '27.0500000', 'critical_chi2': '16.8118938', 'actual_power': '0.9500639'}` | `{'ncp': 27.050000000000004, 'critical_chi2': 16.811893829770927, 'n_total': 2705, 'actual_power': 0.9500639364921998}` |
| g17 | yes | `{'n_total': '284', 'ncp': '25.5600000', 'critical_chi2': '3.8414588', 'actual_power': '0.9990183'}` | `{'ncp': 25.56, 'critical_chi2': 3.8414588206941285, 'n_total': 284, 'actual_power': 0.9990183411403959}` |
| g18 | yes | `{'n_total': '632', 'ncp': '56.8800000', 'critical_chi2': '124.3421', 'actual_power': '0.9501569'}` | `{'ncp': 56.879999999999995, 'critical_chi2': 124.34211340400408, 'n_total': 632, 'actual_power': 0.950156859386762}` |
| g19 | yes | `{'error_text': 'Effect size w must be greater 1e-06.'}` | `{'error': 'w out of range: 0.0', 'code': 'OUT_OF_RANGE', 'field': 'w'}` |
| g20 | yes | `{'error_text': 'Degrees of Freedom must be greater or equal one.'}` | `{'error': 'df out of range: 0', 'code': 'OUT_OF_RANGE', 'field': 'df'}` |
| g21 | yes | `{'ncp': '9.0000000', 'critical_chi2': '11.0704977', 'power': '0.6235846'}` | `{'ncp': 9.0, 'critical_chi2': 11.070497693516355, 'power': 0.6235846116825697}` |
| g22 | yes | `{'ncp': '4.8000000', 'critical_chi2': '3.8414588', 'power': '0.5913305'}` | `{'ncp': 4.800000000000001, 'critical_chi2': 3.8414588206941285, 'power': 0.5913305114419389}` |
| g23 | yes | `{'ncp': '18.0000000', 'critical_chi2': '5.9914645', 'power': '0.9744634'}` | `{'ncp': 18.0, 'critical_chi2': 5.991464547107983, 'power': 0.9744634260889933}` |
| g24 | yes | `{'ncp': '0.1800000', 'critical_chi2': '3.8414588', 'power': '0.0708635'}` | `{'ncp': 0.18, 'critical_chi2': 3.8414588206941285, 'power': 0.07086349410120676}` |
| g25 | **NO** | `{'ncp': '0.0900000', 'critical_chi2': '3.8414588', 'power': '0.0603726'}` | `{'error': 'n_total out of range: 1', 'code': 'OUT_OF_RANGE', 'field': 'n_total'}` |
| g26 | yes | `{'ncp': '0.0250000', 'critical_chi2': '3.8414588', 'power': '0.0528687'}` | `{'ncp': 0.025000000000000005, 'critical_chi2': 3.8414588206941285, 'power': 0.05286873312886927}` |
| g27 | yes | `{'ncp': '9.0000000', 'critical_chi2': '7.6804954', 'power': '0.8252545', 'alpha': '0.1747455', 'beta': '0.1747455'}` | `{'ncp': 9.0, 'critical_chi2': 7.68049543007753, 'alpha': 0.17474549408567394, 'beta': 0.17474549408567386, 'power': 0.8252545059143261}` |
| g28 | yes | `{'ncp': '9.0000000', 'critical_chi2': '9.9516505', 'power': '0.6935326', 'alpha': '0.0766169', 'beta': '0.3064674'}` | `{'ncp': 9.0, 'critical_chi2': 9.951650481139577, 'alpha': 0.07661685727526417, 'beta': 0.3064674291010563, 'power': 0.6935325708989437}` |
| g29 | yes | `{'ncp': '9.0000000', 'critical_chi2': '4.6618452', 'alpha': '0.4585253'}` | `{'ncp': 9.0, 'critical_chi2': 4.66184517941301, 'alpha': 0.45852529298204936}` |
| g30 | yes | `{'ncp': '19.7801344', 'critical_chi2': '11.0704977', 'w': '0.4447486'}` | `{'ncp': 19.7801343739068, 'critical_chi2': 11.070497693516355, 'w': 0.44474862983382873}` |
| g31 | yes | `{'ncp': '7.8488605', 'critical_chi2': '3.8414588', 'w': '0.3962035'}` | `{'ncp': 7.848860509326202, 'critical_chi2': 3.8414588206941285, 'w': 0.39620349592920556}` |
| g32 | yes | `{'ncp': '1e-10', 'critical_chi2': '3.8414588', 'power': '0.0500000'}` | `{'ncp': 1e-10, 'critical_chi2': 3.8414588206941285, 'power': 0.050000000011454944}` |
| g33 | yes | `{'ncp': '1.21e-10', 'critical_chi2': '3.8414588', 'power': '0.0500000'}` | `{'ncp': 1.2100000000000002e-10, 'critical_chi2': 3.8414588206941285, 'power': 0.0500000000138605}` |
| g34 | yes | `{'n_total': '1', 'ncp': '0.2500000', 'critical_chi2': '3.8414588', 'actual_power': '0.0790975'}` | `{'ncp': 0.25, 'critical_chi2': 3.8414588206941285, 'n_total': 1, 'actual_power': 0.07909753416059635}` |
| g35 | yes | `{'n_total': '7.8489e+12', 'ncp': '7.8488605', 'critical_chi2': '3.8414588', 'actual_power': '0.8000000'}` | `{'ncp': 7.848860509326999, 'critical_chi2': 3.8414588206941285, 'n_total': 7848860509327, 'actual_power': 0.8000000000000398}` |
| g36 | yes | `{'error_text': 'Effect size w must be greater 1e-06.'}` | `{'error': 'Effect size w must be at least 1e-06', 'code': 'OUT_OF_RANGE', 'field': 'w'}` |
| g37 | yes | `{'ncp': '2.5e-11', 'critical_chi2': '3.8414588', 'power': '0.0500000'}` | `{'ncp': 2.5e-11, 'critical_chi2': 3.8414588206941285, 'power': 0.05000000000286367}` |
| g38 | **NO** | `{'ncp': '0', 'critical_chi2': '3.8414588', 'power': '0.0500000'}` | `{'error': 'w out of range: 0.0', 'code': 'OUT_OF_RANGE', 'field': 'w'}` |
| g39 | yes | `{'error_text': 'Alpha is outside the admissible range (1e-07, 1).'}` | `{'error': 'alpha is outside the admissible range (1e-07, 0.9999999)', 'code': 'OUT_OF_RANGE', 'field': 'alpha'}` |
| g40 | yes | `{'ncp': '9.0000000', 'critical_chi2': '28.3739874', 'power': '0.009989983'}` | `{'ncp': 9.0, 'critical_chi2': 28.373987361779154, 'power': 0.009989982847600994}` |
| g41 | yes | `{'error_text': 'Power is outside the admissible range (1e-07, 1).'}` | `{'error': 'power is outside the admissible range (1e-07, 0.9999999)', 'code': 'OUT_OF_RANGE', 'field': 'power'}` |
| g42 | yes | `{'error_text': 'β/α ratio is outside the admissible range (0.01, 100)'}` | `{'error': 'beta/alpha ratio is outside the admissible range (0.01, 100)', 'code': 'OUT_OF_RANGE', 'field': 'beta_alpha_ratio'}` |
| g43 | yes | `{'ncp': '9.0000000', 'critical_chi2': '16.0674195', 'power': '0.3345799', 'alpha': '0.006654201', 'beta': '0.6654201'}` | `{'ncp': 9.0, 'critical_chi2': 16.06741954078189, 'alpha': 0.006654201060141824, 'beta': 0.6654201060141834, 'power': 0.33457989398581656}` |
| g44 | yes | `{'error_text': 'Degrees of Freedom must be greater or equal one.'}` | `{'error': 'df out of range: 0', 'code': 'OUT_OF_RANGE', 'field': 'df'}` |

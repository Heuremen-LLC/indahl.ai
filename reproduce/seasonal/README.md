# SEASONAL reproduce kit

Heuremen LLC · https://indahl.ai/seasonal · https://indahl.ai/reproduce

This kit recomputes the SEASONAL headline number and its outcome label with the desk's own code, from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later with numpy (PyPI). It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `bc5c500339489235e7034dd1ab3df2971672bbb776d8c74808320075ada0d87f`.

## What it reproduces

The headline as the live feed https://indahl.ai/seasonal/live.json served it at the feed stamp 2026-11-10T16:32:50Z, read by us at 2026-11-10T23:45:55Z. The feed bytes had sha256 `3252ba09e3390d5b2d9c8c1311efb4dcf1f730579fbf1c97926583d6f8a03653`.

- number: 60%
- value: 0.6011
- interval: 0.5488 to 0.6422
- outcome: ABOVE

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the SEASONAL data pack lists them. Credit each source when you use its values.

- NOAA Climate Prediction Center 3-month outlook verification files, https://www.cpc.ncep.noaa.gov/products/predictions/long_range/tools/briefing/seas_veri.grid.php. NOAA/NWS, public domain, https://www.weather.gov/disclaimer.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/raw/cpc_verif_grid/90day_Pverif_about.txt | 698 | `a7f72da2d2955c6ccef0e36dd863bfc0b1e73e6f5228c87400a1bcf132788905` |
| data/raw/cpc_verif_grid/90day_Tverif_about.txt | 690 | `659a3c6b4ea8adbae0c48665a613187d39fadc1f73f442bea6b667f0cd606836` |
| data/raw/cpc_verif_grid/90day_obs_about.txt | 500 | `88fd12d31a28e0d75841dd28212be9ec80e39c525b7ac7acf03d7f396ea21707` |
| data/raw/cpc_verif_grid/last_fetch | 20 | `2f1438e74474a62493585d040f7d308073b8149ade54a63b59053c8a11c153cd` |
| data/raw/cpc_verif_grid/prec01.heidke.txt | 11,438 | `800f33f09872fd4ce44dba240a212ee44547e106ec60e2fd2060b9c2d88ae292` |
| data/raw/cpc_verif_grid/prec01_forecast.bi | 1,047,888 | `e0d63fd7e4d88e75409f6b2be9e006d204da3c4bf4a970cd842c3adffdaaffc9` |
| data/raw/cpc_verif_grid/prec01_forecast_above.bi | 1,047,888 | `ed343013e0faf77f203da9053b291e0a10bc525d8d659982392ed6dac82cbcb8` |
| data/raw/cpc_verif_grid/prec01_forecast_below.bi | 1,047,888 | `abf0d1c80a5f52edf4e2bdcf49285897c2a49682facf71ef89166cb5dcae339a` |
| data/raw/cpc_verif_grid/prec_seas_verif.bi | 1,039,680 | `0eade481bba1d20db869222ca3f027c5910c1fa227a9edfe7ab8321c1d556e34` |
| data/raw/cpc_verif_grid/temp01.heidke.txt | 11,438 | `e8f26b4326b66880dff6b16af5849327253e3c2c7e6b8ad2444dec9e4f49421d` |
| data/raw/cpc_verif_grid/temp01_forecast.bi | 1,047,888 | `7a3937f60df5ded28c4a6d72f79af062447375abe22ad990ea8be292bf5ff4e8` |
| data/raw/cpc_verif_grid/temp01_forecast_above.bi | 1,047,888 | `112f29021aba4cb796de3593d39533661221d37ad5a080acc65d739f15a96906` |
| data/raw/cpc_verif_grid/temp01_forecast_below.bi | 1,047,888 | `59fd36d799fcf540da2f3c655287b6951e76a40fed98407da77aff91bee0bda4` |
| data/raw/cpc_verif_grid/temp_seas_verif.bi | 1,039,680 | `5e2ad34f805e7f7bdb2cbd93cfeebbed633b71344cfafe4427d01e10b4902733` |
| PLAN.md | 8,162 | `3a5e5ab678043c9f0c1cdd4389caa214f6699adae431af116ac8195aa763ad67` |
| data/plan_seal.json | 241 | `3c3eb023764a1c12c9daebdc2ad9b4573d13affd382f4069ac8eb70c4632c286` |

## Code

The desk's own scripts, byte for byte, under code/. They run in this order: code/seasonal_tick.py --offline. The same files are in the public repository under code/seasonal/.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

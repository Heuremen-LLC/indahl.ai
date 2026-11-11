# TORNADO reproduce kit

Heuremen LLC · https://indahl.ai/tornado · https://indahl.ai/reproduce

This kit recomputes the TORNADO headline number and its outcome label with the desk's own code, from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later with numpy and matplotlib (PyPI). It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `5ff5d0988b98d09801df2459fa0deb6eb6639eaa2ad0ff222460b5408c325930`.

## What it reproduces

The headline as the live feed https://indahl.ai/tornado/live.json served it at the feed stamp 2026-11-10T19:51:19Z, read by us at 2026-11-11T00:12:56Z. The feed bytes had sha256 `053f96211cbe941f2cf415d591da7fa0521581e3a55c653072509cdcfeb3faf6`.

- number: 17.6%
- value: 0.17648
- interval: 0.16246 to 0.19038
- outcome: ABOVE

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. Its inputs are about 550 MB of SPC outlook archives, storm reports, warnings and boundary files, more than a public kit carries. Every source is public domain and listed below, and each file is named with its sha256, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- SPC Day 1 Convective Outlooks, one zip per year, from the Iowa Environmental Mesonet archive, https://mesonet.agron.iastate.edu/request/gis/outlooks.phtml (data/raw/outlooks/day1_YYYY.zip).
- The SPC tornado database 1950 to 2025, https://www.spc.noaa.gov/wcm/ (data/raw/db), and SPC preliminary storm reports (data/raw/prelim).
- NWS storm-based tornado warnings from the Iowa Environmental Mesonet archive, https://mesonet.agron.iastate.edu/vtec/ (data/raw/warnings).
- US Census cartographic state boundaries, cb_2024_us_state_20m.zip, https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html (data/raw/boundaries).

## Sources and their terms

As the TORNADO data pack lists them. Credit each source when you use its values.

- NOAA SPC Day 1 Convective Outlooks (Iowa Environmental Mesonet archive), https://mesonet.agron.iastate.edu/request/gis/outlooks.phtml. U.S. government work, public domain (17 U.S.C. 105), IEM materials are in the public domain.
- SPC tornado database and preliminary storm reports, https://www.spc.noaa.gov/wcm/. U.S. government work, public domain (17 U.S.C. 105).
- NWS storm-based tornado warnings (Iowa Environmental Mesonet archive), https://mesonet.agron.iastate.edu/vtec/. U.S. government work, public domain (17 U.S.C. 105), IEM materials are in the public domain.
- US Census cartographic boundary files, https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html. U.S. government work, public domain (17 U.S.C. 105).

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/tornado_live.json | 29,041 | `053f96211cbe941f2cf415d591da7fa0521581e3a55c653072509cdcfeb3faf6` |
| data/raw/boundaries/cb_2024_us_state_20m.zip | 187,671 | `7bc773d83c01b6df69b8aada9c2b5983d97f22f4551947cc5c00b87c663223ef` |
| data/raw/db/1950-2025_actual_tornadoes.csv | 9,023,445 | `2b2679ead1920ab96eaa390baeb41aeeaeef49d067f613dfcc5e233403b82d76` |
| data/raw/db/SPC_severe_database_description.pdf | 435,348 | `426bd3abc0aa12ff3a7f63f8fdd326d71448119b188f3da8f95b39578fa9779a` |
| data/raw/outlooks/day1_2003.zip | 37,411,666 | `d5f5b9e2b68783473bf88f208399f747f5e231ff4493ba6d3058913293016b28` |
| data/raw/outlooks/day1_2004.zip | 36,525,458 | `5a7bebc92ccbc31b55d0ec215ee0606f79927263f90171fb690451f97f4138a2` |
| data/raw/outlooks/day1_2005.zip | 39,716,232 | `651b9ee237fc03c8c19396eaa4bdbcfa8b59601b8ff0547fecd96f3ace94a9bf` |
| data/raw/outlooks/day1_2006.zip | 38,264,810 | `8507d528c5de2eadda5ddfda465f79e0292b34df100a2df13c41d3f322f4d6be` |
| data/raw/outlooks/day1_2007.zip | 36,704,753 | `9ed607f968a4c459970fe489687155ed661f0c54c61932372015da0839c6b4d6` |
| data/raw/outlooks/day1_2008.zip | 37,795,385 | `76d506f72a9a16d8c2c9f7423e8fbd454e37a64c1124e3cf8741f4029946aed8` |
| data/raw/outlooks/day1_2009.zip | 31,813,955 | `5be6dfcc5bf2406d6b995d2cd40fbee2f8ec64996fe5712ddc9c0a6d6d93e26a` |
| data/raw/outlooks/day1_2010.zip | 27,804,079 | `5807932aba7ba0f3dfe7b1b17980c0f38c776a3e16c8ad3bfde9d22c8c196844` |
| data/raw/outlooks/day1_2011.zip | 27,413,336 | `710fb0b287f539d88e9b22dd31cd449f2c8843e3c87aae46779ac219ca6c1ea5` |
| data/raw/outlooks/day1_2012.zip | 32,043,087 | `64fab4d1205a6e578152adc971876e913f634eecbf89ae8531935e77a531748e` |
| data/raw/outlooks/day1_2013.zip | 26,426,132 | `8625afbb60b6dfd4cc3b0482ac25a32e6a6807f6d1da3dcdfb5b15ee7fd94dd5` |
| data/raw/outlooks/day1_2014.zip | 26,220,594 | `7f1973008c87aa6636e471e40a60982ead87f202fc92a4a865435fdf73330bf3` |
| data/raw/outlooks/day1_2015.zip | 31,087,525 | `a3b4d6fe4ce2df2492140081c41870e000eac03e30a8e49c3fd2bc243eabefcb` |
| data/raw/outlooks/day1_2016.zip | 29,464,254 | `e2dba48c2d56688c903213e2596cdbd6c46bb21c036f8b5004bb5ef8de7dbf43` |
| data/raw/outlooks/day1_2017.zip | 28,376,666 | `bf2c2b8237634841e7428306a9716d4c81e65a257e209c1262e1fe100be8f56a` |
| data/raw/outlooks/day1_2018.zip | 29,721,541 | `13c14cf5e7e4b6239caa841260d58acdb4822c26b40289d313ccd4eb2b432e0f` |
| data/raw/outlooks/day1_2019.zip | 6,105,312 | `ac8f4e566e2a17d4bd887b6ee5c9a373ae87e693a2ba7e7f1b6b0d082167d24b` |
| data/raw/outlooks/day1_2020.zip | 1,466,166 | `b26c6f4a0dc69f112209af907cde902ef79a5eb5dc551c28e28c5d4315ad61fd` |
| data/raw/outlooks/day1_2021.zip | 1,397,056 | `b4f004dcd9c17d1a5cd20a6289f1d0a6ee81c8676326fb48f7fc417a49ba7b6e` |
| data/raw/outlooks/day1_2022.zip | 1,411,807 | `f80e6419afb4ac67931de3fd4e9e9c4bcf704a61231ff37e1e1c46c264a70b40` |
| data/raw/outlooks/day1_2023.zip | 1,514,285 | `e9f4cceb1df64d62ccaa1715fab68402a2dca557f9677008c62a4f770b10849d` |
| data/raw/outlooks/day1_2024.zip | 1,486,215 | `d88b049695a046e354a67d272f6d7ca853e349709c71ee3ffa43341eecfb4089` |
| data/raw/outlooks/day1_2025.zip | 1,426,738 | `dd4da36a8f8ae436fdb3e7129d2e8005936208f8876f4c00eb236fa925eb3a6d` |
| data/raw/outlooks/day1_2026.zip | 1,485,652 | `472ed8494e21eca59a197d6a95a318c489c0bf0c2083faae78e95f9df3631a80` |
| data/raw/prelim/20260101.csv | 276 | `03beab4df83d5eb4a36dd4f4f5af8cb86e8972f15d977dca317cd58e20ba2da2` |
| data/raw/prelim/20260102.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260103.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260104.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260105.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260106.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260107.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260108.csv | 618 | `3584aa6c2f4868b8f6ec2cb14d5f51979f64fb19262907c1fb16669efc87d7be` |
| data/raw/prelim/20260109.csv | 2,016 | `88ae63ec21e47632aa5c598444f6f4cba0782eaae311fa18a60641720798a460` |
| data/raw/prelim/20260110.csv | 456 | `c6446606cedeaf946e518187fdc81d673e05f20be34d29b1a3995fd80dd1d935` |
| data/raw/prelim/20260111.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260112.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260113.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260114.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260115.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260116.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260117.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260118.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260119.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260120.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260121.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260122.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260123.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260124.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260125.csv | 858 | `ca5b18f56217a438556b506d994048969144d201cf9c7de25f5f0ed8167ce882` |
| data/raw/prelim/20260126.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260127.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260128.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260129.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260130.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260131.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260201.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260202.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260203.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260204.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260205.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260206.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260207.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260208.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260209.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260210.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260211.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260212.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260213.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260214.csv | 7,459 | `5697fb9ceb94e408b582edd7cffbfea098e656a8c20ec9392fbad6cad88e9ecb` |
| data/raw/prelim/20260215.csv | 249 | `581a9894aa74f16f7564a57042addaea5f51107b2464063f5e98dfaf766d4aca` |
| data/raw/prelim/20260216.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260217.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260218.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260219.csv | 2,760 | `f709bcb5d8960f3887fa43ceb7d318f0875bdfb5153222d16def126b3bc1125f` |
| data/raw/prelim/20260220.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260221.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260222.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260223.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260224.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260225.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260226.csv | 240 | `3f0479151a4cd9ad7d15ebceb2c4fcdc77b2f6e64319ee92a9a12c62837c5cbc` |
| data/raw/prelim/20260227.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260228.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260301.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260302.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260303.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260304.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260305.csv | 771 | `3cb3b647094e96ede20f2b1b6fbd2311cac4f53ae96e9c904eab5888a52cfa89` |
| data/raw/prelim/20260306.csv | 4,465 | `74cd5a6cd485b03f379f7d86652ff2cd82bb6fdbc795a93fc37a423d1d521700` |
| data/raw/prelim/20260307.csv | 716 | `de3043a0dbf80bd620f1976723631645034379abcde02febc723dfe865dc6ace` |
| data/raw/prelim/20260308.csv | 199 | `ce02ac2b8390df80fb48c8700e2946d18b8ed41db33d3cefcfae9c6bab8e6ad6` |
| data/raw/prelim/20260309.csv | 236 | `86a5ab0462cabb979b2276b46c9953550378a7690913021d1fce802b848988fa` |
| data/raw/prelim/20260310.csv | 6,469 | `6796f579d10cfe795dcdbcde134f1f5c6109156b2f49912f11f567b7e4b198e2` |
| data/raw/prelim/20260311.csv | 10,797 | `1a6d515d950234754ddc73048696523da55888250bb586f16d9c363aa55963ae` |
| data/raw/prelim/20260312.csv | 2,350 | `7a92c405a936a94c3d1e11888801e1cfc2807231bf475518d22bf74fc4647cc2` |
| data/raw/prelim/20260313.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260314.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260315.csv | 12,410 | `2b21343a448ee5bb5daebab978ba118de5b858234610916e7d40fab3ca55a0c9` |
| data/raw/prelim/20260316.csv | 951 | `412ac0709d7915995310e922320b6b0552a869ff9802a391e8c35c58e618954d` |
| data/raw/prelim/20260317.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260318.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260319.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260320.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260321.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260322.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260323.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260324.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260325.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260326.csv | 1,165 | `8b0a3378bfc24a2b21566302f36cc165d5277413ffe6befe7f2c42a6a661066b` |
| data/raw/prelim/20260327.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260328.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260329.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260330.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260331.csv | 885 | `18ce07b28c78e7ca7407d7180c1ace720ff24bbb4be8a941d1039fca4c0c455c` |
| data/raw/prelim/20260401.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260402.csv | 3,215 | `f8ee3f4b77df04883ca7b3115bfdf999279fc58bc8a5b8bd2015126d2b260c0a` |
| data/raw/prelim/20260403.csv | 936 | `905b3460613b2654653c27e11536e97e7d37b70ac3f301e89be785b1248ead63` |
| data/raw/prelim/20260404.csv | 916 | `5ed7b5edfd97c5ce85f0e369100bdee0bfeae6cf1b87c363cf25406a158165c4` |
| data/raw/prelim/20260405.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260406.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260407.csv | 179 | `50a36f57d87789afc354e8296c1834fd414936981d5ba728248a1187b8bd34c4` |
| data/raw/prelim/20260408.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260409.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260410.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260411.csv | 615 | `5a161ec8948a1fdbaa493a898ebf8c1a12096c1cc785e21aa4df4e57aaa7ae08` |
| data/raw/prelim/20260412.csv | 462 | `ee205b2c424680f63fdebe614fb8304900bda3d9a621470fd2a86ea8ab80a45b` |
| data/raw/prelim/20260413.csv | 3,123 | `b0e7bce366ab3aaaa5c7edc1e24a2b150d9f9dcd92ab67357f8e9ebfd100e212` |
| data/raw/prelim/20260414.csv | 6,028 | `ba36a2fb1d1456ca5aa0bcbaef424de64039059f5a3f3efd95a6200259d04d88` |
| data/raw/prelim/20260415.csv | 1,225 | `3c7817faab6731636232db26df4ab55b74c61a0e0d2d59618f98d44e5e0e2903` |
| data/raw/prelim/20260416.csv | 278 | `637f17361c71bcaebab8b71a2fd8a6c8ab5fcb38ab35ea3d66aba2fd84c85ae6` |
| data/raw/prelim/20260417.csv | 20,275 | `ac740e140107c5910c5a1768161e2e6a29e27fa70dedd30ef19ea3d6b49a1363` |
| data/raw/prelim/20260418.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260419.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260420.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260421.csv | 1,104 | `eb8f8e7fb249c41f3317b51acdd39834e2c4bdc7b291e35f6c054b2a384459e4` |
| data/raw/prelim/20260422.csv | 168 | `1db6d99ed75f5e521d644e18f593f940eaa25f09901a0ad7e39e7c7d9d9f072a` |
| data/raw/prelim/20260423.csv | 2,913 | `64fe440b51155c489cc1954a829c5b3754ff92c883d8f7bd9542282e37b03d6b` |
| data/raw/prelim/20260424.csv | 2,387 | `eee571763ba0dd44fa9d8804bbf3e027e448333f5c7b968fbaaea677ab3a6fbc` |
| data/raw/prelim/20260425.csv | 1,740 | `1e0c61459c299704ce4487245f89b0b106972904c83327a7beebebc449c3f5f5` |
| data/raw/prelim/20260426.csv | 3,169 | `b9fb4a22194117b641f2b3cf879331cf81b4cf48f031f82289cc51ff088c025b` |
| data/raw/prelim/20260427.csv | 5,205 | `e01cbc07c10bc5a24a004074d9ba2364d478e9dff002a9a292dd29f0ebc138a9` |
| data/raw/prelim/20260428.csv | 2,809 | `c1e9ce17aed9b9fece885f4a735818550d94d01b9715e5e92abed2495ac28f90` |
| data/raw/prelim/20260429.csv | 489 | `05b2bc9505525584733d4f3846adfd78a457df7fae444a4a11bcdbd87e3258af` |
| data/raw/prelim/20260430.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260501.csv | 148 | `0bd7cc5e0e4d49dfc581888d0294579a67efe0844f02bc216c1b5045ca349e51` |
| data/raw/prelim/20260502.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260503.csv | 272 | `94808176c334c8a632bd7ae5d36d074e4990385d336b5c574f986436935e67ae` |
| data/raw/prelim/20260504.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260505.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260506.csv | 4,522 | `e2ffd98411ee54aa71311308646fc29d63e162e1e1c2046b648f13a27ea06c6d` |
| data/raw/prelim/20260507.csv | 495 | `1156bb54d9850f10d154c1581eb913382d3e4a22dfe379e665084041109f8b36` |
| data/raw/prelim/20260508.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260509.csv | 303 | `49a85be3893916a1a742bae3ca850226d0328f20f26effaf6104f3fbd6a2c2ff` |
| data/raw/prelim/20260510.csv | 510 | `5c2bb9753fcc51ba6bdf75a8797882f57797be1cdef2d34f6399599e3e919671` |
| data/raw/prelim/20260511.csv | 225 | `a3cad4147fe63f6e32e73d377a2a5588ee7739b9ed126bab2f3e8a3aabb9e9f4` |
| data/raw/prelim/20260512.csv | 162 | `c402e33811a396f430082557685a422e8d14e21434dfa8714f40fd1b7e38f288` |
| data/raw/prelim/20260513.csv | 500 | `39b2437cd9eab6f1b805c7bde78b00a49b8ad313a71f7bc10d4885965b78950e` |
| data/raw/prelim/20260514.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260515.csv | 275 | `0c5ec35cb28bcdae196f2ae60763b3ad94707d1664968d122fa77d2f0916b04c` |
| data/raw/prelim/20260516.csv | 1,248 | `6253c76bf47ff78f09d83f5f71d823491c2bae135863080c702a26fcc21691a2` |
| data/raw/prelim/20260517.csv | 4,649 | `f3c516863ac4588dbdf9dec4f63a234ff2cd8707e243f65d42d4ed66399e06a9` |
| data/raw/prelim/20260518.csv | 4,337 | `258eeaa75a96310840cbcf717ede0effae0dde0a83a7c0c8ad94b36cbfa287da` |
| data/raw/prelim/20260519.csv | 286 | `88622debdf3c9feee562bc29946bcdc6400224255d90c816aa76c4b8b9657408` |
| data/raw/prelim/20260520.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260521.csv | 1,231 | `3d0a0dd1df9b920f40076ab48ba35aa8efbde8366d1f32747f4d73b3d6540d4c` |
| data/raw/prelim/20260522.csv | 3,176 | `ff4da6e8de35b9fcced4a402e02b9569131231867367b60974e3b805ba50548f` |
| data/raw/prelim/20260523.csv | 480 | `b56f2bde9666d3ad2a2cca6b848e333ead065db1a9120987a1ff736dadb3837f` |
| data/raw/prelim/20260524.csv | 282 | `f8bcf4a381860ab076101404604aa64fa7456f11941adb6570312cff98c0518e` |
| data/raw/prelim/20260525.csv | 836 | `6bd88073ae114fdfb1e7775ab3c2825be104232974d29245abbecbafd9ef9370` |
| data/raw/prelim/20260526.csv | 848 | `dd4dfe7d3b1dfbb2cd453d85646d9a52e25db27e095e409796512fc788ed4986` |
| data/raw/prelim/20260527.csv | 572 | `393380aacd3d89aae4ed6d3cb26888265672d4f40d084a4d9148b46216e9ce49` |
| data/raw/prelim/20260528.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260529.csv | 344 | `d6f938bba26fd2ff85703c77c71ea0a25c3d08b8195ff99fb883db76a6c24c2a` |
| data/raw/prelim/20260530.csv | 1,255 | `0365de0844626f52b204fb774ff778164bd6758e2e74736f4bd6b7150af49abf` |
| data/raw/prelim/20260531.csv | 429 | `6d006fcf2be1c1b1b0559c11cfb5a6549889b4639931059b9768e70018734e6f` |
| data/raw/prelim/20260601.csv | 232 | `29586c9e82032b53c9a72ea2158b9be8b239c4282cf2c78169f493fe5edac9a4` |
| data/raw/prelim/20260602.csv | 539 | `b4c8b86b70cfb04560f0a6ae92102b4cf60fc5bf29554725cf6aa8a49c791b1b` |
| data/raw/prelim/20260603.csv | 429 | `8285014de7ddc70a98ff3f8d26fc38483e89e9dfe7f82f1c6a9279f2ad615195` |
| data/raw/prelim/20260604.csv | 518 | `c8d627ee441f3366f008136e63a5367c0437a2239b01f705cff32132f6c750ce` |
| data/raw/prelim/20260605.csv | 235 | `0e7f3e84f418b81fb6fd96d93a170ff9270daa45ecbb6d9b248b5cf9b4dc0180` |
| data/raw/prelim/20260606.csv | 1,315 | `436f44d2303445d3bb41f6b9c5df1c9fdbd0fd1f9a00910e3a3116c9ffb56cb4` |
| data/raw/prelim/20260607.csv | 2,111 | `233b05de61965dbd85637fbc0e36730d79a85237fb725b4e4cffd64414e75026` |
| data/raw/prelim/20260608.csv | 383 | `bba74bdc27ce9e027ec70e622c50524f08b156d32ca43dfb2d513a3dc8008753` |
| data/raw/prelim/20260609.csv | 917 | `dbe30ec17f18d9ca780d42a4e3cad82c03547a8e11d01000d71d22c620a772e2` |
| data/raw/prelim/20260610.csv | 7,532 | `5ee687b6ed7a8df0fc42768f47d6ceda8a1158b59c7fd9e3f2de1532df5815ef` |
| data/raw/prelim/20260611.csv | 12,493 | `c61f375d5c7739071df34340c9a0019dda2766582336ecd07b2d375b70aed881` |
| data/raw/prelim/20260612.csv | 418 | `09bca6eb6f0cd0416dd38b1657aa5efe8565384c68c47d11dea59b33c7afc954` |
| data/raw/prelim/20260613.csv | 1,495 | `fba09f8685b7c5ffa810f0fafb1656c59161f2484fc60eb4349ef9f15543ce48` |
| data/raw/prelim/20260614.csv | 2,992 | `6699a61fb66c57c0f19a1071cc4c89a852a7cd5881d4f9d8a9ec28783b409b6f` |
| data/raw/prelim/20260615.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260616.csv | 929 | `a394c54b96313273ef693e0783b0a20e5e237bc30eb63b15b1bf6e9b4383bcb9` |
| data/raw/prelim/20260617.csv | 9,323 | `9b618c612fecf6226fe9025adcd898dc8c42956b36c9a10c0616da40682ef231` |
| data/raw/prelim/20260618.csv | 6,030 | `45a45db1566ca6e4def19beef2d23108b2ccd655eba53f9c35618cfa59329440` |
| data/raw/prelim/20260619.csv | 687 | `7824d9452a199cbf99f0ea50663a7e111e6fe2d325b26b57e7c0b1422f23ef4e` |
| data/raw/prelim/20260620.csv | 1,860 | `a93374b04b75bca205feb79fe97f12425cd149146535f366dd06ac76947c0a81` |
| data/raw/prelim/20260621.csv | 11,387 | `b46f264244d86e2b33fa95bf6a948f6e04d0ea54c922dffe3ff69346c6fcec5c` |
| data/raw/prelim/20260622.csv | 3,206 | `0f7f9cfb1ad3d2cec5c74c0f5d16eab3af668ba7ea2b13e664dda97cc3790656` |
| data/raw/prelim/20260623.csv | 595 | `8fbed44037f675c1a9d4166a9a4682ba0b4f66f0546d269ca8f99d2b4a8fecd5` |
| data/raw/prelim/20260624.csv | 792 | `1c2de67911e6ec7184948f7713116ca6913887c8af82b513f4bc5aaffa6367f8` |
| data/raw/prelim/20260625.csv | 840 | `4ec99f044fe5a82999636fd69699ec00e529853ac731e19c624a2eb77ccfc0ed` |
| data/raw/prelim/20260626.csv | 1,608 | `5779ca5fb09272390ae33b7a7cf3c3c750d142ca7ebefa834ff4673b4fc539f5` |
| data/raw/prelim/20260627.csv | 1,341 | `066d3fe5b5af7b4d6a209946d3e14834c6bc3a8adb8978f1c7271866c628a1c6` |
| data/raw/prelim/20260628.csv | 415 | `c0481dc258106cb79c14986659710e7b7bda46444a59ade162559102c516fee0` |
| data/raw/prelim/20260629.csv | 777 | `2ac67960cb85c5023ca30720ff3111bec3fba40518b044e4e0a704f97b781411` |
| data/raw/prelim/20260630.csv | 1,272 | `eb9dfb2045653bbd54e62a077645686ccc75904baf0ee04044ff4df588516e41` |
| data/raw/prelim/20260701.csv | 319 | `ff4b9879f8c93064965d7d468a0781117be724ebefb4a5907fcdb4b6e2ce2936` |
| data/raw/prelim/20260702.csv | 749 | `5790f1c9efd358ad4e1f6d4ae136b4dbe29d2ff079fe4d741e2b19f0bf85e1e3` |
| data/raw/prelim/20260703.csv | 326 | `6c4ceb7e0d508c247c468a4809d20c3d562491ee30f16636c63c38c6d865c193` |
| data/raw/prelim/20260704.csv | 516 | `7b6ac1bfab8df7ca13ab139aa6c108d59a5faf86c692b24391a03f7243a14913` |
| data/raw/prelim/20260705.csv | 325 | `f7b44736cbb69c34d4fb7a27d6413cc58b91af114d9a9846bced5405d81d645d` |
| data/raw/prelim/20260706.csv | 861 | `c0760b3eab2fdb59e5229ae876b53653d32788291ce5e74691c0d28ffc87316a` |
| data/raw/prelim/20260707.csv | 290 | `b83f6dd8462c993c5aab6796b0287a24260d5e6a9e659175b0773907b6cfb861` |
| data/raw/prelim/20260708.csv | 247 | `69cebc9fad3061b0e1848f6952b0ba14509116bdab292ac9333268ce0b45e27a` |
| data/raw/prelim/20260709.csv | 747 | `f00cbb997c72915c9003d83914ef082e9f1d84203efebd8bdb941f7335bb5e59` |
| data/raw/prelim/20260710.csv | 773 | `2aed7bebc620fc259554081e4fb6ae8a39f47dc783d7e8b20ca6f53638812328` |
| data/raw/prelim/20260711.csv | 239 | `9353df0179b11b5c6c5377b7a798ec614f3c55aa5e24bd6ffa2d9abe7af3173e` |
| data/raw/prelim/20260712.csv | 210 | `9610b30a9582b351f531319afb939aecfa308965bba762ca2119785853f5fc6c` |
| data/raw/prelim/20260713.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260714.csv | 275 | `2354ad4aa16954abee77b99c4949145de364efc0edc2368a18022ab3868ebf61` |
| data/raw/prelim/20260715.csv | 620 | `659ec17c9b6013b499869573b9d085097f68f81303eaf7a6174ef01f8e3d7b8a` |
| data/raw/prelim/20260716.csv | 472 | `93f1b347dd6062445b4c31de27c58aeb92dd5af69b7ae4012d1eeb13fad0e468` |
| data/raw/prelim/20260717.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260718.csv | 2,165 | `2f66871045fe5962ebd2bc20800f1928ec5ef3b497536d93be8b716d2fc10765` |
| data/raw/prelim/20260719.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260720.csv | 1,295 | `961f8cf4e5286bad4c17dd3192b5b6f31bcf969e952a3efcd1ad2fd0247d03d7` |
| data/raw/prelim/20260721.csv | 8,933 | `3194ed996cee5362096a3c58b28eea0223ee342d26b1a79d8556a791a0bb32c5` |
| data/raw/prelim/20260722.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260723.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260724.csv | 254 | `486b49767133dc68f39056673e854216efeb43dc40ec884593dcdd4c9c580141` |
| data/raw/prelim/20260725.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260726.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260727.csv | 2,285 | `474f58cc54066518951bb87edeaa44816d2d1eb2e221f4d2fabea066a517d49b` |
| data/raw/prelim/20260728.csv | 1,847 | `e02d29121a1939c91ff6b705ad3e9836e0d46d8b9f20aede68265d2e50a17feb` |
| data/raw/prelim/20260729.csv | 282 | `65c60a92ca324df09f8b42bf17dd880166b6c58142b25397734429558efd314f` |
| data/raw/prelim/20260730.csv | 129 | `1fe89063f0631d1c6088d5f44976a10fadb82c46de151b7e194c0fc80cdf862d` |
| data/raw/prelim/20260731.csv | 1,155 | `bde92446b15b09f3c50d85841b80312d9bfb32fed71d38c76075394af4a10116` |
| data/raw/prelim/20260801.csv | 2,260 | `799e9d2f389ee60938e2fdacb4c72b38a3e2e9db3a693ddf4614407367f12f00` |
| data/raw/prelim/20260802.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260803.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260804.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260805.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260806.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260807.csv | 828 | `402298adc658bd43cdb1b9627bf8ef6963c977647c1712ab4baec5637781fced` |
| data/raw/prelim/20260808.csv | 280 | `b6d5014e7bf3e780a67abc13ef344acec0a835f28acbb49150c72f2b17282900` |
| data/raw/prelim/20260809.csv | 1,407 | `4f983e9df18480798513449b43f5c8aca45c5b564af5c4d47bf6df81e9d97d15` |
| data/raw/prelim/20260810.csv | 946 | `84dd46ee1fa017586b55f410c141aa2974d7a79edc1282d2ef4558b9d6aeee27` |
| data/raw/prelim/20260811.csv | 4,692 | `697f05cd139bdd9781422d5de2afe1367d3d1b3e4ba71ec6dba105c2a626e4f4` |
| data/raw/prelim/20260812.csv | 1,631 | `5ebe3bf294fb1b56c6c9828f7ca915f341f83eaaedcde1d4ec9482c5a369733b` |
| data/raw/prelim/20260813.csv | 454 | `8262d8879d6c868b3ad470fb54eb28c4680fa8c2134cc77314533c395e66b167` |
| data/raw/prelim/20260814.csv | 278 | `a2b812428684ce142ad7e7d8778e5c6128874032ff102edd8dde1233edf9f293` |
| data/raw/prelim/20260815.csv | 477 | `579774c87043649e88d9d7d8e1de31d47bc67d6947b25624f4d1806bb279077e` |
| data/raw/prelim/20260816.csv | 485 | `d301e7d7fea4a0b494ab4947fe4c5087440ea926d875f2d6db8b6fee96dc6455` |
| data/raw/prelim/20260817.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260818.csv | 278 | `02460142b94f0cbc081090d8908820c1d26d2b93cb9883cf1439f1424ad41c87` |
| data/raw/prelim/20260819.csv | 1,321 | `3ce5513894b363ee8078770e6aa3854bbf1ba36c69486901741be60d0230d5a7` |
| data/raw/prelim/20260820.csv | 2,798 | `245b99b30e7b2082bfba95f6a473202d9e2686e6c939d8fc610332e748276068` |
| data/raw/prelim/20260821.csv | 629 | `4c446ece1a15cab318178a6a3cef5dcd9d0be70452e1f5c416322e54ccc1ffdf` |
| data/raw/prelim/20260822.csv | 638 | `32e95c23d56e123d42082a9f17d64acc5164593908d27325168b6c3fd1c631e7` |
| data/raw/prelim/20260823.csv | 236 | `89ea095afc4e0c9a920147afc3b49eccb8fee9886225b1abb3a3c16a1b6b79b7` |
| data/raw/prelim/20260824.csv | 276 | `440b43f650c89579eff9ef50218795f39a4836ff6a82da5ee038d238ac4c9546` |
| data/raw/prelim/20260825.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260826.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260827.csv | 772 | `43f1d30d904a8b933af23a76aedc8b29e2a7fd1ec31a639de9a8dae166e6e688` |
| data/raw/prelim/20260828.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260829.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260830.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260831.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260901.csv | 589 | `e7d99b1b7f80da17a89902175651e1eaba75d28664f7b7281f1e10f52a8a3845` |
| data/raw/prelim/20260902.csv | 2,285 | `35377a7cbdb162ab01a66306dc409e334eeff6ca5956a8a4e95c9222b5c01a74` |
| data/raw/prelim/20260903.csv | 433 | `d9e79e7f4889e12047fad797619df7be1f5054808dc8c4fc5d8fe1d8048b946e` |
| data/raw/prelim/20260904.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260905.csv | 499 | `88e287f2e26d056a18a231c618de6b66261c4dbbb2c3feff272c39e780b86f4e` |
| data/raw/prelim/20260906.csv | 397 | `b54f22a8fd72b97c61fe735441695590e44b003f2c54c06def294d1f5718e938` |
| data/raw/prelim/20260907.csv | 562 | `39a3dd191ff2a60ba5f7637a2016bcda5b23558cf855dc19a909d87eff5a1a40` |
| data/raw/prelim/20260908.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260909.csv | 496 | `0676d6f4e4c415bb951d867e8d016c7d947305b932602984f18ec29da5236e16` |
| data/raw/prelim/20260910.csv | 215 | `24115c471d7428df67c27d2aa1ff48d50e7d0bb104fde26e8bad946903b4636e` |
| data/raw/prelim/20260911.csv | 275 | `45d5e21e3e40fccf21ea961ec072334cccbe05f5266ef784a8df9fab7cc70dc8` |
| data/raw/prelim/20260912.csv | 483 | `a8f884ffcd24070470d3181fc6d49f19ba6f6794692290f7a6271ea009586ab3` |
| data/raw/prelim/20260913.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260914.csv | 329 | `f0c6a10e737c8e5df9642d40bda18fd002255f5229eac57b8efab36a80e8100a` |
| data/raw/prelim/20260915.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260916.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260917.csv | 180 | `a95150120c8c528a06d866358afc9ab07fb5f27c25032e05179cc5925070e344` |
| data/raw/prelim/20260918.csv | 685 | `1dfffecfeaac512c880776866a9e4ce707f99fedfee52cdbf187cc3c9a633820` |
| data/raw/prelim/20260919.csv | 282 | `f47ae2fe5cb57e62b47b4171de6122e482826949f3bcd1387dc89f9f376259a3` |
| data/raw/prelim/20260920.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260921.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260922.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260923.csv | 261 | `ec1c9c295d52e8830874bb3fabfffbd42bb5a3d5fc10b3651da7a6279cb87430` |
| data/raw/prelim/20260924.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260925.csv | 271 | `a25cd3c407f29b8b4ee394c2d2127f0765f4b8aebdbed1e5f783c31a6a9175c5` |
| data/raw/prelim/20260926.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260927.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20260928.csv | 278 | `7433a99e2ea621044a759de01c5e543e2ea986467bc11b90933451c376a1e148` |
| data/raw/prelim/20260929.csv | 800 | `54cc73b6c2d20703e5ebb16a9c879c4d4c1d5212ad59790a3e1284f5132a8b07` |
| data/raw/prelim/20260930.csv | 1,527 | `41a6303dea7b3f19035b0351762e6d0d7793b3c5d0ce77becbc4a95e2a09bba6` |
| data/raw/prelim/20261001.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261002.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261003.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261004.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261005.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261006.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261007.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261008.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261009.csv | 179 | `8de2280b33fdbe55ed3e0e1401b275f4a5fe10d55db47ba1ce14b4f698bd5d60` |
| data/raw/prelim/20261010.csv | 3,061 | `b8e74f95c133cfdfd87b9c75791a363ee834790d3ee078cee291a7e7f428af1e` |
| data/raw/prelim/20261011.csv | 3,075 | `b64b38dc45dfd3921357397950f4410771b25adb7b3b17e39c099a3ad3f4797f` |
| data/raw/prelim/20261012.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261013.csv | 325 | `60a0eb56d115ee7deaf497f461a69686d94fd5a8623c87d4028d122943234e42` |
| data/raw/prelim/20261014.csv | 669 | `329aa640e542c1521082261f142e15dfe8e9738c0c9aba308169c1456faddb16` |
| data/raw/prelim/20261015.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261016.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261017.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261018.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261019.csv | 269 | `0362d7677a74781a5b61537fc515127a1e34a2e0c22821d07418fe727bb59d16` |
| data/raw/prelim/20261020.csv | 272 | `7de5ed2df94f496c859794a0945b4d1ba701a407168196afa3fe09b18e19cdf1` |
| data/raw/prelim/20261021.csv | 742 | `eceb468daf7b9f936f9fa4eda23b0895f5df3fb0343a4b250fb56374f359d747` |
| data/raw/prelim/20261022.csv | 276 | `cb0b58b8dc6abee3ee410288ba1ca6ee45d54576c2802894c4c54914d7c9dc6d` |
| data/raw/prelim/20261023.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261024.csv | 408 | `d98caa1068269623a436afbafb9ca878cd3dc9a4c058e453359f2d858ecf2ee2` |
| data/raw/prelim/20261025.csv | 406 | `8b4847ad4aeb352200c17aa72d7bd2d8bf3e08cc5fb1dad4d71bfa0ad66cb79a` |
| data/raw/prelim/20261026.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261027.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261028.csv | 253 | `09f995c1a8cd0051542610fc260f9cb0cf0dd7dd4bedf3d1047379e1c5a841cc` |
| data/raw/prelim/20261029.csv | 1,166 | `8e5b35dda263371756e6a1588607f0afe4abaf7964bd3de2245b281160776cc6` |
| data/raw/prelim/20261030.csv | 271 | `0b0cf97747f8bfa8b6aae3dafe233d6a4f49e7a706f3297fc3f6834852451783` |
| data/raw/prelim/20261031.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261101.csv | 268 | `5f6854f852f6f8cc3c7dfb8973f88fe21356d6d9984a1d1f6a3596e69b924add` |
| data/raw/prelim/20261102.csv | 713 | `e06582bb74f3ccee74a57ac03a953f792230f3e20067ef8acec3e0e584dc9f6a` |
| data/raw/prelim/20261103.csv | 490 | `a0da55406faf2ba716791f8a55f27c0d91b9c940f2fe7c6d07765e72743c41f8` |
| data/raw/prelim/20261104.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261105.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261106.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261107.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/prelim/20261108.csv | 52 | `8a77826acbbde91de2c791a583e2ddcca48d13cdb012d57f232f1ea166e4621d` |
| data/raw/warnings/to_2024.geojson | 2,372,705 | `fdd0cbd90ef76f4a1bedf0bd6eb8c6f605c06befb7ee1b50083f10fe670711ed` |
| data/raw/warnings/to_fy2008.geojson | 3,128,170 | `139981cd6fd41b07f14737188fe293bab6a769c42913696bb944af27a050ac96` |
| data/raw/warnings/to_fy2009.geojson | 2,076,990 | `58a7de1b6d94c448e8f8743d6de6e0de4b223fce9cb30ef2350f676bef21542b` |
| data/raw/warnings/to_fy2010.geojson | 2,018,306 | `fd5c9ead9311a0744e9ccdd24c83e68aa53cee1605eb668442f395d87af71416` |
| data/raw/warnings/to_fy2011.geojson | 3,424,660 | `1809675e6a5c76ce1b58dd150075d18f06e3fe4c10baad121e974effa4861ee5` |
| data/raw/warnings/to_fy2012.geojson | 1,589,940 | `93ce00ebc129e0feea08bdc93fb82ab7e93c74e0f693e2068949132882d86c1e` |
| data/raw/warnings/to_fy2013.geojson | 1,208,506 | `30f0d556eb1ae552b0720591ef311851aaaf2a2e0c16be64e47c564d76302914` |
| data/raw/warnings/to_fy2014.geojson | 1,218,953 | `b8e7ac93ea99b8dd83b7919b69eed9b11f58cc3400946c5ce3c1b1721ca35313` |
| data/raw/warnings/to_fy2015.geojson | 1,346,470 | `c88815e53fcabf361b191e2f942ac427a5f63467f85a7dcffe1b098c49195466` |
| data/raw/warnings/to_fy2016.geojson | 1,512,350 | `de3dedbafc58f14cd4c8b0e72951a889de4f0ab0fb5841adad37b3ca575610ad` |
| data/raw/warnings/to_fy2017.geojson | 1,902,427 | `64c3a10b6d8530cbc06c33c274138d0a50011dc800936d3808282e10d8e07377` |
| data/raw/warnings/to_fy2018.geojson | 1,064,101 | `b611213cb056436398acb9f6d6db1d565d0ad3470ccbcc7b79b2ed5a2e3bb67b` |
| data/raw/warnings/to_fy2019.geojson | 2,145,803 | `6b942738b96ace358518532d8884db9101efd7ed4bfd70201c2ab3c7d88d441a` |
| data/raw/warnings/to_fy2020.geojson | 1,481,625 | `3d4e122fde50e5d2727c23e539561879163690c4d2982d5dde3d6cb6cc3cf6ea` |
| data/raw/warnings/to_fy2021.geojson | 1,351,189 | `2f3eda34063fcc85006f2747a26258a23eb9b6dad12dc888d124f936edd077e4` |
| data/raw/warnings/to_fy2022.geojson | 1,607,362 | `c0993f91b188e6d45b530465a99cd04a7fff06ac487fd6009e1cef0e9931692b` |
| data/raw/warnings/to_fy2023.geojson | 1,823,742 | `634ad23683e21a63a629ca01fbaad4ec62007810be85a4844788ac2b0b9e2fa9` |
| data/raw/warnings/to_fy2024.geojson | 2,204,178 | `da78dcd1427c86a54f3c4971c771bac68ad59e9c44971a0cc2fabe706bd988cf` |
| data/raw/warnings/to_fy2025.geojson | 2,216,822 | `e8374ca32bce18561e5e9c9006a9c337372c6c500ebff6d98ad0285bcd14fe90` |
| data/raw/warnings/to_fy2026.geojson | 1,838,824 | `a4848048c412c8a956748681680acaf9e1fd6dd8e7bbb1e36389339f47880740` |
| data/raw/warnings/to_fy2027.geojson | 79,626 | `1f2ee8450149518f39b7f0acfc853a8af8f649a31774a115451488c8e8421d52` |
| data/cache/pointcheck.json | 71,094 | `3cb9b911d701d60eba2e632275b426acf4f50866ac936d8fa9a21034f140b1b9` |
| PLAN.md | 15,369 | `40153979fc0608c821521dd0d7182e468d4c4a342205f92d120df2d6473ea565` |
| data/plan_seal.json | 241 | `de9e435d49de15344226074552eb46c67ecf6cbf17424b0c004b07d811be9550` |

## Code

code/clock_run.py runs the desk's own scripts in code/, byte for byte, and changes the clock only. It runs tornado_tick.py with --offline and the clock pinned to the time the published run read (the generated field of data/tornado_live.json), which the desk uses to tell a settled or passed row from an open one. The same files are in the public repository under code/tornado/. Scripts that run: code/clock_run.py tornado_tick.py data/tornado_live.json --offline.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

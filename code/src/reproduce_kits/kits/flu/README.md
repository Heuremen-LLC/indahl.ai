# FLU reproduce kit

Heuremen LLC · https://indahl.ai/flu · https://indahl.ai/reproduce

This kit recomputes the FLU headline number and its outcome label with the desk's own code, from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later with numpy (PyPI). It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `415e3325a57de347e6374fe695bdea772cfdaaeaa4a02ca704ac72e2428c9a8d`.

## What it reproduces

The headline as the live feed https://indahl.ai/flu/live.json served it at the feed stamp 2026-11-12T14:01:52Z, read by us at 2026-11-12T16:05:56Z. The feed bytes had sha256 `a556159250795df5b2ede392e82492b4289614489cfeb6e6524ca9f15478b1b2`.

- number: 16,416 of 18,544
- value: 0.8852
- interval: 0.8158 to 0.9454
- outcome: BELOW

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the FLU data pack lists them. Credit each source when you use its values.

- CDC FluSight Forecast Hub (FluSight-ensemble, FluSight-baseline, NHSN target data), https://github.com/cdcepi/FluSight-forecast-hub. Repository MIT licence, FluSight-ensemble CC BY 4.0 (credit the CDC FluSight team and UMass Amherst), NHSN data U.S. government work.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/flu_live.json | 156,202 | `1906c876146edf018ba2af9cf6eacf0ae3d0ba3cacc35dd801426f5c036e0d14` |
| data/raw/hub/model-output/FluSight-ensemble/2023-10-14-FluSight-ensemble.csv | 524,323 | `0495532d8fc3885fb64b62f541a35cc1aa851a6869f82480645a8c58831293bc` |
| data/raw/hub/model-output/FluSight-ensemble/2023-10-21-FluSight-ensemble.csv | 531,866 | `047c6086ce9ed1bb864c05caf640fb028afa8e22c3151210b43e5f664988e23a` |
| data/raw/hub/model-output/FluSight-ensemble/2023-10-28-FluSight-ensemble.csv | 524,028 | `9b6e7391ca116c160e0efa34a07cda890dfb5a2bce060f092dbf1f0f30f42071` |
| data/raw/hub/model-output/FluSight-ensemble/2023-11-04-FluSight-ensemble.csv | 533,097 | `162b23402ced53430cc8e5f571680116c2e1f2e293b76d526a01a8aaaf07ca5b` |
| data/raw/hub/model-output/FluSight-ensemble/2023-11-11-FluSight-ensemble.csv | 525,177 | `f3609fa223906f681ddffd6853c665b742ffc9bb04dc7de63a4de65fd38ff8f4` |
| data/raw/hub/model-output/FluSight-ensemble/2023-11-18-FluSight-ensemble.csv | 523,470 | `b334656ef393e5be77816b23707cb8648bb006be8921d0844b498c98c8830563` |
| data/raw/hub/model-output/FluSight-ensemble/2023-11-25-FluSight-ensemble.csv | 521,218 | `e6792783b4e6e1b16d1e85f19f0d41b5a4938326595c0245707ad505377425a9` |
| data/raw/hub/model-output/FluSight-ensemble/2023-12-02-FluSight-ensemble.csv | 524,082 | `2000f662432078c454819800a7b99ab1c195ea27214454c8c419b4d8fd851c3c` |
| data/raw/hub/model-output/FluSight-ensemble/2023-12-09-FluSight-ensemble.csv | 517,894 | `4383a58aa74bf4224097896bd5a9c983261b2862c4751f996f4ece7abbdc2ac5` |
| data/raw/hub/model-output/FluSight-ensemble/2023-12-16-FluSight-ensemble.csv | 522,581 | `818c7a84e68cfbb33821c6fef34532e42d85429f1e1ee4413d44ca6e4fa2035f` |
| data/raw/hub/model-output/FluSight-ensemble/2023-12-23-FluSight-ensemble.csv | 525,370 | `d3ec72d524011f186d2b7f898a29e50606dc7e610a6a33d15e1afff6706751fe` |
| data/raw/hub/model-output/FluSight-ensemble/2023-12-30-FluSight-ensemble.csv | 532,102 | `00f5e92c2a024f657f101bce5c8d1c14f5fefb998748a3c8b43f4e8ba7f25772` |
| data/raw/hub/model-output/FluSight-ensemble/2024-01-06-FluSight-ensemble.csv | 522,958 | `b45584863813245c9e41330a9ac8aa453335e89a8e5cd16145d29bcceeafdd68` |
| data/raw/hub/model-output/FluSight-ensemble/2024-01-13-FluSight-ensemble.csv | 530,517 | `8c4291e70c5b47dd1475136daa5ffdf9a833a3a9c567dd863ebc14bdcab9951a` |
| data/raw/hub/model-output/FluSight-ensemble/2024-01-20-FluSight-ensemble.csv | 524,342 | `6389a83d3aff69a8138b2220c10c7c21fd14d61daf895dd42bc53b53a4479a6b` |
| data/raw/hub/model-output/FluSight-ensemble/2024-01-27-FluSight-ensemble.csv | 529,998 | `a9c200a1395433deb24ec71ef2ae7210f9d7cbba5b3b166cf04303b7629f01c3` |
| data/raw/hub/model-output/FluSight-ensemble/2024-02-03-FluSight-ensemble.csv | 519,229 | `c276963e4f30094e9ddd71c811349161d4a7aa1b97a2b8cc4cd162cab09ccd10` |
| data/raw/hub/model-output/FluSight-ensemble/2024-02-10-FluSight-ensemble.csv | 532,036 | `b03fc33babde3f32ef15780fdbddb603d7156379d2cc6663e4d6ca275b08c8f5` |
| data/raw/hub/model-output/FluSight-ensemble/2024-02-17-FluSight-ensemble.csv | 519,604 | `ab2aba8cfaff6fdc76e8d8c5224e44f12d465f63e02b4200e8a8510420142417` |
| data/raw/hub/model-output/FluSight-ensemble/2024-02-24-FluSight-ensemble.csv | 525,554 | `fd19dd168b080e56d593e1e2cefefce893f4e5efe1ee1c1739b5d65dd6dcffe5` |
| data/raw/hub/model-output/FluSight-ensemble/2024-03-02-FluSight-ensemble.csv | 537,652 | `076d6e2876c2f4af916020a7bea7c5cf691b11420e4f3f06a7e35542512c87be` |
| data/raw/hub/model-output/FluSight-ensemble/2024-03-09-FluSight-ensemble.csv | 526,838 | `618a5502e6c38e97f016cca4889605289b3aabe7be8fefa3fa2cc83757f94f14` |
| data/raw/hub/model-output/FluSight-ensemble/2024-03-16-FluSight-ensemble.csv | 527,611 | `1f4fac2368357d70c17d8d9a8df18dfa4bfcd745d6934cdd8d9d44cfc9b55a7b` |
| data/raw/hub/model-output/FluSight-ensemble/2024-03-23-FluSight-ensemble.csv | 514,690 | `d569e10bae9221350ab9dbb215c254e676d3a2a9376b81c04ebd2dea237c1698` |
| data/raw/hub/model-output/FluSight-ensemble/2024-03-30-FluSight-ensemble.csv | 529,207 | `fdb9b4ec47e44bf7d5609eb6c6f8b1be94ab51c7589de126a555de329fe97207` |
| data/raw/hub/model-output/FluSight-ensemble/2024-04-06-FluSight-ensemble.csv | 523,289 | `91b49e7b92a27faecfcdc5ceea76cfb140e4394d39f3c6bec1519bdf9445c61f` |
| data/raw/hub/model-output/FluSight-ensemble/2024-04-13-FluSight-ensemble.csv | 505,669 | `80eef2e9467ec5163381ad8896b974e694cbd4b73611508841fb51982655111e` |
| data/raw/hub/model-output/FluSight-ensemble/2024-04-20-FluSight-ensemble.csv | 517,904 | `b05295fb232f9e8526c1fa70a5ba07bbeaf809e6cc9051baddf0df2df42a6e75` |
| data/raw/hub/model-output/FluSight-ensemble/2024-04-27-FluSight-ensemble.csv | 517,120 | `3730576ed02066ec7bd389972cb0d45e751ca1c3224ec0950cbf78de59299ade` |
| data/raw/hub/model-output/FluSight-ensemble/2024-05-04-FluSight-ensemble.csv | 516,774 | `ea5f0deebb7d16eb948f5d5acb9ca2358ffd0a3e1b8f1dba0b47117d441c1880` |
| data/raw/hub/model-output/FluSight-ensemble/2024-11-23-FluSight-ensemble.csv | 647,370 | `c465c4c4f73cbb47f0bd7c412e3950216dc8a68ca3c1e66c4e1fb672a6d9050a` |
| data/raw/hub/model-output/FluSight-ensemble/2024-11-30-FluSight-ensemble.csv | 648,016 | `cec0d545ab82b55a33c0ae57412b17e86ad513c291f8ed82967649277f498a99` |
| data/raw/hub/model-output/FluSight-ensemble/2024-12-07-FluSight-ensemble.csv | 651,959 | `a826062c33b865d9db39acac987140bae665d46a5f656cd7ea5807a08bb31ae7` |
| data/raw/hub/model-output/FluSight-ensemble/2024-12-14-FluSight-ensemble.csv | 578,777 | `8bd843fd80f396637abd7427b5fb362bd2611da105a61f919368194b85e62782` |
| data/raw/hub/model-output/FluSight-ensemble/2024-12-21-FluSight-ensemble.csv | 578,999 | `3b1fe87c177864b54c1bd4c299d63abf33a30f7bc798b4e466502befe9c5c98c` |
| data/raw/hub/model-output/FluSight-ensemble/2024-12-28-FluSight-ensemble.csv | 579,036 | `37f739dceebdeeba65d2fce2533f8f0d6312ace8b91990e374e2aabeb52f454d` |
| data/raw/hub/model-output/FluSight-ensemble/2025-01-04-FluSight-ensemble.csv | 578,838 | `49f23c3a385965d8a89d88ef5df991289547cc78ca8b2f4f770e1bcd746c1308` |
| data/raw/hub/model-output/FluSight-ensemble/2025-01-11-FluSight-ensemble.csv | 579,220 | `2fe5b14b22c0ed20a51fe69d94dbafadc4a44f6848592634841bd6b0f7574e6d` |
| data/raw/hub/model-output/FluSight-ensemble/2025-01-18-FluSight-ensemble.csv | 579,273 | `e5f43f74d8e8a996c2e38ed2c3410290c17fa64098231dc96bdcbca8134aba21` |
| data/raw/hub/model-output/FluSight-ensemble/2025-02-01-FluSight-ensemble.csv | 580,492 | `6c3b428efbdf33b11fa322ed7d2953acea8c77baf3312d4519d98a929723f5e4` |
| data/raw/hub/model-output/FluSight-ensemble/2025-02-08-FluSight-ensemble.csv | 579,023 | `0f0354c678f4d1e78bfe881528fe32f9da2e22367bab738f0c5ab8bea392487a` |
| data/raw/hub/model-output/FluSight-ensemble/2025-02-15-FluSight-ensemble.csv | 577,955 | `07d438fa2f6105b0f013367f5ce5947ade3d002275bc53added995f6dbe48aa5` |
| data/raw/hub/model-output/FluSight-ensemble/2025-02-22-FluSight-ensemble.csv | 575,922 | `0f317cb957a4cfb192420d53d59a6875f4414e354373f8781dbc1e9737047ade` |
| data/raw/hub/model-output/FluSight-ensemble/2025-03-01-FluSight-ensemble.csv | 574,775 | `627ce1611a7cee45ba88a6eea60528501f6da24892e5733b16ac70da358a7b96` |
| data/raw/hub/model-output/FluSight-ensemble/2025-03-08-FluSight-ensemble.csv | 574,077 | `5a1b40fa89e66f29639841004542a7f049c6e72b110c487845ae7e85b33aa772` |
| data/raw/hub/model-output/FluSight-ensemble/2025-03-15-FluSight-ensemble.csv | 578,359 | `ff14567dab273b0e144ebba04862d480c24860e56353801c116edafbe420adb6` |
| data/raw/hub/model-output/FluSight-ensemble/2025-03-22-FluSight-ensemble.csv | 577,117 | `9762aef907a36cdde57302e0cf4850872d0b8cd9d48102930ba221014c1498bf` |
| data/raw/hub/model-output/FluSight-ensemble/2025-03-29-FluSight-ensemble.csv | 574,936 | `890bd69e772c98de73e561474e0a2651b06fe948b698270301c2e12ae3888d31` |
| data/raw/hub/model-output/FluSight-ensemble/2025-04-05-FluSight-ensemble.csv | 564,699 | `c7c2decd346a55d1ac80723052d3c7624146c5f9f89592ac5247f2ac01aa17c0` |
| data/raw/hub/model-output/FluSight-ensemble/2025-04-12-FluSight-ensemble.csv | 563,788 | `a0a0f2b399c954d496ed3ccdc47ec7b3745d4b4bf070fef94332793726717b6a` |
| data/raw/hub/model-output/FluSight-ensemble/2025-04-19-FluSight-ensemble.csv | 560,265 | `9f3a441ce65d4876db7e679337a723b59af27b1eb2f77326b965bec6795b4aaa` |
| data/raw/hub/model-output/FluSight-ensemble/2025-04-26-FluSight-ensemble.csv | 559,180 | `2d8f8c752966eeb7d4c04d7d0e0853f52302e47044f18f3bbc786e266653abba` |
| data/raw/hub/model-output/FluSight-ensemble/2025-05-03-FluSight-ensemble.csv | 559,477 | `e407d9da602fe17afd64a2fae6977bf220f9ebd8dbae6bd13273db71422b4bce` |
| data/raw/hub/model-output/FluSight-ensemble/2025-05-10-FluSight-ensemble.csv | 558,024 | `12eac14f926880b54e807aca7b60515ade807a72358d3d9bc3fdd501ece70293` |
| data/raw/hub/model-output/FluSight-ensemble/2025-05-17-FluSight-ensemble.csv | 539,493 | `de768af3cee37ee49720616a045b238e6b93cde7f0248b4918597843ffe951bd` |
| data/raw/hub/model-output/FluSight-ensemble/2025-05-24-FluSight-ensemble.csv | 537,488 | `6353466a39a2c90cf5c3ed1ff6526d006ffd47dd30c33acf75206511964cf2f9` |
| data/raw/hub/model-output/FluSight-ensemble/2025-05-31-FluSight-ensemble.csv | 538,713 | `d8bd291cd55907e7e3dd56d01aa76b495105ac8975a18dfca6b60cedade1983d` |
| data/raw/hub/model-output/FluSight-ensemble/2025-11-22-FluSight-ensemble.csv | 1,079,439 | `2d19a10cdd85f831de5a260de0b3d7f148e27924b6d5281fffa759a1d6b798cb` |
| data/raw/hub/model-output/FluSight-ensemble/2025-11-29-FluSight-ensemble.csv | 1,072,231 | `3ffeb280862e493e013d233a0d547a63b215fb6646f7d3ee0b9ba46d1e221148` |
| data/raw/hub/model-output/FluSight-ensemble/2025-12-06-FluSight-ensemble.csv | 1,074,040 | `cd2e2d0e8ea216edc6ca10e3e908f527547f9cccddbc5cf47384ff7a6e5a82c6` |
| data/raw/hub/model-output/FluSight-ensemble/2025-12-13-FluSight-ensemble.csv | 1,070,826 | `5906b050dabdbf5398585e3bc1f8395211bc09d685e92be4d50ef640a4e0d874` |
| data/raw/hub/model-output/FluSight-ensemble/2025-12-20-FluSight-ensemble.csv | 1,073,044 | `efa7628032de99e259ce3b6aa694c2dc9b1164608f2456a3b02435e51ea0b1e2` |
| data/raw/hub/model-output/FluSight-ensemble/2025-12-27-FluSight-ensemble.csv | 1,073,369 | `d3e601092fd7b2d3eae3c7c80c00657513bfe1a4dbc84d0d585bb0bd17957ccb` |
| data/raw/hub/model-output/FluSight-ensemble/2026-01-03-FluSight-ensemble.csv | 1,071,826 | `57dff31d12c3ee5fec130a5ca776f07ff8867cf38d5d5130eb9850f9dc5cbbea` |
| data/raw/hub/model-output/FluSight-ensemble/2026-01-10-FluSight-ensemble.csv | 1,071,584 | `b751a094026c1c1aa5283a52e415087d30b18162cb0b452bc5cd9fb7beb5fb61` |
| data/raw/hub/model-output/FluSight-ensemble/2026-01-17-FluSight-ensemble.csv | 1,073,718 | `cd5c92969c026e98dfe970a4e9202c1cf8d1df19b41ad35021100243e7a4637f` |
| data/raw/hub/model-output/FluSight-ensemble/2026-01-24-FluSight-ensemble.csv | 1,071,033 | `abae020ef585cc757675a9f576bce84af6ded942845bc52425d274a28a7b0735` |
| data/raw/hub/model-output/FluSight-ensemble/2026-01-31-FluSight-ensemble.csv | 1,069,118 | `f610ef90c0e67be7adf2d26329143957f0eb6509db337fb3bf8d9b7ab4a2acd9` |
| data/raw/hub/model-output/FluSight-ensemble/2026-02-07-FluSight-ensemble.csv | 1,068,783 | `ca9eb0414601063d707009a7f49f414bf3c8570c23a3a92683b293cb38d1c9ed` |
| data/raw/hub/model-output/FluSight-ensemble/2026-02-14-FluSight-ensemble.csv | 1,070,758 | `10ce61e9e0151c828dbd92c0ea225157c367a433e7d4eb40f0d167c1c8b1ab00` |
| data/raw/hub/model-output/FluSight-ensemble/2026-02-21-FluSight-ensemble.csv | 1,070,008 | `d79352cb78e501f14e611af678f8eef6cffc391f55ca9c3b2493b229bffb80ac` |
| data/raw/hub/model-output/FluSight-ensemble/2026-02-28-FluSight-ensemble.csv | 1,069,345 | `dfc25ad8793c3f9aee7b3bacb44cda013281291057b847c4509e8da8a3f9e8bb` |
| data/raw/hub/model-output/FluSight-ensemble/2026-03-07-FluSight-ensemble.csv | 1,063,666 | `036da39368381a2486800b802c8366bc3e09cbdc0edfdfb073ad38f1f8b2645d` |
| data/raw/hub/model-output/FluSight-ensemble/2026-03-14-FluSight-ensemble.csv | 1,063,180 | `3e41303eaa87d62cfb56d50fad4b874351e446a37f4be32309a434fee726e3dc` |
| data/raw/hub/model-output/FluSight-ensemble/2026-03-21-FluSight-ensemble.csv | 1,060,171 | `f7d2fbf4bdc35a40553d64907143936e3fd0a954c085922edddc449b7a537b84` |
| data/raw/hub/model-output/FluSight-ensemble/2026-03-28-FluSight-ensemble.csv | 1,059,173 | `0689584e8261bff56c3c6741d83f48f2a87763014b5ac007e20e406ea4410abe` |
| data/raw/hub/model-output/FluSight-ensemble/2026-04-04-FluSight-ensemble.csv | 1,055,964 | `a1f6ff7614a3614ad2407c203ef79b8a130264faf9a88f79519380425bd9a0ec` |
| data/raw/hub/model-output/FluSight-ensemble/2026-04-11-FluSight-ensemble.csv | 1,049,432 | `c37ae23060c6c075c054e75bc01922cfb90b665ba72ae8e4e731f0f198da7ae0` |
| data/raw/hub/model-output/FluSight-ensemble/2026-04-18-FluSight-ensemble.csv | 1,044,810 | `6cf2cda4d4d33f00f19b78eed6f0fb379c956760d7ac9659a805f10385db6dc5` |
| data/raw/hub/model-output/FluSight-ensemble/2026-04-25-FluSight-ensemble.csv | 1,046,490 | `b7ffaaf10f5bc0ff2676a3b338becef15841aa06932c3497177234c88e3eda4d` |
| data/raw/hub/model-output/FluSight-ensemble/2026-05-02-FluSight-ensemble.csv | 1,043,385 | `b19eecdaed2c45bb266f076bec9db160e77b33d0dc86f7bfdd1324e4fad0b943` |
| data/raw/hub/model-output/FluSight-ensemble/2026-05-09-FluSight-ensemble.csv | 1,046,806 | `b9b893599f8f58eef933457790fac634e1bed23b027bcd9c7f7cf4cacc98b7fb` |
| data/raw/hub/model-output/FluSight-ensemble/2026-05-16-FluSight-ensemble.csv | 1,043,383 | `5c50a161f5906b0a0692432177e8929a0af60df949ec012cbb729e47f7610f27` |
| data/raw/hub/model-output/FluSight-ensemble/2026-05-23-FluSight-ensemble.csv | 1,038,724 | `8ae490af6c6d6b8f4dfc62b58bc0a08fdd5e4ae7c4980e4e2736461ba18fb9b3` |
| data/raw/hub/model-output/FluSight-ensemble/2026-05-30-FluSight-ensemble.csv | 1,050,062 | `da7f92cf11b1f05df55913dcb0107e3ff1affccd0df5bf132d7be42d2f1909c8` |
| data/raw/hub/model-output/FluSight-ensemble/2026-10-10-FluSight-ensemble.csv | 1,117,126 | `c0969ca9e20e898f3d428058b161cdf5e90fbf7f58cc0ae57e4f7a59bfa17ed2` |
| data/raw/hub/model-output/FluSight-ensemble/2026-10-17-FluSight-ensemble.csv | 1,114,958 | `1b85d431a8d563904ea4ecfc624becaf7607a4c8ccb2aa0d9d488efbbc6aea66` |
| data/raw/hub/model-output/FluSight-ensemble/2026-10-24-FluSight-ensemble.csv | 1,111,506 | `b3d59ed12221298edc91b2a383434bd04499e76060bc8f713ad9ab2abfe93326` |
| data/raw/hub/model-output/FluSight-ensemble/2026-10-31-FluSight-ensemble.csv | 1,114,126 | `5494a4935e3798c4a5656d78d92d2e4782a9692a560f7a8ecd23074cdfa4af3b` |
| data/raw/hub/model-output/FluSight-ensemble/2026-11-07-FluSight-ensemble.csv | 1,114,677 | `f22dba7ebcad2a0e697d4d0af14efabef1ba5da4ba0e1a0110f9bdb63659a03a` |
| data/raw/hub/target-data/time-series.csv | 95,069,683 | `2524463c6b02791b4276054986287e747c8a8f6c99dfe59cf6d23ed67812f98d` |
| data/raw/hub/target-data/target-hospital-admissions.csv | 616,178 | `c1a98bd361f75024bb2391f594af69a3f246bb104845b855624340df66bbb949` |
| data/raw/hub/auxiliary-data/locations.csv | 3,197 | `80aaa24750044a837e063812a1d0a22339c8b3a92513f71a23dac613eaaa29e0` |
| data/known_good_rows.json | 453 | `53ba7dd6abbd3ad748961363591cf8efb63ab2eeceb02c670204a73a948d0f00` |
| PLAN.md | 10,016 | `b68f3fa1fe96eb0a7ad870c01038153467a83fdf9a4ca0c327fb5b38ac0018c2` |
| data/plan_seal.json | 241 | `f9422093d9ea46e4bd013264c6562bab9b3d266567c087071724e904fa2db9f7` |

## Code

code/clock_run.py runs the desk's own scripts in code/, byte for byte, and changes the clock only. It runs flu_tick.py with --offline and the clock pinned to the time the published run read (the generated field of data/flu_live.json), which the desk uses to tell a settled or passed row from an open one. The same files are in the public repository under code/flu/. Scripts that run: code/clock_run.py flu_tick.py data/flu_live.json --offline.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

locations.csv comes from the FluSight Forecast Hub repository, under its MIT licence (https://github.com/cdcepi/FluSight-forecast-hub/blob/main/LICENSE). The hub baseline model files are left out. They feed only the interval score beside the headline, so a full run of this kit prints those cells empty while the headline cell is unchanged.

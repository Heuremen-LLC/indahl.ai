# AIRQ reproduce kit

Heuremen LLC · https://indahl.ai/airq · https://indahl.ai/reproduce

This kit recomputes the AIRQ headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `a105a4e665f0c2eef3ebd8bd394bae4a764c41aefc25cd5db23ad288ac8a3aed`.

## What it reproduces

The headline as the live feed https://indahl.ai/airq/live.json served it at the feed stamp 10 Nov 23:21 UTC, read by us at 2026-11-11T00:07:52Z. The feed bytes had sha256 `833b9f3f5fead4c7cda0650fd98e163ee727a3b05d7efac99ebc7f80fd300f22`.

- number: 93%
- value: 0.9281
- interval: 0.8726 to 0.9605
- outcome: ABOVE

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. PurpleAir terms allow its data and anything derived from it only for internal testing and bar passing it on, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- EPA Air Quality System hourly PM2.5 (parameter 88101), https://aqs.epa.gov/data/api/sampleData/byState for each state, 1 March to 30 June 2026, read month by month. data/w2026/aqs_NN.json keeps the daily means the read built from those rows.
- PurpleAir outdoor sensors within 200 metres of each monitor, https://api.purpleair.com/v1/sensors (data/w2026/pa_near.json), and each sensor's daily history, https://api.purpleair.com/v1/sensors/ID/history with average=1440 (data/w2026/pa_ID.json, the answer as served, with its time_stamp). A PurpleAir read needs a PurpleAir key.

## Sources and their terms

As the AIRQ data pack lists them. Credit each source when you use its values.

- EPA Air Quality System (AQS) API, https://aqs.epa.gov/aqsweb/documents/data_api.html. U.S. government work, public domain (17 U.S.C. 105).
- EPA AirNow, https://www.airnow.gov/. U.S. government work, public domain (17 U.S.C. 105), preliminary data.
- PurpleAir API, https://www.purpleair.com/policies/terms-of-service. PurpleAir terms of service, no redistribution.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/w2026/aqs_01.json | 46,497 | `69f6183dde0ca12c2cceb75f0a772da699987ec0f1b23bd53b8510e45c68e2a0` |
| data/w2026/aqs_02.json | 11,334 | `2cddadc9bb290322360f480ca0a1f3d003d9d7b426329f2aacee220fd8042d21` |
| data/w2026/aqs_04.json | 66,358 | `a43df315c66d0ca2136e9b4403ad7ec5fcfd0733b6099c3cb66f2ae8d397b494` |
| data/w2026/aqs_05.json | 5,067 | `5bcd60c9362211c6c557246d91d202813daa885e78f299c03da17d1f8debb667` |
| data/w2026/aqs_06.json | 296,272 | `039b89444c832b1cfe884e8491efd915f59482539cf0a1c7c5e37164bfc6581f` |
| data/w2026/aqs_08.json | 90,592 | `8d1f51507d2a67d7f335f655fc792d8ef0cfc7b3fdf9413992800d192a7b5f7c` |
| data/w2026/aqs_09.json | 31,018 | `3071ec96831c8d1a7d377cbae572ba8512f235161e2efd56e6b741f49b763fc8` |
| data/w2026/aqs_10.json | 27,333 | `a8cb605730ca09ffe7b29036dda744aa663812d6f31e634fafbc32ec360fd5c4` |
| data/w2026/aqs_11.json | 18,353 | `c7bcf257cb69c45aa531ad362192bf58be71f1b7ba3fed0988c3f9aa215003e5` |
| data/w2026/aqs_12.json | 112,996 | `36a53b8bc72c37af7c6ef523f191b59f054861b66bf2a912d90e5aba59cd943c` |
| data/w2026/aqs_13.json | 34,155 | `54afe356cdf5767458caf3fd45c1ee74d14f1a9ac5816bbf30cef75cbfb44467` |
| data/w2026/aqs_15.json | 56,381 | `99e6833b9700bf9b1f8e186f0f8d27191486a646ec6316b2c38aa24ab095aa1a` |
| data/w2026/aqs_16.json | 13,118 | `47ff2ad8196ce7a73c3b9d950b64be8ec399da9f8a8805fce47c00fbc79e1300` |
| data/w2026/aqs_17.json | 128,492 | `4a2acae89f6dc56cf0c4c59ce2956e8c3f4ac5e7245d035659c732a9c797e8cb` |
| data/w2026/aqs_18.json | 117,113 | `1106caaed3b1912cd0f56b747d9ed971ca6603b717115b2b71eb19742b9924d0` |
| data/w2026/aqs_19.json | 61,807 | `bd59f59e54609d786a1cd42eeef9dbdc5483c17e8a9632d3e0fbd66b377b2386` |
| data/w2026/aqs_20.json | 13,998 | `f4dfeabf5d9bf2003687638265a025441b8f6306cf4f6bbdb451d2152d373c83` |
| data/w2026/aqs_21.json | 73,818 | `c596bbde15e0ea1ca2ca11110663f13758c93095c0190601fdb1b4345d6ae116` |
| data/w2026/aqs_22.json | 30,357 | `b272b6382344dd511e0c7c806a092d229ea3faa368b01635476cec8096eadbe2` |
| data/w2026/aqs_23.json | 41,917 | `321ca00a9d6e2f8a2974112d934e79fec3826311a80f5fcc4c3906b324231596` |
| data/w2026/aqs_24.json | 39,906 | `74eea36e7b24f3505d269a3cad1b990548f5302269b44df3a993fd55f882c46e` |
| data/w2026/aqs_25.json | 89,201 | `8820ba860db6b62b05067b4585116059d0eb2cacd181a12956a48bff978d2842` |
| data/w2026/aqs_26.json | 96,675 | `0581e85afbec7dc5b79f63c10443c55c4c0f1eda248d55968d45e7792194a946` |
| data/w2026/aqs_27.json | 102,343 | `560449425bcb35a1c09c30369d41449e2e70451a88c8a08653d680ecd137b688` |
| data/w2026/aqs_28.json | 30,652 | `3e730a5b1b9e3f3002484e93da3fca5723fa9639495372b46cca0e7192188d24` |
| data/w2026/aqs_29.json | 69,384 | `59c24f6396d397d032a40f882dcee6387c00f8c6cbcc768cb9f7464b909baa0d` |
| data/w2026/aqs_30.json | 59,053 | `124fc0f5d9141504f9950c53d839af9130aa418eeb67b38829138e9fe2a6e4f4` |
| data/w2026/aqs_31.json | 24,048 | `7f39c2a38e089f46f667ae662848abb3b7097975af96ea56d4ced67553ce6b34` |
| data/w2026/aqs_32.json | 79,337 | `640cdd60fda103d66bd18c9e1344959f0b05e3adb2ebaf978369acfb3b1aeccb` |
| data/w2026/aqs_33.json | 21,312 | `78dfe289d7b1d6731e611e146d53ceaf205a7f6b8f6d906588c0ca8a646933dd` |
| data/w2026/aqs_34.json | 76,960 | `28b90b09d6fd2802ef5c86e92c908e58b2f58cfa6b9aedd88597cc398dab3d5d` |
| data/w2026/aqs_35.json | 53,018 | `7756ece874e195e539ad0932e7196729e1d214f83b52f7b78068580b833bf814` |
| data/w2026/aqs_36.json | 76,372 | `2e43830a28d96f7f177730558360ebb79f0546cc28a6d8219606244bf85bafc4` |
| data/w2026/aqs_37.json | 85,556 | `03d649877eebcaf13a896077ad0aca0e72d622a145c19d85c72342df6ffd65bd` |
| data/w2026/aqs_38.json | 41,727 | `af4aae97ea3f4e783a8fb06b9794a101665f35adb188da930414614382fb0a08` |
| data/w2026/aqs_39.json | 144,023 | `02bb1d92318239ee1646360414207acf14dbd94d4666cc258684a9ff3ba0a737` |
| data/w2026/aqs_40.json | 46,087 | `72a6a4b2937acbb1f7d29097938834e27f1c30ced4fc5d2e48ecae806e297e67` |
| data/w2026/aqs_41.json | 66,784 | `a13e416d8b4c244bd30e533c4e4ccb3b79a14aee27ff9a0dc2c4d6c7831f7083` |
| data/w2026/aqs_42.json | 198,739 | `cc871812bcab876b4e1a4344ccb135c8143dae8a2911f81d60313a0796e96b49` |
| data/w2026/aqs_44.json | 21,907 | `ba3d03b437d0f81f5896af59ac41dd9e3dc2768e725ff17ff7f5190b11aead4c` |
| data/w2026/aqs_45.json | 17,774 | `15a784f5bf7d6866602e8a84c26a7eb018e5bf85e86ecbe5b6334f552036e3c1` |
| data/w2026/aqs_46.json | 34,207 | `02f378a7b2d4d3dad8d04f68a336838573e35763884f55415a03d5831e692282` |
| data/w2026/aqs_47.json | 64,300 | `2efd2e42e1d21debb2ceacfba52460280f4a429bd485588f41c55e23a314ad61` |
| data/w2026/aqs_48.json | 214,952 | `dcdf96ed05dfbe71b758efcfe1fda650a920fed6110d8c30a87f8a4688d2703e` |
| data/w2026/aqs_49.json | 110,115 | `9cd9ee6884687e22957136a49d49b919030ab25061396d5d59da365ca71ea1e5` |
| data/w2026/aqs_50.json | 12,725 | `7496c00ae998647612e857fbe379ae73f96c148bf28a0ac44500823ecbdeb222` |
| data/w2026/aqs_51.json | 67,774 | `a4ae870d9f4ee534ab3f102b9fd1b50cd301676cf0b3efb75d0f65238feb74e6` |
| data/w2026/aqs_53.json | 86,273 | `318b8f02090a10aff1b9b86b695014472e7a808f3a40b8bbb9a76626280f41b9` |
| data/w2026/aqs_54.json | 10,617 | `c9601c98b873c408638031d145b160e655945f5ea1287cfb0e052b51a64e118b` |
| data/w2026/aqs_55.json | 70,885 | `b4747d41fc4ca03e2291829ccb6c3b3657dab4f29577fe5f7f5765d113d70e09` |
| data/w2026/aqs_56.json | 61,652 | `caa510b8de9e9198644a6b2f928137996975e2ff3782d1b273573cd6442ab999` |
| data/w2026/aqs_66.json | 97 | `0b60ccab515bd4d43890ba0bc7b89adc0d45c6e176ee58681f34f4dda84e005d` |
| data/w2026/aqs_72.json | 2,710 | `6ef35cf6dc8f77cd9b09bb1c4d6b163d2b250b4cbb77dba0ae5f81178f4830f3` |
| data/w2026/aqs_78.json | 97 | `0b60ccab515bd4d43890ba0bc7b89adc0d45c6e176ee58681f34f4dda84e005d` |
| data/w2026/aqs_80.json | 3,891 | `ca03ee5294d99e5efa74fcdc7a22dbece81deced513beac20495514182010be3` |
| data/w2026/aqs_CC.json | 78 | `c6ae5245efad3a333af42b4fef91726e6c26a38133814dd094f5ce07aa7db83f` |
| data/w2026/pa_101281.json | 2,338 | `51e9e4b2db8779e85606e6780cf4a5b45c3dd3e18482e0e4dc575008b7fc5623` |
| data/w2026/pa_10264.json | 5,137 | `933400f5b07dbea14e03037ef16fe695e7b9008d7b34649a31ccf7f92438c1b1` |
| data/w2026/pa_102720.json | 5,030 | `7c400f741b8667fb32164e5e5a8bbad5ba0053403b31856702cd41a0365a9205` |
| data/w2026/pa_104096.json | 5,225 | `c36caddd56e79586495fc544ca0d24cd97debdd5f0bbdac11b8db0b41a5f6ac3` |
| data/w2026/pa_104100.json | 5,175 | `58ad7f186c5a649e828a3fe0a0c727be2bb9b7b0b43cc816ec123d15814e9dca` |
| data/w2026/pa_104108.json | 4,983 | `5ed67730987e74fa66bcf968aab1cc2d803df5f8bc619b33ce0a813ea7ed19e2` |
| data/w2026/pa_104230.json | 5,333 | `010fe6b9d230504aa47ed7adddceaae6ad9144d00defb5b0ef3b4a190c04f45a` |
| data/w2026/pa_104234.json | 5,129 | `002566236c4ea5b07821da9d285139eff2fceab241c410d258241c172cebbd18` |
| data/w2026/pa_104246.json | 2,622 | `aad6bdd538a7d7fb9a8d031b3000bf7155783cc2ac028400274373bb0e6116e7` |
| data/w2026/pa_104816.json | 2,778 | `9353fd27c80730d307c312925f050b8699e6d0514aab7e180afc85654fada619` |
| data/w2026/pa_104850.json | 5,237 | `affd1f3ec4d0fd67f7b60c23af89686feed68dafeae5b178337a5a145a665fa1` |
| data/w2026/pa_105076.json | 4,821 | `dad09ea8f210d4ca38948e51b2a8b03f61884e1709cb193f9e0bd2a63266f322` |
| data/w2026/pa_105160.json | 1,773 | `38bab7fba9abdb333a6454708a3c86e8dd698f41a5128283646d960ef0b8374f` |
| data/w2026/pa_105192.json | 285 | `f4835ceb0bee2e99b4a405e2a092e6fd0f0795143f4467918355d06560a0f46e` |
| data/w2026/pa_119957.json | 4,865 | `c9d1e668f970dcffaf752a2f37ea2bb7e190d44dd4490d150ec1f5f9b0c60604` |
| data/w2026/pa_125271.json | 4,302 | `6ff36727a83a12816ca90ace97b5928b5efac0356598d9b5424770302bf34aa5` |
| data/w2026/pa_126315.json | 4,892 | `9587a2ff4d25246c909b721c5a1b65105c6da8148f4cc52447fe33c9edef5d60` |
| data/w2026/pa_126367.json | 2,219 | `f8037d01ae038ec669d270b27691479998289530243b9c11dcfb725952d3caad` |
| data/w2026/pa_127269.json | 4,615 | `7ce54a839fe41f41886e2c4297d84ab07dcc79c7e30e650b4c6930f4093137d4` |
| data/w2026/pa_128715.json | 4,994 | `1fd0ac319e193c6060542060f28139a154f3bb9bce76001a24a0a02ca5c8b433` |
| data/w2026/pa_12917.json | 4,649 | `cde22ce8dc35401762281b95c3880bbfceac03275fbf381aaafc6f0376c2d9ae` |
| data/w2026/pa_131785.json | 285 | `5457cfb67697f2f420dff753ecbd5986736fb2a588528f39767e89aaadd7ede3` |
| data/w2026/pa_132273.json | 321 | `c954d0f80ae0b54998a17c0e2362e6ed287054ff9d42f1ef98edbe40cb19c5f9` |
| data/w2026/pa_133221.json | 4,999 | `a9b87c4a9c4cce0998c3f0b7a3bed9b63cf76e8e1d37da40bbbe2c60b6d9bead` |
| data/w2026/pa_13469.json | 1,118 | `003473864fdf52e0b6c7539d1e59320b96dddc0186175fb73d9c150878dec83e` |
| data/w2026/pa_137756.json | 5,029 | `d0842236f5dac3cd0e8aba679f5f54181b48ac466a7806fe12fa99980d663cc2` |
| data/w2026/pa_138970.json | 4,941 | `cccae502c0da075a8dff64dd7c8f31f2a868ca3972e7fe67da1c6239a4aff4ac` |
| data/w2026/pa_140768.json | 285 | `932680212206fe0bc5d976e694fbc488b64d4f421fb1eba8e40c93f4840e3201` |
| data/w2026/pa_140804.json | 285 | `b064411825b1f1bf072c47a0b58aa7e95ec02b314fe4a142865cbb2e8edda6f2` |
| data/w2026/pa_142428.json | 5,168 | `ae8c3a489ff7c1bd0fd2876df2bcc68d3478940ca7c28589d7ad9e953f6c19a7` |
| data/w2026/pa_145364.json | 5,001 | `e7609a9c1c0e797c30de0905d1a8a31cf1ea2986d0a3bdb943f3e99d0d8ceed4` |
| data/w2026/pa_146018.json | 4,408 | `c8ed739b0731ffaeecf7e130183f2ebcc795d144fc50c9ccb4cf4e031bea49e7` |
| data/w2026/pa_146162.json | 4,957 | `e0e66f939e5b027e3482e476650c377b2daf977ae0c05c53ad222151543f3254` |
| data/w2026/pa_146208.json | 285 | `99aa34230dd216485b62c4a56885e9715cb06070d8ecadab8def0bf91cc63a02` |
| data/w2026/pa_146264.json | 5,016 | `ff8bdb5bd8b20d43d03fabe7dc755d60ac0a883068691f6678beadf308524e5b` |
| data/w2026/pa_146498.json | 5,526 | `5b2deaa8f3ea30475a9d2dc24cbda023ef95430e8564f2d84f7c059326cf8a61` |
| data/w2026/pa_148123.json | 4,951 | `ed6e3ccf4abe501a4b3d43b0b0a4b489208a22ed3b8d21b55cdead08c3bf245b` |
| data/w2026/pa_148375.json | 4,768 | `c9a14f2515f9c8f2aeb6edd702852ead8dda40deb738e51dd94239c160c3450d` |
| data/w2026/pa_148591.json | 1,693 | `f1e76662809607e1f667d2a9ad24ee5d6d3c7b83ea1fb3bae5d9353699269cd5` |
| data/w2026/pa_150132.json | 5,183 | `e12409e4ca4722654a8b454223323ccbcaa6a94f076790eff72919975c43c71a` |
| data/w2026/pa_150464.json | 363 | `4c3ba6a577df2c08803630b8b4225b72e6555fc1073605883594cf2d29ebbed3` |
| data/w2026/pa_150474.json | 4,927 | `f4693826452399d486d63c1a4225c95269ee25cdcaae3765399eafd6a982fcb9` |
| data/w2026/pa_150516.json | 4,931 | `30e88dead80d6a71d78d0d0d1ff06e62851f086635a1e96b405e7827b4c7c75a` |
| data/w2026/pa_151634.json | 4,967 | `21db4fe7726c06166d34f1611147afa12cb7e70e2e9d50c83be176cc93734d98` |
| data/w2026/pa_151768.json | 5,012 | `8f7b5e1d3e70037f3ec1cf0102fba2c467ba6f0abe5015bef303f7cabc9c5181` |
| data/w2026/pa_15229.json | 4,936 | `12b96c1c49243a94880176544194e51e3425bea12bc34a545a01172d6b9ca562` |
| data/w2026/pa_155005.json | 5,054 | `87952a2c1f3af80f9495046aa9b1396d393f0d9e091e48674b1f2c279b6ff88c` |
| data/w2026/pa_155013.json | 5,262 | `2ff3f5e27345a3e29e62f7b1fb6171933ee3797f541e616c58b022bfe0f11a44` |
| data/w2026/pa_155015.json | 5,033 | `4f37b2177ed5017ba657ce5e77f73c812d91ac630fda22a6b7bf69d7f4fb978f` |
| data/w2026/pa_155053.json | 5,205 | `530d992a2c1fd236c9ed0080cead0b3fbc98ec1d40aa29f4bb295523cebbb7ac` |
| data/w2026/pa_155613.json | 4,953 | `8ad20c1f4d6d0e87bd3ce56825d29fa256d93ca67d853fa12749b5e8cd4c725a` |
| data/w2026/pa_156163.json | 5,091 | `8dd86906a71994f8c10763966fa2f535c02855b3791771e1c7cf90a444339608` |
| data/w2026/pa_157993.json | 4,631 | `355bf8d82b0804d06653f446d7f4e1c123845795b7678b78d718233e4311bc1e` |
| data/w2026/pa_158031.json | 3,140 | `32e6d1c44d8395c1fe4abd3761b4a94de223cdbb381b85c80e94667d9284af66` |
| data/w2026/pa_158769.json | 5,043 | `ac0bc7f31480afbf5d3deb3e0c1e9afaba1cc5d77c87d0e66635fc420a7fa07d` |
| data/w2026/pa_158771.json | 4,700 | `718e13eff0aef4219bd103d889cd43740d8712ed88fbd4957ab710ee5adb0617` |
| data/w2026/pa_158773.json | 5,037 | `ffeedd99639bf71a811db09f4306ac666bd165deab15cfa68656e248a5520ed5` |
| data/w2026/pa_158797.json | 5,045 | `83de72c081658b688bace781083276e86b41c268ffaaa096a7f53242fb8c30ec` |
| data/w2026/pa_159361.json | 5,201 | `409260e328a6f1e40c042e167f813d440dd3c94fe50710052b2b74dbd8ccd315` |
| data/w2026/pa_159965.json | 5,069 | `002fe4598fc84eae41cab1428a781c19db8c22213f260e340f04813418803388` |
| data/w2026/pa_162113.json | 5,061 | `98cc03467ef9cc3d3fd42f0b5228e853b7c5bee6a36ac0613e95e33179501c45` |
| data/w2026/pa_16315.json | 3,645 | `715bd9490bc38616085ee332e21a8150e917f7fb927b6688e2db4c04c10e1f9b` |
| data/w2026/pa_164295.json | 2,628 | `efaa5e6d06b6c99ad625d4662b033fa8e9498cc7400f2c11c28f5e81afa8de18` |
| data/w2026/pa_164303.json | 2,613 | `320bc80117c15529f0bcfa96675c2532787e1d3636485a6540cc1e6c507a8e82` |
| data/w2026/pa_165481.json | 4,963 | `2c63ec893be23f992238218d434eb21cd3e9dbf2e778458bde06303b519d6cb0` |
| data/w2026/pa_166421.json | 4,244 | `170e15e676d318aafd91f10220725f9e4e3238bc89d41410b28005e71c437094` |
| data/w2026/pa_16735.json | 359 | `f5e0daa6827f5ca67dd7db5b6992275fff0070ca8187bf43d9e1bafa033b2477` |
| data/w2026/pa_168067.json | 4,967 | `c527775b523fe8dcdd317dbf5fc2dcb28f0afabc6aa67f45b9ecdc117d67ad78` |
| data/w2026/pa_174659.json | 4,926 | `f77c73b792d53be9fdb11f9c68a4b04440a2d4c24b6f1befa644330bc4bfba61` |
| data/w2026/pa_176279.json | 4,919 | `b8e53ae4869da4f4ef6d9cd849c31dc935ef8fdb4888f98b6eeb233b7ba3b72a` |
| data/w2026/pa_176311.json | 5,029 | `73514878d61ade285ea140a5aaaceb6b626ae7d8abd8f65404c263c3c72e0b7f` |
| data/w2026/pa_177525.json | 5,183 | `35d65015e637e5314d3a723b058d0fdd42416196448a42a46d7ea01cd38661af` |
| data/w2026/pa_178279.json | 5,138 | `54217d83f63511b8f84415bc1a7578e3586cc8cd7064f3ba1045f655f580af4d` |
| data/w2026/pa_180081.json | 5,202 | `25775552dac80727a6ddf1fe910530b9dcd93c32c8339703bebddb07ae758d7f` |
| data/w2026/pa_180085.json | 5,116 | `f5eb0f4297581ed285900311c1da575f47e8e81bce118fed421e30b81ed8b0f0` |
| data/w2026/pa_180125.json | 5,018 | `615877c04f34f3c5761a4c2fbe826b64419f5fdf70875a76c0a775c359af3306` |
| data/w2026/pa_180137.json | 4,667 | `b1a1b3275d18a62119daec28ed99bbb5fdcccaf62e97582e0838a541458d481f` |
| data/w2026/pa_185009.json | 1,613 | `98b08da734a47fca0243211bd28590ee1476fdc3595b93acb55d78dc7694f1c1` |
| data/w2026/pa_1854.json | 1,671 | `ec83e3e10fb2e5b1e9ce5949e673976cc73f6380b9d5b5c3e2855a29812fc9d0` |
| data/w2026/pa_185651.json | 4,937 | `e5ac51fed58d02abd3c63165032fda3f93b2792451d2e04f700420ea8c889eec` |
| data/w2026/pa_18625.json | 4,983 | `4e076c4507358f39c22858701c1079e6be4a6c8e7279407eb626e9af373bdc8b` |
| data/w2026/pa_188259.json | 4,951 | `77db2c12898a7d1a5e14bc47c26c5f6c5677d05eab5369e66d38a9be2f4b2750` |
| data/w2026/pa_192079.json | 931 | `6f4b846f137d4e6be332cb7e7560f660022edf33af55764be88d4e9c48619614` |
| data/w2026/pa_193347.json | 4,797 | `ad99562a0d0f92252c73a369a05d42ea059f4da2015ffc3194e7ee13e9708354` |
| data/w2026/pa_195337.json | 5,012 | `69321f21fa1dfedb0d0a646852a9d2d0f738d0147021f7b8f71bbbcd256bbd1c` |
| data/w2026/pa_195829.json | 5,036 | `ec5dcbed3dea49fb364d0bb98785a9d649cae072d429a991364a99e39a738e46` |
| data/w2026/pa_196805.json | 4,959 | `ee881d1d33fce0f09ea7f7d1821441937612e84e62de3c2b8988c31f83f003c9` |
| data/w2026/pa_201935.json | 1,021 | `f56d6e9b9a5c9c916f4916868001570c430d56a0b451ca58748381b755c3b326` |
| data/w2026/pa_204141.json | 285 | `4dc03d318b97873e52f8520e4cc9826bafdaeec357c20a05dde806c09573d06b` |
| data/w2026/pa_204423.json | 285 | `1b552229ccd29dcb193d88fee017676610708fa2a40e35cedc1a27a834a691d0` |
| data/w2026/pa_20607.json | 4,962 | `ef86ab97f76501ab45e17a128fd77c71eaa530934e3911a7f52c606e7dcde08e` |
| data/w2026/pa_208129.json | 4,933 | `472e4aef85e488bbbd88ad930535edb39f111235dbd46ccdf074a80830196926` |
| data/w2026/pa_208649.json | 4,949 | `625f6b8bc3935d9348aef90eeb3db761673ecf0959d1e36dcfa8868fb1fc9d78` |
| data/w2026/pa_210991.json | 5,011 | `59a284dbeec60a8c1426fac7f49d6a2271ea5163b7a55a222c22074975454ec1` |
| data/w2026/pa_21109.json | 5,080 | `ceddf22583032815e7422c8f39eb232ce885560c4d9604b5c91020f11859a757` |
| data/w2026/pa_211605.json | 2,539 | `1c5a6697868b157583689f18496fda7a08d0682c3ebd7a7b376ed9cbd39e07d6` |
| data/w2026/pa_212083.json | 321 | `bc59836e522cac19b7acee9a36eb70caee389ed7a8d37ad26b14d165ff89d7b8` |
| data/w2026/pa_212361.json | 321 | `40ff88771083b56b582b4fe7e4cdea50b6e6c2387e8aa6d2fbf1bf8c8636c13b` |
| data/w2026/pa_2155.json | 1,280 | `b88a3f969aec70a6add698612e961833ce63831096bbb211a902e7bc7daa431c` |
| data/w2026/pa_215895.json | 4,390 | `8086ba30d36c5d23f8a170b897375bb5217df52e0433ca45eddb2f172bd374fa` |
| data/w2026/pa_215985.json | 2,679 | `bc17dd0d270e3fe0d5d30448825f5d618e41c029f51debc2a183d7ad0e8a9289` |
| data/w2026/pa_216253.json | 4,967 | `788dfee9fc754a23a946b7870b2aac9f30c9d48e70dacffdb13786f1d4a5f121` |
| data/w2026/pa_2167.json | 765 | `44d192d4f1b1a1abb3cd96cbe7af7028bd6cf0e8673773056eadbab9612e1576` |
| data/w2026/pa_217345.json | 5,333 | `10159492ffd02c98244d64e267bf793b2e19cef1b7856106598f57c8ee02553c` |
| data/w2026/pa_217785.json | 4,252 | `a839fdb618f868f2b2cd3c39860bb361b9370d71069bf3ff540333fec20e10dd` |
| data/w2026/pa_218059.json | 2,276 | `191711e45509975cf53fd6afd6aedd081727584e41a1fb62893c19bc72cdfbd6` |
| data/w2026/pa_218137.json | 1,997 | `917ef61b3487cfa5e82f9564cb9eb173ae940bb07df3e27d898cc59cad392ee8` |
| data/w2026/pa_218237.json | 3,757 | `36d7eafd970a3386aaeb4d150b24384bac556ca168bca32ce0cde052ade7d776` |
| data/w2026/pa_219519.json | 5,051 | `0d5bf3efddffbf903cd3c7126cd19e6030eaafac7410d1a64661d08330f8e4eb` |
| data/w2026/pa_219521.json | 4,771 | `3915da6eeea73ef8ac0eba30adc536f967d7a2a876e086c19b07da47ac779758` |
| data/w2026/pa_219539.json | 5,006 | `f16af908fa5e80f768c2e1e4e377e605943130be96c0f07a6d18f68c99e48214` |
| data/w2026/pa_219915.json | 285 | `7779a2fec1dc84960e3dfb29a56f75eed3b839919f08ba8bf73b80fcf37ff91a` |
| data/w2026/pa_225235.json | 2,343 | `3d5c761f8f0091985a3c5be9a6782214461895ce702da4e86d7a34ae1225763b` |
| data/w2026/pa_225329.json | 4,968 | `679eaebef1c46c990c6dbdf9242dd59e4369f3d1d4024ca2f4ac32645d7fd103` |
| data/w2026/pa_226145.json | 5,136 | `3ba748dbaaa4d787e3b1c2df0c2ffc8941ab97b97502e23883dd8124262a2849` |
| data/w2026/pa_22937.json | 5,030 | `15f598f5a770e2d8c939d135b1339e5aadc0451b15f512112d7e0ba214921b28` |
| data/w2026/pa_231846.json | 4,923 | `d9454d80f97243f18d6c11dbc5acdb5a98c1011843e2c7d58c5930e0aea17f0a` |
| data/w2026/pa_2346.json | 1,286 | `751867ed843768f3221f473f1b0c5346572bf6fec0f1ad54854b4fb8e80300f6` |
| data/w2026/pa_2368.json | 283 | `7f0b5ddb1c648e899e025fa329e333b07613e4f6465e65220df5d94d869328d2` |
| data/w2026/pa_237189.json | 5,075 | `98560c94f70626ba1314805e1af8b3fed0ebfcb2b0b21f647305333ca045af4d` |
| data/w2026/pa_237205.json | 4,991 | `5c70b7d03031ad499e95a60298e1c23290a1c647ef17acc8a53d2ea4f9f1b6b4` |
| data/w2026/pa_239151.json | 5,167 | `fbdbbfe1af157fb7e3310c69b1026299ad25898fcb8c9f5c4af9a91f50c4c002` |
| data/w2026/pa_242423.json | 285 | `41b05db40ba4b2811d6ee120c7f0582444d1ddfccc0dbc37f46ea83fc3aaefff` |
| data/w2026/pa_242873.json | 4,294 | `2c9eed2dbc12276b975df4c88dee4bfb657c211248f3b12a833adf75ccbf8cc1` |
| data/w2026/pa_243731.json | 5,057 | `357e4fb27d9c151c4e271092ec3ccc7b984a403d1e3f3564aabade94b37ead9b` |
| data/w2026/pa_243733.json | 5,058 | `a63bec80b7c55c11c374b26f65d9361ea5fa6f4d423abc755c053d0aa970fc4f` |
| data/w2026/pa_245113.json | 285 | `af6aac8ec2793b1a3815c584e6c3b3313eba3ef49a17a3754211dd4f5648be58` |
| data/w2026/pa_246283.json | 285 | `5d05b1e8b9f06b795f3c75d32993907902f6c820317b99a05caf58adfdf378df` |
| data/w2026/pa_249171.json | 285 | `6e75a75c4d26dd0c9be05af8ca838300eb80de2b4d45e99dd4163ddb3e24520b` |
| data/w2026/pa_249449.json | 3,445 | `9d7778972387bf42f128374de64642e88e5a1ab6e52f6158588016856525d9eb` |
| data/w2026/pa_250829.json | 2,300 | `de86467cfc7a940f388815b2319286d41415ad7c47e1515d94ca061946057620` |
| data/w2026/pa_251043.json | 5,093 | `56e248c193f7489dcedbf94ff890830f4787b15541d7a71738e99fca7fcaf2c7` |
| data/w2026/pa_251301.json | 4,936 | `144fab65688d2095f9ba889a63a22e76d019cd28230aa580f27caacd3ee58cb6` |
| data/w2026/pa_253033.json | 4,988 | `992d70feea7e397cb93208e17a407af461b0adb09668e5046d59b7ceca4c36d7` |
| data/w2026/pa_257019.json | 4,935 | `005a18dcfc6aa9c001c23e6a2ce5db8413b7607c77edaa922b079412e2b99ab2` |
| data/w2026/pa_257165.json | 4,937 | `127bb78a454e17ad6bbc5031ebc3d9ea4a3f7fc28e782d619e1819543c9c8b6f` |
| data/w2026/pa_257176.json | 4,800 | `3207cbdf26622f6736463e8c33f6b6fb081695e83b65b60106cf0b12af55c746` |
| data/w2026/pa_257183.json | 4,949 | `1d56efbd01dd63012d82546a8d8c430094a306239eef046f1babf987647841aa` |
| data/w2026/pa_257221.json | 4,939 | `591aa5c5e5227d81a407c172a5850a32c5d895917d65c9e3eae8456e9367e83b` |
| data/w2026/pa_257429.json | 699 | `200fa756b1ea2306d6dc4a221963c31cf04bcf21d7deca830660cfe9388cdb8f` |
| data/w2026/pa_25835.json | 5,527 | `3125bc7ae58b4a0a94d6e98a40f02015718b29a9db09a3f423f9bb6cfafe4c70` |
| data/w2026/pa_258463.json | 285 | `cd3a51cd9b5ad1dfd111aed502bf39ff2a182b2bae3c7d39f04640ecf5634aae` |
| data/w2026/pa_261271.json | 5,164 | `5960a056e0804b617e69e302173fff53b361e794fa8d1e17b7e40b89d1f6260f` |
| data/w2026/pa_261289.json | 5,091 | `6bb913fb19c8a42158a19a300e186a1965ce70191b900b381431ad13a64e1461` |
| data/w2026/pa_261319.json | 663 | `bbe70b79738f0177e080bac1c9a7d9ac0978462c7a329c62c24f0a3ac9fdad62` |
| data/w2026/pa_261331.json | 5,554 | `32c9664bf43b4ce72c22b32dfff515d8a79b1a0fba5efc9845399629a24c764d` |
| data/w2026/pa_261457.json | 5,181 | `5f5f3b3b6a528e6851370506e80f6f82ff134c5277ca33c96958d71975e418a4` |
| data/w2026/pa_262243.json | 5,237 | `8247827214f76f45cc4e73a7fe5f1ef7c5a516ed312b5bf7587110b4cd2b2916` |
| data/w2026/pa_266317.json | 5,015 | `b46c2ea7639d0620f979d50c35b4a157ac76fde3c0ff494c98b5cee1a2e8cbc5` |
| data/w2026/pa_266321.json | 5,015 | `2d3166df103050ba8320b3a87030180b6e81b105594773f386942b50e427c92d` |
| data/w2026/pa_266325.json | 1,519 | `56af79bb446851074a40424e7aed0301d0e9072be715d34588864c57f199cb02` |
| data/w2026/pa_266893.json | 531 | `1ed5d22b0fdc9dc28b679a774e027429501fb60f2afd1f206d586627c828e164` |
| data/w2026/pa_269080.json | 700 | `7e2345f0ae345c545650c0867fb64b8cf44e2fd64e78c7170850bb367d17c855` |
| data/w2026/pa_269590.json | 4,927 | `7f32531a163d640583430fa264978646643dbecea74ddc7f990756544e701c6e` |
| data/w2026/pa_270130.json | 4,937 | `407e725e8e56cb9da1a97debbbf2adb735153b0494a48a099bf735dbebfbd666` |
| data/w2026/pa_270506.json | 641 | `64ae5581100603c7ac6e6439fbd9452a95f76ad0472d1edab8bd8c78c3247dca` |
| data/w2026/pa_2717.json | 4,929 | `a50f549ebf494758d2e0e138b42b474074b82a53f2a82ec99dee28747b26dde4` |
| data/w2026/pa_272139.json | 5,107 | `1199c1767240e0c806288a0a3725c436b5fc016b62cbe07930dc06fb626535c2` |
| data/w2026/pa_272158.json | 4,407 | `648e5350bd702f14008009674e30558c827cf19c9b5e5ac6c6928f0d99cd8884` |
| data/w2026/pa_2758.json | 1,677 | `18c557eba3781cac84973332141d36c7e13e6ccb08534f302bda7861e36b91e4` |
| data/w2026/pa_279724.json | 2,296 | `cdf15fb9b2250eff9a83d27ba39ffdc65ed976c6a6ccf018c311ac27794ec714` |
| data/w2026/pa_279742.json | 2,295 | `f7e6fb331496e121e260a1974758a110ab05d4d3b5b5a40636e82c34f2510fb7` |
| data/w2026/pa_281254.json | 5,123 | `bbd85397d8a24edf163c63d264cf239217de393b9e08eb3e1aafab2a536fbf53` |
| data/w2026/pa_281276.json | 4,971 | `951cb78db598c65f14ef07af183d90511b9517cbe1ee083882a2d55ebbf1521e` |
| data/w2026/pa_283738.json | 285 | `0007d811bad9effed1c247a743d02b43296685d7bdf802fc30bf2d89be1695a8` |
| data/w2026/pa_287862.json | 5,107 | `c174b7a370da661fc4976caa23c582cee9e879a4c83c72ffe135bd5104054ee3` |
| data/w2026/pa_288256.json | 285 | `510f2623b66428c75db32383f4a93bd97593b92c86f427f3b10c431345c4fc0d` |
| data/w2026/pa_289032.json | 4,923 | `1f0296e15c5e8ffd9de550a1e997992e3b5c3a72c95c0fd83ce28f017c8e1a0d` |
| data/w2026/pa_289056.json | 4,751 | `753cff3af06f57913897bf2a99d06cac83584818317d362da72ed85b5b36a468` |
| data/w2026/pa_289058.json | 5,097 | `2a392814b283a529fb9182e53cfe67868ce3d810ea8f8bd7649d925252b9ed53` |
| data/w2026/pa_290198.json | 285 | `100f1bfb506a2e04d1a07ea82b860bcf0450d83a6ded1e5cfc4ddab5fd776934` |
| data/w2026/pa_290680.json | 3,137 | `62c3265b710096340c607770b5c06d89a5a13156e883bccf786e3c1b18a55a25` |
| data/w2026/pa_292205.json | 285 | `5884970801ba044cdb83407270006afa9d1e42ec1a956e19a7f0154f9957662d` |
| data/w2026/pa_294183.json | 285 | `1ff82475978c200126fb7b056b56cd51afb53e3f088c7ff9d31e496e08605f65` |
| data/w2026/pa_295781.json | 5,099 | `d5e5ead887b282e724e8ad0ea3290efcd2d2859ad97aa435fb22727a8a307166` |
| data/w2026/pa_296291.json | 5,084 | `d18215f624d6acaefd158fdedf2137171d46aaefb77516a50210c2306f08d12b` |
| data/w2026/pa_296319.json | 4,309 | `028f648602684dd1e49ad1e65651789b205ebf3cf71f6556f7f022d2dec19ab5` |
| data/w2026/pa_296337.json | 4,296 | `086f822ac197acbe727efa78873e7c8ab8ec0be19651bf52b4e2291ada6ffff8` |
| data/w2026/pa_300339.json | 5,027 | `135c7a8740fb07ef42db6d50624e43a36f508d5f658222fef3675e642bd7a59c` |
| data/w2026/pa_300347.json | 4,995 | `3c8bb562472c1afc702c65033e5f903fca747052b5a65938329c41d43d430b7d` |
| data/w2026/pa_302528.json | 3,153 | `c315d4e80e2840534a74d1dca8306998de6670686948da1ecccfad3a02af86cb` |
| data/w2026/pa_308038.json | 2,667 | `7c8c7a354117839c6efe867dc28e3151f11fe1c40c2ce80d5a3d25f5dc7b88a6` |
| data/w2026/pa_309804.json | 285 | `d6af91723bae4a42ba41b412a9aaff7b138225279e8f4ae1a5240e50c3613003` |
| data/w2026/pa_311707.json | 285 | `6ba2acd07c0540bfff0f42a684f9e52e4583f8ec4615bfa3ef077a95871dd254` |
| data/w2026/pa_316205.json | 473 | `756e372a589ffd7a47fefb463ddd22193df170f595f514fe0fd963ba96e000e8` |
| data/w2026/pa_34099.json | 5,134 | `36d2e3078b58c1f0c5fdd30a305cd7ab8eb6fb35116afb57178f443bb6b28c06` |
| data/w2026/pa_34153.json | 5,138 | `786ab81fa4b0204051ac804f2aadd36305ee431751d3955d5fa0cbee8773c8d8` |
| data/w2026/pa_34835.json | 5,007 | `6ab8fc8e56b26807a58029336839ba2150d5ec0e1493992d707ce2e711d1af5b` |
| data/w2026/pa_3537.json | 357 | `e9674fc1b12a3a3015aa43516d4db270ad3009757782604749f13f50f3db3aee` |
| data/w2026/pa_35461.json | 2,275 | `c5d7f79e6b933f435814e7d18d853cdf5c0a2ada24b5618df367d9e5cadb10c9` |
| data/w2026/pa_3633.json | 4,947 | `f0b4271527a9318951e41fb50de69e34cbfe4261fbe51ea1a618dbb09798669d` |
| data/w2026/pa_36353.json | 1,999 | `f0a2f98e325648ce92c425eabed71b465fd2c522d1bfee9988e08d48a0254b6c` |
| data/w2026/pa_3659.json | 5,100 | `35e1baa0f78402806f98bad412ce1ab51f9ac449e83fcd5b23827be51656cd86` |
| data/w2026/pa_36673.json | 4,928 | `0499e1bcff32c3e604d4108c0ed20e0b9216ce828b94a2f8670b336617d60510` |
| data/w2026/pa_38631.json | 4,964 | `4f24e248435666602fe70af286b211f4ec9ca51c1be6d7cd10098c5e5427a5b5` |
| data/w2026/pa_38831.json | 5,317 | `ba9a98a1d81ec9407b9ebeadf55c03938a8a2fd6d9f4363725b71ab0c051511f` |
| data/w2026/pa_44633.json | 5,259 | `3fc7982e522c0ab78ab502ae800ec349089ffc3176259f3616a85fbdd41bdfec` |
| data/w2026/pa_47037.json | 817 | `d58aa9c81d35f5d6973c2724054c9705749a2b8cf76ffefc593362c68ef6a593` |
| data/w2026/pa_51559.json | 4,971 | `dc8f17a3d8735709143fa1345cb67d7e8ab70d02f02d9f2bb09bb5c7b703b2a9` |
| data/w2026/pa_51703.json | 5,110 | `bb31580f710394d60c924b16b08e0f4683b7ea9b22f207d1a2a6fc5fd1fee539` |
| data/w2026/pa_51733.json | 284 | `c4212cb9aea30910f821608304dcf2775759b13d07b38cfaeb9d8e92fb5ea91e` |
| data/w2026/pa_51737.json | 5,137 | `89fc2d408959746384cc8c8c118ea26fa69c472bf1f31635b3ce2fc9ddacac7c` |
| data/w2026/pa_51741.json | 1,829 | `831c6ae7c6a8815a0c3439daf0773dffc95d16e4fc595080fa8b5d17ec2a378a` |
| data/w2026/pa_51749.json | 5,127 | `6248736cbf70613b6fa193d3724b3bafe62796a12c3682af7da4521fd0f0c696` |
| data/w2026/pa_51867.json | 5,171 | `decff91d424bcba7c0c53f8b9bfa209bf8f102a35f4567849fdec6942a63dbca` |
| data/w2026/pa_51913.json | 284 | `94e2e270e1360114a4837bf6a603fd2515534f92787d482ffe66b48b0cb19d8b` |
| data/w2026/pa_5280.json | 1,175 | `44b2f372101050c33a157e708c3c7df2f6c2e4a14a695e8f33f8799f750aa5ed` |
| data/w2026/pa_5284.json | 1,249 | `b394c4206b484085b4d12d270963ee501db83a783ab164d57a257c614dbfad80` |
| data/w2026/pa_56793.json | 4,275 | `f36b7204e00364438b178186a2dd65476660f59f81b789e537b178bd926f2ed7` |
| data/w2026/pa_57865.json | 5,438 | `7a18b0a74085b64b83e4558e0beb4c8d538ca6ebc76e35a7fed8257dd605f72f` |
| data/w2026/pa_6008.json | 5,053 | `da2f74d3815d50557d6a28c2a45f8ad81a37ab598f26a533d54731c716658cf0` |
| data/w2026/pa_60151.json | 5,139 | `034563193e1fcf68ee7cc6f4e845ed931236f7b3a677529168004c01b65ae8ac` |
| data/w2026/pa_60273.json | 5,030 | `6c182297bd15e77145adb82fb9336f57cc83a5f407590fb40050cec1e3a9984c` |
| data/w2026/pa_60277.json | 5,069 | `fb2c97bd266dda28a6dd94c59faab73485bc725393ad6e65c81d6a8bd44ac2f7` |
| data/w2026/pa_63897.json | 5,516 | `eca6df903204041e2d994aa92c863625fdb1b6ce7f1103ac39642966187f4fea` |
| data/w2026/pa_70191.json | 5,159 | `5c2e51c6b64fdd1c31a1211024ca9c0373eb307d02427030841fea3f080a3d6c` |
| data/w2026/pa_70737.json | 4,948 | `d55ca8a8e23809c492f94e2a1af095765ef32097bc07661ece2d314058cb53e7` |
| data/w2026/pa_73219.json | 4,937 | `a02d474ed4348e009805e5786804e50b283a53401644bb13387f166d80e065a1` |
| data/w2026/pa_80381.json | 4,986 | `8a9c89826aa0d2bb8799b8190cd6ecd337d92c240bb4676acf465a27ba4b5be4` |
| data/w2026/pa_83617.json | 5,091 | `69ec00538d2f0ee0ed42b4c4675f634fa451848773de02d720e57bbf8b306298` |
| data/w2026/pa_84231.json | 4,971 | `42ade3db4e9017bc95011df45e9ebaf3c19e59a576885ebd7d93e8b26c4e380b` |
| data/w2026/pa_84393.json | 5,033 | `9e275eee7b1fcd13e8591ea459cd9b70a4e4db5239b755104f6db201b4fa1a43` |
| data/w2026/pa_84401.json | 5,045 | `041bcbac282ce0e0a670eac036f8c697ab23e9cc890cfa403dbd3155dc06713d` |
| data/w2026/pa_84545.json | 5,157 | `92d7f3b5f67a0c6986a4056d0d06695ccba7e62d77c6b87f4af30a2e1ffa560a` |
| data/w2026/pa_87253.json | 4,932 | `a7844da44d88bc22690e8ac3d60bfd42db00212967a75ea8ba1dc2f0c2f036e7` |
| data/w2026/pa_89383.json | 4,984 | `ab1aeb77f3cb627c4739f9bdff1f880ea8954eea3d776a50121ac025adf6d0ca` |
| data/w2026/pa_91121.json | 2,493 | `c3d185a56934bbc6f8bc1e0507006e51a292a16b6e993078c95744e1e080cdf8` |
| data/w2026/pa_92527.json | 4,593 | `d68bc6e7218fe23e024533c56e422dba3993267d3b906d7f52c7208f6baeb872` |
| data/w2026/pa_93323.json | 284 | `e97a911f6868527522f555646d342e4b8955cda239e985b4a0f046241e17bf6f` |
| data/w2026/pa_93577.json | 3,272 | `c8084bf035d61f235c47aced2cece8adc4f3cb5eb153452f27b3f61f53386ae2` |
| data/w2026/pa_9358.json | 1,433 | `d88f8f9f77190d0d8052918e9b358dad15e386bc262e5246b20ca27133550362` |
| data/w2026/pa_93593.json | 4,998 | `adc10789ad0e90787b3f47ab7684f2bd56060bc04780fa18958f79571be7a6c4` |
| data/w2026/pa_93645.json | 5,140 | `7b8e11ce20142f0198ef19a6f98f4612161a323eb397949212653e488c52467a` |
| data/w2026/pa_93659.json | 5,071 | `750f3144f1558d4aa2412939b8b1d146c8fc92920f17f1c35f22b3a639ccd620` |
| data/w2026/pa_97639.json | 4,942 | `9e4c8d52052a70be22357d61d3ae4866d2e995e8a4bf286ca7a24d4e3c969803` |
| data/w2026/pa_97797.json | 1,128 | `3e6c795c99ca7eb5bfeba3b79937ad11a38f2cb842ba9e1882f35a0c0805359f` |
| data/w2026/pa_97863.json | 4,926 | `3d7586db7b42793199b87ec39f67ed7f9861d0c6d0c8e8774aa7ec5825505aa4` |
| data/w2026/pa_97965.json | 4,987 | `7228484772fab816ce3349d2f7d6201f2cb0987916854f571f0eb1878d8e608e` |
| data/w2026/pa_98407.json | 5,063 | `3578ef5f75cf1228811de1998a3dbfedfb5525204e729ed453a0791f9dacb039` |
| data/w2026/pa_98519.json | 3,732 | `cc98736bae9072899f89619cddb68b5cbfbda581494063c6a3e93b189ae763bc` |
| data/w2026/pa_98623.json | 3,696 | `c9d3dd01e740cb61d24a775a3c3dcc4d6e8a84a4e13ab576801c2464e5a872a4` |
| data/w2026/pa_99005.json | 5,030 | `3c80425115fa998f8489e7fb41aebd93bf4845a153fa788c48657b11d55a8232` |
| data/w2026/pa_99047.json | 4,412 | `18429c0ea0feed08e203cff07893b8822693556264be0a2ff44f147b8512b1a9` |
| data/w2026/pa_99277.json | 5,027 | `1c00d723d7fb76df82387e37d7dfb4fa02381d21bf136f0d0ca8318594a04fd9` |
| data/w2026/pa_99291.json | 5,074 | `5b0b2f66b3d7f10572f596a9ff5765d355cf270400fb8464acb47b1c94715ab8` |
| data/w2026/pa_near.json | 24,029 | `798dff085af59fbb4836d04e094a41b9ef617914079260e95fcb4dcf558ade5a` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/airq_score.py is the scoring step of that script and nothing else: airq_tick.py run with AIRQ_WINDOW=2026: the constants and metrics, meets, corrected, ab_ok, haversine and outcome as written, stage A over the kept AQS files and stage E as written. airq_promote.py and airq_tie.py, which run after it, leave these fields as they are. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/airq_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

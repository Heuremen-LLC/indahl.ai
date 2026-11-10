# STEO reproduce kit

Heuremen LLC · https://indahl.ai/steo · https://indahl.ai/reproduce

This kit recomputes the STEO headline number and its outcome label with the desk's own code, from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later with numpy and xlrd (PyPI). It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `62582754f487e4bbb247ecb496530bfe0811c434a8f16222e973664ae554574d`.

## What it reproduces

The headline as the live feed https://indahl.ai/steo/live.json served it at the feed stamp 2026-11-10T16:19:16Z, read by us at 2026-11-10T23:46:53Z. The feed bytes had sha256 `4d878afd9c2fbcb9d12e660f466b33aa217eb6a9e30c2515d2163a792885b999`.

- number: 392 of 452
- value: 0.8673
- interval: 0.7311 to 0.9736
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

The exact files the desk's scoring read, stored gzip-compressed under inputs/. run.py checks the sha256 of each one before it runs.

## Sources and their terms

As the STEO data pack lists them. Credit each source when you use its values.

- EIA Short-Term Energy Outlook chart gallery workbooks (Internet Archive copies), https://www.eia.gov/outlooks/steo/. U.S. government work, public domain (17 U.S.C. 105). Interval inputs credited by EIA to CME Group, Bloomberg, L.P., and Refinitiv an LSEG Business.
- EIA monthly spot prices RWTC and RNGWHHD, https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=M. U.S. government work, public domain (17 U.S.C. 105).

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/raw/wayback/cg_20111119111250_LUTRMTMZ.xls | 1,006,080 | `6af41b833ab08d583c5b9a8806d2e9af710c0b2b17d5770b9c91c5e20308b1ee` |
| data/raw/wayback/cg_20120207180925_FDZOLAQ5.xls | 1,040,896 | `a4991d178f2408be6e0678a5da0ac401844769b1eb8a0301e30e4ed7d549b7e6` |
| data/raw/wayback/cg_20120524194946_2EXNPRZF.xls | 1,022,976 | `ed69b0edbca0619c8ce010665177a5da258d86923d5496b605dd3c3b043a1b6d` |
| data/raw/wayback/cg_20120915182948_UBVSAT44.xls | 2,638,336 | `9005058540aa471a2d3b6069263ca649382e5db60f1aabd2864b774707c4483c` |
| data/raw/wayback/cg_20121017200336_27FY2LBG.xls | 2,638,336 | `6645c3cdcf867515b410c3e10975f73e9b8687399fd1734d6388211a9348af6b` |
| data/raw/wayback/cg_20121114193036_2MGZVWOP.xls | 2,638,848 | `80bf3a5756a9461da9bbd2e7dd6d49e395158be23a8dfb33e2628520361b9101` |
| data/raw/wayback/cg_20130421080307_HLSTNFGK.xls | 2,973,696 | `f35d5117a12c2c4b6584065c07088394b7f64b89c6c50cf738bb4df385312324` |
| data/raw/wayback/cg_20130615165917_AO6QONPW.xls | 2,974,208 | `3faf9f634cef0562274d40f2b5cb2c94c87fb2e42659cd224889fac7400d156f` |
| data/raw/wayback/cg_20130822231302_DSK5LN3T.xls | 2,974,720 | `701cf7075e404e23886ae3a5bc3eb6a425992ceccdc12fa2c83280d3b6a2c0c1` |
| data/raw/wayback/cg_20131108110438_HPSA3LJO.xls | 3,104,768 | `1efedcd8432fd43c0855bb3b81918a4e96bf5d8f927de41ae3b120bca9eb9443` |
| data/raw/wayback/cg_20140418084732_V6PSIPYY.xlsx | 588,085 | `28781ec6b34e43a5469c6b90c302bffcfaef116eada535fc3c9de814b55da761` |
| data/raw/wayback/cg_20140719063848_D3L3TVBT.xlsx | 588,694 | `49bf4b3e54f7d6daf7d63559cf7f624b7c0f7ec87ca5a118eee7aae9ca32f8ec` |
| data/raw/wayback/cg_20140918041426_BAHWL2H5.xlsx | 588,589 | `f02a4634c48bf8b4203b8657bb024074bbfb72632c1f1c996cc7b1cdf2177bbb` |
| data/raw/wayback/cg_20141108093314_OM2OO27C.xlsx | 588,706 | `417f702512adc91b166157f799fcbdd97e93d01c5c2a75100ebe1952996155d5` |
| data/raw/wayback/cg_20150101145614_3RP73BLX.xlsx | 590,451 | `c77319223d85ec595be85cc3fcba7e3649f5b1a6b0d2e2050081cc75fc85ad8a` |
| data/raw/wayback/cg_20150211045454_4V2QCQ2E.xlsx | 591,321 | `c3c6a9b955d8de5fbaa87210da0ef77fbe5bcdc41e92de03c27defaf00d32016` |
| data/raw/wayback/cg_20150221082727_AHZ4ER2Q.xlsx | 591,373 | `9e333bacef287de7df5baa1b6d5e947e0ac84af3da9e327a8948423f0c84eb1c` |
| data/raw/wayback/cg_20150321151454_WWKKPROM.xlsx | 591,887 | `99732a7ae6065f7f477be7291ab30eb5d36c86cff18b231b3c69ffd9b88877c3` |
| data/raw/wayback/cg_20150507102052_TH5GJBUH.xlsx | 590,857 | `cba3876765cd03293efb37904621db984854f162c6c59bcd7047b4c035640a4d` |
| data/raw/wayback/cg_20150905142825_YOKF5HEX.xlsx | 593,587 | `22ec9658ff5375bf859d06df7fd1fb993d92427f2dfd08c20925712392fde043` |
| data/raw/wayback/cg_20160215091356_KPHASYU7.xlsx | 596,784 | `838f3a0f195cd794e659e126dbb457f02afc6154bea530e5799834789e222d23` |
| data/raw/wayback/cg_20160314152820_23IIXKRG.xlsx | 582,726 | `3e6c39bbe238afe469db30f903668aa19ce5659f81942ff182c460012f05fe25` |
| data/raw/wayback/cg_20160620010257_AXEVVGQR.xlsx | 582,753 | `daf4844d52ec103d344ba0507cd71602eac2e8deb3dd4e06096df4d957ecfafe` |
| data/raw/wayback/cg_20161210020200_EUBALXLH.xlsx | 582,246 | `af0a510e4ba0d708b60ea54a68db1dd81bec5c7ed68c043c250d70f5adda4da7` |
| data/raw/wayback/cg_20170119044508_HNP5LUG6.xlsx | 582,199 | `f30f8d17a5ee9e448146b98bb3ac46fc9af1bc48427b9a647299f306e8f6a49a` |
| data/raw/wayback/cg_20170221030052_XZD32BZN.xlsx | 583,329 | `3e740ee64bf51aeba22fb0a4ab1e426e2963e37cd991f78b764c4b6d26d68966` |
| data/raw/wayback/cg_20170427165319_TULUGDXW.xlsx | 582,028 | `a677385441d07fd10a7c494f60f598b232001d05c8c81cdea7c4821f974cff7b` |
| data/raw/wayback/cg_20170527214817_K4GMVRRA.xlsx | 582,220 | `babfde2277d5c649fb53a894af1097f6829f923368fa2888dd56b1f6d99fd915` |
| data/raw/wayback/cg_20170710225416_TH6Y4C6Y.xlsx | 582,282 | `9fbde621daa7849ac32183ad52a79c7f0d677f1df74b4938d335788ad839e10b` |
| data/raw/wayback/cg_20170801184158_VEDRXTR6.xlsx | 581,954 | `1e8a11fb9a98dcacfc2856d251c88ac07dfd1e4c4a31e02e0bb41fdb0319e4a6` |
| data/raw/wayback/cg_20170930101055_AGNPILJD.xlsx | 582,308 | `bfdd5575ac3c8460581a48f7d4ba5715ff53c911788bfdf65cfefc5c0027f8ff` |
| data/raw/wayback/cg_20180907151404_64HQZHVB.xlsx | 1,106,962 | `ce4a0b937f4a1c17ffd486b5cfd50e1cc48e421e1afc056a907e86a3a95dcc43` |
| data/raw/wayback/cg_20190110203138_JGEJEBON.xlsx | 1,039,026 | `c0182667de60d8cff71905390e66a6a46a6156ad881491c718bc4d768c5dbea2` |
| data/raw/wayback/cg_20190510182812_QJVYLYW3.xlsx | 1,037,250 | `3606fe521232a83d8851f64325db95b4d6bab64191a2884620699a75fc8a704e` |
| data/raw/wayback/cg_20190623231107_RY2QX5WF.xlsx | 1,036,965 | `de67e2bb719b6a504fce25ee0c45787d5d454e92d2c367412690115e47de481c` |
| data/raw/wayback/cg_20191115230623_6EGAXXL5.xlsx | 1,034,064 | `9574f80359b8b463b7b2f7d9c1bfc630d4c62a0eb266e559b01f785de357d216` |
| data/raw/wayback/cg_20200115205340_2AIFWCFQ.xlsx | 1,035,551 | `9b175b0dcd29f47d6f42486e7c840e9a50e626485ba13f34888dd08329aa66ba` |
| data/raw/wayback/cg_20200407182537_J44COBQG.xlsx | 1,037,689 | `a51edebec247c15bc5c4d245e782be2ec6973ab0dd7700dbd2ac3f2febdd57c1` |
| data/raw/wayback/cg_20200528203411_OS77OCPE.xlsx | 1,040,184 | `5ae9b87338d471020ddaa72b03ba40646043d4126b265d078982f928c77da4e9` |
| data/raw/wayback/cg_20200610130207_7JVGNCE3.xlsx | 993,510 | `35f8f3ba475fbc6fed0119a1b9cf6cac1dfa3aaf6a06afa959f2cc77d0ecccae` |
| data/raw/wayback/cg_20200919171235_I5OOQQXZ.xlsx | 1,001,065 | `990dc6d874c4a5d887839aca1b1c321f3bc313e0247dfec4100a854cebdce01f` |
| data/raw/wayback/cg_20201017141250_C6U4T2OH.xlsx | 1,002,032 | `82ec579d248a539815b77a670217aa4aa58f51c118ac3abb14ae82b5ae21fad1` |
| data/raw/wayback/cg_20201118122742_F4ITZV7A.xlsx | 997,957 | `655283c8e30781058833793b7183bd149798b6e3c4053eb5d78e28d9398336e6` |
| data/raw/wayback/cg_20210113051958_KQJAFCEY.xlsx | 998,859 | `a1b163c8fc9e35bd5f16258102f8e3681a85331ec38090e77461366d2f0e34dc` |
| data/raw/wayback/cg_20210305093022_OROCD57R.xlsx | 998,943 | `8e9f929e60280edeb04ac20e414a1ab6bea4fc11f66af764f36925cd33aee245` |
| data/raw/wayback/cg_20210318001239_NITVH4KJ.xlsx | 999,148 | `98519988cbfd0618d4c71c490d4b74455ac7d6dfe580cd6d39259c83c6917d13` |
| data/raw/wayback/cg_20210406180326_NOO2PLAS.xlsx | 998,950 | `672156cf6fe61dae579805b8339f7bab2ad3519d10644afd1ced6ccdbeb596ba` |
| data/raw/wayback/cg_20210623141602_REV3QRWM.xlsx | 1,154,250 | `14fea430bd3fe167820d927965eabb0959984dccea23f3041e0df472b0069018` |
| data/raw/wayback/cg_20211009213741_6KTNQ6JE.xlsx | 1,154,456 | `aada19f3164577359c1523301e4dda65bef462957d87834a5b137a3a2bc5068b` |
| data/raw/wayback/cg_20211014200724_L7OKT7TY.xlsx | 1,154,279 | `e976232769db187efe3904f54cc4801bd9fe475ae683c68af2d690365e105f0c` |
| data/raw/wayback/cg_20211208054926_6Z2E7SBA.xlsx | 1,154,683 | `f48c70eaa45d050d5139852181cdd9319691338e89aa0b268596a641a43ea743` |
| data/raw/wayback/cg_20220111210239_GH6DJBLO.xlsx | 1,154,153 | `d65c9554ac53e3dd58ddcd2c85dd247c876a48cff7c14a1147abd415cf60c612` |
| data/raw/wayback/cg_20220209054045_PCWSZMYI.xlsx | 1,156,808 | `b459517ee457688c04968f7608df66a2308dbde309c2cf3166ba9c050fa7501b` |
| data/raw/wayback/cg_20220322110339_2HHMCFIF.xlsx | 1,157,168 | `b767cd7102eae79dcc564ecca59cb4259e31fe2b6738d9f4290ce13c62d40ea8` |
| data/raw/wayback/cg_20220412182326_UYXCC73N.xlsx | 1,156,989 | `f131f1d578913b90e7768bb717b8b83815b9e5147abb69d700cd810676246f81` |
| data/raw/wayback/cg_20220510163217_KK3C3PLJ.xlsx | 1,156,958 | `517530129f1273d4d6a0519bcf8f946622a66fc65ed961d68ffe8383d7e5431f` |
| data/raw/wayback/cg_20220625010813_4TX4DE7R.xlsx | 1,158,261 | `dd9e73eaf38c6a9da1ffe308b251a9a0dfeb3f3d85dbb20af8511d9151f4f9bf` |
| data/raw/wayback/cg_20220809222733_TEOL2P7X.xlsx | 1,156,149 | `fd03f9290714066b8f0c966ba60c59ada30907f94407701112afef37612b9cd9` |
| data/raw/wayback/cg_20220908144321_5DMPY7ET.xlsx | 1,157,733 | `41651e2250be9031da25ea67a57af1d2add1f63c954dc59adad14de78cbab687` |
| data/raw/wayback/cg_20221013162734_OPFDI5PB.xlsx | 1,158,109 | `66eb91451cf78c2919017b9039da8061b532fd5baaa0e9021066911f2d560002` |
| data/raw/wayback/cg_20221109193211_E4QLJKWV.xlsx | 1,133,855 | `8728f537f0cd5fa89d13b91fa81746410c7963fd6f7b8c2cf987a77d392de060` |
| data/raw/wayback/cg_20230111221724_4AJNOW3D.xlsx | 1,132,850 | `abd6c8a87949e1d3ec589872515d6b36fa54d6dcbaf58df097c2a024b5a276d3` |
| data/raw/wayback/cg_20230321122743_ZGAG6BII.xlsx | 1,133,030 | `cf2ebb1b363ac0c27309130560bdf661c0f57f2a8f6a7e2bcb136e726c46e747` |
| data/raw/wayback/cg_20230510143148_O3BQLSQI.xlsx | 1,149,146 | `e22ba13cc8d3abdbc760f64d9f487fd9a9b57ddea3adf4da154830518cd2e691` |
| data/raw/wayback/cg_20230608022723_PUQWD45H.xlsx | 1,149,096 | `c554374486b2715818288059eedb722cdd495505c853376e8f94bb0c2860445d` |
| data/raw/wayback/cg_20230711184914_7KRMSR6H.xlsx | 1,150,357 | `69a94ca7ebfd4e5029d8a4fc7667807186fe721180a4a583ad2347ccf865c279` |
| data/raw/wayback/cg_20230912163248_UAA5BTEI.xlsx | 1,149,610 | `81e322595cca7c2df7fc1ecd794c4032463e5883d5161a03650c6722f2014de2` |
| data/raw/wayback/cg_20231213175605_LWXVHCHD.xlsx | 1,148,605 | `f14d9a1eeb242d71e290d3458137e5861cad3f3dd77578e4c8e2aed126dd31c0` |
| data/raw/wayback/cg_20240110213529_QE7T7DFZ.xlsx | 1,145,894 | `32ea9d6ce97f9c10bfbc51f1c112f76b0f06237111ed090e0569a5cedf55daed` |
| data/raw/wayback/cg_20240926192337_VP2BU6MQ.xlsx | 1,835,492 | `a6c3ac1fbfd1eda2ba946a912e0f3259d55605ed0d011f67775a2859daea926a` |
| data/raw/wayback/cg_20241009153015_ZDGTBP4A.xlsx | 1,797,356 | `694a70ea61c129c3e85c95e6264c2450e8c2c8ac1b038b23d09f1f96c059bda2` |
| data/raw/wayback/cg_20241127183118_YAIULV3N.xlsx | 1,798,158 | `8aab0f62f88ba5a659dc48e3cd17d0837bb84efa845aa0529611437d574f87fe` |
| data/raw/wayback/cg_20241212103623_V76TPD6F.xlsx | 1,797,255 | `2d2b66b942fc5778b7dfa8c52a1bc0513cc962a63eede0a271a7303896f7a28d` |
| data/raw/wayback/cg_20250202222550_AHIFJWIB.xlsx | 1,795,612 | `2522024ca7fa6950575f1f81ac09b5ff936edc08fa258fb6e457f97c33577e94` |
| data/raw/wayback/cg_20250222144756_KZJG4ND6.xlsx | 1,799,318 | `51a1842285d6b68427f269beb1c43857b4f3fbf4cfea64a5ff505e24a584fc7a` |
| data/raw/wayback/cg_20250318101156_25QHIOVB.xlsx | 1,799,024 | `bf92073a21385a4a19786f865f0d9ece791872e201a38103ecc6360b61b12b56` |
| data/raw/wayback/cg_20250421081002_44RF5GQY.xls | 61,594 | `506dcab6f5dc8e3286da1a78c13698bb9744857cd11f259c3a42b45356284a3d` |
| data/raw/wayback/cg_20250510032424_53UMKSER.xlsx | 1,799,212 | `95ccddcf7d8e847e0c0686ed1671ab837687e9daf9c03f5bae760a2f71d2ebed` |
| data/raw/wayback/cg_20250804134512_ATNZZUHQ.xlsx | 1,800,625 | `03097493aea7673679104d94100ded3e2174f55fdefa84af69c485b1ea9bb56b` |
| data/raw/wayback/cg_20250818121003_3ZZ5PNB6.xlsx | 1,800,480 | `bc410ecee93c6516d93388e05bbcf2e47a597be98e87831be68b38c3d77ae8b2` |
| data/raw/wayback/cg_20251012233536_XGDUX5TQ.xlsx | 1,779,695 | `fef0c9ce57cd70ad42d20f865eec003a2d2e9c99dfe4c622da7e309d8e46488d` |
| data/raw/wayback/cg_20260212153738_CPI52HFE.xlsx | 1,793,464 | `2a83ad8c298562c0a7627c532fa490cc7025c7fb3f5a496dfff5e1698474cf01` |
| data/raw/wayback/cg_20260407193602_6L66ZTAE.xlsx | 1,806,783 | `73f768d777099b516a509d56e73f5a9d21b7eee7fe9777b07933d87a31fdcd97` |
| data/raw/wayback/cg_20260709090841_WWESLQDI.xlsx | 1,808,182 | `7030693a771246b6a75432c25c59d0b12f647b598220167270d16fdd1cde73ef` |
| data/raw/wayback/cg_20261005033530_RQGEYLBT.xlsx | 1,809,772 | `0d64f5349314dcf435a2b88e940fcbae4418c61ba9ce83cdc993a8d98c36c425` |
| data/raw/wayback/cdx_chart_gallery.json | 13,838 | `64398da2ecdab97fb463f0668170cfeadec9693b641b4b79c6b90c64340e64ad` |
| data/releases.json | 27,260 | `5fe48375cc2d29f338b2133ed1faad8881a3c75fe898f43aa5bc177016291928` |
| data/raw/spot/RWTCm.xls | 55,808 | `6f2992d2414b8ba1ec045ba631bb66900fe2f8ae25dab6ed5b2eb2b09011b860` |
| data/raw/spot/RNGWHHDm.xls | 49,664 | `0426d2d6a14ab697aaa8582f696611f883e12af986bc0194021700f9e451ba28` |
| data/pdf_levels.json | 1,087 | `2996d5c0b2e9f1708af13a2187f8deab7f40bbacb32abaae9397eb6f827caf3f` |
| data/known_good_rows.json | 695 | `aaee60d916f0246b1c616621d160646050c0136abf485c949e2a26b02cf8dbbf` |
| PLAN.md | 8,622 | `fa986c17b07dda016a902984188d8467f2b795a0e3b9ed3d4d31b5f4fdee9871` |
| data/plan_seal.json | 241 | `592577bc81d240ee6197320b00e13ba341a481b8561cb2cb9bbaa40fdfed5199` |

## Code

The desk's own scripts, byte for byte, under code/. They run in this order: code/steo_tick.py --offline. The same files are in the public repository under code/steo/.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

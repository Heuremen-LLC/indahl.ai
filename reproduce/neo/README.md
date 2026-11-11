# NEO reproduce kit

Heuremen LLC · https://indahl.ai/neo · https://indahl.ai/reproduce

This kit recomputes the NEO headline number and its outcome label with the desk's own code, from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later and nothing else. It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `af9e650b727b5e763ee28e91326c4cb76c7a9c7687ef76d7b82df626b403ab31`.

## What it reproduces

The headline as the live feed https://indahl.ai/neo/live.json served it at the feed stamp 2026-11-11T11:55:52Z, read by us at 2026-11-11T11:56:17Z. The feed bytes had sha256 `4cd70557e17dfffa9721878e9744b3146ea13b9e345b510878fd23cd04262b6c`.

- number: 464 of 478
- value: 0.9707
- interval: 0.9514 to 0.9825
- outcome: BELOW

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. JPL states no reuse licence for its Solar System Dynamics APIs, and the archived copies are served under the Internet Archive terms of use, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- The current JPL record, https://ssd-api.jpl.nasa.gov/cad.api with the query neo_tick.py builds (data/raw/cad_current.json, written at each run).
- Internet Archive copies of earlier Close-Approach answers: the capture list at https://web.archive.org/cdx/search/cdx?url=ssd-api.jpl.nasa.gov/cad.api*&from=2024 (stored as data/raw/wayback/cdx_cad_api.json), each capture fetched from web.archive.org by its timestamp and address.
- Our own dated copies of the JPL record (data/snapshots/cad_*.json.gz), each with its address and read time inside.
- The Close-Approach answers for renamed or numbered objects the desk keeps in data/cache/des_*.json, https://ssd-api.jpl.nasa.gov/cad.api?des=OBJECT with the date window neo_tick.py builds (line 175).

## Sources and their terms

As the NEO data pack lists them. Credit each source when you use its values.

- NASA/JPL SBDB Close-Approach Data API, https://ssd-api.jpl.nasa.gov/doc/cad.html. JPL SSD API, no reuse licence stated, fair use policy https://ssd-api.jpl.nasa.gov/doc/index.php.
- NASA/JPL SBDB API, https://ssd-api.jpl.nasa.gov/doc/sbdb.html. JPL SSD API, no reuse licence stated.
- Internet Archive Wayback Machine copies of the Close-Approach service, https://web.archive.org/. Internet Archive terms of use, https://archive.org/about/terms.php.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/raw/wayback/cad_20240126214516_d897c2fb.json | 101 | `850637754eb225cd5264f2fadbd7fb18da3b0955c362098ed70022a771116195` |
| data/raw/wayback/cad_20240209054243_4af6cb8a.json | 4,814,330 | `c2e44d8417680539db5c27b3a2e183808d5140bedb12ba77564b0d84995c54ac` |
| data/raw/wayback/cad_20240209054426_4efadd98.json | 15,055 | `3a2b105c1418bde56cc2e65d2fdd42a877559d54deb73d28f0337f49c041a0d8` |
| data/raw/wayback/cad_20240405011428_4661896f.json | 8,693 | `acd33b7c00e8b65b8fc0ae90058167dc41d2b0d52c54820e5b0d03d5e979988d` |
| data/raw/wayback/cad_20240405011428_d897c2fb.json | 101 | `16e6c5114ac4bcf5c94900f2a284b01cd06242312b35c370aeaafd90ef4cba5c` |
| data/raw/wayback/cad_20240519035817_8c1d1a71.json | 6,515 | `6c50c9ec643ef409a6f9f60ce972c5017596344c7ab9a4ee4018475eafc96c5f` |
| data/raw/wayback/cad_20240527152918_a01bd7b3.json | 680,880 | `f6a16b97d4edab4fc35e2775dedea35b678404aee9b5e688d51e64e11c11f150` |
| data/raw/wayback/cad_20240527164858_8c1d1a71.json | 4,586 | `51372ea612f52e40a35d3e528a69de2249a79d9f9e957517c557eccdf61f2833` |
| data/raw/wayback/cad_20240607052331_aa63a8ef.json | 90 | `504f999474409eabf31c2dc2d424a8254aeae1825df66005e67a162dea61ff06` |
| data/raw/wayback/cad_20240608081724_4154e813.json | 5,089 | `e3b2b04aaa5727bfdc44bafa15a2dc86c97835f130fc64ef69c1a660a7d32a68` |
| data/raw/wayback/cad_20240611091251_06a7ffd6.json | 1,002,736 | `a0c9f30106087f73142456cd8606c055701e6410518bba4a9dcfa8d000a1e4a6` |
| data/raw/wayback/cad_20240615200612_8c1d1a71.json | 5,808 | `d4c0898a60b18b8084eb397eca693e02291ca0ddde02212e607107d6cadb1959` |
| data/raw/wayback/cad_20240705105844_2fb61cdb.json | 104 | `adfbd66451afced0ffcd0a1e78e88e32a21f2d140332ffb9179caaa7b4cb116c` |
| data/raw/wayback/cad_20240705110946_a23fa9a7.json | 104 | `4049cb05a859637a30fa833df38bffda861fbc5e1a60a321e36812a33cdc8596` |
| data/raw/wayback/cad_20240817135947_d897c2fb.json | 101 | `eb318e676f782b87ee282e0f13d74ddd15cf8a19a494b80f83a9a02c6099dcd3` |
| data/raw/wayback/cad_20240904113204_d897c2fb.json | 101 | `01d5c2294d444b708a80cd44c820e0e93b2db240d137caae33e6c0bfe29cdee6` |
| data/raw/wayback/cad_20240923052744_d897c2fb.json | 101 | `7ca9a90767f30b9efc4d8a69c88918e50574199aa922d514b62d56142041a663` |
| data/raw/wayback/cad_20241004112004_a01bd7b3.json | 734,708 | `3d707cca1579db562a29690b9db415bff4722c5c319fc70780027e37749edfc0` |
| data/raw/wayback/cad_20241004124633_8c1d1a71.json | 10,375 | `cc08aa784f47b64fc802ea2643ce63c0b9c54c035c567af8dbce9339ed868af6` |
| data/raw/wayback/cad_20241129193832_486bd186.json | 17,765 | `b6d221ff9f565ed7747c36a068d153428fad162519d432d80fa6e843057cda3d` |
| data/raw/wayback/cad_20241129193843_f668a342.json | 2,483 | `9c18191407e5624c5f1f964e1e96573b708ed170171c29b15aa21a2727e565b3` |
| data/raw/wayback/cad_20250101175107_d897c2fb.json | 101 | `fe0114a16a9d7c0720e0482fbf2e57784e3f501cb5dc18962ada9da8679802a1` |
| data/raw/wayback/cad_20250125144053_7dbfa30e.json | 1,460 | `732c574c34bba741f7d9de8e692c557fa6432bf770b018ea23693d556da50e95` |
| data/raw/wayback/cad_20250131135535_d897c2fb.json | 101 | `7bdd309fcc290db41e5a411606bcf1899569ede081e0369cbc09953590ba7989` |
| data/raw/wayback/cad_20250220192850_d897c2fb.json | 101 | `682f4cccf6f0ec8c63a9583d5a8767616da68039c29071da623ca42c66177a62` |
| data/raw/wayback/cad_20250226064441_4661896f.json | 10,845 | `b68b07b6c28a6a8c1c9f2d3516470aa77f20fe4c5a9ed9ba9ed688aeb7a2146e` |
| data/raw/wayback/cad_20250226064441_d897c2fb.json | 101 | `b8a1fdb7686c5edf52d08e631f55f5e259f62f3b26d7827cd9a1ed4901234970` |
| data/raw/wayback/cad_20250227121917_d897c2fb.json | 101 | `d24f1bc2f4fe0e8475f4b93ffa96ed4e02d7f5f2b78c494363ac0c592b6ef9e3` |
| data/raw/wayback/cad_20250512114055_a01bd7b3.json | 876,891 | `467faf442d4099234f41297c44b8726a9f3ff8d1686cbbcb3837819c520a89c2` |
| data/raw/wayback/cad_20250528162114_8c1d1a71.json | 6,884 | `dbd2f5d20ec59ece852e9bb4be9ca4a65d223d2a406e13c90b7fde099bbfaa16` |
| data/raw/wayback/cad_20250528223000_cf9fd4e4.json | 301,960 | `18dacfc154dc08469ef9d8c653dc6aa614b0a50e0415dea9bed516595101886e` |
| data/raw/wayback/cad_20250620233311_8c1d1a71.json | 3,528 | `b599f7602d7b158c0fa8671c96419e5f567bd657d1bbb048142f311520d5b5ad` |
| data/raw/wayback/cad_20250719132330_d897c2fb.json | 101 | `cb96028aab7437ac3798427fd0cac6b26cdfabf30ef76b4b6095809da0a58249` |
| data/raw/wayback/cad_20251112073955_4661896f.json | 8,251 | `02f784cd3e1c9553ae2feb10deb32c883f741a72f8fd4287e0f0c4671c8e8ae7` |
| data/raw/wayback/cad_20251112073955_d897c2fb.json | 101 | `56de117577f8910a34fd7db6716d33e5042fa77eb725169f215d8ecf2a59f904` |
| data/raw/wayback/cad_20251210160735_d897c2fb.json | 101 | `e616197ba7143a9f93009fb9433dc67fa7076e9ee5135a7d46feb74e18ba07dc` |
| data/raw/wayback/cad_20251211140947_d897c2fb.json | 101 | `e04a129288592cffa7ce27d4a13662690d04f59a939340cee268e439e646a097` |
| data/raw/wayback/cad_20251212151420_d897c2fb.json | 101 | `3a8cbf53a40ed7d51925168f5bb6c37fe2f4847f37d49f83b7eda92a49137292` |
| data/raw/wayback/cad_20251212151421_4661896f.json | 7,377 | `dedcb7685edd1cc380f3a9fd9fa9af2f56b9fa0bd8bf5a5349b2392eb8526083` |
| data/raw/wayback/cad_20251215213238_d897c2fb.json | 101 | `16e6c5114ac4bcf5c94900f2a284b01cd06242312b35c370aeaafd90ef4cba5c` |
| data/raw/wayback/cad_20251215213239_4661896f.json | 8,665 | `e4eb6f1a7995f5b95d02095d7317c8a8155dbe13019647374fcaa89884a4d9a1` |
| data/raw/wayback/cad_20260128053553_8c1d1a71.json | 8,078 | `fdc399894011bdf46f98babc398104222cc8312305b67089895842a73e1bf55a` |
| data/raw/wayback/cad_20260129112147_8c1d1a71.json | 8,078 | `1371ce5b735c7dbec47129ab3e9d65d2f7bcc5a8217a23ad70c17dd81752621e` |
| data/raw/wayback/cad_20260302131928_8c1d1a71.json | 9,505 | `0e84482157f04f118bf31140c44c668b140d45a48dfa6c7d653dfa5ee22fe092` |
| data/raw/wayback/cad_20260323163925_428ca0cb.json | 6,690 | `0df42fc2fa76ac616bff8762fd48f224e14786f55029d06e7c242af44ad4aae2` |
| data/raw/wayback/cad_20260325141742_ba792c84.json | 6,160 | `22742a28068567f0b36305f68558bf59a680cd7d6e5bc23412f1bee55bf42d29` |
| data/raw/wayback/cad_20260516161327_d897c2fb.json | 101 | `9c516e6b9de90cd54c7f02a61427db6708c536697cc9c0435b3a84c92c99e242` |
| data/raw/wayback/cad_20260611055315_8c1d1a71.json | 3,880 | `760baa8920e6fe967478ea57d0802073ce4c592d9687fb3c820377b24f65b156` |
| data/raw/wayback/cad_20260709220123_4661896f.json | 7,807 | `23d9f504a618d92d5ab0194e84a8c3cd62f19a46924efaf4eb0c918b8b3e7188` |
| data/raw/wayback/cad_20260709220123_d897c2fb.json | 101 | `dcda4ab30c607fa7915d09123c2ba037980e240a721ea7b5085908a034a3c6ba` |
| data/raw/wayback/cad_20260808165614_8c1d1a71.json | 5,990 | `ac1f24cbc3401166531ea5a13553625a676f7c40cdc6b23f01e11916e957c8df` |
| data/raw/wayback/cad_20260908000109_1bd41e2f.json | 7,591 | `441f65c1457588bbd0c2a14f1ffaca744772afaa23fa9351a3a6ff4c21a7b8df` |
| data/raw/wayback/cad_20260911233956_8dde4fb9.json | 1,977 | `07381e9f646aef1cd273733a49f0a6255d6031522cba1a63b80e5f1a44996619` |
| data/raw/wayback/cad_20260912100134_8dde4fb9.json | 1,978 | `5fa1d5d101905aea75da623a666720eb77d07075adeab0f03ae1df8f4ef8c732` |
| data/raw/wayback/cad_20260912124823_8dde4fb9.json | 1,978 | `5fa1d5d101905aea75da623a666720eb77d07075adeab0f03ae1df8f4ef8c732` |
| data/raw/wayback/cad_20260913062336_8dde4fb9.json | 1,972 | `40b0a6212131a456d8845ff99cb46856a42b4bf987cdc81323ab3f85ee12e595` |
| data/raw/wayback/cad_20260915182921_43bfc757.json | 383 | `aa8b628dbcc2b1027315ea9a286293ade2a03d17a81710e5d10892fc5fcba0eb` |
| data/raw/wayback/cad_20260916015605_8dde4fb9.json | 1,977 | `a7cd3741cdcc4d685c90398337536b0a9f757cf3684aee2909307733bae5ac6c` |
| data/raw/wayback/cad_20260917061514_8dde4fb9.json | 1,976 | `0275d173a5f2e9e00521576de8ede252ea56f0176fd144f6d4ea3b6596bcc6be` |
| data/raw/wayback/cad_20260919053034_9a4041cc.json | 9,426 | `567726df8083e95ae36931e2f65f9bcadd7555faa47c607e21a38168ae60c68a` |
| data/raw/wayback/cad_20260919053043_8c1d1a71.json | 7,734 | `e4fc4e1351cc3f2011c83cce836d8ef9064adf5e622537b4e231bff67906c1bc` |
| data/raw/wayback/cad_20260919121514_8dde4fb9.json | 1,966 | `ecb249d1f36a8bccaed52b265fe7f6f916ad876563c5686475748015e84b60af` |
| data/raw/wayback/cad_20260921123613_8dde4fb9.json | 1,980 | `36bc74dcfedf763ddd22e77f761750f05e801ea13611fc49735462baef8101da` |
| data/raw/wayback/cad_20260921173534_48445508.json | 11,501 | `552e1d679cd7247c8879fb319fc7a8f4b43e4ab35254775e75fc93657801a041` |
| data/raw/wayback/cad_20260922221139_6ba877f6.json | 9,646 | `885daefa7443a6c87f274ad3b8670ebace35e7cc76207e3cb2eaf200ccf359ed` |
| data/raw/wayback/cad_20260926132620_8dde4fb9.json | 1,964 | `6188cac5fa8ab4657439017fff08534d49d5f644f0c3c8b8b319174ef6dbf4e2` |
| data/raw/wayback/cad_20260928132629_8dde4fb9.json | 1,968 | `0a7bff4da2af6ac81eb61f4f9995b6bb3f6ce50b755f3849341a34ea539c120a` |
| data/raw/wayback/cad_20261003164156_e152c1a3.json | 8,176 | `09b10d6166f1244f2507de7aafaa668d95e33ceaeeb99b902c019ecd60c9fb2d` |
| data/raw/wayback/cad_20261004083927_a00bfac0.json | 5,878 | `cc9f8b170a2ebf867f2ee9386fc6330c978a76e254213ec25ddb14ea2cc47442` |
| data/raw/wayback/cad_20261004175937_d3bf0975.json | 7,564 | `39b89d658980712d1a594558402413cc70cc7a7c6dd6e479b58a4802cb8fe922` |
| data/raw/wayback/cad_20261004222622_a00bfac0.json | 6,273 | `b33daad03a9614cf1d2c1487f3aff211683400d8a952264a287cceb7ee3c9af6` |
| data/raw/wayback/cad_20261005102829_a00bfac0.json | 7,053 | `d724780efce3345072563bdc88a56bc7c18e29fd48ee3ba526e7b123a85ceb7f` |
| data/raw/wayback/cad_20261006000319_1048f5dc.json | 90 | `6800f125e2bc1dc1932cece4e4121caa1327374a25d8a1959f65524b33ce6f3c` |
| data/raw/wayback/cad_20261006013624_a00bfac0.json | 7,253 | `85c5bff32bf91601966505a0e76feb857eda8514bd536412117ba7b96ee9f0d7` |
| data/raw/wayback/cad_20261006163942_a00bfac0.json | 8,045 | `baaa682bad1ccd59503b163889da7d85fa894b68f1b8dbe2d746baae220171b3` |
| data/raw/wayback/cad_20261007055235_a00bfac0.json | 9,023 | `db147e04d25e0421a45b7e0c3c24964a4b4fa51a5ead2399f0b3bdeafa39bd18` |
| data/raw/wayback/cad_20261007185901_a00bfac0.json | 9,606 | `f4b564c18bb6021c68ca01746674c53b93048ae2d2a1d81641d77ca285281cee` |
| data/raw/wayback/cad_20261008073230_bf64932e.json | 45,886 | `45f67513e5bd6826d165c2f1dd810a020196db38699c69ed73f2606e6d182671` |
| data/raw/wayback/cad_20261012150147_8c1d1a71.json | 8,275 | `f826cb8263bb5a41f48624b283bc559ffb14f7a080122b2cedf91db9f306a456` |
| data/raw/wayback/cad_20261014030310_58f24c76.json | 3,758 | `6fc3c8d8c05df8aecab117fc89850734cc84cbc76f9f2d58cd012155bfe3daf9` |
| data/raw/wayback/cad_20261017075410_107ccb34.json | 90 | `6800f125e2bc1dc1932cece4e4121caa1327374a25d8a1959f65524b33ce6f3c` |
| data/raw/wayback/cad_20261017075410_1d6f2bae.json | 90 | `cf49b63b12d003ba6203007f81e2913d859b52af87c72a15b5d691fddd5cc6be` |
| data/raw/wayback/cad_20261029072822_58f24c76.json | 7,842 | `26d186510729b0a2888b9cb64462968dc9dea6b6064cbef4134a90df98bf767a` |
| data/raw/wayback/cdx_cad_api.json | 10,078 | `748fe45916ac58ba794b8e75872fb25370145ec388643d3cac7e02a55f676f3f` |
| data/snapshots/cad_20261110T111023Z.json.gz | 73,036 | `4264229743c1d209da0aab124a76b2333bca22988b0e69fe929bab5babdce5fd` |
| data/snapshots/cad_20261110T204224Z.json.gz | 73,346 | `25ce640b3ac449f961ad01d3e02e1a9f7cc26d54cbb9faa97ce94bc1998ff52b` |
| data/snapshots/cad_20261111T033236Z.json.gz | 72,753 | `5f42970dd8ee9f788b5db392461695bd5092c2acaba55bce64f26d04c86d2bee` |
| data/snapshots/cad_20261111T095331Z.json.gz | 73,203 | `f1d43e9bac48aef3e61cc9b98a262dc8149b17a04281565388338e5ada4e9cd6` |
| data/raw/cad_current.json | 3,563,135 | `50f05e05d1a8eb5256a2fc8871aa0f3d4be7cedffe7da44ad9fe49ada1c5248e` |
| data/cache/des_1998_SH2_2460918.json | 400 | `2c21e4cf49fd81d826f189cf2f793fd4730ea1850174de1d206df7d5ef853b43` |
| data/cache/des_2003_AY2_2460849.json | 402 | `5db6d168f0ad979a008b2ed8103e168dc3ee2f8e742e62a5a7fc50ecac907ee7` |
| data/cache/des_2004_MO3_2461058.json | 403 | `537114bf638641c55b9e0880f033779a7dd53c4be4e8ea87e1f1a243b120db17` |
| data/cache/des_2005_VO5_2460868.json | 403 | `8935d78b8aa6754f26d2643291ee66dc750cd266f8bdc6f2f986cf21b18e21fc` |
| data/cache/des_2007_DB61_2461093.json | 403 | `6fe204cadaac4e3af7ec60fc5527b727457159cfd046c8e4c85eb0a125bcd358` |
| data/cache/des_2007_SQ6_2460771.json | 403 | `fa8cfd9394112d407be6ff482e775dfefada297c079a3d841465df3a730af4ee` |
| data/cache/des_2009_FF_2460930.json | 403 | `553f2e1ac6877cb07cc4766eddc84e40dbd9a34b6b20d2c48440aedd9827bc80` |
| data/cache/des_2011_AM24_2460518.json | 403 | `5c42342828ea150dbfafa8f36c914ee23e2819f1162c55154d435fe46c3d103d` |
| data/cache/des_2011_HJ7_2460808.json | 403 | `45f17074e3638fc0635783e523b9d554402c2287b3b264faae115a590647db7b` |
| data/cache/des_2012_YD7_2461355.json | 400 | `615335900d311b7f9d7b70392a99366a248c0a9db32cfbc73d299cea90b49dc7` |
| data/cache/des_2013_FW13_2460572.json | 403 | `7bf6e3f10d5d7298105c5077e2bdd8166c8bbf698f53b3686ebcf53cf9cfe719` |
| data/cache/des_2014_FP47_2460591.json | 402 | `8e646d09324bbacf01b2c9818ca9aedd0339371fd3673ded94f9df28de1c3ea4` |
| data/cache/des_2015_FM34_2460382.json | 402 | `838992d2189e49b65008c9c5f3f77ff286271319f0f612053fddfe685c8b1381` |
| data/cache/des_2015_VH65_2461355.json | 404 | `e15948ec00769883b0f6a794ca36e219322f70b1493b879a6f753a85b54ce7e6` |
| data/cache/des_2020_BP13_2460410.json | 401 | `a6c2516e8abd30bd6ad0f608fac7731027ebf52a231f6fccf757d43569c1b8f7` |
| data/cache/des_2020_XR_2460649.json | 402 | `6eb172119acbe114d80bd7c712b61151c6b3a544c6374601ffeec12a229eb7f3` |
| data/cache/des_2022_FR3_2460767.json | 402 | `d17e5e69fe4708b8a0a8c169cbdfee770a643d0ca54069607b5fab0d3f5125dc` |
| data/cache/des_2023_VF3_2461356.json | 401 | `e7176d1d4b445207fc6edb8ffdce417d27f688ff828a9951a47329303dbed1b0` |
| data/cache/des_2024_CR9_2460473.json | 403 | `07ab680b31cdf6721d75727f2f04f66fcf5810f3fe88626243860341a19d1d11` |
| data/cache/des_2026_VK5_2461355.json | 403 | `efa5c92e51b196c73e4e7d5edfb7e0d26bee6664ce66f9eff67b48172d8ff286` |
| data/cache/des_2026_VL8_2461356.json | 403 | `13c95921270c06ccbcb02a4219ae9b81cf9995003e3f0e4a1b5b049dd9379a3e` |
| data/cache/des_2026_VN4_2461356.json | 403 | `548c3b11c7b33fd78401b749548118fab683f9cbe2eaac5cccbdef51752b0fa0` |
| data/cache/des_2026_VO8_2461356.json | 403 | `a4ba275ed6732d6b9f517ee61abba5df992874d35782053e0bc8e5183d800bc7` |
| data/known_good_rows.json | 546 | `4162db426c14edb02ecee30dfb7ab00c5b264958eea5e4465f5b39c493e2fcb1` |
| data/plan_seal.json | 241 | `96a924bf3215fcc716f5c763f29f35623a2e7eaec117c1069a3f689d39916900` |
| PLAN.md | 10,979 | `1a5714047dd33f4aaf83580ad0e57063c60b8be90883af3148aed79099917214` |
| data/neo_live.json | 33,969 | `4cd70557e17dfffa9721878e9744b3146ea13b9e345b510878fd23cd04262b6c` |

## Code

code/clock_run.py runs the desk's own scripts in code/, byte for byte, and changes the clock only. It runs neo_tick.py with --offline --no-sbdb and the clock pinned to the time the published run read (the generated field of data/neo_live.json), which the desk uses to tell a settled or passed row from an open one. The same files are in the public repository under code/neo/. Scripts that run: code/clock_run.py neo_tick.py data/neo_live.json --offline --no-sbdb.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

data/neo_live.json is read only for the time the published run read, which pins the clock. The run writes a fresh data/neo_live.json and the headline is read from that.

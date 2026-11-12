# Reproduce a desk headline

Heuremen LLC · https://indahl.ai/reproduce

Each folder recomputes one desk's headline number and outcome label with the desk's own code, offline. In each folder run `python3 run.py --check`.

reproduce_kits.py is the code that makes the kits and the release gate that reruns every kit before each release.

| Desk | Inputs | Expected output sha256 |
|---|---|---|
| [AILUMINATE](ailuminate/) | fetch and verify | `75252261f72159cfe6fe6ac1235a36d033769a95c57b19d985c4d55f09a5033c` |
| [AIRLINE](airline/) | included | `f32a4e777ddcb767a5d232aacfb62cb2fdaa988637a2dba251a24714e2230e58` |
| [AIRQ](airq/) | fetch and verify | `a105a4e665f0c2eef3ebd8bd394bae4a764c41aefc25cd5db23ad288ac8a3aed` |
| [CADENCE](cadence/) | included | `c02b58f3a52bf8c0d5edd6fec83ad5b45b7ab10e6127dc2cb3a15a0495f8d1c0` |
| [CAMPUS](campus/) | fetch and verify | `e5f3789d15dfc9987b79a37085319a0f91401da5d9a8a46ef2b2d0b85944f9b8` |
| [CENSUS](census/) | included | `43f7368f318b9aef23d0af04771a2eb2dcdbc8eb4e81455405b5762fdccc2f1b` |
| [CHANGE](change/) | fetch and verify | `4aaa2bbf381335f18c0ca16e247bd5122f9ecb01bbe3c93ba392fac653a01749` |
| [CONE](cone/) | included | `3a3cc8410a5f9d20204e42be09f230296d0a5d27a7f22182b340590551e02201` |
| [CREDIT](credit/) | included | `c4bbbebe5e465479ebda2c9119dd058d7ef97807e75f5c08009462c3ff5bf5ff` |
| [FEDSEP](fedsep/) | included | `c6978bc2ff30064c0bfe7edb79752a04b912fb7edaf9ed88a8f1bb9571bea7c0` |
| [FLU](flu/) | included | `415e3325a57de347e6374fe695bdea772cfdaaeaa4a02ca704ac72e2428c9a8d` |
| [HFSIZE](hfsize/) | fetch and verify | `b7864ec3b1b652803e643594f90ff123fc5a681fabb7a029b1f2c25c67cb85ad` |
| [HPT](hpt/) | included | `dac673f0c2d2251f1f72fbd267e6dd77d98bf8effd0ae09d0deb6bf704e77b56` |
| [LAUNCH](launch/) | fetch and verify | `f91d5f1d0e8633f38789842658885b2448ca3376ff7eeeb0e512841cc7c41ba4` |
| [LINKROT](linkrot/) | included | `a68001ac446bea6ff9593871ffc5973bdd8316e9bf9c737be39e7873f3fd5858` |
| [NEO](neo/) | fetch and verify | `ebe615b627d6afc89051f9b1ca060c2ac432eb630f8fdf9ddd13fb9cfae34a8f` |
| [PKGINSTALL](pkginstall/) | fetch and verify | `50cd23a1327ebbdd6bf56db81e4b2200c5bb37460a70de0ef4d75659518d6baa` |
| [PKGLICENSE](pkglicense/) | fetch and verify | `46ab84f4bef32aaa4d529cf50cf780da6697bf1850dab424d7115153b5766933` |
| [QUAKE](quake/) | included | `ad1d0ddddf72554eb2d2460f51f4fa3860269cc68e6ddeb4f991a858b3090649` |
| [SEASONAL](seasonal/) | included | `bc5c500339489235e7034dd1ab3df2971672bbb776d8c74808320075ada0d87f` |
| [SECRECORDS](secrecords/) | fetch and verify | `73ae7a2326190eb4a2b8fc9537d11223f609814674fc53b60dcd7e77b6a85cfa` |
| [SOLAR](solar/) | fetch and verify | `815650f7fe3e788b8c763be25e95f09e136e9c376d27b5d7209a214f9d26bdf9` |
| [STEO](steo/) | included | `62582754f487e4bbb247ecb496530bfe0811c434a8f16222e973664ae554574d` |
| [SUPPORT](support/) | fetch and verify | `7b50da5963d4ea65bfbfd163b110d6ef3e64f5a9c2ba3bcd3bb25958f1033c95` |
| [TORNADO](tornado/) | fetch and verify | `5ff5d0988b98d09801df2459fa0deb6eb6639eaa2ad0ff222460b5408c325930` |
| [TRIALS](trials/) | included | `1b18b25916c0caf76c90a0f35d185455a85e83d7411d31301aaf52f22e752213` |
| [WATER](water/) | included | `9fa82deee3bf63d3989a180ae7ff29fed0d2d341b59a49bcbe5a37f4640537cf` |
| [WEIGHTS](weights/) | fetch and verify | `1cfd14205d4d8704128200f6ad4cc73bcd3598bd874decb3f214b8068adb2a4f` |

## Desks without a kit

- CADA: The desk asks public DNS resolvers live whether they block fresh abuse listings. A resolver answer cannot be replayed.
- HOSTS: The headline is the count at the newest poll of OpenRouter, a live service whose answers cannot be replayed, and its flag test reads the 24 hours before the poll by the clock. We keep each poll as parsed rows, not as the service's answers.
- REVISE: The headline compares the first BLS estimate with the most recent value, read from the BLS flat file on each run. The BLS table of first, second and third estimates is kept with its sha256. Until 10 Nov 2026 the flat file was not kept, so the published values cannot be replayed. From the next read on, each version of the flat file is kept by its sha256, and the start of its sha256 is in the feed.
- TAPE: The headline is a clock, the time since the newest entry was chained.
- TIME: The desk measures public time servers live against a GPS-disciplined clock. A time reading cannot be replayed.
- UPTIME: The desk probes vendor services and their status pages live from two networks. A probe answer cannot be replayed.

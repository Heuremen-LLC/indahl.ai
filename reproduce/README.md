# Reproduce a desk headline

Heuremen LLC · https://indahl.ai/reproduce

Each folder recomputes one desk's headline number and outcome label with the desk's own code, offline. In each folder run `python3 run.py --check`.

reproduce_kits.py is the code that makes the kits and the release gate that reruns every kit before each release.

| Desk | Inputs | Expected output sha256 |
|---|---|---|
| [AILUMINATE](ailuminate/) | fetch and verify | `c8b880287c02d1391439b93353357ceb7123096c42b965ae0d9a2aa35398b752` |
| [AIRLINE](airline/) | included | `f32a4e777ddcb767a5d232aacfb62cb2fdaa988637a2dba251a24714e2230e58` |
| [AIRQ](airq/) | fetch and verify | `a105a4e665f0c2eef3ebd8bd394bae4a764c41aefc25cd5db23ad288ac8a3aed` |
| [CADENCE](cadence/) | included | `bd1fa582abf223661c0665a91e2e38bef375cd629fa2b611f126480bb6be114a` |
| [CAMPUS](campus/) | fetch and verify | `e5f3789d15dfc9987b79a37085319a0f91401da5d9a8a46ef2b2d0b85944f9b8` |
| [CHANGE](change/) | fetch and verify | `4aaa2bbf381335f18c0ca16e247bd5122f9ecb01bbe3c93ba392fac653a01749` |
| [CONE](cone/) | included | `3a3cc8410a5f9d20204e42be09f230296d0a5d27a7f22182b340590551e02201` |
| [CREDIT](credit/) | included | `c4bbbebe5e465479ebda2c9119dd058d7ef97807e75f5c08009462c3ff5bf5ff` |
| [FEDSEP](fedsep/) | included | `680a854c4505ecb81bdc0636b200e87c996e7ee0b9ed1ac8b7d7dc322cb1492d` |
| [FLU](flu/) | included | `415e3325a57de347e6374fe695bdea772cfdaaeaa4a02ca704ac72e2428c9a8d` |
| [HFSIZE](hfsize/) | fetch and verify | `308cd3c6ee10384ebb7a7d0439a5415567248201d94eb7646b3e3a5aace37119` |
| [HPT](hpt/) | included | `dac673f0c2d2251f1f72fbd267e6dd77d98bf8effd0ae09d0deb6bf704e77b56` |
| [LAUNCH](launch/) | fetch and verify | `4458223a64af0f20788218f8ae587b981879eedfef44caadde985c17f5c61a38` |
| [LINKROT](linkrot/) | included | `466e6e2647e13ff7fd765b6b6debaad69f46bfc49084232ee60cc0735919aaf2` |
| [NEO](neo/) | fetch and verify | `85bd43d84b32db972d81ec7a61e50bdd00659eafdcf230a8766525c7f2afc7ce` |
| [PKGINSTALL](pkginstall/) | fetch and verify | `50cd23a1327ebbdd6bf56db81e4b2200c5bb37460a70de0ef4d75659518d6baa` |
| [PKGLICENSE](pkglicense/) | fetch and verify | `46ab84f4bef32aaa4d529cf50cf780da6697bf1850dab424d7115153b5766933` |
| [QUAKE](quake/) | included | `04c5991de0c9e183eaec21f81776d2391235f2dc1add25d889efa18f9d79794d` |
| [SEASONAL](seasonal/) | included | `bc5c500339489235e7034dd1ab3df2971672bbb776d8c74808320075ada0d87f` |
| [SECRECORDS](secrecords/) | fetch and verify | `143c8e7cbf29f81b88662acb49a55a7073e67f030acfe23a680720cd57ed878b` |
| [SOLAR](solar/) | fetch and verify | `336e3ae79281b594f30b1ad6497dcf7103702986d2f9ee016b672e787bd5fa9c` |
| [STEO](steo/) | included | `62582754f487e4bbb247ecb496530bfe0811c434a8f16222e973664ae554574d` |
| [SUPPORT](support/) | fetch and verify | `9fc34e209b7b6fbd8193eb2737e61f188a60a1193cfc1871060a384b73527817` |
| [TORNADO](tornado/) | fetch and verify | `5ff5d0988b98d09801df2459fa0deb6eb6639eaa2ad0ff222460b5408c325930` |
| [TRIALS](trials/) | included | `465d4475aaf21301d6efeaaf2a0c76e2e1f11b3d6cced0694da959dd1886c9d8` |
| [WATER](water/) | included | `9fa82deee3bf63d3989a180ae7ff29fed0d2d341b59a49bcbe5a37f4640537cf` |
| [WEIGHTS](weights/) | fetch and verify | `4c7210eb6fb63bf4497494951561cbe86b54f11a182c89eccfaaeaf4bdc8eaa8` |

## Desks without a kit

- CADA: The desk asks public DNS resolvers live whether they block fresh abuse listings. A resolver answer cannot be replayed.
- HOSTS: The headline is the count at the newest poll of OpenRouter, a live service whose answers cannot be replayed, and its flag test reads the 24 hours before the poll by the clock. We keep each poll as parsed rows, not as the service's answers.
- REVISE: The headline compares the first BLS estimate with the most recent value, read from the BLS flat file on each run. The BLS table of first, second and third estimates is kept with its sha256. Until 10 Nov 2026 the flat file was not kept, so the published values cannot be replayed. From the next read on, each version of the flat file is kept by its sha256, and the start of its sha256 is in the feed.
- TAPE: The headline is a clock, the time since the newest entry was chained.
- TIME: The desk measures public time servers live against a GPS-disciplined clock. A time reading cannot be replayed.
- UPTIME: The desk probes vendor services and their status pages live from two networks. A probe answer cannot be replayed.

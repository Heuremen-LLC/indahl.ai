import * as tl from 'tlock-js';
import { defaultChainOptions } from 'drand-client';
const HASH = '52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971';
function client(base) {
  const opts = { ...defaultChainOptions, chainVerificationParams: { chainHash: HASH, publicKey: tl.defaultChainInfo.public_key } };
  return new tl.HttpChainClient(new tl.HttpCachingChain(base + '/' + HASH, opts), opts, { userAgent: 'heuremen-vault' });
}
window.VAULT_TL = {
  encrypt: function (u8, round, base) { return tl.timelockEncrypt(round, tl.Buffer.from(u8), client(base)); },
  decrypt: function (text, base) { return tl.timelockDecrypt(text, client(base)).then(function (b) { return new Uint8Array(b); }); },
  roundAt: function (ms) { return tl.roundAt(ms, tl.defaultChainInfo); },
  roundTime: function (n) { return tl.roundTime(tl.defaultChainInfo, n); }
};

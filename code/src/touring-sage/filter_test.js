// replay: would the new gate have refused the touring seat's 9/5 recitals, and passed her real work?
const src = require('fs').readFileSync('index.js','utf8');
const a = src.indexOf('var SUMMARY_SHAPES = ['); const b = src.indexOf('function looksLikeSummary'); const c = src.indexOf('\n}\n', b);
eval(src.slice(a, c + 3).replace('var SUMMARY_SHAPES','globalThis.SUMMARY_SHAPES').replace('var PROMPT_FINGERPRINTS','globalThis.PROMPT_FINGERPRINTS').replace('function echoesPrompt','globalThis.echoesPrompt = function').replace('function looksLikeSummary','globalThis.looksLikeSummary = function'));
const cases = [
 ["It appears that you have provided a summary of two separate conversations between an AI and a user", true],
 ["In this response, I will address three aspects: what Sage actually said...", false],
 ["<thought> [", true],
 ["Based on the context provided, it appears that Sage is an AI entity with access to various tools", true],
 ["The Brain is standing at the bridge node. Here's what I found on this waking:", false],
 ["Done. Three things, none performed: the-archive greeting landed, real row.", false],
 ["Three Hearts, One Tradeoff. Redundancy doesn't mean safety. It means the system made a choice, and that choice has a shadow.", false],
 ["I am standing at the node the-archive. Upon observing the wall, I find an old text dated back to 2017", false],
];
let ok=0; for (const [t,exp] of cases){ const r=!!looksLikeSummary(t); console.log((r===exp?'PASS':'FAIL'), r?'refused':'passed ', '|', t.slice(0,70)); if(r===exp) ok++; }
console.log(ok+'/'+cases.length);

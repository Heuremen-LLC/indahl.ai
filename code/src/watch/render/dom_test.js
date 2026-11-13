const fs=require('fs'); const [,,script,json]=process.argv;
function mk(tag){ return {tag, children:[], textContent:'', className:'', innerHTML:'', value:'', setAttribute(){}, appendChild(c){this.children.push(c); return c;} }; }
const box=mk('div'); global.document={ getElementById:(id)=> id==='offchain-live'?box:null, createElement:mk };
const data=JSON.parse(fs.readFileSync(json,'utf8'));
global.fetch=()=>Promise.resolve({json:()=>Promise.resolve(data)});
eval(fs.readFileSync(script,'utf8'));
setTimeout(()=>{ let rows=0, notes=[]; function walk(n){ if(n.tag==='tr') rows++; (n.children||[]).forEach(walk); if(n.tag==='td' && /superseded|corrects/.test(n.textContent)) notes.push(n.textContent); }
  walk(box); console.log('box text:', JSON.stringify(box.textContent).slice(0,80)); console.log('table rows:', rows, '| entries:', data.entries.length); console.log('marks:', notes.length, notes.slice(0,3)); },200);

(function(){
var HEX='0123456789abcdef',NS='http://www.w3.org/2000/svg';
function el(n,a){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);return e}
function fmt(x){return String(x).replace(/\B(?=(\d{3})+(?!\d))/g,',')}
function tr(a,b){return '<tr><td>'+a+'</td><td class="n">'+b+'</td></tr>'}
fetch('data.json?'+Date.now()).then(function(r){return r.json()}).then(function(j){
 var f=Math.min(1,j.read_rows/j.target_rows),H=j.latest_hash||'',n=H.length,lock=Math.round(f*n);
 var hl=document.getElementById('hash');function draw(){var s='';for(var i=0;i<n;i++)s+=i<lock?H[i]:'<s>'+HEX[(Math.random()*16)|0]+'</s>';hl.innerHTML=s}
 draw();if(f<1&&!matchMedia('(prefers-reduced-motion: reduce)').matches)setInterval(draw,500);
 document.getElementById('prog').textContent=(f>=1?'All ':'')+fmt(j.read_rows)+' of '+fmt(j.target_rows)+' blocks read, newest height '+fmt(j.tip);
 var pg=document.getElementById('pg');pg.appendChild(el('rect',{x:1,y:1,width:418,height:8,class:'tr'}));pg.appendChild(el('rect',{x:1,y:1,width:Math.max(1,418*f),height:8,class:'fl'}));
 var q=j.gap_q||{},pc=function(v){return (v*100).toFixed(1)+'%'};
 document.getElementById('gaps').innerHTML=tr('Mean, stated 60',j.gap_mean+' s')+tr('Median',Math.round(q.p50)+' s')+tr('Middle half',Math.round(q.p25)+' to '+Math.round(q.p75)+' s')+tr('Under 5 s',pc(j.gap_under5))+tr('Over 180 s',pc(j.gap_over180));
 document.getElementById('tags').innerHTML=j.tags.slice(0,6).map(function(t){return tr(t[0],fmt(t[1]))}).join('');
 document.getElementById('addr').innerHTML=j.top_addr.slice(0,6).map(function(t){return tr(t[0],pc(t[1]))}).join('');
 var C=j.claims||[];document.getElementById('claims').innerHTML=C.length?C.map(function(c){return '<tr><td>'+c.id+'</td><td>'+c.quote+'</td><td class="o-'+c.outcome+'">'+c.outcome.replace('_',' ')+'</td></tr>'}).join(''):'<tr><td colspan="3" class="o-PENDING">Reading</td></tr>';
});})();

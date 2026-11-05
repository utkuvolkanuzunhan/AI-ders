var R=document.getElementById('%ID%');
var CK='<svg class="ic" viewBox="0 0 24 24"><path d="M5 12l5 5l10 -10"/></svg>';
var XX='<svg class="ic" viewBox="0 0 24 24"><path d="M18 6l-12 12"/><path d="M6 6l12 12"/></svg>';
var L='ABCDE';
function th(){var c=getComputedStyle(R.querySelector('.pb')).color.match(/\d+/g);R.classList.toggle('dk',!!c&&(+c[0]+ +c[1]+ +c[2])>384)}th();
function kc(el,k){el.className=el.className.replace(/\b(k\d|rd)\b/g,'').replace(/\s+/g,' ').trim()+' '+k}
function q1(s,e){return (e||R).querySelector(s)}
function qa(s,e){return [].slice.call((e||R).querySelectorAll(s))}
function sp(s){s=String(s).trim();if(s.charAt(s.length-1)==')'){var d=0,k=-1;for(var j=s.length-1;j>=0;j--){var c=s.charAt(j);if(c==')')d++;else if(c=='('){d--;if(d==0){k=j;break}}}if(k>0&&s.charAt(k-1)==' ')return[s.slice(0,k).trim(),s.slice(k)]}return[s,'']}
var tabs=qa('.tb'),pans=qa('.pn'),XS=[],IN=[];
function sel(i){tabs.forEach(function(t,k){t.classList.toggle('on',k==i)});pans.forEach(function(p,k){p.style.display=k==i?'block':'none'})}
function done(i){tabs[i].classList.add('dn');tabs[i].querySelector('.n').innerHTML=CK}
function banner(ok,title,txt){return '<div class="bn bx '+(ok?'%DOGRU%':'%YANLIS%')+'"><div class="ib">'+(ok?CK:XX)+'</div><div><b>'+title+'</b><span>'+txt+'</span></div></div>'}
/*@sort*/
function initSort(sg,items,tabIdx){
  var S=0,D=0,n=items.length,sc=q1('.sc',sg);
  qa('.it',sg).forEach(function(d){var k=+d.getAttribute('data-i'),x=items[k],bs=qa('.cp',d),dn=0;
    d._go=function(b){if(dn)return;dn=1;D++;var v=+b.getAttribute('data-v'),ok=v==x[2];if(ok)S++;
      bs.forEach(function(y){y.classList.add('dn')});b.classList.remove('dn');bs[x[2]].classList.remove('dn');kc(b,ok?'%DOGRU%':'%YANLIS%');b.classList.add('on');kc(bs[x[2]],'%DOGRU%');bs[x[2]].classList.add('on');
      q1('.fb',d).innerHTML=banner(ok,ok?'Doğru':'Tersi',x[3]);
      if(D==n){sc.style.display='block';sc.innerHTML='<b>'+S+' / '+n+'</b>'+(S==n?'Hepsi doğru':'Yanlışlara bir daha bak');done(tabIdx)}}})
}
/*@/sort*/
/*@test*/
function initTest(pi,qs,tabIdx){
  var p=pans[pi],S=0,D=0,n=qs.length,h='';
  qs.forEach(function(q,i){var a=sp(q[0]);h+='<div class="q bx" data-a="'+q[2]+'" data-i="'+i+'"><span class="sk k4">Soru '+(i+1)+' / '+n+'</span><div class="qe">'+a[0]+'</div>'+(a[1]?'<div class="qr">'+a[1]+'</div>':'')+'<div class="os">';
    q[1].forEach(function(o,j){var b=sp(o);h+='<div role="button" tabindex="0" class="o" data-act="opt" data-j="'+j+'"><span class="l">'+L.charAt(j)+'</span><span class="x"><span class="e">'+b[0]+'</span>'+(b[1]?'<span class="t">'+b[1]+'</span>':'')+'</span><span class="mk"></span></div>'});
    h+='</div>';
    if(q[4])h+='<div role="button" tabindex="0" class="hn" data-act="hint"><svg class="ic" viewBox="0 0 24 24"><path d="M3 12h1m8 -9v1m8 8h1m-15.4 -6.4l.7 .7m12.1 -.7l-.7 .7"/><path d="M9 16a5 5 0 1 1 6 0a3.5 3.5 0 0 0 -1 3a2 2 0 0 1 -4 0a3.5 3.5 0 0 0 -1 -3"/><path d="M9.7 17l4.6 0"/></svg>İpucu</div><div class="ht">'+q[4]+'</div>';
    h+='<div class="fb"></div></div>'});
  h+='<div class="sc bx k1"></div>';
  p.insertAdjacentHTML('beforeend',h);
  p._opt=function(x){var q=x.closest('.q');if(q.getAttribute('data-done'))return;q.setAttribute('data-done','1');
    var a=+q.getAttribute('data-a'),j=+x.getAttribute('data-j'),os=qa('.o',q),i=+q.getAttribute('data-i');
    os.forEach(function(o,k){if(k==a){o.classList.add('ok');o.querySelector('.mk').innerHTML=CK}else if(k==j){o.classList.add('no');o.querySelector('.mk').innerHTML=XX}else o.classList.add('dn')});
    var hb=q1('.hn',q);if(hb){hb.style.display='none';q1('.ht',q).style.display='none'}
    q1('.fb',q).innerHTML=banner(j==a,j==a?'Doğru':'Yanlış · doğru cevap: '+L.charAt(a),qs[i][3]);
    D++;if(j==a)S++;
    if(D==n){var sc=q1('.sc',p);sc.style.display='block';sc.innerHTML='<b>'+S+' / '+n+'</b>'+(S==n?'Hepsi doğru':'Yanlışlara bir daha bak');done(tabIdx)}}
}
/*@/test*/
R.addEventListener('click',function(e){var x=e.target.closest?e.target.closest('[role=button]'):null;if(x&&R.contains(x))act(x)});
R.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){var x=e.target.closest?e.target.closest('[role=button]'):null;if(x&&R.contains(x)){e.preventDefault();act(x)}}});
function act(x){th();var a=x.getAttribute('data-act');
  if(a=='tab')sel(+x.getAttribute('data-i'));
  else if(a=='opt')x.closest('.pn')._opt(x);
  else if(a=='hint'){x.style.display='none';x.nextElementSibling.style.display='block'}
  else if(a=='srt')x.closest('.it')._go(x);
  else XS.forEach(function(f){f(x,a)})}
R.addEventListener('input',function(e){IN.forEach(function(f){f(e)})});
/*@rv*/
var RV={};
function rvset(g,n){var d=RV[g][n],st=q1('[data-st="'+g+'"]');qa('[data-g="'+g+'"]').forEach(function(c){c.classList.toggle('on',+c.getAttribute('data-n')==n)});kc(st,d[0]);st.innerHTML='<span class="sk">'+d[1]+'</span><div class="bg2" style="margin-top:8px">'+d[2]+'</div><div class="sm">'+d[3]+'</div>'}
XS.push(function(x,a){if(a=='rv')rvset(x.getAttribute('data-g'),+x.getAttribute('data-n'))});
/*@/rv*/
/*@secici*/
var SC={};
function scset(g,n){var d=SC[g],o=d.o[n],c=q1('[data-sc="'+g+'"]'),mx=d.mx;
  qa('[data-sg="'+g+'"]').forEach(function(b){b.classList.toggle('on',+b.getAttribute('data-n')==n)});
  d.b.forEach(function(id){var v=o.v[id],i=q1('[data-b="'+g+id+'"]'),w=Math.round(v/mx*1000)/10;i.style.width=w+'%';i.style.borderRightWidth=w>0?'2px':'0';q1('[data-v="'+g+id+'"]').textContent=d.p+v});
  q1('[data-r="'+g+'"]').innerHTML=o.r}
XS.push(function(x,a){if(a=='sc')scset(x.getAttribute('data-g'),+x.getAttribute('data-n'))});
/*@/secici*/
/*@kaydirici*/
var KD={};
function kdset(g,s){var d=KD[g],i=0;d.s.forEach(function(e,k){if(s>=e[0])i=k});var e=d.s[i],el=q1('[data-st="'+g+'"]');
  kc(el,e[1]);el.innerHTML='<span class="sk" style="background:var(--sf);color:var(--tx)">'+e[2]+'</span><div class="bg2" style="margin-top:8px">'+e[3]+'</div><div class="sm">'+e[4]+'</div>';
  qa('[data-pg="'+g+'"]').forEach(function(b){var v=+b.getAttribute('data-s'),j=0;d.s.forEach(function(f,k){if(v>=f[0])j=k});b.classList.toggle('on',j==i)});
  if(d.y){var dot=q1('[data-dot="'+g+'"]');dot.setAttribute('cx',d.x[0]+(d.x[1]-d.x[0])*s/100);dot.setAttribute('cy',d.y[s]);dot.setAttribute('fill','var(--'+e[1]+')')}
  if(d.f)d.f(s,i)}
XS.push(function(x,a){if(a=='pg'){var g=x.getAttribute('data-pg'),v=+x.getAttribute('data-s');q1('[data-sl="'+g+'"]').value=v;kdset(g,v)}});
IN.push(function(e){var g=e.target.getAttribute&&e.target.getAttribute('data-sl');if(g)kdset(g,+e.target.value)});
/*@/kaydirici*/

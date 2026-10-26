// Menú móvil
(function(){
  var b=document.querySelector('.nav-toggle'), n=document.getElementById('site-nav');
  if(b&&n){b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});}
})();
// Vídeo de portada: no se reproduce si el usuario prefiere menos movimiento; botón de pausa
(function(){
  var v=document.querySelector('.hero-media video'), t=document.querySelector('.video-toggle');
  if(!v)return;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce){v.removeAttribute('autoplay');v.pause();if(t)t.textContent='Reproducir vídeo';}
  if(t)t.addEventListener('click',function(){
    if(v.paused){v.play();t.textContent='Pausar vídeo';}else{v.pause();t.textContent='Reproducir vídeo';}
  });
})();
// Calculadora de tiempo
(function(){
  var f=document.getElementById('calc'); if(!f)return;
  var pace=330;
  var levels={principiante:{st:2700,rz:480},intermedio:{st:2040,rz:360},avanzado:{st:1500,rz:240}};
  function fmt(s){s=Math.round(s);var h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;
    var mm=String(m).padStart(2,'0'),ss=String(x).padStart(2,'0');return h?h+':'+mm+':'+ss:m+':'+ss;}
  function upd(){
    var l=levels[f.querySelector('input[name=nivel]:checked').value], runs=pace*8;
    document.getElementById('pace-out').textContent=fmt(pace);
    document.getElementById('o-runs').textContent=fmt(runs);
    document.getElementById('o-st').textContent=fmt(l.st);
    document.getElementById('o-rz').textContent=fmt(l.rz);
    document.getElementById('o-total').textContent=fmt(runs+l.st+l.rz);
  }
  document.getElementById('faster').addEventListener('click',function(){pace=Math.max(210,pace-5);upd();});
  document.getElementById('slower').addEventListener('click',function(){pace=Math.min(480,pace+5);upd();});
  f.addEventListener('change',upd); upd();
})();
// Cuenta atrás en días
document.querySelectorAll('[data-countdown]').forEach(function(el){
  var d=new Date(el.getAttribute('data-countdown')+'T00:00:00'), now=new Date();
  var n=Math.ceil((d-now)/86400000); el.textContent=n>0?n:'¡Ya!';
});
// Consentimiento de cookies: Google Analytics solo se carga si la persona acepta
(function(){
  var id=document.documentElement.getAttribute('data-ga'); if(!id)return;
  var KEY='ch_cookies';
  function get(){try{return localStorage.getItem(KEY)}catch(e){return null}}
  function set(v){try{localStorage.setItem(KEY,v)}catch(e){}}
  function loadGA(){
    var s=document.createElement('script'); s.async=true; s.src='https://www.googletagmanager.com/gtag/js?id='+id; document.head.appendChild(s);
    window.dataLayer=window.dataLayer||[]; window.gtag=function(){dataLayer.push(arguments)};
    gtag('js',new Date()); gtag('config',id,{anonymize_ip:true});
  }
  var box=document.getElementById('cookie');
  var c=get();
  if(c==='si'){loadGA();}
  else if(c!=='no'&&box){box.hidden=false;}
  if(box){
    box.querySelector('[data-c=si]').addEventListener('click',function(){set('si');box.hidden=true;loadGA();});
    box.querySelector('[data-c=no]').addEventListener('click',function(){set('no');box.hidden=true;});
  }
  document.querySelectorAll('[data-cookie-reset]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();try{localStorage.removeItem(KEY)}catch(x){} if(box)box.hidden=false;});});
})();
// Correo protegido: la dirección se monta aquí para que no aparezca escrita en la página
document.querySelectorAll('a[data-c]').forEach(function(a){
  var dir=atob(a.dataset.c), q=a.dataset.asunto?'?subject='+encodeURIComponent(a.dataset.asunto):'';
  a.href='mailto:'+dir+q; if(a.hasAttribute('data-mostrar')) a.textContent=dir;
});

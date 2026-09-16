/* Chapter cinema: local WebGL, four acts, deterministic concept experiments. */
const ChapterIntro3D = (() => {
  const stories = {
    1: { tag:'THE FIRST SIGNAL', title:'让世界，听见你的第一行。', quote:'编程，是把一个想法变成可以运行的现实。', definition:'Python 按顺序执行指令，print() 把结果送到屏幕。', code:'message = "Hello, Python!"\nprint(message)', action:'发送第一束信号', results:['Hello, Python!','Hello, Universe!'], kind:'signal', color:0x9dff85 },
    2: { tag:'MEMORY CONSTELLATION', title:'给数据，一个名字。', quote:'数据在变化，名字让我们找到它。', definition:'变量引用对象；重新赋值会让名字指向新的值。', code:'energy = 10\nenergy = 20\nprint(energy)  # 20', action:'重新赋值 energy', results:['energy → 10','energy → 20'], kind:'memory', color:0x7dfce4 },
    3: { tag:'THE EXPRESSION ENGINE', title:'让符号，产生力量。', quote:'表达式把已知，推向一个新的答案。', definition:'运算符连接数据；括号可以改变运算顺序。', code:'print(2 + 3 * 4)    # 14\nprint((2 + 3) * 4)  # 20', action:'切换括号，改变优先级', results:['2 + 3 × 4 = 14','(2 + 3) × 4 = 20'], kind:'operator', color:0xffcf7d },
    4: { tag:'PATHS & LOOPS', title:'在选择中，找到方向。', quote:'判断决定去哪里，循环决定走多远。', definition:'if 选择分支；for 与 while 重复执行一段代码。', code:'for score in [45, 86]:\n    if score >= 60:\n        print("通过")\n    else:\n        print("再试一次")', action:'切换分数，预测分支', results:['score = 45 → 再试一次','score = 86 → 通过'], kind:'branch', color:0xb2a1ff },
    5: { tag:'THE LANGUAGE WEAVER', title:'把字符，编织成意义。', quote:'每一段文字，都藏着可以被索引的秩序。', definition:'字符串是不可变的字符序列；切片取出其中一段。', code:'word = "PYTHON"\nprint(word[0:3])  # PYT\nprint(word[::-1]) # NOHTYP', action:'反转字符序列', results:['PYTHON → PYT','PYTHON → NOHTYP'], kind:'string', color:0xff94ba },
    6: { tag:'ORDER IN MOTION', title:'让数据，有序流动。', quote:'容器赋予数据结构，操作让结构产生价值。', definition:'列表可以修改；元组的元素引用在创建后不可替换。', code:'orbit = [3, 1, 2]\norbit.sort()\nprint(orbit)  # [1, 2, 3]', action:'排列数据轨道', results:['原始列表 [3, 1, 2]','排序完成 [1, 2, 3]'], kind:'list', color:0x88baff },
    7: { tag:'A MAP OF MEANING', title:'用关联，定位世界。', quote:'一个名字，一条线索，一次准确的抵达。', definition:'字典用键查值；集合保存不重复的元素。', code:'star = {"name": "Sirius"}\nprint(star["name"])\nprint(len(set([1, 1, 2]))) # 2', action:'从重复信号中去重', results:['收到信号 [1, 1, 2]','集合去重 {1, 2}'], kind:'map', color:0x79ead4 },
    8: { tag:'THE ART OF ABSTRACTION', title:'把复杂，藏进一个名字。', quote:'函数不是代码的堆叠，而是思维的容器。', definition:'函数封装可复用的行为：参数接收输入，return 交回结果。', code:'def transform(value):\n    return value ** 2\n\nprint(transform(3))  # 9\nprint(transform(4))  # 16', action:'把参数送入函数核心', results:['transform(3) → 9','transform(4) → 16'], kind:'function', color:0xb69aff },
    9: { tag:'BEYOND THE MEMORY', title:'让思想，留下痕迹。', quote:'文件让结果留存，异常处理让程序从容面对意外。', definition:'with 管理文件关闭；try / except 处理预期的运行错误。', code:'try:\n    with open("signal.txt") as f:\n        print(f.read())\nexcept FileNotFoundError:\n    print("文件尚未创建")', action:'切换文件是否存在', results:['signal.txt → Hello, Python!','FileNotFoundError → 文件尚未创建'], kind:'file', color:0xffb879 }
  };
  // 教材换成 39 章后章节号有位移，这里把新章号对回原来按主题写的开场分镜，
  // 避免"章节标题与开场动画讲的不是一回事"。
  const STORY_ALIAS = {1:1, 2:2, 3:4, 4:5, 5:6, 6:7, 7:8, 9:9};
  const escape = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let current=null, lastArgs=null;
  function open(id,title,description,points,onClose,force=false) {
    id=Number(id); if(current) return; lastArgs=[id,title,description,points,onClose];
    const key='pymaster.cinema.v2.'+id;
    try { if(!force && sessionStorage.getItem(key)){onClose?.();return;} } catch(e) {}
    const story=stories[STORY_ALIAS[id]]; if(!story){onClose?.();return;}
    const oldFocus=document.activeElement, oldOverflow=document.body.style.overflow;
    const root=document.createElement('section');root.className='chapter-cinema';root.setAttribute('role','dialog');root.setAttribute('aria-modal','true');root.setAttribute('aria-label',title+' 章节开场');
    root.style.setProperty('--act-accent','#'+story.color.toString(16).padStart(6,'0'));
    root.innerHTML=`<div class="cinema-world" aria-label="可拖动的三维概念模型"></div><div class="cinema-vignette"></div>
      <header class="cinema-head"><span class="cinema-brand">✳ PYMASTER <i>/ LEARNING ATLAS</i></span><span class="cinema-signal">● CHAPTER ${String(id).padStart(2,'0')} / ${String(window.PYMASTER_TOTAL_CHAPTERS||9).padStart(2,'0')}</span><button data-close>跳过开场 ↗</button></header>
      <div class="cinema-main"><div class="cinema-copy"><div class="cinema-kicker">${story.tag}</div><p class="cinema-course">第 ${id} 章 / ${escape(title)}</p><h1>${story.title.replace('，','，<br>')}</h1><p class="cinema-caption"></p><div class="cinema-definition"></div><button class="cinema-experiment" data-experiment>${story.action} <span>↗</span></button><output class="cinema-output" aria-live="polite"></output></div>
      <aside class="cinema-terminal"><div class="terminal-bar"><span>● ● ●</span><span>chapter_${String(id).padStart(2,'0')}.py</span><span>PYTHON 3</span></div><pre><code></code></pre><div class="terminal-foot">输入 → 执行 → 观察结果</div></aside></div>
      <div class="cinema-scene-caption"><span class="scene-mode">3D CONCEPT STUDY</span><span>拖动旋转 · 滚轮缩放</span></div>
      <footer class="cinema-foot"><div class="cinema-acts">${['序幕','代码','概念','实验'].map((label,i)=>`<button data-act="${i}"><small>0${i+1}</small>${label}<i></i></button>`).join('')}</div><button class="cinema-next" data-next>下一幕 <span>→</span></button></footer>`;
    document.body.append(root);document.body.style.overflow='hidden';current=root;
    let act=0, value=0, typeTimer=null, autoTimer=null, closed=false;
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    const scene=initScene(root.querySelector('.cinema-world'),story,id,reduced);
    function setAct(next){
      clearInterval(typeTimer);clearTimeout(autoTimer);act=next;root.dataset.act=act;
      root.querySelectorAll('[data-act]').forEach((b,i)=>{b.classList.toggle('active',i===act);b.setAttribute('aria-pressed',String(i===act));});
      root.querySelector('.cinema-caption').textContent=act===0?story.quote:act===1?'从一段可运行的代码开始，观察数据如何穿过这个世界。':act===2?story.definition:'先预测结果，再点击按钮验证你的直觉。';
      root.querySelector('.cinema-definition').textContent=act===2?description:'';
      const code=root.querySelector('code');code.textContent='';let index=0;
      if(act>0){if(reduced)code.textContent=story.code;else typeTimer=setInterval(()=>{code.textContent=story.code.slice(0,++index);if(index>=story.code.length)clearInterval(typeTimer);},16);}
      root.querySelector('[data-next]').innerHTML=act===3?'进入章节 <span>↗</span>':'下一幕 <span>→</span>';
      scene.stage(act); if(act===3)root.querySelector('output').textContent=story.results[value];
      if(!reduced && act<3)autoTimer=setTimeout(()=>setAct(act+1),act===1?6500:5500);
    }
    function experiment(){clearTimeout(autoTimer);value=1-value;root.querySelector('output').textContent=story.results[value];if(id===1){clearInterval(typeTimer);root.querySelector('code').textContent='message = '+JSON.stringify(value?'Hello, Universe!':'Hello, Python!')+'\nprint(message)';}scene.change(value);}
    function close(){
      if(closed)return;closed=true;clearInterval(typeTimer);clearTimeout(autoTimer);scene.dispose();root.remove();document.body.style.overflow=oldOverflow;document.removeEventListener('keydown',keys);current=null;
      try{sessionStorage.setItem(key,'1');}catch(e){} oldFocus?.focus();onClose?.();
    }
    function keys(e){if(e.key==='Escape')close();if(e.key==='Tab'){const bs=[...root.querySelectorAll('button')].filter(b=>b.offsetParent!==null);if(e.shiftKey&&document.activeElement===bs[0]){e.preventDefault();bs.at(-1).focus();}else if(!e.shiftKey&&document.activeElement===bs.at(-1)){e.preventDefault();bs[0].focus();}}}
    root.querySelector('[data-close]').onclick=close;root.querySelector('[data-next]').onclick=()=>act===3?close():setAct(act+1);root.querySelector('[data-experiment]').onclick=experiment;
    root.querySelectorAll('[data-act]').forEach(b=>b.onclick=()=>setAct(Number(b.dataset.act)));
    document.addEventListener('keydown',keys);setAct(0);root.querySelector('[data-next]').focus();
  }
  function initScene(host,story,id,reduced){
    let renderer;
    try {if(typeof THREE==='undefined')throw Error('WebGL unavailable'); renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});}
    catch(e){host.innerHTML='<div class="cinema-fallback">'+['{ }','[ ]','⟶'][id%3]+'</div>';(host.closest('.chapter-cinema')?.querySelector('.scene-mode') || document.createElement('span')).textContent='静态概念视图 · WebGL 不可用';return {stage(){},change(){},dispose(){}};}
    renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));host.append(renderer.domElement);
    const scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(40,1,.1,100);camera.position.set(0,0,9);
    const group=new THREE.Group();scene.add(group);const accent=story.color, nodes=[], resources=[]; let frame=0, disposed=false, angle=.3, pitch=.18, zoom=9, pulse=0, variant=0;
    const mat=new THREE.MeshStandardMaterial({color:accent,metalness:.65,roughness:.22,emissive:accent,emissiveIntensity:.18});resources.push(mat);
    scene.add(new THREE.AmbientLight(0xb2caff,.9));const light=new THREE.PointLight(accent,3,30);light.position.set(2,3,5);scene.add(light);const white=new THREE.DirectionalLight(0xffffff,1.6);white.position.set(-3,4,5);scene.add(white);
    function mesh(geometry,x=0,y=0,z=0,material=mat){resources.push(geometry);const m=new THREE.Mesh(geometry,material);m.position.set(x,y,z);group.add(m);return m;}
    function wire(geometry,x=0,y=0,z=0){resources.push(geometry);const edges=new THREE.EdgesGeometry(geometry), material=new THREE.LineBasicMaterial({color:accent,transparent:true,opacity:.65});resources.push(edges,material);const line=new THREE.LineSegments(edges,material);line.position.set(x,y,z);group.add(line);return line;}
    function ring(radius,rotation=0){const m=mesh(new THREE.TorusGeometry(radius,.013,8,100));m.rotation.x=1.15;m.rotation.y=rotation;return m;}
    function connect(a,b){const geo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]);const material=new THREE.LineBasicMaterial({color:accent,transparent:true,opacity:.5});resources.push(geo,material);group.add(new THREE.Line(geo,material));}
    if(story.kind==='signal'){mesh(new THREE.IcosahedronGeometry(.58,1));[1.05,1.55,2.1].forEach((r,i)=>ring(r,i*.5));}
    if(story.kind==='memory'){for(let i=0;i<4;i++){const a=i*Math.PI/2;nodes.push(mesh(new THREE.SphereGeometry(.26,24,16),Math.cos(a)*1.6,Math.sin(a)*1.6));connect([0,0,0],[Math.cos(a)*1.6,Math.sin(a)*1.6,0]);}wire(new THREE.BoxGeometry(.8,.8,.8));}
    if(story.kind==='operator'){for(let i=-1;i<2;i++){const m=mesh(new THREE.TorusGeometry(.48,.12,12,48),i*1.5,0,0);m.rotation.y=i*.4;nodes.push(m);}wire(new THREE.OctahedronGeometry(1.1));}
    if(story.kind==='branch'){mesh(new THREE.OctahedronGeometry(.5));for(let s of [-1,1]){connect([0,0,0],[s*1.7,1.2,0]);connect([s*1.7,1.2,0],[s*1.7,-1,0]);nodes.push(mesh(new THREE.IcosahedronGeometry(.35,1),s*1.7,1.2,0));}ring(2.3);}
    if(story.kind==='string'){for(let i=0;i<6;i++){const m=wire(new THREE.BoxGeometry(.5,.7,.5),(i-2.5)*.65,Math.sin(i*.6)*.4);nodes.push(m);}ring(2.4,.3);}
    if(story.kind==='list'){for(let i=0;i<3;i++){const height=[1.8,.6,1.2][i];nodes.push(mesh(new THREE.BoxGeometry(.65,height,.65),(i-1)*1.1,height/2-.8));}ring(2.1);}
    if(story.kind==='map'){mesh(new THREE.IcosahedronGeometry(.45,0));for(let i=0;i<6;i++){const a=i*Math.PI/3,p=[Math.cos(a)*1.75,Math.sin(a)*1.6,(i%2)*.6];nodes.push(mesh(new THREE.SphereGeometry(.23,20,14),...p));connect([0,0,0],p);}}
    if(story.kind==='function'){const core=mesh(new THREE.IcosahedronGeometry(.85,1));wire(new THREE.IcosahedronGeometry(1,1));for(let i=0;i<3;i++)ring(1.5+i*.35,i*.8);nodes.push(mesh(new THREE.SphereGeometry(.2,20,14),-2.3,0),mesh(new THREE.SphereGeometry(.4,20,14),2.3,0));connect([-2.3,0,0],[2.3,0,0]);}
    if(story.kind==='file'){for(let i=0;i<4;i++)nodes.push(wire(new THREE.BoxGeometry(1.6,2,.09),i*.18,i*.12,-i*.32));mesh(new THREE.OctahedronGeometry(.35),1.5,-.7,.4);}
    const starGeo=new THREE.BufferGeometry(), positions=new Float32Array(450*3);for(let i=0;i<positions.length;i++)positions[i]=(Math.random()-.5)*28;starGeo.setAttribute('position',new THREE.BufferAttribute(positions,3));const starMat=new THREE.PointsMaterial({color:0xb8c9dd,size:.025,transparent:true,opacity:.65});scene.add(new THREE.Points(starGeo,starMat));resources.push(starGeo,starMat);
    function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();render();}
    function render(){if(disposed)return;group.rotation.y=angle;group.rotation.x=pitch;camera.position.z=zoom;renderer.render(scene,camera);}
    function tick(){if(disposed)return;if(!document.hidden){if(!reduced)angle+=.0025;if(pulse>0){pulse*=.95;group.scale.setScalar(1+pulse*.12);}render();}if(!reduced)frame=requestAnimationFrame(tick);}
    let drag=null;const down=e=>{drag=[e.clientX,e.clientY];host.setPointerCapture(e.pointerId);};const move=e=>{if(!drag)return;angle+=(e.clientX-drag[0])*.008;pitch=Math.max(-.8,Math.min(.8,pitch+(e.clientY-drag[1])*.006));drag=[e.clientX,e.clientY];render();};const up=()=>drag=null;const wheel=e=>{e.preventDefault();zoom=Math.max(6,Math.min(12,zoom+e.deltaY*.006));render();};
    host.addEventListener('pointerdown',down);host.addEventListener('pointermove',move);host.addEventListener('pointerup',up);host.addEventListener('pointercancel',up);host.addEventListener('wheel',wheel,{passive:false});const observer=new ResizeObserver(resize);observer.observe(host);resize();tick();
    return {stage(n){light.intensity=3+n*.35;render();},change(v){variant=v;pulse=1;
      if(story.kind==='list')nodes.forEach((m,i)=>m.position.x=([2,0,1][i]*(v?1:0)+(v?0:i)-1)*1.1);
      else if(story.kind==='string')nodes.forEach((m,i)=>m.position.x=((v?5-i:i)-2.5)*.65);
      else if(story.kind==='map')nodes.forEach((m,i)=>m.visible=!(v&&i>3));
      else if(story.kind==='branch')nodes.forEach((m,i)=>m.scale.setScalar(i===v?1.65:1));
      else if(story.kind==='memory')nodes.forEach((m,i)=>m.scale.setScalar(i===v?1.8:1));
      else if(story.kind==='file')nodes.forEach(m=>m.visible=!v);
      else nodes.forEach(m=>m.scale.setScalar(v?1.35:1));
      if(story.kind==='signal')group.scale.setScalar(v?1.15:1);render();},dispose(){disposed=true;cancelAnimationFrame(frame);observer.disconnect();resources.forEach(r=>r.dispose());renderer.dispose();renderer.forceContextLoss();host.replaceChildren();}};
  }
  return {open,mountAtlas(host){const world=initScene(host,stories[1],1,matchMedia('(prefers-reduced-motion: reduce)').matches);addEventListener('pagehide',()=>world.dispose(),{once:true});},replay(){if(lastArgs)open(...lastArgs,true);},stories};
})();

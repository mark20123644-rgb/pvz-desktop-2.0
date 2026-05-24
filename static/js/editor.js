// Встроенный редактор уровней
let editorOverlay = null;

function openEditor() {
    if (editorOverlay) {
        editorOverlay.style.display = 'flex';
        return;
    }
    
    editorOverlay = document.createElement('div');
    editorOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: #0a0a1a;
        z-index: 100000;
        overflow: auto;
        display: flex;
        flex-direction: column;
    `;
    
    editorOverlay.innerHTML = \`
        <div style="background:#e94560; padding:15px; display:flex; justify-content:space-between; position:sticky; top:0;">
            <span style="color:white; font-size:20px;">🌱 PvZ РЕДАКТОР УРОВНЕЙ 🧟</span>
            <button id="closeEditorBtn" style="background:#c0392b; color:white; border:none; padding:8px 20px; border-radius:8px;">✖ ЗАКРЫТЬ</button>
        </div>
        <div style="padding:20px; max-width:700px; margin:0 auto; width:100%;">
            <div style="background:#1a2a1a; border:2px solid #5cb85c; border-radius:12px; padding:15px; margin-bottom:15px;">
                <h3 style="color:#ffd700;">📝 ПАРАМЕТРЫ УРОВНЯ</h3>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <input type="text" id="edName" placeholder="Название уровня" style="flex:2; background:#0d1a0d; color:#ffd700; border:1px solid #5cb85c; border-radius:6px; padding:8px;">
                    <input type="number" id="edSun" value="150" style="width:100px; background:#0d1a0d; color:#ffd700; border:1px solid #5cb85c; border-radius:6px; padding:8px;">
                    <label style="display:flex; align-items:center; gap:5px; color:white;"><input type="checkbox" id="edNight"> 🌙 НОЧЬ</label>
                </div>
            </div>
            
            <div style="background:#1a2a1a; border:2px solid #5cb85c; border-radius:12px; padding:15px; margin-bottom:15px;">
                <h3 style="color:#ffd700;">➕ ДОБАВИТЬ ЗОМБИ</h3>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
                    <select id="edType" style="flex:2; background:#0d1a0d; color:#ffd700; border:1px solid #5cb85c; border-radius:6px; padding:8px;"></select>
                    <input type="number" id="edRow" placeholder="ряд" value="3" style="width:60px; background:#0d1a0d; color:#ffd700; border:1px solid #5cb85c; border-radius:6px; padding:8px;">
                    <input type="number" id="edDelay" placeholder="мс" value="0" style="width:80px; background:#0d1a0d; color:#ffd700; border:1px solid #5cb85c; border-radius:6px; padding:8px;">
                    <button id="edAddBtn" style="background:#2d6a2d; color:white; border:none; padding:8px 15px; border-radius:6px;">➕</button>
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:15px; padding:8px; background:#0d1a0d; border-radius:8px;">
                    <label style="color:#aaa;"><input type="checkbox" id="edRandDelay"> 🎲 РАНДОМ ЗАДЕРЖКА</label>
                    <label style="color:#aaa;"><input type="checkbox" id="edRandRow"> 🎲 РАНДОМ РЯД</label>
                    <button id="edRandomBtn" style="background:#9b59b6; color:white; border:none; padding:5px 12px; border-radius:5px;">🎲 5 РАНДОМНЫХ</button>
                    <button id="edBossBtn" style="background:#c0392b; color:white; border:none; padding:5px 12px; border-radius:5px;">👑 БОСС</button>
                    <button id="edClearBtn" style="background:#e67e22; color:white; border:none; padding:5px 12px; border-radius:5px;">🗑 ОЧИСТИТЬ</button>
                </div>
                
                <div style="background:#0d1a0d; border-radius:8px; min-height:60px; max-height:120px; overflow:auto; margin:10px 0;" id="edCurrentList"></div>
                <button id="edSaveWaveBtn" style="width:100%; background:#3498db; color:white; border:none; padding:8px; border-radius:6px; margin-bottom:10px;">💾 СОХРАНИТЬ ВОЛНУ</button>
                
                <div style="background:#0d1a0d; border-radius:8px; min-height:60px; max-height:120px; overflow:auto; margin:10px 0;" id="edWavesList"></div>
                <div style="display:flex; gap:5px;">
                    <button id="edUpBtn" style="flex:1; background:#f39c12; color:white; border:none; padding:5px; border-radius:5px;">⬆ ВВЕРХ</button>
                    <button id="edDownBtn" style="flex:1; background:#f39c12; color:white; border:none; padding:5px; border-radius:5px;">⬇ ВНИЗ</button>
                    <button id="edEditBtn" style="flex:1; background:#2d6a2d; color:white; border:none; padding:5px; border-radius:5px;">✏ РЕДАКТ</button>
                    <button id="edDelBtn" style="flex:1; background:#c0392b; color:white; border:none; padding:5px; border-radius:5px;">🗑 УДАЛИТЬ</button>
                </div>
            </div>
            
            <button id="edSaveLevelBtn" style="width:100%; background:#e94560; color:white; border:none; padding:15px; border-radius:12px; font-size:18px; font-weight:bold;">💾 СОХРАНИТЬ УРОВЕНЬ</button>
            <p style="text-align:center; color:#666; margin-top:10px; font-size:11px;">Уровень сохранится как JSON файл. Скопируйте его в папку custom_waves/ игры</p>
        </div>
    \`;
    
    document.body.appendChild(editorOverlay);
    
    let edZombies = [];
    fetch('/api/manifest').then(r=>r.json()).then(data=>{
        edZombies = Object.keys(data.zombies || {}).filter(z=>z!='your_death');
        const sel = document.getElementById('edType');
        if(sel) {
            edZombies.forEach(z=>{
                let name = z==='zombie'?'🧟 Зомби':z==='system_zombie'?'📁 Систем':z==='hdd_zombie'?'💾 HDD':z==='ssd_zombie'?'⚡ SSD':z==='winrar_zombie'?'🗜 WinRAR':z==='trojan_catapult'?'🎯 Троян':z;
                sel.innerHTML += `<option value="\${z}">\${name}</option>`;
            });
        }
    }).catch(()=>{
        edZombies = ['zombie','system_zombie','hdd_zombie','ssd_zombie','winrar_zombie','trojan_catapult'];
        const sel = document.getElementById('edType');
        if(sel) edZombies.forEach(z=>sel.innerHTML += `<option value="\${z}">\${z}</option>`);
    });
    
    let edWaves = [], edCurrent = [], edSelected = null;
    
    function edRefresh() {
        const curDiv = document.getElementById('edCurrentList');
        if(curDiv){
            curDiv.innerHTML = '';
            edCurrent.forEach((z,i)=>{
                const d = document.createElement('div');
                d.style.cssText = 'padding:5px;border-bottom:1px solid #2a4a2a;display:flex;justify-content:space-between';
                d.innerHTML = `\${z.type}, ряд \${z.row}, \${z.delay}мс <span style="color:#e74c3c;cursor:pointer" data-idx="\${i}">🗑</span>`;
                d.querySelector('span').onclick = ()=>{ edCurrent.splice(i,1); edRefresh(); };
                curDiv.appendChild(d);
            });
        }
        const wavesDiv = document.getElementById('edWavesList');
        if(wavesDiv){
            wavesDiv.innerHTML = '';
            edWaves.forEach((w,i)=>{
                const d = document.createElement('div');
                d.style.cssText = `padding:5px;border-bottom:1px solid #2a4a2a;cursor:pointer;background:\${edSelected===i?'#3a5a3a':'transparent'}`;
                d.textContent = `Волна \${i+1}: \${w.zombies.length} зомби`;
                d.onclick = ()=>{ edSelected=i; edRefresh(); };
                wavesDiv.appendChild(d);
            });
        }
    }
    
    document.getElementById('edAddBtn').onclick = ()=>{
        let t = document.getElementById('edType').value;
        let r = parseInt(document.getElementById('edRow').value)||3;
        let d = parseInt(document.getElementById('edDelay').value)||0;
        if(document.getElementById('edRandRow').checked) r = Math.floor(Math.random()*5)+1;
        if(document.getElementById('edRandDelay').checked) d = Math.floor(Math.random()*5000);
        edCurrent.push({type:t,row:r,delay:d}); edRefresh();
    };
    document.getElementById('edRandomBtn').onclick = ()=>{
        edCurrent = [];
        for(let i=0;i<5;i++) edCurrent.push({type:edZombies[Math.floor(Math.random()*edZombies.length)], row:Math.floor(Math.random()*5)+1, delay:Math.floor(Math.random()*5000)});
        edCurrent.sort((a,b)=>a.delay-b.delay); edRefresh();
    };
    document.getElementById('edBossBtn').onclick = ()=>{ edCurrent.push({type:'your_death',row:3,delay:0}); edRefresh(); };
    document.getElementById('edClearBtn').onclick = ()=>{ edCurrent=[]; edRefresh(); };
    document.getElementById('edSaveWaveBtn').onclick = ()=>{
        if(!edCurrent.length){alert('Нет зомби!');return;}
        edWaves.push({zombies:[...edCurrent]}); edCurrent=[]; edRefresh();
    };
    document.getElementById('edUpBtn').onclick = ()=>{
        if(edSelected!==null && edSelected>0){
            [edWaves[edSelected], edWaves[edSelected-1]] = [edWaves[edSelected-1], edWaves[edSelected]];
            edSelected--; edRefresh();
        }
    };
    document.getElementById('edDownBtn').onclick = ()=>{
        if(edSelected!==null && edSelected<edWaves.length-1){
            [edWaves[edSelected], edWaves[edSelected+1]] = [edWaves[edSelected+1], edWaves[edSelected]];
            edSelected++; edRefresh();
        }
    };
    document.getElementById('edEditBtn').onclick = ()=>{
        if(edSelected!==null && edWaves[edSelected]){
            edCurrent = [...edWaves[edSelected].zombies];
            edWaves.splice(edSelected,1);
            edSelected=null; edRefresh();
        }
    };
    document.getElementById('edDelBtn').onclick = ()=>{
        if(edSelected!==null && edWaves[edSelected]){
            edWaves.splice(edSelected,1);
            edSelected=null; edRefresh();
        }
    };
    document.getElementById('edSaveLevelBtn').onclick = ()=>{
        const name = document.getElementById('edName').value.trim();
        if(!name){alert('Введите название!');return;}
        if(!edWaves.length){alert('Добавьте волны!');return;}
        const level = {
            name: name,
            author: "Editor",
            startSun: parseInt(document.getElementById('edSun').value)||150,
            nightMode: document.getElementById('edNight').checked,
            plants: null,
            zombies: null,
            waves: edWaves
        };
        const fn = name.toLowerCase().replace(/ /g,'_')+'.json';
        const blob = new Blob([JSON.stringify(level,null,2)],{type:'application/json'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = fn;
        a.click();
        alert(`✅ Уровень "\${name}" сохранён!\nФайл: \${fn}\n\nСкопируйте его в папку custom_waves/ игры`);
        edWaves = []; edCurrent = []; edSelected = null;
        edRefresh();
        document.getElementById('edName').value = '';
    };
    
    document.getElementById('closeEditorBtn').onclick = ()=>{
        editorOverlay.style.display = 'none';
    };
    
    edRefresh();
}

// Привязываем кнопку в настройках
setTimeout(() => {
    const btn = document.getElementById('settings-open-editor');
    if (btn) {
        btn.onclick = (e) => {
            e.preventDefault();
            openEditor();
        };
        console.log('✅ Редактор встроен');
    }
}, 1000);

/* ============================================================
   PLANNING 2026 — interactions
   Everything is saved in localStorage so it persists per-browser.
   ============================================================ */

   const FR_MONTHS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"];
   const FR_DAYS   = ["dimanche","lundi","mardi","mercredi","jeudi","vendredi","samedi"];
   const DAY_LETTERS = ["L","M","M","J","V","S","D"];
   
   function todayKey(){
     // FIX : toISOString() convertit en UTC. Pour un fuseau UTC+1 (Algérie),
     // minuit local devient 23h la veille en UTC → décalage d'un jour.
     // On reconstruit la date à partir des composants LOCAUX.
     const d = new Date();
     return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
   }
   
   /* ── isoWeek — même calcul que dashboard.html ── */
   function isoWeekKey(){
     const d = new Date();
     const t = new Date(d); t.setHours(0,0,0,0);
     t.setDate(t.getDate() + 3 - (t.getDay()+6)%7);
     const w = new Date(t.getFullYear(), 0, 4);
     return `${t.getFullYear()}-W${Math.round(((t-w)/86400000 + w.getDay()+5)/7)}`;
   }
   
   function setDateBadge(){
     const el = document.getElementById('todayDate');
     if(!el) return;
     const d = new Date();
     el.textContent = `${FR_DAYS[d.getDay()]} ${d.getDate()} ${FR_MONTHS[d.getMonth()]} ${d.getFullYear()}`;
   }
   
   /* ---------- generic storage helpers ---------- */
   function loadJSON(key, fallback){
     try{
       const raw = localStorage.getItem(key);
       return raw ? JSON.parse(raw) : fallback;
     }catch(e){ return fallback; }
   }
   function saveJSON(key, value){
     localStorage.setItem(key, JSON.stringify(value));
   }
   
   
   /* ============================================================
      1) Simple checklists  -> data-checklist="namespace"
      ============================================================ */
   function initChecklists(){
     document.querySelectorAll('[data-checklist]').forEach(list=>{
       const store = list.getAttribute('data-checklist');
       const daily = list.getAttribute('data-daily') === 'true';
       const storageKey = daily ? `pl_${store}_${todayKey()}` : `pl_${store}`;
       const state = loadJSON(storageKey, {});
   
       list.querySelectorAll('.check-item').forEach(item=>{
         const cb = item.querySelector('input[type="checkbox"]');
         const id = item.getAttribute('data-id');
         if(!cb || !id) return;
         cb.checked = !!state[id];
         item.classList.toggle('done', cb.checked);
         cb.addEventListener('change', ()=>{
           state[id] = cb.checked;
           saveJSON(storageKey, state);
           item.classList.toggle('done', cb.checked);
           document.dispatchEvent(new CustomEvent('pl:update'));
         });
       });
     });
   }
   
   /* ============================================================
      2) Tile grids
      ============================================================ */
   function buildTileGrid(grid){
     const store = grid.getAttribute('data-tilegrid');
     const count = parseInt(grid.getAttribute('data-count') || '0', 10);
     const showNum = grid.getAttribute('data-numbers') !== 'false';
     const storageKey = `pl_${store}`;
     const state = new Set(loadJSON(storageKey, []));
   
     grid.innerHTML = '';
     for(let i=1;i<=count;i++){
       const tile = document.createElement('div');
       tile.className = 'tile' + (state.has(i) ? ' done' : '');
       tile.setAttribute('role','button');
       tile.setAttribute('tabindex','0');
       tile.setAttribute('aria-pressed', state.has(i) ? 'true':'false');
       if(showNum) tile.textContent = i;
       tile.addEventListener('click', ()=>toggleTile(tile,i,state,storageKey,grid));
       tile.addEventListener('keydown', e=>{
         if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); toggleTile(tile,i,state,storageKey,grid); }
       });
       grid.appendChild(tile);
     }
     updateGridProgress(grid, state, count);
   }
   
   function toggleTile(tile, i, state, storageKey, grid){
     if(state.has(i)){ state.delete(i); tile.classList.remove('done'); tile.setAttribute('aria-pressed','false'); }
     else{ state.add(i); tile.classList.add('done'); tile.setAttribute('aria-pressed','true'); }
     saveJSON(storageKey, Array.from(state));
     updateGridProgress(grid, state, parseInt(grid.getAttribute('data-count'),10));
     document.dispatchEvent(new CustomEvent('pl:update'));
   }
   
   function updateGridProgress(grid, state, count){
     const targetId = grid.getAttribute('data-progress-target');
     if(!targetId) return;
     const wrap = document.getElementById(targetId);
     if(!wrap) return;
     const fill = wrap.querySelector('.progress-fill');
     const label = wrap.querySelector('.progress-label');
     const pct = count ? Math.round((state.size / count) * 100) : 0;
     if(fill) fill.style.width = pct + '%';
     if(label) label.textContent = `${state.size} / ${count}`;
   }
   
   function initTileGrids(){
     document.querySelectorAll('[data-tilegrid]').forEach(buildTileGrid);
   }
   
   /* ============================================================
      3) Weekly tile grid — resets every ISO week automatically.
      ============================================================ */
   function buildWeekGrid(grid){
     const store = grid.getAttribute('data-weekgrid');
     const storageKey = `pl_${store}_${isoWeekKey()}`;
     const state = new Set(loadJSON(storageKey, []));
     const todayIdx = (new Date().getDay() + 6) % 7; // Monday=0
   
     grid.innerHTML = '';
     for(let i=0;i<7;i++){
       const tile = document.createElement('div');
       tile.className = 'tile' + (state.has(i) ? ' done':'') + (i===todayIdx ? ' today':'');
       tile.textContent = DAY_LETTERS[i];
       tile.setAttribute('role','button');
       tile.setAttribute('tabindex','0');
       tile.addEventListener('click', ()=>{
         if(state.has(i)){ state.delete(i); tile.classList.remove('done'); }
         else{ state.add(i); tile.classList.add('done'); }
         saveJSON(storageKey, Array.from(state));
         updateGridProgress(grid, state, 7);
         document.dispatchEvent(new CustomEvent('pl:update'));
       });
       grid.appendChild(tile);
     }
     updateGridProgress(grid, state, 7);
   }
   
   function initWeekGrids(){
     document.querySelectorAll('[data-weekgrid]').forEach(buildWeekGrid);
   }
   
   /* ============================================================
      4) Prayer table — uses isoWeekKey() consistent with dashboard
      ============================================================ */
   function initPrayerTable(){
     const table = document.querySelector('[data-prayertable]');
     if(!table) return;
     const storageKey = `pl_salat_${isoWeekKey()}`;
     const state = loadJSON(storageKey, {});
     const todayIdx = (new Date().getDay() + 6) % 7;
   
     table.querySelectorAll('.dot-check').forEach(dot=>{
       const prayer = dot.getAttribute('data-prayer');
       const day = dot.getAttribute('data-day');
       const key = `${prayer}_${day}`;
       if(state[key]) dot.classList.add('done');
       if(parseInt(day,10) === todayIdx) dot.classList.add('today-col');
       dot.addEventListener('click', ()=>{
         state[key] = !state[key];
         dot.classList.toggle('done', state[key]);
         saveJSON(storageKey, state);
         document.dispatchEvent(new CustomEvent('pl:update'));
       });
     });
   }
   
   /* ============================================================
      5) Water tracker
      ============================================================ */
   function initWaterTrackers(){
     document.querySelectorAll('[data-water]').forEach(row=>{
       const store = row.getAttribute('data-water');
       const target = parseInt(row.getAttribute('data-target') || '12', 10);
       const storageKey = `pl_${store}_${todayKey()}`;
       let filled = loadJSON(storageKey, 0);
   
       row.innerHTML = '';
       for(let i=0;i<target;i++){
         const drop = document.createElement('div');
         drop.className = 'drop' + (i < filled ? ' filled':'');
         drop.innerHTML = `<svg viewBox="0 0 24 30" width="100%" height="100%"><path d="M12 1C12 1 3 12.5 3 19a9 9 0 0 0 18 0c0-6.5-9-18-9-18Z" fill="${i<filled ? 'var(--accent)':'var(--line)'}"/></svg>`;
         drop.addEventListener('click', ()=>{
           filled = (i < filled) ? i : i+1;
           saveJSON(storageKey, filled);
           renderWaterFill(row, filled);
           const label = document.querySelector(`[data-water-label="${store}"]`);
           if(label) label.textContent = `${filled} / ${target}`;
           document.dispatchEvent(new CustomEvent('pl:update'));
         });
         row.appendChild(drop);
       }
       const label = document.querySelector(`[data-water-label="${store}"]`);
       if(label) label.textContent = `${filled} / ${target}`;
     });
   }
   
   function renderWaterFill(row, filled){
     row.querySelectorAll('.drop').forEach((drop,i)=>{
       const on = i < filled;
       drop.classList.toggle('filled', on);
       drop.querySelector('path').setAttribute('fill', on ? 'var(--accent)' : 'var(--line)');
     });
   }
   
   /* ============================================================
      6) Day-selector pills
      ============================================================ */
   function initPillGroups(){
     document.querySelectorAll('[data-pillgroup]').forEach(group=>{
       const store = group.getAttribute('data-pillgroup');
       const max = parseInt(group.getAttribute('data-max') || '99', 10);
       const storageKey = `pl_${store}_${isoWeekKey()}`;
       const state = new Set(loadJSON(storageKey, []));
   
       group.querySelectorAll('.pill').forEach((pill,i)=>{
         if(state.has(i)) pill.classList.add('on');
         pill.addEventListener('click', ()=>{
           if(state.has(i)){ state.delete(i); pill.classList.remove('on'); }
           else{
             if(state.size >= max){
               const note = group.parentElement.querySelector('.pill-counter');
               if(note){ note.classList.add('shake'); setTimeout(()=>note.classList.remove('shake'),300); }
               return;
             }
             state.add(i); pill.classList.add('on');
           }
           saveJSON(storageKey, Array.from(state));
           const counter = document.querySelector(`[data-pill-counter="${store}"]`);
           if(counter) counter.textContent = `${state.size} / ${max}`;
           document.dispatchEvent(new CustomEvent('pl:update'));
         });
       });
       const counter = document.querySelector(`[data-pill-counter="${store}"]`);
       if(counter) counter.textContent = `${state.size} / ${max}`;
     });
   }
   
   /* ============================================================
      7) Free text fields
      ============================================================ */
   function initPersistFields(){
     document.querySelectorAll('[data-persist]').forEach(field=>{
       const key = `pl_text_${field.getAttribute('data-persist')}`;
       field.value = localStorage.getItem(key) || '';
       field.addEventListener('input', ()=>localStorage.setItem(key, field.value));
     });
   }
   
   /* ============================================================
      8) Numeric step field
      ============================================================ */
   function initStepFields(){
     document.querySelectorAll('[data-steps]').forEach(input=>{
       const store = input.getAttribute('data-steps');
       const goal = parseInt(input.getAttribute('data-goal') || '10000', 10);
       const storageKey = `pl_${store}_${todayKey()}`;
       input.value = localStorage.getItem(storageKey) || '';
       const updateBar = ()=>{
         const wrap = document.querySelector(`[data-steps-bar="${store}"]`);
         if(!wrap) return;
         const val = parseInt(input.value || '0', 10);
         const pct = Math.min(100, Math.round((val/goal)*100));
         const fill = wrap.querySelector('.progress-fill');
         const label = wrap.querySelector('.progress-label');
         if(fill) fill.style.width = pct + '%';
         if(label) label.textContent = `${val} / ${goal}`;
       };
       input.addEventListener('input', ()=>{
         localStorage.setItem(storageKey, input.value);
         updateBar();
         document.dispatchEvent(new CustomEvent('pl:update'));
       });
       updateBar();
     });
   }
   
   /* ============================================================
      Dashboard summary (script.js version — for other pages)
      NOTE: The dashboard page has its own full logic in extra_js.
      ============================================================ */
   function refreshDashboard(){
     const dash = document.querySelector('[data-dashboard]');
     if(!dash) return;
   
     const TKEY  = todayKey();
     const TWEEK = isoWeekKey();
     const TIDX  = (new Date().getDay()+6)%7;
   
     // Salat today
     const salatState = loadJSON(`pl_salat_${TWEEK}`, {});
     const prayers = ['fajr','dhuhr','asr','maghrib','isha'];
     const salatDone = prayers.filter(p=>salatState[`${p}_${TIDX}`]).length;
     setStat('stat-salat', `${salatDone}<small>/5</small>`);
   
     // Quran hizb
     const hizb = loadJSON('pl_quran_hizb', []);
     setStat('stat-hizb', `${hizb.length}<small>/60</small>`);
   
     // Juz amma
     const juzAmma = loadJSON('pl_juzamma', {});
     const juzCount = Object.values(juzAmma).filter(Boolean).length;
     setStat('stat-juzamma', `${juzCount}<small>/37</small>`);
   
     // Gym
     const gym = loadJSON(`pl_gym_${TWEEK}`, []);
     setStat('stat-gym', `${gym.length}<small>/5</small>`);
   
     // Water
     const water = loadJSON(`pl_water_${TKEY}`, 0);
     setStat('stat-water', `${water}<small>/12</small>`);
   
     // Steps
     const steps = localStorage.getItem(`pl_steps_${TKEY}`) || 0;
     setStat('stat-steps', `${steps}`);
   
     // 75 hard
     const hard = loadJSON('pl_75hard', []);
     setStat('stat-75hard', `${hard.length}<small>/75</small>`);
   
     // Learning
     const lang = loadJSON(`pl_langcheck_${TKEY}`, {});
     const langDone = Object.values(lang).filter(Boolean).length;
     setStat('stat-learning', `${langDone}<small>/3</small>`);
   
     // Selfcare
     const self = loadJSON(`pl_selfcare_${TKEY}`, {});
     const selfDone = Object.values(self).filter(Boolean).length;
     setStat('stat-selfcare', `${selfDone}`);
   
     // Homecare
     const home = loadJSON(`pl_homecare_${TKEY}`, {});
     let totalMin = 0;
     Object.values(home).forEach(v=>{ if(typeof v === 'number') totalMin += v; });
     setStat('stat-homecare', `${totalMin}<small>/90 min</small>`);
   }
   
   function setStat(id, html){
     const el = document.getElementById(id);
     if(el) el.innerHTML = html;
   }
   
   /* ============================================================
      Boot
      ============================================================ */
   document.addEventListener('DOMContentLoaded', ()=>{
     setDateBadge();
     initChecklists();
     initTileGrids();
     initWeekGrids();
     initPrayerTable();
     initWaterTrackers();
     initPillGroups();
     initPersistFields();
     initStepFields();
     refreshDashboard();
   });
   
   document.addEventListener('pl:update', refreshDashboard);
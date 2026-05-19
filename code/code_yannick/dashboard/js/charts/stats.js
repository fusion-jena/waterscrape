function renderStats(kw) {
  const e = engData[kw] || Object.values(engData)[0];
  const p = platformData[kw];
  const grid = document.getElementById('stats-grid');
  const items = [
    { label:'Avg likes',    value: e.avg_likes, sub: 'max '+fmtNum(e.max_likes), color: '#f5d76e' },
    { label:'Avg reblogs',  value: e.avg_reblogs, sub: 'max '+fmtNum(e.max_reblogs), color: '#4de8b4' },
    { label:'Avg replies',  value: e.avg_replies, sub: 'max '+fmtNum(e.max_replies), color: '#6c8fff' },
    { label:'Original posts',value: fmtNum(p.originals), sub: '', color: '#c97cf5' },
    { label:'Reply posts',  value: fmtNum(p.replies), sub: '', color: '#f7855c' },
    { label:'Reply ratio',  value: (p.replies/(p.originals+p.replies)*100).toFixed(1)+'%', sub: 'of all posts', color: '#60c8f5' },
  ];
  grid.innerHTML = items.map(it => `
      <div class="stat">
        <div class="stat-label">${it.label}</div>
        <div class="stat-value" style="color:${it.color}">${it.value}</div>
        ${it.sub ? `<div class="stat-sub">${it.sub}</div>` : ''}
      </div>
  `).join('');
}


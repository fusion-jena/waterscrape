function renderStats(kw) {
  const e = engData[kw] || Object.values(engData)[0];
  const p = platformData[kw];
  const total = p.originals + p.replies;
  const kwColor = COLORS[0];
  const grid = document.getElementById('stats-grid');
  const items = [
    { label:'Avg likes',      value: e.avg_likes,    sub: 'max '+fmtNum(e.max_likes)   },
    { label:'Avg reblogs',    value: e.avg_reblogs,  sub: 'max '+fmtNum(e.max_reblogs) },
    { label:'Avg replies',    value: e.avg_replies,  sub: 'max '+fmtNum(e.max_replies) },
    { label:'Original posts', value: fmtNum(p.originals), sub: ''                      },
    { label:'Reply posts',    value: fmtNum(p.replies),   sub: ''                      },
    { label:'Reply ratio',    value: total > 0 ? (p.replies/total*100).toFixed(1)+'%' : '—', sub: 'of all posts' },
  ];
  grid.innerHTML = items.map(it => `
    <div class="stat" style="border-top-color: ${kwColor}">
      <div class="stat-label">${it.label}</div>
      <div class="stat-value" style="color:${kwColor}">${it.value}</div>
      ${it.sub ? `<div class="stat-sub">${it.sub}</div>` : ''}
    </div>
  `).join('');
}

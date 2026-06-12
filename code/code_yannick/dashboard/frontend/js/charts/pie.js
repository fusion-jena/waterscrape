function renderDonut(kw) {
  const p = platformData[kw];
  if (!p) return;

  const container = document.getElementById('donut-chart');
  container.innerHTML = '';

  const platforms = (p.by_platform || []).map((r, i) => ({
    label: r.platform,
    value: r.count,
    color: COLORS[i] || '#888',
  }));

  const total = platforms.reduce((s,d)=>s+d.value,0);
 
  const W = container.clientWidth || 320, H = 200;
  const cx = W * 0.35, cy = H / 2, r = 75, ri = 48;
 
  const pie = d3.pie().value(d=>d.value).sort(null);
  const arc = d3.arc().innerRadius(ri).outerRadius(r).cornerRadius(2).padAngle(0.03);
  const arcHover = d3.arc().innerRadius(ri).outerRadius(r+6).cornerRadius(2).padAngle(0.03);
 
  const svg = d3.select(container).append('svg').attr('width', W).attr('height', H);
  const g = svg.append('g').attr('transform',`translate(${cx},${cy})`);
 
  // center label
  const centerG = g.append('g');
  centerG.append('text').attr('text-anchor','middle').attr('y',-10)
    .attr('fill','var(--text)').attr('font-size',22).attr('font-weight',600)
    .attr('font-family','var(--mono)').text(fmtNum(total));
  centerG.append('text').attr('text-anchor','middle').attr('y',10)
    .attr('fill','var(--muted)').attr('font-size',11)
    .text('posts');
 
  g.selectAll('path').data(pie(platforms)).join('path')
    .attr('d', arc)
    .attr('fill', d=>d.data.color)
    .attr('opacity', 0.85)
    .on('mouseover', function(e,d) {
      d3.select(this).attr('d', arcHover).attr('opacity',1);
      showTip(`<div class="tt-row"><div class="tt-dot" style="background:${d.data.color}"></div><span class="tt-name">${d.data.label}</span><span class="tt-val">${fmtNum(d.data.value)}</span></div><div style="color:var(--muted);font-size:11px;margin-top:4px">${(d.data.value/total*100).toFixed(1)}% of total</div>`, e);
    })
    .on('mousemove', moveTip)
    .on('mouseleave', function(e,d) {
      d3.select(this).attr('d', arc).attr('opacity', 0.85);
      hideTip();
    });
 
  // legend on the right
  const lx = cx + r + 24;
  const ly = cy - (platforms.length * 22) / 2;
  const lg = svg.append('g').attr('transform',`translate(${lx},${ly})`);
  platforms.forEach((p, i) => {
    const row = lg.append('g').attr('transform',`translate(0,${i*26})`);
    row.append('rect').attr('width',10).attr('height',10).attr('y',-9).attr('rx',2).attr('fill',p.color);
    row.append('text').attr('x',16).attr('fill','var(--text)').attr('font-size',13)
      .text(p.label);
    row.append('text').attr('x',16).attr('y',14).attr('fill','var(--muted)').attr('font-size',11)
      .attr('font-family','var(--mono)')
      .text(fmtNum(p.value)+' ('+( p.value/total*100).toFixed(0)+'%)');
  });
}

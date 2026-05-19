let smoothMode = true;

function renderFreq(kw) {
  const container = document.getElementById('freq-chart');
  container.innerHTML = '';

  const W = container.clientWidth || 680, H = 240;
  const margin = { top:12, right:20, bottom:36, left:44 };
  const iw = W - margin.left - margin.right;
  const ih = H - margin.top - margin.bottom;

  const allDates = [...new Set(weeklyCounts.map(d => +d.date))].map(t => new Date(t)).sort((a,b)=>a-b);
  const xScale = d3.scaleTime().domain(d3.extent(allDates)).range([0, iw]);

  const kwList = kw === 'all' ? KEYWORDS : [kw];
  const yKey  = smoothMode ? 'n_posts_smooth' : 'n_posts';

  const allVals = weeklyCounts.filter(d => kwList.includes(d.keyword)).map(d => d[yKey]);
  const yScale = d3.scaleLinear().domain([0, d3.max(allVals) * 1.1]).range([ih, 0]);

  const svg = d3.select(container).append('svg')
    .attr('width', W).attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  // grid lines
  g.append('g').selectAll('line').data(yScale.ticks(5)).join('line')
    .attr('class','grid-line')
    .attr('x1',0).attr('x2',iw)
    .attr('y1',d=>yScale(d)).attr('y2',d=>yScale(d));

  // axes
  g.append('g').attr('class','axis').attr('transform',`translate(0,${ih})`)
    .call(d3.axisBottom(xScale).ticks(8).tickSize(0).tickPadding(8)
      .tickFormat(d3.timeFormat('%b %y')));
  g.append('g').attr('class','axis')
    .call(d3.axisLeft(yScale).ticks(5).tickSize(0).tickPadding(8));

  // D3 INTERPOLATION CURVE
  const line = d3.line().x(d=>xScale(d.date)).y(d=>yScale(d[yKey])).curve(d3.curveCatmullRom);

  // overlay for tooltip
  const bisect = d3.bisector(d=>d.date).left;
  const overlay = g.append('rect')
    .attr('width', iw).attr('height', ih)
    .attr('fill','transparent');

  // lines
  const series = kwList.map((kw, i) => ({
    kw, color: COLORS[i],
    data: weeklyCounts.filter(d=>d.keyword===kw).sort((a,b)=>a.date-b.date)
  }));

  series.forEach(s => {
    g.append('path')
      .datum(s.data)
      .attr('fill','none')
      .attr('stroke', s.color)
      .attr('stroke-width', 2)
      .attr('d', line);
  });

  // vertical cursor + tooltip
  const vline = g.append('line')
    .attr('stroke', 'rgba(255,255,255,0.2)')
    .attr('stroke-width', 1)
    .attr('y1', 0).attr('y2', ih)
    .attr('opacity', 0);

  const dots = series.map(s =>
    g.append('circle').attr('r', 4).attr('fill', s.color).attr('opacity', 0)
  );

  overlay.on('mousemove', function(event) {
    const [mx] = d3.pointer(event);
    const x0 = xScale.invert(mx);
    vline.attr('x1', mx).attr('x2', mx).attr('opacity', 1);

    const rows = series.map((s, i) => {
      const idx = Math.min(bisect(s.data, x0, 1), s.data.length-1);
      const d = s.data[idx];
      dots[i].attr('cx', xScale(d.date)).attr('cy', yScale(d[yKey])).attr('opacity', 1);
      return `<div class="tt-row"><div class="tt-dot" style="background:${s.color}"></div><span class="tt-name">${s.kw}</span><span class="tt-val">${d[yKey]}</span></div>`;
    });
    const dateStr = d3.timeFormat('%b %d, %Y')(series[0].data[bisect(series[0].data, x0, 1) % series[0].data.length]?.date || x0);
    showTip(`<div class="tt-label">${dateStr}</div>${rows.join('')}`, event);
  }).on('mouseleave', () => {
    vline.attr('opacity',0);
    dots.forEach(d=>d.attr('opacity',0));
    hideTip();
  });

  // legend
  const legend = document.getElementById('freq-legend');
  legend.innerHTML = series.map(s =>
    `<div class="legend-item"><div class="legend-line" style="background:${s.color}"></div>${s.kw}</div>`
  ).join('');
}


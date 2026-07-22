function renderSentimentOverTime(kw) {
  const container = document.getElementById('sentiment-time-chart');
  container.innerHTML = '';

  const W = container.clientWidth || 680, H = 260;
  const margin = { top:12, right:20, bottom:36, left:50 };
  const iw = W - margin.left - margin.right;
  const ih = H - margin.top - margin.bottom;

  const kwList = kw === 'all' ? KEYWORDS : [kw];

  // aggregate raw sentiment scores into weekly averages per keyword
  const series = kwList.map((kw, i) => {
    const raw = (sentimentData[kw] || []).map(r => ({
      date: new Date(r.date),
      sentiment: r.sentiment,
    }));

    // bin by week (Monday) and average
    const byWeek = {};
    raw.forEach(r => {
      const monday = new Date(r.date);
      monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7));
      monday.setHours(0,0,0,0);
      const key = +monday;
      if (!byWeek[key]) byWeek[key] = { date: monday, sum: 0, count: 0 };
      byWeek[key].sum   += r.sentiment;
      byWeek[key].count += 1;
    });

    const data = Object.values(byWeek)
      .map(w => ({ date: w.date, sentiment: w.sum / w.count }))
      .sort((a, b) => a.date - b.date);

    return { kw, color: COLORS[i], data };
  }).filter(s => s.data.length > 0);

  if (series.length === 0) return;

  const allDates = series.flatMap(s => s.data.map(d => d.date));
  const xScale = d3.scaleTime().domain(d3.extent(allDates)).range([0, iw]);
  const yScale = d3.scaleLinear().domain([-1, 1]).range([ih, 0]);

  const svg = d3.select(container).append('svg').attr('width', W).attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  // grid lines
  g.append('g').selectAll('line').data(yScale.ticks(5)).join('line')
    .attr('class', 'grid-line')
    .attr('x1', 0).attr('x2', iw)
    .attr('y1', d => yScale(d)).attr('y2', d => yScale(d));

  // zero reference line
  g.append('line')
    .attr('x1', 0).attr('x2', iw)
    .attr('y1', yScale(0)).attr('y2', yScale(0))
    .attr('stroke', 'var(--border2)')
    .attr('stroke-width', 1.5)
    .attr('stroke-dasharray', '6,3');

  // axes
  g.append('g').attr('class', 'axis').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(xScale).ticks(8).tickSize(0).tickPadding(8)
      .tickFormat(d3.timeFormat("%b '%y")));
  g.append('g').attr('class', 'axis')
    .call(d3.axisLeft(yScale).ticks(5).tickSize(0).tickPadding(8)
      .tickFormat(d => d > 0 ? `+${d.toFixed(1)}` : d.toFixed(1)));

  const line = d3.line()
    .x(d => xScale(d.date))
    .y(d => yScale(d.sentiment))
    .curve(d3.curveCatmullRom);

  // overlay for tooltip
  const bisect = d3.bisector(d => d.date).left;
  const overlay = g.append('rect')
    .attr('width', iw).attr('height', ih)
    .attr('fill', 'transparent');

  series.forEach(s => {
    g.append('path')
      .datum(s.data)
      .attr('fill', 'none')
      .attr('stroke', s.color)
      .attr('stroke-width', 2)
      .attr('d', line);
  });

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
      const idx = Math.min(bisect(s.data, x0, 1), s.data.length - 1);
      const d = s.data[idx];
      dots[i].attr('cx', xScale(d.date)).attr('cy', yScale(d.sentiment)).attr('opacity', 1);
      const val = d.sentiment >= 0 ? `+${d.sentiment.toFixed(3)}` : d.sentiment.toFixed(3);
      return `<div class="tt-row"><div class="tt-dot" style="background:${s.color}"></div><span class="tt-name">${s.kw}</span><span class="tt-val">${val}</span></div>`;
    });
    const dateStr = d3.timeFormat('%b %d, %Y')(series[0].data[bisect(series[0].data, x0, 1) % series[0].data.length]?.date || x0);
    showTip(`<div class="tt-label">${dateStr}</div>${rows.join('')}`, event);
  }).on('mouseleave', () => {
    vline.attr('opacity', 0);
    dots.forEach(d => d.attr('opacity', 0));
    hideTip();
  });

  // legend
  const legend = document.getElementById('sentiment-time-legend');
  legend.innerHTML = series.map(s =>
    `<div class="legend-item"><div class="legend-line" style="background:${s.color}"></div>${s.kw}</div>`
  ).join('');
}

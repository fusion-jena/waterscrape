function renderHash(kw) {
  const container = document.getElementById('hash-chart');
  container.innerHTML = '';
  const data = (hashData[kw] || hashData[KEYWORDS[0]] || []).slice(0,10).map(r => ({ tag: r.hashtag, freq: r.freq }));
 
  const W = container.clientWidth || 320, H = 10 + data.length * 26;
  const margin = { top:4, right:60, bottom:4, left:120 };
  const iw = W - margin.left - margin.right;
  const ih = H - margin.top - margin.bottom;
 
  const xScale = d3.scaleLinear().domain([0, data[0].freq]).range([0, iw]);
  const yScale = d3.scaleBand().domain(data.map(d=>d.tag)).range([0,ih]).padding(0.25);
 
  const svg = d3.select(container).append('svg').attr('width', W).attr('height', H);
  const g = svg.append('g').attr('transform',`translate(${margin.left},${margin.top})`);
 
  g.selectAll('rect').data(data).join('rect')
    .attr('x', 0).attr('y', d=>yScale(d.tag))
    .attr('width', d=>xScale(d.freq))
    .attr('height', yScale.bandwidth())
    .attr('fill', COLORS[0]).attr('opacity', 1)
    .attr('rx', 3)
    .on('mouseover', (e,d) => showTip(`<div class="tt-label">#${d.tag}</div><div class="tt-val">${d.freq.toLocaleString()} posts</div>`, e))
    .on('mousemove', moveTip)
    .on('mouseleave', hideTip);
 
  g.selectAll('.bar-label').data(data).join('text')
    .attr('class','bar-label')
    .attr('x', -6).attr('y', d=>yScale(d.tag)+yScale.bandwidth()/2+4)
    .attr('text-anchor','end')
    .text(d=>'#'+d.tag);
 
  g.selectAll('.bar-count').data(data).join('text')
    .attr('class','bar-count')
    .attr('x', d=>xScale(d.freq)+6).attr('y', d=>yScale(d.tag)+yScale.bandwidth()/2+4)
    .text(d=>fmtNum(d.freq));
}

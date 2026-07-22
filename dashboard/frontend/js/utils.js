function fmtNum(n) { return n >= 1000 ? (n/1000).toFixed(1)+'k' : String(n); }

function showTip(html, event) {
  const tip = document.getElementById('tooltip');
  tip.innerHTML = html;
  tip.style.opacity = 1;
  moveTip(event);
}
function moveTip(event) {
  const tip = document.getElementById('tooltip');
  tip.style.left = (event.clientX + 14) + 'px';
  tip.style.top  = (event.clientY - 10) + 'px';
}
function hideTip() {
  document.getElementById('tooltip').style.opacity = 0;
}

function populateSelect(id, options, onChange) {
  const sel = document.getElementById(id);
  options.forEach((o, i) => {
    const opt = document.createElement('option');
    opt.value = o; opt.textContent = o;
    sel.appendChild(opt);
  });
  sel.addEventListener('change', () => onChange(sel.value));
  return sel;
}

function addAllOption(sel, onChange) {
  const opt = document.createElement('option');
  opt.value = 'all'; opt.textContent = 'All keywords';
  sel.prepend(opt);
  sel.value = 'all';
  sel.addEventListener('change', () => onChange(sel.value));
}

function renderPosts(kw) {
  const posts = postsData[kw] || postsData[KEYWORDS[0]];
  const tbody = document.getElementById('posts-body');
  tbody.innerHTML = posts.map(p => `
    <tr>
      <td>
        <span class="platform-badge badge-${p.platform}">${p.platform}</span>
        <div style="color:var(--muted);font-size:11px;margin-top:3px">${p.instance}</div>
      </td>
      <td>
        <div class="post-content">${p.content.slice(0,180)}${p.content.length>180?'…':''}</div>
        <div class="post-meta">${p.date}</div>
      </td>
      <td style="text-align:right"><span class="like-count">${p.likes.toLocaleString()}</span></td>
      <td style="text-align:right"><span class="reply-count">${p.replies}</span></td>
    </tr>
  `).join('');
}


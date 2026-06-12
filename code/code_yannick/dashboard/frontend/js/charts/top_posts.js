function renderPosts(kw) {
  const posts = postsData[kw] || postsData[KEYWORDS[0]] || [];
  const tbody = document.getElementById('posts-body');
  tbody.innerHTML = posts.map(p => `
    <tr>
      <td>
        <span class="platform-badge badge-${p.from_platform}">${p.from_platform}</span>
        <div style="color:var(--muted);font-size:11px;margin-top:3px">${p.instance_name}</div>
      </td>
      <td>
        <div class="post-content">${p.content.slice(0,180)}${p.content.length>180?'…':''}</div>
        <div class="post-meta">${p.created_at ? p.created_at.slice(0,10) : ''}</div>
      </td>
      <td style="text-align:right"><span class="like-count">${(p.likes_count||0).toLocaleString()}</span></td>
      <td style="text-align:right"><span class="reply-count">${p.replies_count||0}</span></td>
    </tr>
  `).join('');
}

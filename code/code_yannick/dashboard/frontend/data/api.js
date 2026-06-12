// dashboard/data/api.js
//
// Every function returns a Promise that resolves to the same shape
// the chart files already expect.

let KEYWORDS     = [];
let weeklyCounts = [];
let engData      = {};
let platformData = {};
let hashData     = {};
let postsData    = {};
const BASE = "";

const COLORS = [
  "#244383",
  "#0A224D",
  "#f7855c",
  "#c97cf5",
  "#f5d76e",
  "#60c8f5",
  "#ff7eb3"
];

async function get(path) {
    const res = await fetch(BASE + path);
    if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
    return res.json();
}

// List of distinct keywords from the DB — used to populate dropdowns.
// Returns: string[]
async function fetchKeywords() {
    return get("/api/keywords");
}

// Weekly post counts for one keyword or all.
// Returns: { [keywords]: [{ date, keywords, n_posts, n_posts_smooth }] }
async function fetchWeeklyCounts(keywords = "all") {
    const param = keywords === "all" ? "" : `?keywords=${encodeURIComponent(keywords)}`;
    const rows  = await get(`/api/weekly-counts${param}`);

    // group by keywords so charts can iterate series easily
    const grouped = {};
    for (const row of rows) {
        if (!grouped[row.keywords]) grouped[row.keywords] = [];
        grouped[row.keywords].push({ ...row, date: new Date(row.date) });
    }
    return grouped;
}

// Top hashtags for a keyword.
// Returns: [{ hashtag, freq }]
async function fetchHashtags(keywords, limit = 15) {
    return get(`/api/hashtags?keywords=${encodeURIComponent(keywords)}&limit=${limit}`);
}

// Engagement stats for a keyword.
// Returns: { avg_replies, avg_reblogs, avg_likes,
//             max_replies, max_reblogs, max_likes }
async function fetchEngagement(keywords) {
    console.log("fetching engagement for:", keywords);
    return get(`/api/engagement?keywords=${encodeURIComponent(keywords)}`);
}

// Post type + platform breakdown for a keywords.
// Returns: { originals, replies, by_platform: [{ platform, count }] }
async function fetchPostTypes(keywords) {
    return get(`/api/post-types?keywords=${encodeURIComponent(keywords)}`);
}

// Top posts by likes for a keywords.
// Returns: [{ post_id, created_at, from_platform, instance_name,
//              content, likes_count, replies_count, reblogs_count }]
async function fetchTopPosts(keywords, limit = 5) {
    return get(`/api/top-posts?keywords=${encodeURIComponent(keywords)}&limit=${limit}`);
}

async function fetchAll(keywords) {
  await Promise.all(keywords.map(async kw => {
    const [eng, types, hash, posts] = await Promise.all([
      fetchEngagement(kw),
      fetchPostTypes(kw),
      fetchHashtags(kw, 10),
      fetchTopPosts(kw, 5),
    ]);
    engData[kw]      = eng;
    platformData[kw] = types;
    hashData[kw]     = hash;
    postsData[kw]    = posts;
  }));

  const rows = await fetchWeeklyCounts("all");
  for (const [kw, data] of Object.entries(rows)) {
      weeklyCounts.push(...data.map(r => ({ ...r, keyword: r.keywords })));
  }
}

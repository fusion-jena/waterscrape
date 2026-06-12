const KEYWORDS = ["water flow", "water crisis", "water supply", "water pollution"];
const COLORS   = [
  "#6c8fff", "#4de8b4", "#f7855c", "#c97cf5",
  "#f5d76e", "#60c8f5", "#ff7eb3"
];

// weekly_counts equivalent
function makeWeekly(keyword, seed, baseline) {
  const dates = [];
  const start = new Date("2024-01-01");
  for (let i = 0; i < 52; i++) {
    const d = new Date(start); d.setDate(d.getDate() + i * 7);
    dates.push(d);
  }
  let rng = seed;
  function rand() { rng = (rng * 1664525 + 1013904223) & 0xffffffff; return (rng >>> 0) / 0xffffffff; }
  const raw = dates.map((_, i) => {
    const trend = baseline + i * 0.4;
    return Math.round(Math.max(0, trend + (rand() - 0.5) * baseline * 0.8));
  });
  const smooth = raw.map((v, i) => {
    const window = raw.slice(Math.max(0, i-3), i+4);
    return +(window.reduce((a,b)=>a+b,0)/window.length).toFixed(1);
  });
  return dates.map((date, i) => ({ date, keyword, n_posts: raw[i], n_posts_smooth: smooth[i] }));
}

const weeklyCounts = KEYWORDS.flatMap((kw, i) =>
  makeWeekly(kw, 12345 + i * 9999, 20 + i * 8)
);

// hashtags per keyword
const hashData = {
  "water flow": [["water",352],["dxrandoevent",285],["photography",196],["transparency",190],["fair_world",189],["climatechange",179],["carbontax",160],["pollution",147],["technology",136],["environment",135]],
  "water crisis":      [["llm",2300],["machinelearning",1980],["openai",1550],["chatgpt",1200],["generativeai",980],["deeplearning",760],["neuralnetworks",620],["aiethics",500],["agi",430],["fediverse",310]],
  "water supply":  [["mentalhealth",1650],["covid",1100],["publichealth",920],["nutrition",780],["exercise",650],["medicalresearch",540],["vaccines",480],["healthcare",420],["wellness",360],["pharmacy",290]],
  "water pollution": [["dataprotection",1400],["surveillance",1050],["gdpr",890],["encryption",740],["cybersecurity",630],["bigtech",510],["tracking",470],["anonymity",390],["vpn",320],["foss",270]],
};

// engagement stats per keyword
const engData = {
  "water flow": { avg_replies:0.6, avg_reblogs:2.4, avg_likes:7.3, max_replies:288, max_reblogs:2104, max_likes:7189, originals:17973, replies:7276 },
  "water crisis":      { avg_replies:5.8, avg_reblogs:22.1, avg_likes:34.2, max_replies:312, max_reblogs:2100, max_likes:3800, originals:9100, replies:2640 },
  "water supply":  { avg_replies:2.9, avg_reblogs:8.3,  avg_likes:14.1, max_replies:71, max_reblogs:540, max_likes:960, originals:5200, replies:1020 },
  "water pollution": { avg_replies:4.1, avg_reblogs:16.2, avg_likes:22.8, max_replies:128, max_reblogs:1100, max_likes:1900, originals:4400, replies:980 },
};

// top posts per keyword
const postsData = {
  "water flow": [
    { platform:"mastodon", instance:"fosstodon.org", date:"2024-08-12", likes:1240, replies:94, content:"New IPCC data confirms we are well past 1.5°C thresholds in regional averages. The window for meaningful action is narrower than ever — what are your local governments doing to respond? Thread 🧵" },
    { platform:"misskey",  instance:"misskey.io",    date:"2024-06-03", likes:980,  replies:61, content:"Remarkable satellite imagery shows the Greenland ice sheet losing 280 billion tonnes per year. This is not a future problem. It is happening now, and it is accelerating." },
    { platform:"mastodon", instance:"mastodon.social",date:"2024-03-22",likes:870,  replies:55, content:"A reminder that carbon capture at scale remains economically unviable. Reforestation + stopping deforestation remain the most cost-effective sinks we have." },
    { platform:"bluesky",  instance:"bsky.social",   date:"2024-11-01", likes:710,  replies:44, content:"COP29 draft text is weaker than COP28 on phasing out coal. Deeply disappointing. The fossil fuel lobby has its fingerprints all over this document." },
    { platform:"mastodon", instance:"mastodon.green", date:"2024-01-18", likes:640,  replies:38, content:"Solar installations hit a new global record in 2023 — 400 GW added in a single year. We can do this. The economics are now undeniable." },
  ],
  "water crisis": [
    { platform:"mastodon", instance:"sigmoid.social", date:"2024-09-05", likes:3800, replies:312, content:"The benchmark arms race is getting embarrassing. Every new model is 'state of the art' on some cherry-picked eval. We need standardized, adversarial, and independently run benchmarks — urgently." },
    { platform:"misskey",  instance:"misskey.io",     date:"2024-07-21", likes:2900, replies:198, content:"Spent the weekend reading the leaked training data analysis. The amount of scraped copyrighted material is staggering. The lawsuits are not going to go away." },
    { platform:"mastodon", instance:"fosstodon.org",  date:"2024-05-14", likes:2100, replies:154, content:"Open weights ≠ open source. Let's be precise with language. If you cannot inspect the training data, audit the pipeline, and reproduce the model, it is not open source." },
    { platform:"bluesky",  instance:"bsky.social",    date:"2024-10-30", likes:1750, replies:122, content:"Anthropic, OpenAI, and Google all lobbying against mandatory incident reporting. If these systems are safe, why the opposition to transparency requirements?" },
    { platform:"mastodon", instance:"tech.lgbt",      date:"2024-02-28", likes:1420, replies:99,  content:"Reminder that the 'AI is going to take all jobs' discourse almost always focuses on white-collar work. The automation of logistics, warehousing, and manufacturing has been ongoing for decades with far less media coverage." },
  ],
  "water supply": [
    { platform:"mastodon", instance:"mastodon.social", date:"2024-04-10", likes:960, replies:71, content:"Long COVID research is being chronically underfunded relative to the scale of disability it has caused. Millions of people are still waiting for answers." },
    { platform:"misskey",  instance:"misskey.io",      date:"2024-08-22", likes:740, replies:55, content:"New meta-analysis on ultra-processed food and all-cause mortality — the effect size is sobering. This should be a public health priority, not a lifestyle choice narrative." },
    { platform:"mastodon", instance:"social.coop",     date:"2024-06-15", likes:620, replies:43, content:"Universal basic health coverage is not expensive. The US spends more per capita on healthcare than countries with universal systems and gets worse outcomes." },
    { platform:"bluesky",  instance:"bsky.social",     date:"2024-11-10", likes:510, replies:38, content:"The GLP-1 drugs are remarkable but we need to talk about access. A medication that costs $15 to produce should not retail at $1,000/month." },
    { platform:"mastodon", instance:"mastodon.green",  date:"2024-03-01", likes:430, replies:29, content:"Air pollution causes approximately 7 million premature deaths per year globally. Climate and public health are the same fight." },
  ],
  "water pollution": [
    { platform:"mastodon", instance:"infosec.exchange", date:"2024-07-04", likes:1900, replies:128, content:"The EU Court ruling today guts Privacy Shield 3.0 the same way it did the first two. Transatlantic data transfers are in legal limbo again. Thread on what this means for US cloud providers ↓" },
    { platform:"misskey",  instance:"misskey.io",       date:"2024-09-18", likes:1450, replies:94,  content:"A reminder that 'we anonymize your data' is almost always false. Re-identification attacks on supposedly anonymous datasets have a near-perfect success rate when combined with auxiliary information." },
    { platform:"mastodon", instance:"fosstodon.org",    date:"2024-05-27", likes:1200, replies:80,  content:"End-to-end encryption is not a backdoor risk — it is the foundational security technology that protects banking, healthcare, and every secure communication. Weakening it for governments weakens it for everyone." },
    { platform:"bluesky",  instance:"bsky.social",      date:"2024-10-05", likes:980,  replies:66,  content:"New research shows ad-tech data brokers selling precise location data from reproductive health app users to anti-abortion advocacy groups. This was entirely foreseeable and preventable." },
    { platform:"mastodon", instance:"mastodon.social",  date:"2024-02-14", likes:820,  replies:55,  content:"FOSS alternatives exist for almost every mainstream app. The barrier is not technical — it is network effects and habit. Communities like the Fediverse prove the model works." },
  ],
};

// platform breakdown per keyword
const platformData = {
  "water flow": { originals:17973, replies:7276, mastodon:13245, misskey:0, bluesky:12004 },
  "water crisis":      { originals:9100, replies:2640, mastodon:7200, misskey:2400, bluesky:2140 },
  "water supply":  { originals:5200, replies:1020, mastodon:3800, misskey:1500, bluesky:920  },
  "water pollution": { originals:4400, replies:980,  mastodon:3200, misskey:1200, bluesky:980  },
};


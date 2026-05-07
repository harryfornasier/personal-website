/* ============================================================
   articles.js — master article list for Harry's Site
   ============================================================
   Add new entries at the TOP of the array (newest first).

   Fields:
     date    — display string shown on the page
     dateiso — YYYY-MM-DD (used to group by year on the archive page)
     title   — article headline
     href    — link to the article HTML file (use '#' if not yet published)
     excerpt — short teaser shown on homepage and archive
     tags    — array of tag strings
   ============================================================ */

var ARTICLES = [
  {
    date:    'November 12, 2024',
    dateiso: '2024-11-12',
    title:   'Running Snow Leopard as a Daily Driver in 2025',
    href:    'article.html',
    excerpt: 'Most people think you\'re mad for running a 2009 OS. Those people haven\'t experienced 10.6.8 on a maxed-out Core 2 Duo. It\'s fast, it\'s stable, and everything just works. Here\'s my current setup…',
    tags:    ['Mac OS X', 'Snow Leopard', 'Opinion']
  },
  {
    date:    'October 3, 2024',
    dateiso: '2024-10-03',
    title:   'My Film Photography Setup — What I Shoot and Why',
    href:    '#',
    excerpt: 'I picked up an Olympus OM-1 about two years ago on a whim and haven\'t looked back. There\'s something about the constraint of 36 exposures that makes you slow down and actually think about what you\'re shooting…',
    tags:    ['Photography', 'Film']
  },
  {
    date:    'August 28, 2024',
    dateiso: '2024-08-28',
    title:   'Notes on Learning to Cook Properly, Age 34',
    href:    '#',
    excerpt: 'I spent most of my twenties eating pasta and toast. At some point that stopped being acceptable. Here are some things I\'ve learned over the past year of actually trying to cook real food…',
    tags:    ['Cooking', 'Personal']
  },
  {
    date:    'July 15, 2024',
    dateiso: '2024-07-15',
    title:   'Hidden Mavericks Features Nobody Talks About Anymore',
    href:    '#',
    excerpt: 'OS X 10.9 Mavericks was a huge release — free OS upgrades, timer coalescing, App Nap — but there were a bunch of smaller changes buried in the system that barely got coverage at the time…',
    tags:    ['Mavericks', 'Mac OS X', 'Deep Dive']
  },
  {
    date:    'June 2, 2024',
    dateiso: '2024-06-02',
    title:   'Getting QuickLook Plugins Working on Older OS X Versions',
    href:    '#',
    excerpt: 'QuickLook is one of those features that once you use it you can never go back. But plugin support on Snow Leopard requires a bit of finagling. Here\'s my current plugin stack and how to install them…',
    tags:    ['QuickLook', 'Snow Leopard', 'Tutorial']
  },
  {
    date:    'April 18, 2024',
    dateiso: '2024-04-18',
    title:   'Weekend in the Peak District — Photo Essay',
    href:    '#',
    excerpt: 'Spent three days hiking around the Peak District with my Olympus. The weather was perfect, the light was incredible, and I managed to not lose any rolls of film. A good weekend all around…',
    tags:    ['Photography', 'Travel']
  },
  {
    date:    'March 8, 2024',
    dateiso: '2024-03-08',
    title:   'Why I Still Use TextMate in 2024',
    href:    '#',
    excerpt: 'Everyone\'s moved on to VS Code, but I\'m still happily using TextMate 1.5. It\'s fast, it\'s simple, and it does exactly what I need without any of the bloat. Here\'s why I haven\'t switched…',
    tags:    ['Mac OS X', 'Opinion']
  },
  {
    date:    'January 12, 2024',
    dateiso: '2024-01-12',
    title:   'Setting Up a Home Darkroom on a Budget',
    href:    '#',
    excerpt: 'Developing black and white film at home isn\'t as complicated or expensive as people think. Here\'s how I set up a basic darkroom in my bathroom for under £200…',
    tags:    ['Photography', 'Film', 'Tutorial']
  },
  {
    date:    'December 3, 2023',
    dateiso: '2023-12-03',
    title:   'Year in Review — 2023',
    href:    '#',
    excerpt: 'A look back at what I built, shot, and learned in 2023. More film photography, less social media, and a renewed appreciation for old software that just works…',
    tags:    ['Personal']
  },
  {
    date:    'October 20, 2023',
    dateiso: '2023-10-20',
    title:   'Scotland Highlands — Trip Report',
    href:    '#',
    excerpt: 'Two weeks in the Scottish Highlands with a backpack, a tent, and six rolls of Ilford HP5. Some thoughts on solo hiking and the joy of disconnecting completely…',
    tags:    ['Travel', 'Photography']
  },
  {
    date:    'August 15, 2023',
    dateiso: '2023-08-15',
    title:   'The Joy of Film Cameras That Don\'t Need Batteries',
    href:    '#',
    excerpt: 'There\'s something deeply satisfying about a camera that will still work in 50 years without any electronics. The Olympus OM-1 is one of those cameras…',
    tags:    ['Photography', 'Film']
  }
];

/* ============================================================
   Shared helpers — used by both index.html and articles.html
   ============================================================ */

/* Build the tag span HTML for one article */
function articleTagsHtml(tags) {
  var html = '';
  for (var i = 0; i < tags.length; i++) {
    html += '<span class="tag">' + tags[i] + '</span>';
  }
  return html;
}

/* Build a full article card (.article-item) */
function articleCardHtml(a) {
  return '<div class="article-item">' +
    '<div class="article-date">' + a.date + '</div>' +
    '<div class="article-title"><a href="' + a.href + '">' + a.title + '</a></div>' +
    '<div class="article-excerpt">' + a.excerpt + '</div>' +
    '<div class="article-tags">' + articleTagsHtml(a.tags) + '</div>' +
    '</div>';
}

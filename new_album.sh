#!/bin/bash
# =============================================================
#  new_album.sh — Create a new photo album for Harry's Site
# =============================================================
#
#  Usage:
#    ./new_album.sh <image-folder> "<Title>" "<Description>"
#
#  Example:
#    ./new_album.sh images/suffolk_coast \
#      "Suffolk Coast, March 2025" \
#      "A morning walk along the coast path near Dunwich."
#
#  What it does:
#    1. Generates 300x300 square thumbnails  -> <folder>/thumbs/
#    2. Generates 1100px-wide display images -> <folder>/medium/
#    3. Creates <albumname>.html             (album grid page)
#    4. Creates <albumname>_photo.html       (photo viewer — edit captions here)
#    5. Prints a card snippet to paste into gallery.html
#
#  Requirements: ImageMagick (brew install imagemagick)
# =============================================================

set -e

# ── Arguments ────────────────────────────────────────────────

FOLDER="${1%/}"    # strip any trailing slash
TITLE="$2"
DESC="${3:-No description provided.}"

if [ -z "$FOLDER" ] || [ -z "$TITLE" ]; then
  echo "Usage: $0 <image-folder> \"<Title>\" \"<Description>\""
  echo "Example: $0 images/suffolk_coast \"Suffolk Coast, March 2025\" \"A walk along the coast.\""
  exit 1
fi

if [ ! -d "$FOLDER" ]; then
  echo "Error: '$FOLDER' is not a directory."
  exit 1
fi

if ! command -v convert >/dev/null 2>&1; then
  echo "Error: ImageMagick not found. Install it with: brew install imagemagick"
  exit 1
fi

# Derive a clean album name from the folder (e.g. images/pin_mill -> pin_mill)
ALBUM=$(basename "$FOLDER")

# ── Find images ───────────────────────────────────────────────

IMAGES=()
for f in "$FOLDER"/*.JPG "$FOLDER"/*.jpg "$FOLDER"/*.JPEG "$FOLDER"/*.jpeg; do
  [ -f "$f" ] && IMAGES+=("$f")
done

COUNT=${#IMAGES[@]}

if [ "$COUNT" -eq 0 ]; then
  echo "Error: no JPEG files found in '$FOLDER'."
  exit 1
fi

echo ""
echo "Album:  $TITLE"
echo "Folder: $FOLDER"
echo "Photos: $COUNT"
echo ""

# ── Process images ────────────────────────────────────────────

mkdir -p "$FOLDER/thumbs" "$FOLDER/medium"

for f in "${IMAGES[@]}"; do
  NAME=$(basename "$f")
  STEM="${NAME%.*}"
  THUMB="$FOLDER/thumbs/${STEM}.jpg"
  MEDIUM="$FOLDER/medium/${STEM}.jpg"

  if [ ! -f "$THUMB" ]; then
    printf "  Thumbnail  %s\n" "$NAME"
    convert "$f" -thumbnail 300x300^ -gravity center -extent 300x300 -quality 82 "$THUMB"
  else
    printf "  Thumbnail  %s (exists, skipping)\n" "$NAME"
  fi

  if [ ! -f "$MEDIUM" ]; then
    printf "  Medium     %s\n" "$NAME"
    convert "$f" -resize 1100x -quality 82 "$MEDIUM"
  else
    printf "  Medium     %s (exists, skipping)\n" "$NAME"
  fi
done

echo ""

# ── Build the photo grid and JS array ────────────────────────
# These are assembled as strings and inserted into the templates below.

THUMB_GRID=""
PHOTOS_JS=""
FIRST_THUMB=""
i=1

for f in "${IMAGES[@]}"; do
  NAME=$(basename "$f")
  STEM="${NAME%.*}"

  [ $i -eq 1 ] && FIRST_THUMB="$FOLDER/thumbs/${STEM}.jpg"

  THUMB_GRID="${THUMB_GRID}
            <a href=\"${ALBUM}_photo.html#${i}\" class=\"photo-thumb\">
              <img src=\"../${FOLDER}/thumbs/${STEM}.jpg\" alt=\"Photo ${i}\">
            </a>"

  COMMA=$( [ $i -lt $COUNT ] && echo "," || echo "" )
  PHOTOS_JS="${PHOTOS_JS}
  {
    src:     '../${FOLDER}/medium/${STEM}.jpg',
    title:   'Photo ${i} — edit this title',
    caption: 'Caption for photo ${i} — edit this',
    desc:    'Description for photo ${i}. Open photos/${ALBUM}_photo.html and fill in the desc field for each photo in the array at the bottom of the page.'
  }${COMMA}"

  i=$((i + 1))
done

# ── Write album grid page ─────────────────────────────────────

cat > "photos/${ALBUM}.html" << ENDOFFILE
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="description" content="${TITLE}">
  <title>${TITLE} -- Harry's Site</title>
  <link rel="stylesheet" type="text/css" href="../style.css">
</head>
<body>

<div id="wrapper">

  <div id="header">
    <div id="header-inner">
      <div class="site-title">Harry<span>'s Site</span></div>
      <div class="site-subtitle">writing &middot; photography &middot; computers</div>
    </div>
  </div>

  <div id="navbar">
    <a class="nav-btn" href="../index.html">Home</a>
    <a class="nav-btn" href="../articles.html">Articles</a>
    <a class="nav-btn active" href="../gallery.html">Gallery</a>
    <a class="nav-btn" href="../about.html">About</a>
  </div>

  <div id="columns">

    <div id="left-sidebar">

      <div class="sidebar-box">
        <div class="sidebar-box-title">Album Info</div>
        <div class="sidebar-box-body setup-list">
          <b>Photos:</b> ${COUNT}<br>
          <br>
          <!-- Edit these details -->
          <b>Location:</b> ...<br>
          <b>Date:</b> ...<br>
          <b>Camera:</b> ...
        </div>
      </div>

      <div class="sidebar-box">
        <div class="sidebar-box-title">Albums</div>
        <div class="sidebar-box-body">
          <a class="sidebar-link" href="pin_mill.html">Pin Mill 2025</a>
          <!-- Add new album links here -->
        </div>
      </div>

      <div class="status-badges">
        <div class="badge-88 safari">Best viewed in <b>Safari</b></div>
        <div class="badge-88 osx">Powered by <b>Mac OS X</b></div>
      </div>

    </div><!-- /left-sidebar -->

    <div id="main-content">
      <div class="content-box">
        <div class="box-title-bar">
          <span>${TITLE}</span>
        </div>
        <div class="box-body">

          <p style="margin-bottom: 8px;">
            <a href="../gallery.html" style="font-size: 10px;">&larr; Back to albums</a>
          </p>

          <p style="margin-bottom: 12px;">${DESC}</p>

          <div class="photo-grid">
${THUMB_GRID}
          </div>

        </div>
      </div>
    </div><!-- /main-content -->

  </div><!-- /columns -->

  <div id="footer">
    &copy; 2026 Harry &nbsp;
    <span class="footer-divider">|</span>
    &nbsp;<a href="../about.html">About</a>&nbsp;
    <span class="footer-divider">|</span>
    &nbsp;<a href="mailto:fortune_plans.3n@icloud.com">Contact</a>&nbsp;
    <span class="footer-divider">|</span>
    &nbsp;<a href="../feed.xml">RSS</a>&nbsp;
    <br>
    <span class="footer-small">No cookies &middot; No tracking &middot; No nonsense</span>
  </div>

</div><!-- /wrapper -->

<script type="text/javascript" src="../scripts/script.js"></script>
</body>
</html>
ENDOFFILE

echo "Created photos/${ALBUM}.html"

# ── Write photo viewer page ───────────────────────────────────
# Write directly to file with cat — avoids the newline-stripping and
# backslash-mangling that happens when capturing a large heredoc into
# a variable and then echo-ing it.
#
# The unquoted ENDOFFILE delimiter is intentional: bash variables like
# ${TITLE}, ${COUNT}, ${ALBUM} and ${PHOTOS_JS} must expand here.
# The JS variables (p.src, photos.length, etc.) don't use $ syntax so
# they are not affected.

cat > "photos/${ALBUM}_photo.html" << ENDOFFILE
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="description" content="${TITLE} — photo viewer">
  <title>${TITLE} -- Harry's Site</title>
  <link rel="stylesheet" type="text/css" href="../style.css">
</head>
<body>

<div id="wrapper">

  <div id="header">
    <div id="header-inner">
      <div class="site-title">Harry<span>'s Site</span></div>
      <div class="site-subtitle">writing &middot; photography &middot; computers</div>
    </div>
  </div>

  <div id="navbar">
    <a class="nav-btn" href="../index.html">Home</a>
    <a class="nav-btn" href="../articles.html">Articles</a>
    <a class="nav-btn active" href="../gallery.html">Gallery</a>
    <a class="nav-btn" href="../about.html">About</a>
  </div>

  <div id="columns">

    <div id="left-sidebar">

      <div class="sidebar-box">
        <div class="sidebar-box-title">Photo Info</div>
        <div class="sidebar-box-body setup-list">
          <b>Album:</b> ${TITLE}<br>
          <br>
          <span id="sidebar-counter">Photo 1 of ${COUNT}</span>
        </div>
      </div>

      <div class="sidebar-box">
        <div class="sidebar-box-title">Album</div>
        <div class="sidebar-box-body">
          <a class="sidebar-link" href="${ALBUM}.html">${TITLE}</a>
        </div>
      </div>

      <div class="sidebar-box">
        <div class="sidebar-box-title">Albums</div>
        <div class="sidebar-box-body">
          <a class="sidebar-link" href="pin_mill.html">Pin Mill 2025</a>
          <!-- Add new album links here -->
        </div>
      </div>

      <div class="status-badges">
        <div class="badge-88 safari">Best viewed in <b>Safari</b></div>
        <div class="badge-88 osx">Powered by <b>Mac OS X</b></div>
      </div>

    </div><!-- /left-sidebar -->

    <div id="main-content">
      <div class="content-box">
        <div class="box-title-bar">
          <span id="photo-title">${TITLE}</span>
        </div>
        <div class="box-body">

          <p style="margin-bottom: 10px; font-size: 10px;">
            <a href="${ALBUM}.html">&larr; Back to album</a>
          </p>

          <div class="photo-viewer">

            <div class="photo-main">
              <img id="photo-img" src="" alt="">
            </div>

            <div id="photo-caption" class="photo-caption"></div>

            <div class="photo-nav">
              <a href="#" id="btn-prev">&larr; Previous</a>
              <span id="photo-counter" style="font-size: 10px; color: #666666;">Photo 1 of ${COUNT}</span>
              <a href="#" id="btn-next">Next &rarr;</a>
            </div>

          </div>

          <p id="photo-desc" style="margin-top: 14px; padding-top: 10px; border-top: 1px solid #cccccc; font-size: 12px;"></p>

        </div>
      </div>
    </div><!-- /main-content -->

  </div><!-- /columns -->

  <div id="footer">
    &copy; 2026 Harry &nbsp;
    <span class="footer-divider">|</span>
    &nbsp;<a href="../about.html">About</a>&nbsp;
    <span class="footer-divider">|</span>
    &nbsp;<a href="mailto:fortune_plans.3n@icloud.com">Contact</a>&nbsp;
    <span class="footer-divider">|</span>
    &nbsp;<a href="../feed.xml">RSS</a>&nbsp;
    <br>
    <span class="footer-small">No cookies &middot; No tracking &middot; No nonsense</span>
  </div>

</div><!-- /wrapper -->

<script type="text/javascript" src="../scripts/script.js"></script>
<script type="text/javascript">
/* ── PHOTO DATA ──────────────────────────────────────────────
   Edit the title, caption and desc for each photo below.
   Do not change src — that points to the generated image file.
   To add more photos later: add to the array and re-run the
   script, or just add a new entry manually following the pattern.
   ──────────────────────────────────────────────────────────── */

var photos = [${PHOTOS_JS}
];

/* ── VIEWER — no need to edit below this line ────────────── */

var current = 0;

function showPhoto(n) {
  var p = photos[n];
  current = n;

  document.getElementById('photo-img').src         = p.src;
  document.getElementById('photo-img').alt         = p.caption;
  document.getElementById('photo-title').innerHTML     = p.title;
  document.getElementById('photo-caption').innerHTML   = p.caption;
  document.getElementById('photo-desc').innerHTML      = p.desc;

  var label = 'Photo ' + (n + 1) + ' of ' + photos.length;
  document.getElementById('photo-counter').innerHTML   = label;
  document.getElementById('sidebar-counter').innerHTML = label;

  document.getElementById('btn-prev').style.visibility = (n === 0) ? 'hidden' : 'visible';
  document.getElementById('btn-next').style.visibility = (n === photos.length - 1) ? 'hidden' : 'visible';

  document.title = p.title + ' -- ${TITLE} -- Harry\'s Site';
}

function getStartIndex() {
  var hash = window.location.hash;
  if (hash && hash.length > 1) {
    var n = parseInt(hash.substring(1), 10) - 1;
    if (!isNaN(n) && n >= 0 && n < photos.length) { return n; }
  }
  return 0;
}

document.getElementById('btn-prev').onclick = function () {
  if (current > 0) { showPhoto(current - 1); }
  return false;
};

document.getElementById('btn-next').onclick = function () {
  if (current < photos.length - 1) { showPhoto(current + 1); }
  return false;
};

showPhoto(getStartIndex());
</script>

</body>
</html>
ENDOFFILE

echo "Created photos/${ALBUM}_photo.html"

# ── Print the gallery.html card snippet ───────────────────────

echo ""
echo "================================================================"
echo " Done! One step left: add this card to gallery.html"
echo "================================================================"
echo ""
echo "            <a href=\"photos/${ALBUM}.html\" class=\"album-card\">"
echo "              <div class=\"album-thumb\" style=\"background-image: url('${FIRST_THUMB}');\"></div>"
echo "              <div class=\"album-info\">"
echo "                <div class=\"album-title\">${TITLE}</div>"
echo "                <div class=\"album-meta\">${COUNT} photos</div>"
echo "              </div>"
echo "            </a>"
echo ""
echo "================================================================"
echo " Then open photos/${ALBUM}_photo.html and fill in the captions"
echo " and descriptions in the photos array at the bottom."
echo "================================================================"
echo ""

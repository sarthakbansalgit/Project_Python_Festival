const state = { festival: null, venues: [], artists: [], programme: [] };
const kindLabels = { solo: "Solo", lineup: "Lineup", workshop: "Workshop" };

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  return response.json();
}

function get(id) {
  return document.getElementById(id);
}

function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  }[character]));
}

function showSubtitle(item) {
  if (item.kind === "solo") return `With ${item.artist_name}`;
  if (item.kind === "lineup") return `Hosted by ${item.host_name}`;
  return `By ${item.teacher_name}`;
}

function renderProgramme() {
  const day = get("day-filter").value;
  const venue = get("venue-filter").value;
  const search = get("search-filter").value.trim().toLowerCase();
  const visible = state.programme.filter((item) => {
    const matchesDay = day === "all" || item.day === day;
    const matchesVenue = venue === "all" || item.venue_slug === venue;
    const text = `${item.title} ${showSubtitle(item)} ${item.venue_name}`.toLowerCase();
    return matchesDay && matchesVenue && (search === "" || text.includes(search));
  });
  const list = get("programme-list");
  list.innerHTML = visible.length ? visible.map((item) => `
    <article class="show-card">
      <div>
        <div class="show-time">${safeText(item.time)}</div>
        <div class="show-day">${safeText(item.day.slice(5).replace("-", " / "))}</div>
      </div>
      <div>
        <h3>${safeText(item.title)}</h3>
        <p class="show-details">${safeText(showSubtitle(item))}</p>
        <p class="show-details">${safeText(item.venue_name)}</p>
        <p class="show-description">${safeText(item.description || "A fresh performance waiting for you.")}</p>
      </div>
      <span class="show-type">${safeText(kindLabels[item.kind])}</span>
    </article>
  `).join("") : '<p class="empty-state">No performances match that search. Try another little adventure.</p>';
}

function renderHeader() {
  get("festival-name").innerHTML = "A little more <em>joy.</em>";
  get("festival-dates").textContent = `${state.festival.first_day} to ${state.festival.last_day} · Four days of comedy, conversation and happy accidents by the sea.`;
  get("stat-shows").textContent = state.programme.length;
  get("stat-artists").textContent = state.artists.length;
  get("stat-venues").textContent = state.venues.length;
}

function renderVenues() {
  get("venue-list").innerHTML = state.venues.map((venue, index) => `
    <article class="venue-card">
      <span class="venue-number">0${index + 1}</span>
      <h3>${safeText(venue.name)}</h3>
      <p>${safeText(venue.address)}<br />${safeText(venue.capacity)} seats</p>
    </article>
  `).join("");
}

function renderArtists() {
  get("artist-list").innerHTML = state.artists.slice(0, 8).map((artist) => `
    <article class="artist-card">
      <div class="artist-initial">${safeText(artist.name.charAt(0))}</div>
      <h3>${safeText(artist.name)}</h3>
      <p>${safeText(artist.bio)}</p>
    </article>
  `).join("");
}

function populateFilters() {
  get("day-filter").innerHTML = '<option value="all">All festival days</option>' +
    state.festival.days.map((day) => `<option value="${day}">${day}</option>`).join("");
  get("venue-filter").innerHTML = '<option value="all">Every venue</option>' +
    state.venues.map((venue) => `<option value="${venue.slug}">${safeText(venue.name)}</option>`).join("");
}

function serializeForm(form) {
  const data = new FormData(form);
  const value = (key) => data.get(key)?.toString().trim();
  const payload = {
    kind: value("kind"), title: value("title"), venue: value("venue"),
    start: value("start"), duration_minutes: Number(value("duration_minutes")),
    description: value("description") || "",
  };
  for (const key of ["artist", "host", "teacher"]) if (value(key)) payload[key] = value(key);
  if (value("acts")) payload.acts = value("acts").split(",").map((item) => item.trim()).filter(Boolean);
  if (value("max_participants")) payload.max_participants = Number(value("max_participants"));
  if (value("min_age")) payload.min_age = Number(value("min_age"));
  return payload;
}

function wireForm() {
  get("add-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = get("form-message");
    message.textContent = "Saving your show…";
    try {
      await fetchJson("/api/programme", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(serializeForm(event.currentTarget)),
      });
      state.programme = await fetchJson("/api/programme");
      renderHeader();
      renderProgramme();
      event.currentTarget.reset();
      message.textContent = "Saved. The programme has been updated.";
    } catch (error) {
      message.textContent = `Could not save: ${error.message}`;
    }
  });
}

async function init() {
  [state.festival, state.venues, state.artists, state.programme] = await Promise.all([
    fetchJson("/api/festival"), fetchJson("/api/venues"),
    fetchJson("/api/artists"), fetchJson("/api/programme"),
  ]);
  renderHeader();
  populateFilters();
  renderProgramme();
  renderVenues();
  renderArtists();
  ["day-filter", "venue-filter", "search-filter"].forEach((id) => get(id).addEventListener("input", renderProgramme));
  wireForm();
}

init().catch((error) => {
  get("festival-name").textContent = "The festival is taking a tiny break.";
  get("festival-dates").textContent = error.message;
});

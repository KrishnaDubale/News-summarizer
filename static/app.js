const form = document.getElementById("news-form");
const responsePanel = document.getElementById("response-panel");
const queryInput = document.getElementById("query");

function renderLoading(query) {
  responsePanel.className = "response-panel";
  responsePanel.innerHTML = `
    <div class="status-row">
      <span class="status-badge">Working</span>
      <span class="status-query">${query}</span>
    </div>
    <p>Fetching articles and preparing a summary...</p>
  `;
}

function renderResponse(data) {
  responsePanel.className = `response-panel ${data.mode}`;
  const topic = data.topic ? `<p class="topic">Topic: ${data.topic}</p>` : "";
  const highlights = data.highlights.length
    ? `<ul class="highlights">${data.highlights
        .map((item) => `<li>${item}</li>`)
        .join("")}</ul>`
    : '<p class="muted">No highlights available.</p>';
  const articles = data.articles.length
    ? `<div class="article-list">${data.articles
        .map(
          (article) => `
            <a class="article-card" href="${article.url}" target="_blank" rel="noreferrer">
              <p class="article-source">${article.source}</p>
              <h3>${article.title}</h3>
              <p class="article-date">${article.published_at || "Unknown date"}</p>
            </a>
          `
        )
        .join("")}</div>`
    : '<p class="muted">No linked articles to show.</p>';
  const error = data.error ? `<p class="error-text">${data.error}</p>` : "";

  responsePanel.innerHTML = `
    <div class="status-row">
      <span class="status-badge">${data.mode}</span>
      <span class="status-query">${data.query}</span>
    </div>
    ${topic}
    <p class="summary">${data.summary}</p>
    <h2>Key points</h2>
    ${highlights}
    <h2>Source articles</h2>
    ${articles}
    ${error}
  `;
}

function renderError(message) {
  responsePanel.className = "response-panel error";
  responsePanel.innerHTML = `
    <div class="status-row">
      <span class="status-badge">error</span>
    </div>
    <p class="summary">${message}</p>
  `;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) {
    return;
  }

  renderLoading(query);

  try {
    const response = await fetch("/summarize-news", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    renderResponse(data);
  } catch (error) {
    renderError(error.message || "Something went wrong while fetching the summary.");
  }
});

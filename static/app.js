(() => {
  const reportList = document.getElementById("report-list");
  const reportCount = document.getElementById("report-count");
  const titleNode = document.getElementById("report-title");
  const summaryNode = document.getElementById("report-summary");
  const generatedAtNode = document.getElementById("report-generated-at");
  const newsCountNode = document.getElementById("news-count");
  const updatesListNode = document.getElementById("updates-list");
  const insightListNode = document.getElementById("insight-list");
  const ideaGridNode = document.getElementById("idea-grid");

  if (!reportList || !titleNode) {
    return;
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function parseDate(value) {
    const parsed = new Date(value || "");
    if (Number.isNaN(parsed.getTime())) {
      return "";
    }
    return parsed.toISOString().slice(0, 10);
  }

  async function fetchJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Failed to fetch ${path}: ${response.status}`);
    }
    return response.json();
  }

  function renderSidebar(reports) {
    reportCount.textContent = String(reports.length);

    if (!reports.length) {
      reportList.innerHTML =
        '<div class="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-4 text-sm text-zinc-400">No reports found in /data.</div>';
      return;
    }

    reportList.innerHTML = reports
      .map(
        (report) => `
          <button
            type="button"
            data-report-id="${escapeHtml(report.file_name)}"
            class="report-card group w-full rounded-2xl border border-zinc-800 bg-zinc-900/70 p-4 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-cyan-400/40 hover:bg-zinc-800/80 hover:shadow-xl"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-zinc-400">${escapeHtml(report.generated_date || parseDate(report.generated_at))}</span>
              <span class="rounded-full border border-zinc-700 bg-zinc-950 px-2 py-0.5 text-[11px] text-zinc-400">${escapeHtml(report.generated_year || (report.generated_at || "").slice(0, 4))}</span>
            </div>
            <p class="mt-2 max-h-10 overflow-hidden text-sm font-medium leading-5 text-zinc-100">${escapeHtml(report.title || "Research Report")}</p>
          </button>
        `
      )
      .join("");
  }

  function setActiveButton(reportId) {
    reportList.querySelectorAll(".report-card").forEach((button) => {
      const isActive = button.dataset.reportId === reportId;
      button.classList.toggle("active", isActive);
      button.classList.toggle("ring-1", isActive);
      button.classList.toggle("ring-cyan-400/60", isActive);
      button.classList.toggle("border-cyan-500/30", isActive);
      button.classList.toggle("bg-zinc-800/90", isActive);
      if (!isActive) {
        button.classList.remove("ring-cyan-400/60", "border-cyan-500/30", "bg-zinc-800/90");
      }
    });
  }

  function renderUpdates(items) {
    if (!items.length) {
      updatesListNode.innerHTML =
        '<div class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 text-sm text-zinc-400">No updates available.</div>';
      return;
    }

    updatesListNode.innerHTML = items
      .map(
        (item, index) => `
          <article class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 transition hover:border-cyan-400/30">
            <div class="flex items-start gap-3">
              <div class="mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-cyan-500/20 text-xs font-semibold text-cyan-200">${index + 1}</div>
              <div>
                <h4 class="text-sm font-semibold text-zinc-100 sm:text-base">${escapeHtml(item.title)}</h4>
                <p class="mt-1 text-xs text-zinc-500">${escapeHtml(item.source)} · ${escapeHtml((item.published_at || "").slice(0, 10))}</p>
                <p class="mt-2 text-sm leading-6 text-zinc-300">${escapeHtml(item.summary || "")}</p>
              </div>
            </div>
          </article>
        `
      )
      .join("");
  }

  function renderInsights(analysis) {
    const trends = (analysis.key_trends || []).map(
      (item) => `
        <article class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 transition hover:border-emerald-400/30">
          <h4 class="text-sm font-semibold text-zinc-100 sm:text-base">${escapeHtml(item.trend)}</h4>
          <p class="mt-2 text-sm leading-6 text-zinc-300">${escapeHtml(item.detail)}</p>
        </article>
      `
    );

    const companyUpdates = (analysis.company_product_moves || analysis.company_product_updates || []).map(
      (item) => `
        <article class="rounded-xl border border-zinc-800 bg-zinc-950/50 p-4 transition hover:border-emerald-400/30">
          <h4 class="text-sm font-semibold text-zinc-100 sm:text-base">${escapeHtml(item.company_or_product)}</h4>
          <p class="mt-2 text-sm leading-6 text-zinc-300">${escapeHtml(item.move || item.update)}</p>
        </article>
      `
    );

    insightListNode.innerHTML = [...trends, ...companyUpdates].join("");
    if (!insightListNode.innerHTML.trim()) {
      insightListNode.innerHTML =
        '<div class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 text-sm text-zinc-400">No insights available.</div>';
    }
  }

  function renderIdeas(ideas) {
    if (!ideas.length) {
      ideaGridNode.innerHTML =
        '<div class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 text-sm text-zinc-400">No startup ideas available.</div>';
      return;
    }

    ideaGridNode.innerHTML = ideas
      .map(
        (idea) => `
          <article class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 transition hover:border-fuchsia-400/30">
            <h4 class="text-sm font-semibold text-zinc-100 sm:text-base">${escapeHtml(idea.name)}</h4>
            <p class="mt-2 text-sm leading-6 text-zinc-300">${escapeHtml(idea.description)}</p>
          </article>
        `
      )
      .join("");
  }

  function renderReport(reportMeta, reportPayload) {
    const analysis = reportPayload.analysis || {};
    const newsItems = reportPayload.news_items || [];

    titleNode.textContent = reportMeta.generated_date || parseDate(reportMeta.generated_at) || "Report";
    summaryNode.textContent = analysis.overall_summary || analysis.top_10_summary || "No summary available.";
    generatedAtNode.textContent = reportMeta.generated_at || "-";
    newsCountNode.textContent = String(newsItems.length);

    renderUpdates(newsItems);
    renderInsights(analysis);
    renderIdeas(analysis.startup_ideas || []);
    setActiveButton(reportMeta.file_name);
  }

  async function loadReportById(reportMetaById, reportId) {
    const reportMeta = reportMetaById.get(reportId);
    if (!reportMeta) {
      return;
    }
    const payload = await fetchJson(`/data/${reportMeta.file_name}`);
    renderReport(reportMeta, payload);
  }

  async function init() {
    try {
      const index = await fetchJson("/data/index.json");
      const reports = Array.isArray(index.reports) ? index.reports : [];
      reports.sort((a, b) => (a.generated_at < b.generated_at ? 1 : -1));

      renderSidebar(reports);
      if (!reports.length) {
        return;
      }

      const reportMetaById = new Map(reports.map((report) => [report.file_name, report]));
      const params = new URLSearchParams(window.location.search);
      const requested = params.get("report");
      const selectedId = requested && reportMetaById.has(requested) ? requested : reports[0].file_name;

      await loadReportById(reportMetaById, selectedId);

      reportList.addEventListener("click", async (event) => {
        const button = event.target.closest(".report-card");
        if (!button) {
          return;
        }

        const reportId = button.dataset.reportId;
        if (!reportId) {
          return;
        }

        try {
          await loadReportById(reportMetaById, reportId);
          const url = new URL(window.location.href);
          url.searchParams.set("report", reportId);
          window.history.replaceState({}, "", url);
        } catch (error) {
          console.error(error);
        }
      });
    } catch (error) {
      console.error(error);
      reportList.innerHTML =
        '<div class="rounded-2xl border border-red-700/40 bg-red-900/20 p-4 text-sm text-red-200">Failed to load /data/index.json. Run the backend once to generate report index.</div>';
      titleNode.textContent = "Unable to load reports";
      summaryNode.textContent = "Check that /data/index.json exists and you are serving this app over HTTP.";
    }
  }

  init();
})();

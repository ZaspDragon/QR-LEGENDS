const MODULES = [
  ["Control Center", "/main_dashboard", "CC"],
  ["Receiving", "/receiving", "RC"],
  ["Putaway", "/putaway", "PA"],
  ["Inventory", "/inventory_hub", "IN"],
  ["Replenishment", "/replenishment", "RP"],
  ["Picking", "/order_picking", "PK"],
  ["Shipping", "/shipping", "SH"],
  ["Labor", "/labor_management", "LB"],
  ["Safety", "/safety_protocols", "SF"],
  ["Reports", "/reports_hub", "RE"],
  ["Administration", "/admin_hub", "AD"]
];

const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
}[char]));

function renderNavigation() {
  $("#primary-nav").innerHTML = MODULES.map(([label, href, icon], index) => `
    <a href="${href}" class="${index === 0 ? "active" : ""}">
      <span class="nav-icon">${icon}</span><span>${label}</span>
    </a>`).join("");
}

function renderKpis(items) {
  $("#kpis").innerHTML = items.map((item) => `
    <article class="card kpi ${escapeHtml(item.tone)}">
      <div class="kpi-label">${escapeHtml(item.label)}</div>
      <div class="kpi-value">${escapeHtml(item.value)}<small>${escapeHtml(item.unit)}</small></div>
      <div class="target"><span>Target</span><b>${escapeHtml(item.target)}</b></div>
      <div class="meter"><span style="width:${Math.min(100, Number(item.value) || 86)}%"></span></div>
    </article>`).join("");
}

function renderWorkload(items) {
  $("#workload").innerHTML = items.map((item) => `
    <a class="card workload ${escapeHtml(item.tone)}" href="${escapeHtml(item.href)}">
      <span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.value)}</strong>
    </a>`).join("");
}

function renderExceptions(items) {
  $("#exceptions").innerHTML = items.length ? items.map((item) => `
    <a class="exception" href="${escapeHtml(item.href)}">
      <i class="severity ${escapeHtml(item.severity)}"></i>
      <div><div class="row-title">${escapeHtml(item.title)}</div>
      <div class="row-meta">${escapeHtml(item.type)} · ${escapeHtml(item.detail)}</div></div>
      <span class="location">${escapeHtml(item.location)}</span>
    </a>`).join("") : '<div class="empty">No open exceptions.</div>';
}

function renderTasks(items) {
  $("#late-tasks").innerHTML = items.length ? items.map((item) => `
    <a class="task" href="${escapeHtml(item.href)}">
      <span class="priority ${escapeHtml(item.priority)}">${escapeHtml(item.priority)}</span>
      <div><div class="row-title">${escapeHtml(item.task)}</div>
      <div class="row-meta">${escapeHtml(item.owner)}</div></div>
      <span class="task-age">${escapeHtml(item.age)}</span>
    </a>`).join("") : '<div class="empty">No late tasks.</div>';
}

function renderSummary(summary, receipts) {
  const rows = [
    ["SKUs tracked", summary.sku_count],
    ["Units on hand", Number(summary.units_on_hand).toLocaleString()],
    ["Open receipts", receipts],
    ["Quality holds", summary.quality_holds, summary.quality_holds ? "alert" : ""],
    ["Negative inventory", summary.negative_inventory, summary.negative_inventory ? "alert" : ""],
    ["Empty pick faces", summary.empty_pick_faces, summary.empty_pick_faces ? "alert" : ""]
  ];
  $("#inventory-summary").innerHTML = rows.map(([label, value, tone]) => `
    <div class="summary-row"><span>${escapeHtml(label)}</span><strong class="${tone || ""}">${escapeHtml(value)}</strong></div>
  `).join("");
}

function renderAi(items) {
  $("#ai-readiness").innerHTML = items.map((item) => `
    <div class="ai-item"><b>${escapeHtml(item.name)}</b><span>${escapeHtml(item.status)}</span></div>
  `).join("");
}

async function loadControlCenter() {
  try {
    const response = await fetch("/api/warehouse-os/control-center", { credentials: "same-origin" });
    if (!response.ok) throw new Error(`Control Center returned ${response.status}`);
    const data = await response.json();
    renderKpis(data.kpis);
    renderWorkload(data.workload);
    renderExceptions(data.exceptions);
    renderTasks(data.late_tasks);
    renderSummary(data.inventory_summary, data.open_receipts);
    renderAi(data.ai_readiness);
    $("#warehouse-name").textContent = data.warehouse;
    $("#shift-name").textContent = data.shift;
    $("#user-role").textContent = String(data.user.role).replaceAll("_", " ");
    $("#updated").textContent = `Updated ${new Date(data.generated_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
    document.querySelectorAll(".loading").forEach((element) => element.classList.remove("loading"));
  } catch (error) {
    console.error(error);
    $("#exceptions").innerHTML = '<div class="empty">Operational data is temporarily unavailable. Existing modules remain accessible.</div>';
  }
}

function bindSearch() {
  const input = $("#command-search");
  input.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") return;
    const query = input.value.trim().toLowerCase();
    const match = MODULES.find(([label]) => label.toLowerCase().includes(query));
    if (match) window.location.href = match[1];
  });
}

renderNavigation();
bindSearch();
$("#menu-button").addEventListener("click", () => document.body.classList.toggle("nav-open"));
document.addEventListener("click", (event) => {
  if (event.target.closest(".sidebar") || event.target.closest("#menu-button")) return;
  document.body.classList.remove("nav-open");
});
loadControlCenter();
setInterval(loadControlCenter, 60000);

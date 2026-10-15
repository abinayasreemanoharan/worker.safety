
let incidents = [];
let zoneViolations = 0;
let ppeViolations = 0;
let sosActive = false;

document.getElementById("workerImage").addEventListener("change", function () {
  const file = this.files[0];

  if (!file) return;

  if (!file.type.startsWith("image/")) {
    alert("Please choose an image file.");
    return;
  }

  const reader = new FileReader();

  reader.onload = function () {
    const img = document.getElementById("preview");
    img.src = reader.result;
    img.style.display = "block";
  };

  reader.readAsDataURL(file);
});

function addIncident(name, priority, action) {
  incidents.unshift({
    time: new Date().toLocaleTimeString(),
    name: name,
    priority: priority,
    action: action,
    status: "Open"
  });

  renderIncidents();
  updateRisk();
}

function checkPPE() {
  // Demo only: this does not analyze the uploaded image.
  const missingHelmet = Math.random() < 0.5;
  const missingVest = Math.random() < 0.5;

  if (missingHelmet || missingVest) {
    ppeViolations++;

    let missing = [];
    if (missingHelmet) missing.push("helmet");
    if (missingVest) missing.push("safety vest");

    document.getElementById("ppeResult").textContent =
      "DEMO alert: " + missing.join(" and ") + " missing (simulated).";

    addIncident(
      "PPE demo violation",
      "Medium",
      "Supervisor to verify PPE before work continues."
    );
  } else {
    document.getElementById("ppeResult").textContent =
      "Demo result: no violation simulated. This is not AI detection.";
  }
}

function zoneAlert() {
  zoneViolations++;

  document.getElementById("location").textContent = "Crane Zone";
  document.getElementById("zoneResult").textContent =
    "⚠ ALERT: Simulated worker entered a restricted zone!";

  document.getElementById("worker").style.left = "72%";
  document.getElementById("worker").style.top = "55%";

  addIncident(
    "Restricted-zone entry",
    "High",
    "Verify worker safety and clear the restricted zone."
  );
}

function sendSOS() {
  if (sosActive) return;

  sosActive = true;
  document.getElementById("sosResult").textContent =
    "🚨 DEMO SOS ACTIVE — supervisor action required.";

  addIncident(
    "Worker SOS activated",
    "High",
    "Contact worker and follow site emergency procedures."
  );
}

function resolveSOS() {
  if (!sosActive) {
    document.getElementById("sosResult").textContent =
      "No active demo emergency.";
    return;
  }

  sosActive = false;

  document.getElementById("sosResult").textContent =
    "SOS marked resolved in this demo.";

  const incident = incidents.find(
    item => item.name === "Worker SOS activated" &&
            item.status === "Open"
  );

  if (incident) incident.status = "Resolved";

  renderIncidents();
  updateRisk();
}

function renderIncidents() {
  const table = document.getElementById("incidentList");
  table.innerHTML = "";

  incidents.forEach(item => {
    const row = document.createElement("tr");

    [
      item.time,
      item.name,
      item.priority,
      item.action,
      item.status
    ].forEach(value => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    });

    table.appendChild(row);
  });

  document.getElementById("openCount").textContent =
    incidents.filter(item => item.status === "Open").length;
}

function updateRisk() {
  const openCount = incidents.filter(
    item => item.status === "Open"
  ).length;

  const score = Math.min(
    100,
    10 + openCount * 5 + zoneViolations * 20 + ppeViolations * 10
  );

  document.getElementById("risk").textContent = score + "/100";
  document.getElementById("riskDetail").textContent = score + "/100";
  document.getElementById("riskBar").style.width = score + "%";

  const message = document.getElementById("riskMessage");

  if (score >= 60) {
    message.textContent = "HIGH RISK — urgent supervisor review required.";
    document.getElementById("riskBar").style.background = "#ff596d";
  } else if (score >= 30) {
    message.textContent = "MEDIUM RISK — review active incidents.";
    document.getElementById("riskBar").style.background = "#ffb454";
  } else {
    message.textContent = "LOW RISK — continue routine monitoring.";
    document.getElementById("riskBar").style.background = "#35d49a";
  }
}

function exportCSV() {
  if (incidents.length === 0) {
    alert("No incidents to export yet.");
    return;
  }

  const headers = ["Time", "Incident", "Priority", "Action", "Status"];

  const rows = incidents.map(item =>
    [item.time, item.name, item.priority, item.action, item.status]
  );

  const csv = [headers, ...rows]
    .map(row => row.map(value =>
      '"' + String(value).replace(/"/g, '""') + '"'
    ).join(","))
    .join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "siteguard-incidents.csv";
  link.click();

  URL.revokeObjectURL(url);
}




   

 

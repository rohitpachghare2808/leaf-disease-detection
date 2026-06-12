function login() {
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const email = emailInput.value.trim();
  const password = passwordInput.value.trim();

  const errorDiv = document.getElementById("login-error");
  errorDiv.classList.add("hidden");

  if (!email || !password) {
    const errorText = document.getElementById("login-error-text");
    errorText.innerHTML = "Please enter both email and password.";
    errorDiv.classList.remove("hidden");
    return;
  }

  fetch("http://127.0.0.1:5000/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  })
    .then(async (res) => {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Login failed");
      return data;
    })
    .then(() => {
      document.getElementById("auth-page").classList.remove("active-page");
      document.getElementById("home-page").classList.add("active-page");
      loadHistory();
    })
    .catch((err) => {
      const errorDiv = document.getElementById("login-error");
      const errorText = document.getElementById("login-error-text");

      let errorMessage = err && err.message ? err.message : "Invalid login.";
      if (errorMessage === "Failed to fetch") {
        errorMessage = "Connection failed. Please ensure the backend is running (<code>python backend/app.py</code>) AND you are using <a href='http://127.0.0.1:5000/' class='underline text-blue-600 font-bold'>http://127.0.0.1:5000/</a> instead of double-clicking the HTML file.";
      }
      errorText.innerHTML = `${errorMessage}<br><br><span class="font-semibold text-xs text-red-800">Demo login:<br>Email: leafcare@example.com<br>Password: leaf123</span>`;

      errorDiv.classList.remove("hidden");
    });
}

// Toggle side menu visibility
function toggleMenu() {
  const menu = document.getElementById("side-menu");
  if (!menu) return;
  if (menu.classList.contains("-translate-x-full")) {
    menu.classList.remove("-translate-x-full");
  } else {
    menu.classList.add("-translate-x-full");
  }
}

// Attach click handler to top-left menu button and check auth status
document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  if (menuToggle) {
    menuToggle.addEventListener("click", toggleMenu);
  }

  // Check if we are already logged in
  fetch("http://127.0.0.1:5000/me", { credentials: "include" })
    .then(res => res.json())
    .then(data => {
      if (data.ok) {
        document.getElementById("auth-page").classList.remove("active-page");
        document.getElementById("home-page").classList.add("active-page");
        loadHistory();
      }
    })
    .catch(err => console.log("Not logged in or backend off:", err));
});

// Back button from history to dashboard
function backToDashboard() {
  switchTab("home");
}

// Logout back to login screen
function logout() {
  fetch("http://127.0.0.1:5000/logout", { method: "POST", credentials: "include" }).finally(() => {
    document.getElementById("home-page").classList.remove("active-page");
    document.getElementById("auth-page").classList.add("active-page");
  });
}

function switchTab(tab) {
  const dashboard = document.getElementById("dashboard-view");
  const history = document.getElementById("history-view");
  const resultView = document.getElementById("result-view");

  if (dashboard) dashboard.classList.add("hidden");
  if (history) history.classList.add("hidden");
  if (resultView) resultView.classList.add("hidden");

  if (tab === "home" && dashboard) {
    dashboard.classList.remove("hidden");
  } else if (tab === "history" && history) {
    history.classList.remove("hidden");
  } else if (tab === "result" && resultView) {
    resultView.classList.remove("hidden");
  }
}

function triggerUpload() {
  document.getElementById("file-input").click()
}

function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  event.target.value = ""
  const previewUrl = URL.createObjectURL(file)
  sendImageForPrediction(file, file.name, previewUrl)
}

let scanStream = null

function startScan() {
  const modal = document.getElementById("scan-modal")
  const video = document.getElementById("scan-video")
  const msg = document.getElementById("scan-camera-msg")
  modal.classList.remove("hidden")
  msg.textContent = "Starting camera..."
  video.srcObject = null

  navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false })
    .then((stream) => {
      scanStream = stream
      video.srcObject = stream
      msg.textContent = "Position the leaf in frame, then tap Capture"
    })
    .catch((err) => {
      msg.textContent = "Camera access denied or unavailable. Use Upload Photo instead."
      console.error(err)
    })
}

function closeScanModal() {
  if (scanStream) {
    scanStream.getTracks().forEach((t) => t.stop())
    scanStream = null
  }
  const video = document.getElementById("scan-video")
  video.srcObject = null
  document.getElementById("scan-modal").classList.add("hidden")
}

function captureFromCamera() {
  const video = document.getElementById("scan-video")
  if (!video.srcObject || !video.videoWidth) {
    alert("Camera not ready. Wait a moment and try again.")
    return
  }
  const canvas = document.createElement("canvas")
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext("2d").drawImage(video, 0, 0)
  canvas.toBlob((blob) => {
    if (!blob) {
      alert("Failed to capture image")
      return
    }
    closeScanModal()
    sendImageForPrediction(blob, "scan.jpg", URL.createObjectURL(blob))
  }, "image/jpeg", 0.92)
}

function sendImageForPrediction(fileOrBlob, fileName, previewUrl) {
  const scanner = document.getElementById("scanner")
  const scanText = document.querySelector(".scan-text")
  scanner.classList.remove("hidden")
  scanText.innerText = "Uploading Image..."

  const formData = new FormData()
  formData.append("image", fileOrBlob, fileName || "image.jpg")

  fetch("http://127.0.0.1:5000/predict", {
    method: "POST",
    credentials: "include",
    body: formData
  })
    .then((response) => response.json())
    .then((data) => {
      scanText.innerText = "Analyzing Leaf..."
      setTimeout(() => {
        scanner.classList.add("hidden")
        if (!data.ok) {
          alert(data.error || "Prediction failed")
          return
        }
        const result = data.result
        const confidences = data.confidences || {}
        const percentage = confidences[result] ? (confidences[result] * 100).toFixed(1) + "%" : "N/A"

        const description = data.description || ""
        const treatment = data.treatment || ""
        const date = new Date().toLocaleTimeString()
        let imageUrl = data.imageUrl || previewUrl
        if (imageUrl && imageUrl.startsWith("/")) {
          imageUrl = "http://127.0.0.1:5000" + imageUrl;
        }

        addHistory(result, percentage, fileName || "image.jpg", date, description, treatment, imageUrl)

        const resultContent = document.getElementById("result-content");
        if (resultContent) {
          resultContent.innerHTML = `
            ${imageUrl ? `<img src="${imageUrl}" alt="Leaf Image" class="w-full h-auto max-h-56 object-cover rounded-xl border border-green-200 shadow-sm mb-4" />` : ""}
            <h2 class="text-2xl font-extrabold text-green-800">${result}</h2>
            <div class="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold mt-2 mb-4">
              ${percentage} Confidence
            </div>
            ${description ? `
              <div class="bg-gray-50 w-full p-4 rounded-xl text-left border border-gray-100 mt-2 shadow-sm">
                <h4 class="font-bold text-gray-800 mb-1"><i class="fas fa-shield-alt text-blue-500 mr-2"></i>Prevention:</h4>
                <p class="text-sm text-gray-600">${description}</p>
              </div>
            ` : ""}
            ${treatment ? `
              <div class="bg-green-50 w-full p-4 rounded-xl text-left border border-green-100 mt-3 shadow-sm">
                <h4 class="font-bold text-green-900 mb-1"><i class="fas fa-medkit text-green-600 mr-2"></i>Remedy:</h4>
                <p class="text-sm text-green-800">${treatment}</p>
              </div>
            ` : ""}
            <div class="w-full flex gap-3 mt-6">
               <button onclick="switchTab('history')" class="flex-1 py-3 rounded-2xl border-2 border-green-600 text-green-700 font-semibold text-sm hover:bg-green-50 transition-colors">History</button>
               <button onclick="backToDashboard()" class="flex-1 py-3 rounded-2xl bg-green-600 hover:bg-green-700 text-white font-semibold text-sm shadow-md transition-colors">New Scan</button>
            </div>
          `;
        }
        switchTab("result");
      }, 2000)
    })
    .catch((error) => {
      scanner.classList.add("hidden")
      alert(error && error.message ? error.message : "Error connecting to AI server")
      console.error(error)
    })
}

function addHistory(result, percentage, fileName, date, description, treatment, previewUrl) {

  const historyList = document.getElementById("history-list")

  if (historyList.querySelector("p.italic")) historyList.innerHTML = ""

  const item = document.createElement("div")

  item.className = "bg-green-50 p-3 rounded-xl flex justify-between items-center border border-green-100"

  item.innerHTML = `

<div>
<p class="font-bold text-green-900">${result} <span class="text-xs text-green-700 bg-green-200 px-2 py-0.5 rounded-full ml-1">${percentage}</span></p>
<p class="text-[10px] text-gray-500">${fileName} • ${date}</p>
${previewUrl ? `<img src="${previewUrl}" alt="${fileName}" class="mt-2 rounded-lg max-h-28 w-full object-cover border border-green-100" />` : ""}
${description ? `<p class="text-[11px] text-green-800 mt-1">Prevention: ${description}</p>` : ""}
${treatment ? `<p class="text-[11px] text-emerald-900 mt-1 font-medium">Remedy: ${treatment}</p>` : ""}
</div>

<i class="fas fa-chevron-right text-green-300"></i>

`

  historyList.prepend(item)

}

function loadHistory() {
  const historyList = document.getElementById("history-list")
  historyList.innerHTML = `

<p class="text-gray-500 text-center italic">
Loading history...
</p>
`

  fetch("http://127.0.0.1:5000/history", { credentials: "include" })
    .then(async (res) => {
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.error || "Failed to load history")
      return data
    })
    .then(data => {
      const items = data.items || []
      if (items.length === 0) {
        historyList.innerHTML = `
      <p class="text-gray-500 text-center italic">
      No history yet. Start scanning!
      </p>
    `
        return
      }

      historyList.innerHTML = ""

      items.forEach(item => {

        const div = document.createElement("div")

        div.className = "bg-green-50 p-3 rounded-xl flex justify-between items-center border border-green-100"

        const confidences = item.confidences || {}
        const percentage = confidences[item.result] ? (confidences[item.result] * 100).toFixed(1) + "%" : "N/A"
        let fullImageUrl = item.imageUrl;
        if (fullImageUrl && fullImageUrl.startsWith("/")) {
          fullImageUrl = "http://127.0.0.1:5000" + fullImageUrl;
        }

        div.innerHTML = `

<div>
<p class="font-bold text-green-900">${item.result} <span class="text-xs text-green-700 bg-green-200 px-2 py-0.5 rounded-full ml-1">${percentage}</span></p>
<p class="text-[10px] text-gray-500">${item.file} • ${new Date(item.time).toLocaleString()}</p>
${fullImageUrl ? `<img src="${fullImageUrl}" alt="${item.file}" class="mt-2 rounded-lg max-h-28 w-full object-cover border border-green-100" />` : ""}
${item.description ? `<p class="text-[11px] text-green-800 mt-1">Prevention: ${item.description}</p>` : ""}
${item.treatment ? `<p class="text-[11px] text-emerald-900 mt-1 font-medium">Remedy: ${item.treatment}</p>` : ""}
</div>

<i class="fas fa-chevron-right text-green-300"></i>

`

        historyList.appendChild(div)

      })
    })
    .catch(err => {
      historyList.innerHTML = `
    <p class="text-red-600 text-center text-sm font-semibold">
    ${err && err.message ? err.message : "Failed to load history"}
    </p>
  `
    })

}

function clearHistory() {
  fetch("/history")
    .then(() => {
      // No delete endpoint for now; just clear UI text
      document.getElementById("history-list").innerHTML = `
  <p class="text-gray-500 text-center italic">
  History is stored in database. (Clear from DB not implemented yet.)
  </p>
  `
    })


}

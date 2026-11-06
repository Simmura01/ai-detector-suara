/**
 * GuardiVoice — api.js
 * Frontend controller for audio analysis, live microphone recording,
 * waveform visualization, and UI interactions.
 */

// ⚠️ DEPLOY: Ganti URL ini dengan URL Render.com kamu setelah deploy backend
// Contoh: const API_BASE_URL = "https://guardivoice-api.onrender.com";
// Untuk development lokal: gunakan "http://localhost:8000"
const API_BASE_URL = "https://GANTI-DENGAN-URL-RENDER-KAMU.onrender.com";

// ─────────────────────────────────────────────────────────────
// STATE MANAGEMENT
// ─────────────────────────────────────────────────────────────
let selectedFile = null;
let recordedBlob = null;
let currentTab = "upload";

// Audio & Recording State
let audioContext = null;
let mediaStream = null;
let audioInputNode = null;
let analyserNode = null;
let scriptProcessor = null;
let pcmDataLeft = [];
let sampleRate = 44100;

let isRecording = false;
let recordStartTime = 0;
let timerInterval = null;
let animFrameId = null;

// DOM Elements
const dropZone        = document.getElementById("dropZone");
const fileInput       = document.getElementById("fileInput");
const fileInfo        = document.getElementById("fileInfo");
const fileName        = document.getElementById("fileName");
const fileSize        = document.getElementById("fileSize");
const clearBtn        = document.getElementById("clearBtn");
const audioPlayer     = document.getElementById("audioPlayer");
const analyzeBtn      = document.getElementById("analyzeBtn");

const panelUpload     = document.getElementById("panel-upload");
const panelRecord     = document.getElementById("panel-record");

const waveCanvas      = document.getElementById("waveCanvas");
const visIdle         = document.getElementById("visIdle");
const recTimer        = document.getElementById("recTimer");
const recStatus       = document.getElementById("recStatus");
const btnRecord       = document.getElementById("btnRecord");
const recIcon         = document.getElementById("recIcon");
const btnStopRec      = document.getElementById("btnStopRec");
const btnResetRec     = document.getElementById("btnResetRec");
const recResult       = document.getElementById("recResult");
const recPlayer       = document.getElementById("recPlayer");

const loadingSection  = document.getElementById("loadingSection");
const resultSection   = document.getElementById("resultSection");
const errorSection    = document.getElementById("errorSection");
const errorMsg        = document.getElementById("errorMsg");

const apiPill         = document.getElementById("apiPill");
const footerApiStatus = document.getElementById("footerApiStatus");

// ─────────────────────────────────────────────────────────────
// INITIALIZATION
// ─────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  setupNavbar();
  setupUploadZone();
  setupCanvas();
  checkApiStatus();
  setInterval(checkApiStatus, 25000);
});

// ─────────────────────────────────────────────────────────────
// NAVBAR & MOBILE MENU
// ─────────────────────────────────────────────────────────────
function setupNavbar() {
  const menuBtn = document.getElementById("navMenuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
    });
    mobileMenu.querySelectorAll("a").forEach(link => {
      link.addEventListener("click", () => mobileMenu.classList.add("hidden"));
    });
  }
}

// ─────────────────────────────────────────────────────────────
// TAB SWITCHING (UPLOAD VS REKAM)
// ─────────────────────────────────────────────────────────────
window.switchTab = function(tab) {
  currentTab = tab;
  document.querySelectorAll(".tab-btn").forEach(btn => {
    const isTarget = btn.getAttribute("data-tab") === tab;
    btn.classList.toggle("active", isTarget);
    btn.setAttribute("aria-selected", isTarget ? "true" : "false");
  });

  if (tab === "upload") {
    panelUpload.classList.remove("hidden");
    panelRecord.classList.add("hidden");
  } else {
    panelUpload.classList.add("hidden");
    panelRecord.classList.remove("hidden");
  }

  // Sembunyikan hasil lama jika ganti tab
  resultSection.classList.add("hidden");
  errorSection.classList.add("hidden");
};

// ─────────────────────────────────────────────────────────────
// UPLOAD & DRAG DROP
// ─────────────────────────────────────────────────────────────
function setupUploadZone() {
  if (!dropZone) return;

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragging");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragging");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragging");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  dropZone.addEventListener("click", (e) => {
    if (e.target !== fileInput && !e.target.closest("label")) {
      fileInput.click();
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  clearBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    clearSelectedFile();
  });
}

function handleFileSelected(file) {
  const allowed = [".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aiff", ".webm"];
  const ext = "." + file.name.split(".").pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showError(`Format file '${ext}' belum didukung. Gunakan: ${allowed.join(", ")}`);
    return;
  }

  selectedFile = file;
  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);

  fileInfo.classList.remove("hidden");
  analyzeBtn.classList.remove("hidden");

  const url = URL.createObjectURL(file);
  audioPlayer.src = url;
  audioPlayer.classList.remove("hidden");

  resultSection.classList.add("hidden");
  errorSection.classList.add("hidden");
}

function clearSelectedFile() {
  selectedFile = null;
  fileInput.value = "";
  audioPlayer.src = "";
  audioPlayer.classList.add("hidden");
  fileInfo.classList.add("hidden");
  analyzeBtn.classList.add("hidden");
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}

// ─────────────────────────────────────────────────────────────
// LIVE MICROPHONE RECORDING & VISUALIZER
// ─────────────────────────────────────────────────────────────
function setupCanvas() {
  if (!waveCanvas) return;
  const ctx = waveCanvas.getContext("2d");
  waveCanvas.width = waveCanvas.parentElement.clientWidth || 600;
  waveCanvas.height = 120;
  drawFlatLine(ctx);
}

function drawFlatLine(ctx) {
  ctx.clearRect(0, 0, waveCanvas.width, waveCanvas.height);
  ctx.lineWidth = 2;
  ctx.strokeStyle = "rgba(129, 140, 248, 0.25)";
  ctx.beginPath();
  ctx.moveTo(0, waveCanvas.height / 2);
  ctx.lineTo(waveCanvas.width, waveCanvas.height / 2);
  ctx.stroke();
}

window.toggleRecord = async function() {
  if (!isRecording) {
    await startRecord();
  } else {
    stopRecord();
  }
};

async function startRecord() {
  try {
    pcmDataLeft = [];
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
      }
    });

    mediaStream = stream;
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioContext = new AudioContextClass();
    sampleRate = audioContext.sampleRate;

    audioInputNode = audioContext.createMediaStreamSource(stream);
    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 1024;

    // Gunakan scriptProcessor untuk merekam PCM 16-bit asli
    scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
    scriptProcessor.onaudioprocess = (e) => {
      if (!isRecording) return;
      const channelData = e.inputBuffer.getChannelData(0);
      pcmDataLeft.push(new Float32Array(channelData));
    };

    audioInputNode.connect(analyserNode);
    analyserNode.connect(scriptProcessor);
    scriptProcessor.connect(audioContext.destination);

    isRecording = true;
    recordStartTime = Date.now();

    // UI Updates
    btnRecord.classList.add("recording");
    recIcon.textContent = "STOP";
    btnStopRec.disabled = false;
    btnResetRec.disabled = true;
    recStatus.textContent = "Sedang merekam... Bicaralah atau putar suara";
    recResult.classList.add("hidden");
    visIdle.style.opacity = "0";

    timerInterval = setInterval(updateRecTimer, 200);
    renderWaveform();

  } catch (err) {
    console.error("Microphone access error:", err);
    showError("Akses mikrofon ditolak atau tidak tersedia. Pastikan izin mikrofon telah diberikan di browser.");
  }
}

function updateRecTimer() {
  const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
  const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const s = String(elapsed % 60).padStart(2, "0");
  recTimer.textContent = `${m}:${s}`;
}

window.stopRecord = function() {
  if (!isRecording && !mediaStream) return;
  isRecording = false;

  clearInterval(timerInterval);
  if (animFrameId) cancelAnimationFrame(animFrameId);

  // Stop MediaStream tracks
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop());
  }

  // Disconnect nodes
  if (scriptProcessor) scriptProcessor.disconnect();
  if (analyserNode) analyserNode.disconnect();
  if (audioInputNode) audioInputNode.disconnect();
  if (audioContext && audioContext.state !== "closed") {
    audioContext.close();
  }

  // Encode PCM chunks ke standard WAV
  const wavBlob = encodeWAV(pcmDataLeft, sampleRate);
  recordedBlob = wavBlob;

  // UI Updates
  btnRecord.classList.remove("recording");
  recIcon.textContent = "REC";
  btnStopRec.disabled = true;
  btnResetRec.disabled = false;
  recStatus.textContent = "Rekaman selesai. Dengarkan atau analisis di bawah:";

  if (recordedBlob && recordedBlob.size > 1000) {
    const audioUrl = URL.createObjectURL(recordedBlob);
    recPlayer.src = audioUrl;
    recResult.classList.remove("hidden");
  } else {
    recStatus.textContent = "Rekaman terlalu pendek. Silakan coba lagi.";
  }

  const ctx = waveCanvas.getContext("2d");
  drawFlatLine(ctx);
  visIdle.style.opacity = "1";
};

window.resetRecord = function() {
  if (isRecording) {
    stopRecord();
  }
  recordedBlob = null;
  pcmDataLeft = [];
  recTimer.textContent = "00:00";
  recStatus.textContent = "Siap merekam";
  recPlayer.src = "";
  recResult.classList.add("hidden");
  btnResetRec.disabled = true;
  btnStopRec.disabled = true;
  resultSection.classList.add("hidden");
  errorSection.classList.add("hidden");
};

function renderWaveform() {
  if (!isRecording || !analyserNode) return;

  const ctx = waveCanvas.getContext("2d");
  const width = waveCanvas.width;
  const height = waveCanvas.height;
  const bufferLength = analyserNode.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  analyserNode.getByteTimeDomainData(dataArray);

  ctx.clearRect(0, 0, width, height);
  ctx.lineWidth = 2.5;

  // Gradient line stroke
  const grad = ctx.createLinearGradient(0, 0, width, 0);
  grad.addColorStop(0, "#818cf8");
  grad.addColorStop(1, "#34d399");
  ctx.strokeStyle = grad;

  ctx.beginPath();
  const sliceWidth = width / bufferLength;
  let x = 0;

  for (let i = 0; i < bufferLength; i++) {
    const v = dataArray[i] / 128.0;
    const y = (v * height) / 2;
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
    x += sliceWidth;
  }
  ctx.lineTo(width, height / 2);
  ctx.stroke();

  animFrameId = requestAnimationFrame(renderWaveform);
}

/**
 * Encode raw Float32Array PCM samples directly into a 16-bit uncompressed WAV Blob.
 * Universally supported by Python librosa/soundfile.
 */
function encodeWAV(samplesArrays, sampleRate) {
  let totalLength = 0;
  for (let i = 0; i < samplesArrays.length; i++) {
    totalLength += samplesArrays[i].length;
  }

  const mergedSamples = new Float32Array(totalLength);
  let offset = 0;
  for (let i = 0; i < samplesArrays.length; i++) {
    mergedSamples.set(samplesArrays[i], offset);
    offset += samplesArrays[i].length;
  }

  const numChannels = 1;
  const bytesPerSample = 2;
  const blockAlign = numChannels * bytesPerSample;
  const byteRate = sampleRate * blockAlign;
  const dataSize = mergedSamples.length * bytesPerSample;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);

  // Write RIFF Header
  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  writeString(view, 8, "WAVE");

  // Write FMT Chunk
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM Format
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 16, true); // 16-bit

  // Write DATA Chunk
  writeString(view, 36, "data");
  view.setUint32(40, dataSize, true);

  // Write 16-bit PCM Audio Samples
  let p = 44;
  for (let i = 0; i < mergedSamples.length; i++, p += 2) {
    let s = Math.max(-1, Math.min(1, mergedSamples[i]));
    s = s < 0 ? s * 0x8000 : s * 0x7FFF;
    view.setInt16(p, s, true);
  }

  return new Blob([view], { type: "audio/wav" });
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

// ─────────────────────────────────────────────────────────────
// ANALYZE DISPATCHERS
// ─────────────────────────────────────────────────────────────
window.analyze = function() {
  if (!selectedFile) {
    showError("Pilih file audio terlebih dahulu.");
    return;
  }
  executeAnalysis(selectedFile, selectedFile.name);
};

window.analyzeRec = function() {
  if (!recordedBlob) {
    showError("Belum ada rekaman yang siap dianalisis.");
    return;
  }
  const fileObj = new File([recordedBlob], "mic_recording.wav", { type: "audio/wav" });
  executeAnalysis(fileObj, "Rekaman Mikrofon (.wav)");
};

// ─────────────────────────────────────────────────────────────
// EXECUTE API ANALYSIS & STEP ANIMATION
// ─────────────────────────────────────────────────────────────
async function executeAnalysis(fileObject, displayName) {
  loadingSection.classList.remove("hidden");
  resultSection.classList.add("hidden");
  errorSection.classList.add("hidden");

  // Animate progress steps
  const steps = [
    document.getElementById("step1"),
    document.getElementById("step2"),
    document.getElementById("step3"),
    document.getElementById("step4"),
  ];

  function setStep(idx) {
    steps.forEach((s, i) => {
      if (!s) return;
      s.className = "step";
      if (i < idx) s.classList.add("done");
      else if (i === idx) s.classList.add("active");
    });
  }

  setStep(0);
  const stepTimer1 = setTimeout(() => setStep(1), 700);
  const stepTimer2 = setTimeout(() => setStep(2), 1500);
  const stepTimer3 = setTimeout(() => setStep(3), 2800);

  try {
    const formData = new FormData();
    formData.append("file", fileObject, fileObject.name || "audio.wav");

    const resp = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      body: formData,
    });

    clearTimeout(stepTimer1);
    clearTimeout(stepTimer2);
    clearTimeout(stepTimer3);

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(err.detail || "Server error " + resp.status);
    }

    const data = await resp.json();
    setStep(4);
    setTimeout(() => {
      loadingSection.classList.add("hidden");
      renderResult(data, displayName);
    }, 400);

  } catch (err) {
    clearTimeout(stepTimer1);
    clearTimeout(stepTimer2);
    clearTimeout(stepTimer3);
    loadingSection.classList.add("hidden");
    console.error("Analysis error:", err);

    if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
      showError(
        "Tidak dapat terhubung ke Backend API (http://localhost:8000).\n" +
        "Pastikan server FastAPI telah dijalankan di terminal dengan perintah:\n\n" +
        "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
      );
    } else {
      showError(err.message);
    }
  }
}

// ─────────────────────────────────────────────────────────────
// RENDER ANALYSIS RESULTS
// ─────────────────────────────────────────────────────────────
function renderResult(data, customFilename) {
  const isAi = data.label === "ai";
  const probs = data.probabilities || {};
  const pHuman = Math.round((probs["human"] || 0) * 100);
  const pAi = Math.round((probs["ai"] || 0) * 100);
  const conf = data.confidence || Math.max(pHuman, pAi);

  // Verdict Box
  const verdictBox   = document.getElementById("verdictBox");
  const verdictEmoji = document.getElementById("verdictEmoji");
  const verdictLabel = document.getElementById("verdictLabel");
  const verdictSub   = document.getElementById("verdictSub");

  verdictBox.className = "verdict-box " + (isAi ? "ai-box" : "human-box");
  if (verdictEmoji) verdictEmoji.textContent = "";
  verdictLabel.textContent = isAi ? "Terdeteksi: Suara AI (Sintetis)" : "Terdeteksi: Suara Manusia Asli";
  verdictSub.textContent = isAi
    ? "Pola akustik, kestabilan pitch, dan kelicinan sinyal menunjukkan audio ini digenerate oleh AI TTS."
    : "Variasi mikro-akustik, jitter natural, dan dinamika vokal mengindikasikan suara manusia asli.";

  // Confidence Meter
  document.getElementById("confPct").textContent = `${conf}%`;
  setTimeout(() => {
    document.getElementById("confFill").style.width = `${conf}%`;
  }, 100);

  // Probability Cards
  document.getElementById("probHumanVal").textContent = `${pHuman}%`;
  document.getElementById("probAiVal").textContent = `${pAi}%`;
  setTimeout(() => {
    document.getElementById("probHumanBar").style.width = `${pHuman}%`;
    document.getElementById("probAiBar").style.width = `${pAi}%`;
  }, 150);

  // ── Render 4 Batasan Akustik (BAMBS) ───────────────────
  const boundaries = data.boundaries || {};
  const boundariesGrid = document.getElementById("boundariesGrid");
  const violationsBadge = document.getElementById("violationsBadge");
  const boundariesSummary = document.getElementById("boundariesSummaryText");

  if (boundariesGrid && Object.keys(boundaries).length > 0) {
    const vCount = data.violations_count !== undefined ? data.violations_count : 0;
    const totalB = data.total_boundaries || Object.keys(boundaries).length;

    if (violationsBadge) {
      violationsBadge.textContent = vCount === 0 ? "Profil Akustik Normal" : `${vCount} / ${totalB} Parameter Berbeda`;
      violationsBadge.className = "violations-badge " + (vCount > 0 ? "has-violation" : "all-passed");
    }

    if (boundariesSummary && data.summary_text) {
      boundariesSummary.textContent = data.summary_text.replace(/[🤖✅⚠️]/g, "").trim();
    }

    const bKeys = ["pitch_range", "shimmer", "hnr", "mfcc_7_std"];
    boundariesGrid.innerHTML = bKeys.map(k => {
      const b = boundaries[k];
      if (!b) return "";
      const isViolated = b.zone === "ai";
      const cardClass = isViolated ? "violated" : "passed";
      const statusPill = isViolated ? "Artifisial" : "Alami";
      const threshCondition = b.direction === -1 ? `Ambang Alami: ≥ ${b.threshold}` : `Ambang Alami: ≤ ${b.threshold}`;
      const fillPct = Math.min(100, Math.max(5, Math.round(b.score * 100)));

      return `
        <div class="boundary-card ${cardClass}">
          <div class="boundary-card-top">
            <span class="boundary-name">${b.name}</span>
            <span class="boundary-pill">${statusPill}</span>
          </div>
          <div class="boundary-metrics">
            <span class="boundary-val">${b.value} <small style="font-size:0.75rem;font-weight:500;color:var(--text2);">${b.unit}</small></span>
            <span class="boundary-thresh">${threshCondition}</span>
          </div>
          <div class="boundary-track">
            <div class="boundary-fill" style="width: ${fillPct}%"></div>
          </div>
          <div class="boundary-desc">${b.explanation.replace(/[🤖✅⚠️]/g, "")}</div>
        </div>
      `;
    }).join("");
  }

  // Feature Grid
  const fs = data.features_summary || {};
  const featItems = [
    { label: "Sumber Audio", val: customFilename || data.filename || "-" },
    { label: "Durasi Dianalisis", val: `${fs.duration_sec ? fs.duration_sec.toFixed(2) : "-"} detik` },
    { label: "Pitch Rata-rata (F0)", val: `${fs.pitch_mean_hz ? fs.pitch_mean_hz.toFixed(1) : "-"} Hz` },
    { label: "Variasi Pitch (Std)", val: `${fs.pitch_std_hz ? fs.pitch_std_hz.toFixed(2) : "-"} Hz` },
    { label: "Jitter (Ketidakstabilan Frekuensi)", val: fs.jitter !== undefined ? fs.jitter.toFixed(5) : "-" },
    { label: "Shimmer (Variasi Amplitudo)", val: fs.shimmer !== undefined ? fs.shimmer.toFixed(5) : "-" },
    { label: "HNR (Harmonic-to-Noise)", val: fs.hnr !== undefined ? `${fs.hnr.toFixed(2)} dB` : "-" },
    { label: "Rasio Suara Bersuara", val: fs.voiced_ratio !== undefined ? `${(fs.voiced_ratio * 100).toFixed(1)}%` : "-" },
    { label: "Zero Crossing Rate (ZCR)", val: fs.zcr_mean !== undefined ? fs.zcr_mean.toFixed(4) : "-" },
  ];

  const featGrid = document.getElementById("featGrid");
  featGrid.innerHTML = featItems.map(item => `
    <div class="feat-cell">
      <div class="feat-cell-label">${item.label}</div>
      <div class="feat-cell-val">${item.val}</div>
    </div>
  `).join("");

  resultSection.classList.remove("hidden");
  resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ─────────────────────────────────────────────────────────────
// RESET ALL
// ─────────────────────────────────────────────────────────────
window.resetAll = function() {
  clearSelectedFile();
  resetRecord();
  resultSection.classList.add("hidden");
  errorSection.classList.add("hidden");
  loadingSection.classList.add("hidden");
  document.getElementById("confFill").style.width = "0%";
  document.getElementById("probHumanBar").style.width = "0%";
  document.getElementById("probAiBar").style.width = "0%";
};

// ─────────────────────────────────────────────────────────────
// ERROR DISPLAY
// ─────────────────────────────────────────────────────────────
function showError(message) {
  errorMsg.textContent = message;
  errorSection.classList.remove("hidden");
  loadingSection.classList.add("hidden");
  resultSection.classList.add("hidden");
  errorSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ─────────────────────────────────────────────────────────────
// GUIDE & FAQ INTERACTION
// ─────────────────────────────────────────────────────────────
window.showGuide = function(guideId) {
  document.querySelectorAll(".guide-tab").forEach(tab => {
    const isTarget = tab.getAttribute("onclick") && tab.getAttribute("onclick").includes(guideId);
    tab.classList.toggle("active", isTarget);
  });

  const allGuides = ["upload-guide", "rec-guide", "tips-guide"];
  allGuides.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      if (id === guideId) el.classList.remove("hidden");
      else el.classList.add("hidden");
    }
  });
};

window.toggleFaq = function(button) {
  const answer = button.nextElementSibling;
  const isOpen = button.classList.contains("open");

  // Close all other FAQs
  document.querySelectorAll(".faq-q").forEach(q => {
    q.classList.remove("open");
    if (q.nextElementSibling) q.nextElementSibling.classList.remove("open");
  });

  if (!isOpen) {
    button.classList.add("open");
    if (answer) answer.classList.add("open");
  }
};

// ─────────────────────────────────────────────────────────────
// API HEALTH CHECK
// ─────────────────────────────────────────────────────────────
async function checkApiStatus() {
  const pillText = apiPill ? apiPill.querySelector(".pill-text") : null;

  try {
    const resp = await fetch(`${API_BASE_URL}/info`, {
      method: "GET",
      signal: AbortSignal.timeout ? AbortSignal.timeout(4000) : undefined,
    });

    if (resp.ok) {
      const data = await resp.json();
      if (apiPill) {
        apiPill.className = "api-pill api-online";
        if (pillText) {
          pillText.textContent = data.model_name
            ? `Online · ${data.model_name}`
            : "API Online (Model Standby)";
        }
      }
      if (footerApiStatus) {
        footerApiStatus.textContent = `🟢 Backend Online · ${data.model_name || "Siap"}`;
        footerApiStatus.style.color = "#34d399";
      }
    } else {
      throw new Error();
    }
  } catch (e) {
    if (apiPill) {
      apiPill.className = "api-pill api-offline";
      if (pillText) pillText.textContent = "API Offline";
    }
    if (footerApiStatus) {
      footerApiStatus.textContent = "🔴 Backend Offline (Jalankan uvicorn main:app)";
      footerApiStatus.style.color = "#f87171";
    }
  }
}

"use strict";

// DOM refs

const textarea        = document.getElementById("user-prompt");
const charCountEl     = document.getElementById("char-count");
const btnClear        = document.getElementById("btn-clear");
const btnEnter        = document.getElementById("btn-enter");

const sectionRefined  = document.getElementById("section-refined");
const originalEcho    = document.getElementById("original-echo");
const refinedText     = document.getElementById("refined-prompt-text");
const explanationText = document.getElementById("explanation-text");
const btnContinue     = document.getElementById("btn-continue");

const sectionLoading  = document.getElementById("section-loading");
const loadingLabel    = document.getElementById("loading-label");

const sectionResult   = document.getElementById("section-result");
const resultImage     = document.getElementById("result-image");
const resultPromptEcho = document.getElementById("result-prompt-echo");
const btnDownload     = document.getElementById("btn-download");
const btnRestart      = document.getElementById("btn-restart");

const errorToast      = document.getElementById("error-toast");
const errorMessage    = document.getElementById("error-message");

// App state

const state = {
  basicPrompt:   "",
  refinedPrompt: "",
  imageB64:      "",
};

// Utilities

function showSection(el) {
  el.style.display = "block";
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      el.classList.add("visible");
    });
  });
  el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function hideSection(el) {
  el.classList.remove("visible");
  el.addEventListener("transitionend", () => {
    el.style.display = "";
  }, { once: true });
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorToast.classList.add("show");
  setTimeout(() => errorToast.classList.remove("show"), 5000);
}

function setBusy(btn, busy, label = "Working…") {
  if (busy) {
    btn.dataset.idle = btn.innerHTML;
    btn.innerHTML = label;
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.idle;
    btn.disabled = false;
  }
}

async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail);
  return data;
}

// Character counter

textarea.addEventListener("input", () => {
  charCountEl.textContent = textarea.value.length;
});

// Clear

btnClear.onclick = () => {
  textarea.value = "";
  charCountEl.textContent = 0;
  hideSection(sectionRefined);
  hideSection(sectionResult);
};

// Step 1 refine

btnEnter.onclick = async () => {
  const prompt = textarea.value.trim();
  if (!prompt) return showError("Enter prompt");

  setBusy(btnEnter,true,"Refining...");

  try {
    const data = await postJSON("/api/refine",{basic_prompt:prompt});

    state.refinedPrompt = data.refined_prompt;

    originalEcho.textContent = data.original_prompt;
    refinedText.textContent = data.refined_prompt;
    explanationText.textContent = data.explanation;

    showSection(sectionRefined);

  } catch(e){
    showError(e.message);
  }

  setBusy(btnEnter,false);
};

// Step 2 generate

btnContinue.onclick = async () => {

  hideSection(sectionRefined);
  setBusy(btnContinue,true,"Generating...");

  showSection(sectionLoading);

  try{
    const data = await postJSON("/api/generate",{
      refined_prompt: state.refinedPrompt
    });

    state.imageB64 = data.image_base64;

    // Image load
    resultImage.src = "data:image/jpeg;base64," + data.image_base64;

    // Prompt echo
    resultPromptEcho.textContent = data.refined_prompt;

    // ⭐ NEW CHANGE
    console.log("Optimization Report:", data.optimization_report);

    hideSection(sectionLoading);
    showSection(sectionResult);

    setupDownload(data.image_base64);

  }catch(e){
    showError(e.message);
  }

  setBusy(btnContinue,false);
};

// Download

function setupDownload(b64){
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for(let i=0;i<binary.length;i++){
    bytes[i] = binary.charCodeAt(i);
  }
  const blob = new Blob([bytes],{type:"image/jpeg"});
  const url = URL.createObjectURL(blob);
  btnDownload.href = url;
}

// Restart

btnRestart.onclick = () => location.reload();

textarea.focus();
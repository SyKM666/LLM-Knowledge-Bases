import { api } from "../api";

let currentTab: "upload" | "paste" = "upload";
let pendingFiles: File[] = [];

export function initModal(): void {
  const overlay = document.getElementById("ingestModal")!;

  // Open / close
  document.getElementById("btnIngest")!.addEventListener("click", () => {
    pendingFiles = [];
    renderFileList();
    overlay.classList.add("open");
  });
  document.getElementById("btnCancelIngest")!.addEventListener("click", closeModal);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });

  // Tabs
  document.querySelectorAll<HTMLElement>(".modal .tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      currentTab = tab.dataset.tab as "upload" | "paste";
      updateTabs();
    });
  });

  // Submit
  document.getElementById("btnSubmitIngest")!.addEventListener("click", submitIngest);

  // Modal dropzone
  initModalDropzone();

  // Global drag-and-drop
  initGlobalDrop();
}

// ── Modal Dropzone ─────────────────────────

function initModalDropzone(): void {
  const dropzone = document.getElementById("modalDropzone")!;
  const fileInput = document.getElementById("ingestFile") as HTMLInputElement;

  dropzone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    if (fileInput.files) {
      addFiles(Array.from(fileInput.files));
    }
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer?.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  });
}

// ── Global Drag & Drop ─────────────────────

function initGlobalDrop(): void {
  const overlay = document.getElementById("dropOverlay")!;
  let dragCounter = 0;

  document.addEventListener("dragenter", (e) => {
    e.preventDefault();
    dragCounter++;
    if (dragCounter === 1) {
      overlay.classList.add("visible");
    }
  });

  document.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dragCounter--;
    if (dragCounter === 0) {
      overlay.classList.remove("visible");
    }
  });

  document.addEventListener("dragover", (e) => {
    e.preventDefault();
  });

  document.addEventListener("drop", (e) => {
    e.preventDefault();
    dragCounter = 0;
    overlay.classList.remove("visible");

    // Ignore drops inside the modal dropzone (handled separately)
    if ((e.target as HTMLElement).closest("#modalDropzone")) return;

    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      uploadFilesDirectly(Array.from(files));
    }
  });
}

// ── File Management ────────────────────────

function addFiles(files: File[]): void {
  for (const f of files) {
    if (!pendingFiles.some((p) => p.name === f.name)) {
      pendingFiles.push(f);
    }
  }
  renderFileList();
}

function removeFile(index: number): void {
  pendingFiles.splice(index, 1);
  renderFileList();
}

function renderFileList(): void {
  const list = document.getElementById("fileList")!;
  if (pendingFiles.length === 0) {
    list.innerHTML = "";
    return;
  }
  list.innerHTML = pendingFiles
    .map(
      (f, i) =>
        `<li>
          <span class="file-name">${f.name}</span>
          <span class="file-size">${formatSize(f.size)}</span>
          <span class="file-remove" data-index="${i}">&times;</span>
        </li>`,
    )
    .join("");

  list.querySelectorAll<HTMLElement>(".file-remove").forEach((btn) => {
    btn.addEventListener("click", () => {
      removeFile(Number(btn.dataset.index));
    });
  });
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ── Upload ─────────────────────────────────

async function uploadFilesDirectly(files: File[]): Promise<void> {
  const statusBar = document.getElementById("statusBar")!;
  const mainContent = document.getElementById("mainContent")!;
  const names: string[] = [];

  mainContent.innerHTML =
    '<div class="loading-msg"><div class="spinner"></div>Uploading files...</div>';

  for (const file of files) {
    try {
      const data = await api.ingestFile(file);
      names.push(data.filename);
    } catch (e) {
      console.error(`Failed to upload ${file.name}:`, e);
    }
  }

  if (names.length > 0) {
    const list = names.map((n) => `<li>${n}</li>`).join("");
    mainContent.innerHTML = `<div class="panel">
      <div class="panel-title">Ingested ${names.length} file(s)</div>
      <ul>${list}</ul>
      <p style="margin-top:12px;color:var(--text2)">Click <strong>Compile</strong> to process into wiki.</p>
    </div>`;
    statusBar.textContent = `Ingested ${names.length} file(s)`;
  }
}

async function submitIngest(): Promise<void> {
  const statusBar = document.getElementById("statusBar")!;

  try {
    if (currentTab === "upload") {
      if (pendingFiles.length === 0) {
        alert("Please add at least one file");
        return;
      }
      const names: string[] = [];
      for (const file of pendingFiles) {
        const data = await api.ingestFile(file);
        names.push(data.filename);
      }
      statusBar.textContent = `Ingested: ${names.join(", ")}`;
      closeModal();

      const mainContent = document.getElementById("mainContent")!;
      const list = names.map((n) => `<li>${n}</li>`).join("");
      mainContent.innerHTML = `<div class="panel">
        <div class="panel-title">Ingested ${names.length} file(s)</div>
        <ul>${list}</ul>
        <p style="margin-top:12px;color:var(--text2)">Click <strong>Compile</strong> to process into wiki.</p>
      </div>`;
    } else {
      const filename = (document.getElementById("ingestFilename") as HTMLInputElement).value.trim();
      const content = (document.getElementById("ingestContent") as HTMLTextAreaElement).value.trim();
      if (!filename || !content) {
        alert("Filename and content are required");
        return;
      }
      await api.ingestText(filename, content);
      statusBar.textContent = `Ingested: ${filename}`;
      closeModal();

      const mainContent = document.getElementById("mainContent")!;
      mainContent.innerHTML =
        '<div class="panel"><div class="panel-title">Ingested</div>Document added to data/raw/. Click <strong>Compile</strong> to process it into the wiki.</div>';
    }
  } catch (e) {
    alert(`Ingest error: ${e}`);
  }
}

// ── Helpers ────────────────────────────────

function closeModal(): void {
  document.getElementById("ingestModal")!.classList.remove("open");
  pendingFiles = [];
}

function updateTabs(): void {
  document.querySelectorAll<HTMLElement>(".modal .tab").forEach((t) => {
    t.classList.toggle("active", t.dataset.tab === currentTab);
  });
  document.getElementById("tab-upload")!.classList.toggle("active", currentTab === "upload");
  document.getElementById("tab-paste")!.classList.toggle("active", currentTab === "paste");
}

import "./styles.css";
import { initSidebar, loadArticles } from "./components/sidebar";
import { doCompile, doLint, doFix, showIndex, initContentLinks } from "./components/content";
import { initModal } from "./components/modal";

// ── Build DOM ──────────────────────────────

document.getElementById("app")!.innerHTML = `
<div class="app">
  <!-- Top Bar -->
  <header class="topbar">
    <h1><span>KB</span> Agent</h1>
    <div class="status-bar" id="statusBar"></div>
    <button class="btn" id="btnIngest">+ Ingest</button>
    <button class="btn" id="btnCompile">Compile</button>
    <button class="btn" id="btnLint">Lint</button>
    <button class="btn" id="btnFix">Fix</button>
  </header>

  <!-- Sidebar -->
  <aside class="sidebar">
    <div>
      <div class="section-title">Wiki Articles</div>
      <ul class="article-list" id="articleList">
        <li class="empty">Loading...</li>
      </ul>
      <div style="margin-top:8px">
        <button class="btn" id="btnIndex" style="font-size:12px;padding:4px 10px">INDEX.md</button>
      </div>
    </div>

    <div>
      <div class="section-title">Search</div>
      <input type="text" id="searchInput" placeholder="Keywords...">
      <div class="sidebar-actions">
        <button class="btn" id="btnSearch" style="flex:1">Search</button>
      </div>
    </div>

    <div>
      <div class="section-title">Ask a Question</div>
      <textarea id="queryInput" placeholder="Ask anything about the wiki..."></textarea>
      <label class="checkbox-row">
        <input type="checkbox" id="querySave"> Save answer to wiki
      </label>
      <div class="sidebar-actions">
        <button class="btn primary" id="btnQuery" style="flex:1">Ask</button>
      </div>
    </div>
  </aside>

  <!-- Main Content -->
  <main class="main">
    <div class="main-inner" id="mainContent">
      <div class="welcome">
        <h2>Welcome to KB Agent</h2>
        <p>
          Browse wiki articles on the left<br>
          Search, ask questions, or compile new content<br>
          Your personal LLM-powered knowledge base
        </p>
      </div>
    </div>
  </main>
</div>

<!-- Global Drop Overlay -->
<div class="drop-overlay" id="dropOverlay">
  <div class="drop-overlay-inner">
    <div class="drop-overlay-icon">+</div>
    <p>Drop files to ingest into knowledge base</p>
  </div>
</div>

<!-- Ingest Modal -->
<div class="modal-overlay" id="ingestModal">
  <div class="modal">
    <h3>Ingest New Document</h3>
    <div class="tabs">
      <div class="tab active" data-tab="upload">Upload File</div>
      <div class="tab" data-tab="paste">Paste Text</div>
    </div>
    <div class="tab-content active" id="tab-upload">
      <div class="dropzone" id="modalDropzone">
        <div class="dropzone-icon">+</div>
        <p>Drag files here or click to browse</p>
        <p style="font-size:12px;color:var(--text2);margin-top:4px">.md, .txt, .html, .json, .csv</p>
        <input type="file" id="ingestFile" accept=".md,.txt,.html,.json,.csv" multiple hidden>
      </div>
      <ul class="file-list" id="fileList"></ul>
    </div>
    <div class="tab-content" id="tab-paste">
      <input type="text" id="ingestFilename" placeholder="Filename (e.g. my-notes)">
      <textarea id="ingestContent" placeholder="Paste document content here..."></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn" id="btnCancelIngest">Cancel</button>
      <button class="btn primary" id="btnSubmitIngest">Ingest</button>
    </div>
  </div>
</div>
`;

// ── Init ───────────────────────────────────

initSidebar();
initContentLinks();
initModal();

document.getElementById("btnIndex")!.addEventListener("click", showIndex);
document.getElementById("btnCompile")!.addEventListener("click", () => doCompile(false));
document.getElementById("btnLint")!.addEventListener("click", doLint);
document.getElementById("btnFix")!.addEventListener("click", doFix);

loadArticles();

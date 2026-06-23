// static/editor.js

let pages = [];
let activePageId = null;
let currentZoom = 0.8;
let linkMode = false;
let selectedElement = null;
let eventSource = null;

// Page dimensions in pixels at 96 DPI
const PAGE_DIMENSIONS = {
    'A4': { portrait: { w: 794, h: 1123 }, landscape: { w: 1123, h: 794 } },
    'A5': { portrait: { w: 559, h: 794 }, landscape: { w: 794, h: 559 } }
};

// UI Elements
const pagesList = document.getElementById('pages-list');
const paperContainer = document.getElementById('paper-container');
const currentPageTitle = document.getElementById('current-page-title');
const linkModeCheckbox = document.getElementById('link-mode-checkbox');
const linkHelperBanner = document.getElementById('link-helper-banner');
const exportBtn = document.getElementById('export-pdf-btn');

const editorTitle = document.getElementById('editor-title');
const editorPageSize = document.getElementById('editor-pageSize');
const editorStyleTheme = document.getElementById('editor-styleTheme');

const zoomInBtn = document.getElementById('zoom-in-btn');
const zoomOutBtn = document.getElementById('zoom-out-btn');
const zoomValue = document.getElementById('zoom-value');

// Modal Elements
const addModal = document.getElementById('add-page-modal');
const openAddModalBtn = document.getElementById('open-add-modal-btn');
const closeAddModalBtn = document.getElementById('close-add-modal-btn');
const cancelAddBtn = document.getElementById('cancel-add-btn');
const submitAddBtn = document.getElementById('submit-add-btn');

const newPageTitleInput = document.getElementById('new-page-title');
const newPagePromptInput = document.getElementById('new-page-prompt');
const newPageOrientationSelect = document.getElementById('new-page-orientation');

const modalStatusBox = document.getElementById('modal-status-box');
const modalStatusMsg = document.getElementById('modal-status-msg');

// Popup Elements
const linkPopup = document.getElementById('link-selector-popup');
const linkTargetSelect = document.getElementById('link-target-select');
const applyLinkBtn = document.getElementById('apply-link-btn');
const unlinkBtn = document.getElementById('unlink-btn');

const printContainer = document.getElementById('print-container');

// Event Listeners
openAddModalBtn.addEventListener('click', () => showModal(true));
closeAddModalBtn.addEventListener('click', () => showModal(false));
cancelAddBtn.addEventListener('click', () => showModal(false));
submitAddBtn.addEventListener('click', generateNewPage);

zoomInBtn.addEventListener('click', () => adjustZoom(0.1));
zoomOutBtn.addEventListener('click', () => adjustZoom(-0.1));
linkModeCheckbox.addEventListener('change', toggleLinkMode);
editorPageSize.addEventListener('change', renderActivePage);

applyLinkBtn.addEventListener('click', applyHyperlink);
unlinkBtn.addEventListener('click', removeHyperlink);
exportBtn.addEventListener('click', exportToPDF);

// Close link popup on document click (outside of iframe/popup)
document.addEventListener('click', (e) => {
    if (!linkPopup.contains(e.target) && e.target !== linkPopup) {
        hideLinkPopup();
    }
});

// 1. Zoom Controls
function adjustZoom(amount) {
    currentZoom = Math.max(0.4, Math.min(1.5, currentZoom + amount));
    updateZoomUI();
}

function updateZoomUI() {
    zoomValue.textContent = `${Math.round(currentZoom * 100)}%`;
    
    // activePage가 있는지 확인
    const activePage = pages.find(p => p.id === activePageId);
    if (!activePage) {
        paperContainer.style.width = '';
        paperContainer.style.height = '';
        return;
    }
    
    const size = editorPageSize.value;
    const orientation = activePage.orientation || 'portrait';
    const dims = PAGE_DIMENSIONS[size]?.[orientation] || PAGE_DIMENSIONS['A4'].portrait;
    
    // 종이(창 크기)는 100% 규격으로 상시 고정
    paperContainer.style.width = `${dims.w}px`;
    paperContainer.style.height = `${dims.h}px`;
    paperContainer.style.transform = '';
    
    // iframe 내부의 콘텐츠 줌을 수행
    const iframe = document.getElementById('preview-iframe');
    if (iframe) {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        if (doc) {
            applyContentZoom(doc, currentZoom);
        }
    }
}

/**
 * iframe 내부의 body 크기 및 scale 속성을 인위적으로 조율하여 콘텐츠 줌을 형성합니다.
 */
function applyContentZoom(doc, zoom) {
    let style = doc.getElementById('content-zoom-style');
    if (!style) {
        style = doc.createElement('style');
        style.id = 'content-zoom-style';
        doc.head.appendChild(style);
    }
    
    // body를 특정 비율로 축소/확대하고, 스크롤 레이아웃이 찢어지지 않게 calc로 wrap
    style.innerHTML = `
        body {
            transform: scale(${zoom}) !important;
            transform-origin: top left !important;
            width: ${Math.round(100 / zoom)}% !important;
            height: ${Math.round(100 / zoom)}% !important;
            box-sizing: border-box !important;
            margin: 0 !important;
            overflow: auto !important;
        }
        /* html 태그 오버플로우 관리 */
        html {
            overflow: hidden !important;
            width: 100% !important;
            height: 100% !important;
        }
    `;
}

// 2. Modal Management
function showModal(show) {
    if (show) {
        addModal.classList.remove('hidden');
        newPageTitleInput.value = '';
        newPagePromptInput.value = '';
        newPageTitleInput.focus();
    } else {
        addModal.classList.add('hidden');
        modalStatusBox.classList.add('hidden');
        if (eventSource) {
            eventSource.close();
        }
    }
}

// 3. AI Page Generation Flow
function generateNewPage() {
    const title = newPageTitleInput.value.trim();
    const prompt = newPagePromptInput.value.trim();
    
    if (!title) {
        alert('페이지 이름을 입력해 주세요.');
        newPageTitleInput.focus();
        return;
    }
    
    submitAddBtn.disabled = true;
    submitAddBtn.textContent = 'AI 생성 대기 중...';
    modalStatusBox.classList.remove('hidden');
    modalStatusMsg.textContent = '설계를 등록하는 중...';
    
    const requestData = {
        title: title,
        description: prompt,
        pageSize: editorPageSize.value,
        styleTheme: editorStyleTheme.value,
        orientation: newPageOrientationSelect.value
    };
    
    fetch('/api/generate-html', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        listenToGenerationStream(data.task_id);
    })
    .catch(err => {
        alert(`생성 실패: ${err.message}`);
        resetModalBtn();
    });
}

function listenToGenerationStream(taskId) {
    eventSource = new EventSource(`/api/task-stream/${taskId}`);
    
    eventSource.onmessage = function(event) {
        const task = JSON.parse(event.data);
        modalStatusMsg.textContent = task.message || 'AI 디자인 진행 중...';
        
        if (task.status === 'success') {
            eventSource.close();
            resetModalBtn();
            showModal(false);
            
            // Add new page to memory state
            const newPage = {
                id: 'page-' + Date.now() + '-' + Math.floor(Math.random() * 1000),
                title: task.title || newPageTitleInput.value.trim(),
                html: task.html,
                orientation: task.orientation || 'portrait'
            };
            
            pages.push(newPage);
            activePageId = newPage.id;
            
            buildSidebar();
            renderActivePage();
            exportBtn.disabled = false;
        } else if (task.status === 'failed') {
            eventSource.close();
            alert(`AI 생성 실패: ${task.message}`);
            resetModalBtn();
        }
    };
    
    eventSource.onerror = function() {
        eventSource.close();
        alert('서버 연결 에러가 발생했습니다.');
        resetModalBtn();
    };
}

function resetModalBtn() {
    submitAddBtn.disabled = false;
    submitAddBtn.textContent = 'AI로 페이지 생성';
}

// 4. Sidebar Building & Page Controls
function buildSidebar() {
    pagesList.innerHTML = '';
    
    if (pages.length === 0) {
        pagesList.innerHTML = `
            <div class="empty-list-state">
                좌측 상단의 '+ 추가' 버튼을 눌러 첫 페이지를 생성해보세요.
            </div>
        `;
        exportBtn.disabled = true;
        currentPageTitle.textContent = '선택된 페이지 없음';
        paperContainer.innerHTML = `
            <div class="paper-placeholder">
                <div class="placeholder-icon">📖</div>
                <h3>나만의 멀티 페이지 다이어리 빌더</h3>
                <p>좌측 상단의 <strong>'+ 추가'</strong> 버튼을 클릭하여 다이어리 양식 페이지들을 하나씩 AI로 만들어보세요. 생성된 페이지들 사이에 직접 마우스 클릭으로 하이퍼링크를 엮을 수 있습니다.</p>
            </div>
        `;
        return;
    }
    
    pages.forEach(page => {
        const item = document.createElement('div');
        item.className = `page-item ${page.id === activePageId ? 'active' : ''}`;
        item.dataset.pageId = page.id;
        
        // Icon matching
        let icon = '📝';
        const searchTitle = page.title.toLowerCase();
        if (searchTitle.includes('먼슬리') || searchTitle.includes('monthly') || searchTitle.includes('달력')) icon = '🗓️';
        else if (searchTitle.includes('위클리') || searchTitle.includes('weekly')) icon = '📅';
        else if (searchTitle.includes('일기') || searchTitle.includes('daily') || searchTitle.includes('데일리')) icon = '📝';
        else if (searchTitle.includes('표지') || searchTitle.includes('cover')) icon = '📘';
        
        item.innerHTML = `
            <div class="page-item-info">
                <span class="page-item-icon">${icon}</span>
                <span class="page-item-title">${page.title}</span>
            </div>
            <div class="page-item-actions">
                <button type="button" class="item-action-btn rename" title="이름 수정">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4z"></path></svg>
                </button>
                <button type="button" class="item-action-btn duplicate" title="페이지 복제">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </button>
                <button type="button" class="item-action-btn delete" title="페이지 삭제">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            </div>
        `;
        
        // Clicking item selects the page (only if not clicking actions)
        item.addEventListener('click', (e) => {
            if (e.target.closest('.item-action-btn') || e.target.closest('.page-item-title-input')) return;
            selectPage(page.id);
        });
        
        // Bind actions
        item.querySelector('.rename').addEventListener('click', (e) => {
            e.stopPropagation();
            startRename(page, item);
        });
        
        item.querySelector('.page-item-title').addEventListener('dblclick', (e) => {
            e.stopPropagation();
            startRename(page, item);
        });
        
        item.querySelector('.duplicate').addEventListener('click', (e) => {
            e.stopPropagation();
            duplicatePage(page.id);
        });
        
        item.querySelector('.delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deletePage(page.id);
        });
        
        // Drag & Drop event bindings
        item.setAttribute('draggable', 'true');
        
        item.addEventListener('dragstart', (e) => {
            // Only allow drag if not currently editing rename
            if (item.querySelector('.page-item-title-input')) {
                e.preventDefault();
                return;
            }
            e.dataTransfer.setData('text/plain', page.id);
            item.classList.add('dragging');
        });
        
        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
            document.querySelectorAll('.page-item').forEach(el => {
                el.classList.remove('drag-over-above', 'drag-over-below');
            });
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            const draggingEl = document.querySelector('.page-item.dragging');
            if (!draggingEl || draggingEl.dataset.pageId === page.id) return;
            
            const rect = item.getBoundingClientRect();
            const relativeY = e.clientY - rect.top;
            
            if (relativeY < rect.height / 2) {
                item.classList.add('drag-over-above');
                item.classList.remove('drag-over-below');
            } else {
                item.classList.add('drag-over-below');
                item.classList.remove('drag-over-above');
            }
        });
        
        item.addEventListener('dragleave', () => {
            item.classList.remove('drag-over-above', 'drag-over-below');
        });
        
        item.addEventListener('drop', (e) => {
            e.preventDefault();
            const draggedId = e.dataTransfer.getData('text/plain');
            if (draggedId === page.id) return;
            
            const draggedPage = pages.find(p => p.id === draggedId);
            if (!draggedPage) return;
            
            const cleanPages = pages.filter(p => p.id !== draggedId);
            const targetIdx = cleanPages.findIndex(p => p.id === page.id);
            
            const rect = item.getBoundingClientRect();
            const relativeY = e.clientY - rect.top;
            const isAbove = relativeY < rect.height / 2;
            
            const insertIdx = isAbove ? targetIdx : targetIdx + 1;
            cleanPages.splice(insertIdx, 0, draggedPage);
            
            pages = cleanPages;
            buildSidebar();
        });
        
        pagesList.appendChild(item);
    });
}

/**
 * Turns the page title span into an inline input field to rename the page
 */
function startRename(page, item) {
    const titleSpan = item.querySelector('.page-item-title');
    if (!titleSpan || item.querySelector('.page-item-title-input')) return;
    
    // Disable dragging during rename
    item.removeAttribute('draggable');
    
    const originalTitle = page.title;
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'page-item-title-input';
    input.value = originalTitle;
    
    titleSpan.replaceWith(input);
    input.focus();
    input.select();
    
    let isFinished = false;
    
    function saveRename() {
        if (isFinished) return;
        isFinished = true;
        
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== originalTitle) {
            page.title = newTitle;
            // Update active page title if it is the currently selected page
            if (page.id === activePageId) {
                currentPageTitle.textContent = newTitle;
            }
        }
        buildSidebar();
    }
    
    function cancelRename() {
        if (isFinished) return;
        isFinished = true;
        buildSidebar();
    }
    
    input.addEventListener('blur', saveRename);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveRename();
        } else if (e.key === 'Escape') {
            cancelRename();
        }
    });
}

function selectPage(pageId) {
    activePageId = pageId;
    buildSidebar();
    renderActivePage();
}

function duplicatePage(pageId) {
    const original = pages.find(p => p.id === pageId);
    if (!original) return;
    
    // Copy HTML state exactly
    const copy = {
        id: 'page-' + Date.now() + '-' + Math.floor(Math.random() * 1000),
        title: `${original.title} (사본)`,
        html: original.html,
        orientation: original.orientation
    };
    
    pages.push(copy);
    activePageId = copy.id;
    buildSidebar();
    renderActivePage();
}

function deletePage(pageId) {
    if (!confirm('이 페이지를 삭제하시겠습니까?')) return;
    
    const index = pages.findIndex(p => p.id === pageId);
    if (index === -1) return;
    
    pages.splice(index, 1);
    
    if (activePageId === pageId) {
        activePageId = pages.length > 0 ? pages[0].id : null;
    }
    
    buildSidebar();
    renderActivePage();
}

// 5. Render active page inside IFrame
function renderActivePage() {
    const page = pages.find(p => p.id === activePageId);
    if (!page) return;
    
    currentPageTitle.textContent = page.title;
    
    // Set Dimensions via zoom UI
    updateZoomUI();
    
    paperContainer.innerHTML = '';
    const iframe = document.createElement('iframe');
    iframe.id = 'preview-iframe';
    
    // 브라우저 로드 시점에 맞춘 이벤트 리스너 사전 정의
    iframe.onload = () => {
        setupIframeInteractions(iframe);
        updateZoomUI();
    };
    
    paperContainer.appendChild(iframe);
    
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    // Override min-height (e.g. min-height: 1500px) with 100% to fit the A4 container height exactly and prevent scrolling
    let cleanHTML = page.html.replace(/min-height\s*:\s*\d+px/g, 'min-height: 100%');
    doc.write(cleanHTML);
    doc.close();
    
    // 동기식으로 로드가 완료되었을 때를 위한 즉시 초기화
    setupIframeInteractions(iframe);
    updateZoomUI();
}

// 6. IFrame Event Handlers & Link Binding Logic
function setupIframeInteractions(iframe) {
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    console.log("setupIframeInteractions: linkMode =", linkMode, "doc.initialized =", doc ? doc.initialized : 'no-doc');
    if (!doc || doc.initialized === true) return;
    doc.initialized = true;
    
    if (linkMode) {
        // Inject Outline styling in head for visual selection
        const style = doc.createElement('style');
        style.id = 'link-edit-style';
        style.innerHTML = `
            * {
                cursor: cell !important;
            }
            /* 보라색 가이드라인: 하이퍼링크가 걸려있지 않은 일반 요소 */
            *:not(a):not(a *):not(:has(a)):hover {
                outline: 2px dashed #8b5cf6 !important;
                outline-offset: -1px;
                background-color: rgba(139, 92, 246, 0.05) !important;
            }
            /* 초록색 가이드라인: 이미 하이퍼링크가 적용된 요소 및 부모/자식 요소 */
            a:hover, a *:hover, *:has(> a):hover, *:has(> a) *:hover {
                outline: 2px dashed #10b981 !important;
                outline-offset: -1px;
                background-color: rgba(16, 185, 129, 0.05) !important;
            }
            a {
                pointer-events: none !important; /* Disable navigation during edit */
            }
        `;
        doc.head.appendChild(style);
        
        // Listen to clicks inside IFrame to bind hyperlink
        doc.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            let targetEl = e.target;
            // Safari/Webkit text node click target normalization
            if (targetEl && targetEl.nodeType === 3) {
                targetEl = targetEl.parentNode;
            }
            selectedElement = targetEl;
            window.debug_last_click = selectedElement ? selectedElement.tagName : 'unknown';
            console.log("Iframe Click target:", selectedElement, "tag:", selectedElement ? selectedElement.tagName : 'none');
            
            // Calculate screen position relative to parent window scroll & iframe bounding rectangle
            const iframeRect = iframe.getBoundingClientRect();
            const clickX = iframeRect.left + window.scrollX + e.clientX;
            const clickY = iframeRect.top + window.scrollY + e.clientY;
            
            showLinkPopup(clickX, clickY);
        });
    } else {
        // Regular mode: Click links to navigate page list
        doc.addEventListener('click', (e) => {
            const anchor = e.target.closest('a');
            if (anchor && anchor.getAttribute('href')?.startsWith('#')) {
                e.preventDefault();
                const targetPageId = anchor.getAttribute('href').substring(1);
                
                // Switch pages if target exists
                if (pages.some(p => p.id === targetPageId)) {
                    selectPage(targetPageId);
                }
            }
        });
    }
}

function toggleLinkMode() {
    linkMode = linkModeCheckbox.checked;
    
    if (linkMode) {
        linkHelperBanner.classList.remove('hidden');
    } else {
        linkHelperBanner.classList.add('hidden');
        hideLinkPopup();
    }
    
    // Rerender iframe to apply/remove selectors
    renderActivePage();
}

// 7. Tooltip popup positioning and actions
function showLinkPopup(x, y) {
    // Populate select dropdown with other pages
    linkTargetSelect.innerHTML = '<option value="">-- 연결 대상 페이지 선택 --</option>';
    pages.forEach(p => {
        if (p.id !== activePageId) {
            linkTargetSelect.innerHTML += `<option value="${p.id}">${p.title}</option>`;
        }
    });
    
    // Check if element is already an anchor link or wraps/contains one
    const existingAnchor = selectedElement.closest('a') || selectedElement.querySelector('a');
    if (existingAnchor && existingAnchor.getAttribute('href')?.startsWith('#')) {
        const targetId = existingAnchor.getAttribute('href').substring(1);
        linkTargetSelect.value = targetId;
        unlinkBtn.style.display = 'block';
    } else {
        unlinkBtn.style.display = 'none';
    }
    
    linkPopup.style.left = `${x - 120}px`; // center popup horizontally
    linkPopup.style.top = `${y + 15}px`;   // place popup below clicked spot
    console.log("showLinkPopup: pages =", pages.length, "popup position left =", linkPopup.style.left, "top =", linkPopup.style.top);
    linkPopup.classList.remove('hidden');
    window.debug_popup_shown = true;
}

function hideLinkPopup() {
    linkPopup.classList.add('hidden');
    selectedElement = null;
}

function applyHyperlink() {
    if (!selectedElement) return;
    
    const targetPageId = linkTargetSelect.value;
    if (!targetPageId) {
        alert('연결할 대상 페이지를 선택해 주세요.');
        return;
    }
    
    const iframe = document.getElementById('preview-iframe');
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    
    // Check if element is already inside an anchor or contains one
    let anchor = selectedElement.closest('a') || selectedElement.querySelector('a');
    
    if (anchor) {
        // Just update existing anchor
        anchor.setAttribute('href', `#${targetPageId}`);
        anchor.className = 'diary-link';
    } else {
        // Create new anchor wrapper
        anchor = doc.createElement('a');
        anchor.setAttribute('href', `#${targetPageId}`);
        anchor.className = 'diary-link';
        anchor.style.textDecoration = 'none';
        anchor.style.color = 'inherit';
        anchor.style.width = '100%';
        anchor.style.height = '100%';
        
        // Inherit layout/alignment characteristics from the parent element to prevent layout breakage
        const iframeWindow = iframe.contentWindow;
        const computedStyle = iframeWindow.getComputedStyle(selectedElement);
        
        if (computedStyle.display.includes('flex')) {
            anchor.style.display = 'flex';
            anchor.style.flexDirection = computedStyle.flexDirection;
            anchor.style.alignItems = computedStyle.alignItems;
            anchor.style.justifyContent = computedStyle.justifyContent;
        } else {
            anchor.style.display = 'inline-block';
            anchor.style.textAlign = computedStyle.textAlign;
            anchor.style.verticalAlign = computedStyle.verticalAlign;
            // If parent has line-height, match it to keep vertical alignment
            anchor.style.lineHeight = computedStyle.lineHeight;
        }
        
        // Move children of selectedElement into the new anchor wrapper
        while (selectedElement.firstChild) {
            anchor.appendChild(selectedElement.firstChild);
        }
        
        // Append anchor as the child of selectedElement
        selectedElement.appendChild(anchor);
    }
    
    // Remove link-edit-style before saving html to state
    const editStyle = doc.getElementById('link-edit-style');
    if (editStyle) editStyle.remove();
    
    // Save updated HTML
    const activePage = pages.find(p => p.id === activePageId);
    if (activePage) {
        activePage.html = doc.documentElement.outerHTML;
    }
    
    hideLinkPopup();
    renderActivePage(); // refresh
}

function removeHyperlink() {
    if (!selectedElement) return;
    
    const iframe = document.getElementById('preview-iframe');
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    
    const anchor = selectedElement.closest('a') || selectedElement.querySelector('a');
    if (anchor) {
        // Replace anchor with its contents
        const parent = anchor.parentNode;
        while (anchor.firstChild) {
            parent.insertBefore(anchor.firstChild, anchor);
        }
        parent.removeChild(anchor);
    }
    
    // Remove link-edit-style before saving
    const editStyle = doc.getElementById('link-edit-style');
    if (editStyle) editStyle.remove();
    
    // Save updated HTML
    const activePage = pages.find(p => p.id === activePageId);
    if (activePage) {
        activePage.html = doc.documentElement.outerHTML;
    }
    
    hideLinkPopup();
    renderActivePage();
}

// 8. PDF Export (Window.print)
function exportToPDF() {
    if (pages.length === 0) return;
    
    printContainer.innerHTML = '';
    const size = editorPageSize.value;
    const parser = new DOMParser();
    
    pages.forEach(page => {
        const pageDiv = document.createElement('div');
        pageDiv.className = `pdf-page ${size} ${page.orientation || 'portrait'}`;
        pageDiv.id = page.id;
        
        // Replace min-height of body/canvas to prevent A4 pages from stretching
        const cleanHTML = page.html.replace(/min-height\s*:\s*\d+px/g, 'min-height: 100%');
        const doc = parser.parseFromString(cleanHTML, 'text/html');
        
        // Remove content-zoom-style for high-fidelity 100% scaling export
        const zoomStyleEl = doc.getElementById('content-zoom-style');
        if (zoomStyleEl) zoomStyleEl.remove();
        
        // 1. Extract dynamic Google Fonts styles and link references, appending them to the main head
        const linkTags = doc.querySelectorAll('link[rel="stylesheet"]');
        linkTags.forEach(link => {
            const href = link.getAttribute('href');
            if (href && !document.querySelector(`link[href="${href}"]`)) {
                const newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = href;
                document.head.appendChild(newLink);
            }
        });
        
        // 2. Extract style blocks and scope rules to this specific page element
        const styleTags = doc.querySelectorAll('style');
        let cssText = '';
        styleTags.forEach(style => {
            cssText += style.textContent + '\n';
        });
        
        // Scope every CSS rule so it doesn't bleed out of this specific pageDiv ID wrapper
        const scopeSelector = `#${page.id}`;
        const scopedCSS = scopeCSS(cssText, scopeSelector);
        
        // Create style block inside the page div
        const styleEl = document.createElement('style');
        styleEl.textContent = scopedCSS;
        pageDiv.appendChild(styleEl);
        
        // 3. Extract only the actual content container (.page-container)
        const pageContainer = doc.querySelector('.page-container');
        if (pageContainer) {
            pageDiv.appendChild(pageContainer.cloneNode(true));
        } else {
            // Fallback if page-container structure is not found (should not happen normally)
            pageDiv.innerHTML += doc.body.innerHTML;
        }
        
        printContainer.appendChild(pageDiv);
    });
    
    // Trigger native printing popup (PDF export)
    window.print();
}

/**
 * Scopes stylesheet rules by prepending a selector prefix.
 * Falls back to basic regex replacement if parsing fails.
 */
function scopeCSS(cssText, scopeSelector) {
    // Strip global @page directives that can override named page orientation layouts
    cssText = cssText.replace(/@page\s*\{[^}]*\}/gi, '');
    
    const tempStyle = document.createElement('style');
    tempStyle.textContent = cssText;
    document.head.appendChild(tempStyle);
    
    let scopedCss = '';
    try {
        const sheet = tempStyle.sheet;
        const rules = sheet.cssRules || [];
        for (let i = 0; i < rules.length; i++) {
            scopedCss += scopeRule(rules[i], scopeSelector) + '\n';
        }
    } catch (e) {
        console.error('Failed to scope CSS natively, using regex fallback:', e);
        // Robust regex fallback
        scopedCss = cssText
            .replace(/body\s*\{/g, `${scopeSelector} {`)
            .replace(/body\s*,/g, `${scopeSelector},`)
            .replace(/html\s*\{/g, `${scopeSelector} {`)
            .replace(/html\s*,/g, `${scopeSelector},`)
            .replace(/\.page-container/g, `${scopeSelector} .page-container`);
    } finally {
        tempStyle.remove();
    }
    
    // Explicitly add print-color-adjust for backgrounds inside the scoped wrapper
    scopedCss += `
${scopeSelector} {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
`;
    
    return scopedCss;
}

/**
 * Recursively prefixes rule selectors with the scope selector.
 */
function scopeRule(rule, scope) {
    if (rule.type === CSSRule.STYLE_RULE) {
        const selectors = rule.selectorText.split(',');
        const scopedSelectors = selectors.map(sel => {
            const s = sel.trim();
            if (s === 'html' || s === 'body') {
                return scope;
            }
            if (s.startsWith('.page-container')) {
                return `${scope} ${s}`;
            }
            // Prefix other general classes or tags
            return `${scope} ${s}`;
        }).join(', ');
        
        return `${scopedSelectors} { ${rule.style.cssText} }`;
    } else if (rule.type === CSSRule.MEDIA_RULE) {
        let mediaContent = '';
        const subRules = rule.cssRules || [];
        for (let i = 0; i < subRules.length; i++) {
            mediaContent += scopeRule(subRules[i], scope) + '\n';
        }
        return `@media ${rule.media.mediaText} {\n${mediaContent}\n}`;
    } else if (rule.type === CSSRule.KEYFRAMES_RULE || rule.type === CSSRule.KEYFRAME_RULE || rule.type === CSSRule.FONT_FACE_RULE) {
        // Return global definitions as-is
        return rule.cssText;
    }
    return rule.cssText;
}

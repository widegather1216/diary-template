document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const titleInput = document.getElementById('title');
    const descInput = document.getElementById('description');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = document.querySelector('.btn-text');
    
    const appWrapper = document.getElementById('app-wrapper');
    const openDiaryBtn = document.getElementById('open-diary-btn');
    
    // Panels
    const interactiveCanvas = document.getElementById('interactive-canvas');
    const resultContainer = document.getElementById('result-container');
    const canvasStatusText = document.getElementById('canvas-status-text');
    
    // Interactive Sketch Elements
    const blueprintContainer = document.getElementById('blueprint-container');
    const previewIframe = document.getElementById('preview-iframe');
    const loadingAnimationContainer = document.getElementById('loading-animation-container');
    
    const downloadLink = document.getElementById('download-link');
    
    let currentFileId = null;

    const diaryBand = document.getElementById('diary-band');

    // 1. 다이어리 표지 펼치기 이벤트 (고무줄 모션 포함)
    if (openDiaryBtn) {
        openDiaryBtn.addEventListener('click', () => {
            if (diaryBand) {
                diaryBand.classList.add('is-unbanding');
                setTimeout(() => {
                    appWrapper.classList.add('is-open');
                    setTimeout(() => { titleInput.focus(); }, 800);
                }, 400);
            } else {
                appWrapper.classList.add('is-open');
                setTimeout(() => { titleInput.focus(); }, 800);
            }
        });
    }

    // 1.5. 다이어리 3D 북 플립 (Book Flip) 로직
    // 전역 함수로 노출하여 HTML의 onclick 속성에서 바로 호출할 수 있게 함
    window.flipNext = function(sheetIndex) {
        const sheet = document.getElementById(`sheet-${sheetIndex}`);
        if (!sheet) return;
        
        sheet.classList.add('is-flipped');
        
        // 애니메이션 중간 지점(0.6s)에서 z-index를 조정하여 겹침 순서를 변경
        // 1.2s 애니메이션의 정중앙(종이가 수직으로 세워진 순간)에 z-index를 바꿔야 팝핑 현상이 없습니다.
        setTimeout(() => {
            sheet.dataset.originalZ = sheet.style.zIndex;
            // 넘어간 장은 왼쪽 스택에 쌓이므로, 나중에 넘어간 장(더 큰 sheetIndex)이 
            // 위로 올라오도록 z-index를 새롭게 부여 (예: sheet-1 -> 11, sheet-2 -> 12)
            sheet.style.zIndex = (10 + sheetIndex).toString();
        }, 600);
    };

    window.flipPrev = function(sheetIndex) {
        const sheet = document.getElementById(`sheet-${sheetIndex}`);
        if (!sheet) return;
        
        sheet.classList.remove('is-flipped');
        
        // 되돌아갈 때도 종이가 수직으로 세워지는 중간 지점(0.6s)에서 원래 z-index로 복구
        // 즉시 복구하면 아직 왼쪽 스택에 있을 때 z-index가 낮아져 밑장 빼기 현상이 발생함
        setTimeout(() => {
            if (sheet.dataset.originalZ) {
                sheet.style.zIndex = sheet.dataset.originalZ;
            }
        }, 600);
    };

    // 2. Interactive Blueprint & Real Preview 로직
    let preGeneratedLayouts = {};
    const styleThemeSelect = document.getElementById('styleTheme');
    const designModeRadios = document.querySelectorAll('input[name="designMode"]');

    const THEME_CONFIG = {
        'Cute': {
            'fonts': '<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@400;600&family=Nanum+Pen+Script&display=swap" rel="stylesheet">',
            'css': "body { font-family: 'Quicksand', 'Nanum Pen Script', sans-serif; color: #3d348b; } h1, h2, h3, .title { font-family: 'Pacifico', 'Nanum Pen Script', cursive; color: #f15bb5; } .page-container { position: relative; }",
            'border_color': '#e0b1cb',
            'soften_borders': true
        },
        'Editorial': {
            'fonts': '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">',
            'css': "body { font-family: 'Inter', sans-serif; color: #1a1a1a; background-color: #faf9f6 !important; } h1, h2, h3, .title { font-family: 'Playfair Display', serif; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: #0d1b2a; } .page-container { position: relative; }",
            'border_color': '#4a4e69',
            'soften_borders': false
        },
        'Minimal': {
            'fonts': '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">',
            'css': "body { font-family: 'Inter', sans-serif; color: #2b2d42; } h1, h2, h3, .title { font-weight: 800; letter-spacing: -0.03em; color: #1d3557; } .page-container { position: relative; }",
            'border_color': '#8d99ae',
            'soften_borders': false
        }
    };

    async function loadLayouts() {
        try {
            const response = await fetch('/static/pre_generated_layouts.json');
            if (response.ok) {
                preGeneratedLayouts = await response.json();
                updatePreview('');
            }
        } catch (e) {
            console.error('레이아웃 로드 실패:', e);
        }
    }
    loadLayouts();

    function getLayoutCategory(title) {
        const text = title.toLowerCase().replace(/\s+/g, '');
        if (!text) return 'cornell';
        
        const mappings = {
            mandalart: ["mandalart", "만다라트", "만다라", "3x3", "81", "만달아트", "목표달성"],
            weekly: ["weekly", "주간", "위클리", "일주일", "주별"],
            daily: ["daily", "데일리", "일간", "하루", "오늘", "일기장", "저널", "journal", "다이어리", "다이얼리"],
            yearly: ["yearly", "연간", "연간계획", "1년", "이어리", "year", "신년계획", "새해계획"],
            todo: ["to-do", "todo", "투두", "할일", "태스크", "checklist", "체크리스트", "해야할일", "업무목록"],
            habit: ["habit", "해빗", "습관", "루틴", "트래커", "tracker", "습관트래커", "습관형성", "습관기록", "루틴체크", "매일습관"],
            ledger: ["ledger", "가계부", "금전", "지출", "용돈", "소비", "expense", "budget", "용돈기입장", "자산관리", "재정기록", "돈관리"],
            cornell: ["cornell", "코넬", "노트", "필기", "notes", "코넬식", "필기노트", "강의노트", "수업필기"],
            mindmap: ["mindmap", "마인드맵", "브레인스토밍", "생각정리", "idea", "아이디어", "생각그물", "아이디어맵", "생각매핑"],
            reading_note: ["readingnote", "bookreview", "독서록", "독서노트", "책리뷰", "서평", "북리뷰", "책기록", "독서일기", "독후감", "독서감상문"],
            monthly: ["monthly", "calendar", "월간", "캘린더", "달력", "한달", "계획표", "먼슬리", "플래너", "플레너", "스케줄러", "스케쥴러", "월별"]
        };

        for (const [key, keywords] of Object.entries(mappings)) {
            if (keywords.some(kw => text.includes(kw))) {
                return key;
            }
        }
        return 'cornell';
    }

    function updatePreview(title) {
        if (!title) {
            previewIframe.classList.remove('is-loaded');
            previewIframe.srcdoc = '';
            return;
        }
        
        const category = getLayoutCategory(title);
        const designMode = document.querySelector('input[name="designMode"]:checked').value;
        const styleTheme = styleThemeSelect.value;
        
        let html = preGeneratedLayouts[category] || preGeneratedLayouts['cornell'];
        if (!html) return;
        
        let theme = THEME_CONFIG[styleTheme] || THEME_CONFIG['Minimal'];
        let modifiedHtml = html;
        
        // 테마 스타일 주입
        if (designMode !== 'guide') {
            modifiedHtml = modifiedHtml.replace(/#333/g, theme.border_color);
            if (theme.soften_borders) {
                modifiedHtml = modifiedHtml.replace(/border-radius:\s*0/g, 'border-radius: 12px');
            }
            const themeCss = `<style>${theme.css}</style>`;
            modifiedHtml = modifiedHtml.replace('</head>', theme.fonts + themeCss + '</head>');
        }
        
        // 순차 페이드인 애니메이션 스타일 주입 (원래 테마 색상 및 스타일 그대로 페이드인)
        const sketchStyles = `
        <style>
        body {
            background-color: transparent !important;
            overflow: hidden !important;
        }
        .page-container {
            box-shadow: none !important;
            border: none !important;
            top: 20px !important;
            margin-top: 0 !important;
        }
        /* 모든 요소 초기 투명화 및 순차 페이드인 */
        div, section, table, tr, td, th, span, p, h1, h2, h3, h4, h5, h6, li, a, img {
            animation: fadeInElement 1.0s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
            opacity: 0;
        }
        /* 배경 격자선 페이드인 */
        .lined-bg, .grid-bg, .dot-bg {
            animation: fadeInBg 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards !important;
            opacity: 0;
        }
        @keyframes fadeInElement {
            0% { opacity: 0; transform: translateY(2px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeInBg {
            0% { opacity: 0; }
            100% { opacity: 0.35; }
        }
        </style>
        `;
        
        // 양식명 동적 업데이트 및 순차 드로잉 지연시간 스크립트 주입
        const displayTitle = title ? title : (preGeneratedLayouts[category] ? category.toUpperCase() + ' PLANNER' : 'NOTEBOOK');
        const sketchScript = `
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            const titleTags = ['h1', 'h2', '.title', '.header-title'];
            let titleUpdated = false;
            for (const selector of titleTags) {
                const titleEl = document.querySelector(selector);
                if (titleEl) {
                    titleEl.textContent = "${displayTitle.replace(/"/g, '\\"')}";
                    titleUpdated = true;
                    break;
                }
            }
            if (!titleUpdated) {
                const firstHeading = document.querySelector('h1, h2');
                if (firstHeading) {
                    firstHeading.textContent = "${displayTitle.replace(/"/g, '\\"')}";
                }
            }

            const elements = document.querySelectorAll('div, section, span, p, h1, h2, h3, h4, h5, h6, li, tr, td');
            elements.forEach((el, index) => {
                el.style.animationDelay = (index * 0.012) + 's';
            });
        });
        </script>
        `;
        
        modifiedHtml = modifiedHtml.replace('</head>', sketchStyles + sketchScript + '</head>');
        
        previewIframe.classList.remove('is-loaded');
        previewIframe.srcdoc = modifiedHtml;
        
        previewIframe.onload = () => {
            previewIframe.classList.add('is-loaded');
        };
    }

    let debounceTimer = null;
    if (titleInput) {
        titleInput.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            clearTimeout(debounceTimer);
            
            if (!val) {
                updatePreview('');
                return;
            }
            
            debounceTimer = setTimeout(() => {
                updatePreview(val);
            }, 600);
        });
    }

    if (styleThemeSelect) {
        styleThemeSelect.addEventListener('change', (e) => {
            updatePreview(titleInput.value.trim());
        });
    }

    designModeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'guide') {
                styleThemeSelect.disabled = true;
                styleThemeSelect.parentElement.style.opacity = '0.5';
            } else {
                styleThemeSelect.disabled = false;
                styleThemeSelect.parentElement.style.opacity = '1';
            }
            updatePreview(titleInput.value.trim());
        });
    });

    // 사용자가 페이지를 떠날 때 임시 PDF 삭제
    window.addEventListener('beforeunload', () => {
        if (currentFileId) {
            navigator.sendBeacon('/api/cleanup-pdf', JSON.stringify({ file_id: currentFileId }));
        }
    });

    // 3. 폼 제출 (생성 및 로딩 애니메이션 전환)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = titleInput.value.trim();
        const description = descInput.value.trim();
        const pageSize = document.getElementById('pageSize').value;
        const designMode = document.querySelector('input[name="designMode"]:checked').value;
        const styleTheme = document.getElementById('styleTheme').value;

        if (!title) {
            alert('양식명은 필수 입력 항목입니다.');
            return;
        }

        if (currentFileId) {
            navigator.sendBeacon('/api/cleanup-pdf', JSON.stringify({ file_id: currentFileId }));
            currentFileId = null;
        }

        // UI 상태 업데이트: 생성 모드
        document.body.classList.add('is-generating-mode');
        
        generateBtn.disabled = true;
        btnText.textContent = '생성 중...';
        
        canvasStatusText.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        interactiveCanvas.classList.remove('hidden');

        // 블루프린트 날려버리고(fly-away) 로딩 애니메이션 전환
        if (blueprintContainer && loadingAnimationContainer) {
            blueprintContainer.classList.add('fly-away');
            setTimeout(() => {
                blueprintContainer.classList.add('hidden');
                loadingAnimationContainer.classList.remove('hidden');
            }, 600); // CSS 애니메이션 시간(0.6s)과 동기화
        }

        try {
            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, description, pageSize, designMode, styleTheme })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '알 수 없는 에러가 발생했습니다.');
            }

            const data = await response.json();
            currentFileId = data.file_id;

            const encodedTitle = encodeURIComponent(data.title);
            downloadLink.href = `/api/download-pdf/${currentFileId}?title=${encodedTitle}&page_size=${data.page_size}`;
            downloadLink.download = `${data.title}_${data.page_size}.pdf`;
            
            // 결과창으로 전환
            interactiveCanvas.classList.add('hidden');
            resultContainer.classList.remove('hidden');

        } catch (error) {
            console.error('Error:', error);
            alert(`오류: ${error.message}`);
            // 에러 시 로딩 텍스트 숨기고 상태 원복
            canvasStatusText.classList.add('hidden');
            document.body.classList.remove('is-generating-mode');
            
            // 캔버스 초기화
            if (blueprintContainer && loadingAnimationContainer) {
                blueprintContainer.classList.remove('fly-away', 'hidden');
                loadingAnimationContainer.classList.add('hidden');
            }
        } finally {
            generateBtn.disabled = false;
            btnText.textContent = 'PDF 생성하기';
        }
    });
});

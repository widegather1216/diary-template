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
    let typewriterTimeout = null;

    function adjustPreviewScale() {
        const paper = document.querySelector('.sketch-paper');
        const iframe = document.getElementById('preview-iframe');
        if (!paper || !iframe) return;
        
        const rect = paper.getBoundingClientRect();
        
        const computedStyle = window.getComputedStyle(paper);
        const paddingLeft = parseFloat(computedStyle.paddingLeft) || 0;
        const paddingRight = parseFloat(computedStyle.paddingRight) || 0;
        const paddingTop = parseFloat(computedStyle.paddingTop) || 0;
        const paddingBottom = parseFloat(computedStyle.paddingBottom) || 0;
        
        const containerWidth = rect.width - (paddingLeft + paddingRight);
        const containerHeight = rect.height - (paddingTop + paddingBottom);
        
        const a4Width = 794;
        const a4Height = 1123;
        
        const scaleWidth = containerWidth / a4Width;
        const scaleHeight = containerHeight / a4Height;
        const scale = Math.min(scaleWidth, scaleHeight);
        
        iframe.style.setProperty('--preview-scale', scale);
    }

    window.addEventListener('resize', adjustPreviewScale);

    function typeWriter(element, text, speed, callback) {
        element.textContent = '';
        let i = 0;
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                typewriterTimeout = setTimeout(type, speed);
            } else if (callback) {
                callback();
            }
        }
        type();
    }

    const diaryBand = document.getElementById('diary-band');

    // 1. 다이어리 표지 펼치기 이벤트 (고무줄 모션 포함)
    if (openDiaryBtn) {
        openDiaryBtn.addEventListener('click', () => {
            const onOpenComplete = () => {
                appWrapper.classList.add('is-open');
                // 다이어리가 열릴 때 스케일 조정을 즉시 및 트랜지션 완료(1.2초) 후 수행
                adjustPreviewScale();
                setTimeout(adjustPreviewScale, 1200);
                setTimeout(() => { titleInput.focus(); }, 800);
            };

            if (diaryBand) {
                diaryBand.classList.add('is-unbanding');
                setTimeout(onOpenComplete, 400);
            } else {
                onOpenComplete();
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
    let themeConfig = {};
    let categoryMappings = {
        "mandalart": ["mandalart", "만다라트", "만다라", "3x3", "81", "만달아트", "목표달성"],
        "monthly": ["monthly", "calendar", "월간", "캘린더", "달력", "한달", "계획표", "먼슬리", "플래너", "플레너", "스케줄러", "스케쥴러", "월별"],
        "weekly": ["weekly", "주간", "위클리", "일주일", "주별", "플래너", "플레너", "스케줄러", "스케쥴러"],
        "daily": ["daily", "데일리", "일간", "하루", "오늘", "일기장", "저널", "journal", "다이어리", "다이얼리", "스케줄러", "스케쥴러", "플래너", "플레너", "일기"],
        "yearly": ["yearly", "연간", "연간 계획", "1년", "이어리", "year", "신년 계획", "새해 계획", "플래너", "플레너", "스케줄러", "스케쥴러"],
        "todo": ["to-do", "todo", "투두", "할 일", "할일", "태스크", "checklist", "체크리스트", "해야할일", "해야할 일", "업무 목록"],
        "habit": ["habit", "해빗", "습관", "루틴", "트래커", "tracker", "습관 트래커", "습관 형성", "습관 기록", "루틴 체크", "매일 습관"],
        "ledger": ["ledger", "가계부", "금전", "지출", "용돈", "소비", "expense", "budget", "용돈 기입장", "용돈기입장", "자산 관리", "재정 기록", "돈 관리"],
        "cornell": ["cornell", "코넬", "노트", "필기", "notes", "코넬식", "필기 노트", "강의 노트", "수업 필기"],
        "diet": ["diet", "meal", "식단", "식단표", "다이어트", "식사", "food", "메뉴 플래너", "메뉴 플레너", "식단 일기"],
        "reading_note": ["reading note", "book review", "독서록", "독서 노트", "책 리뷰", "서평", "북리뷰", "책 기록", "독서 일기", "독후감", "독서 감상문", "독서", "책"],
        "reading_tracker": ["reading tracker", "book log", "독서 기록", "독서 리스트", "책 목록", "독서 트래커", "책장", "도서 목록", "책 리스트", "book list"],
        "travel": ["travel", "itinerary", "여행", "일정표", "휴가", "trip", "여행 계획", "여행 일정", "이티너러리", "패킹 리스트", "준비물 리스트"],
        "fitness": ["fitness", "workout", "헬스", "운동", "피트니스", "트레이닝", "gym", "운동 일지", "헬스 일지", "운동 기록", "운동 트래커", "오운완"],
        "project": ["project", "goal", "목표", "프로젝트", "로드맵", "roadmap", "달성", "목표 달성표", "프로젝트 관리", "마일스톤"],
        "gratitude": ["gratitude", "감사", "긍정", "일기", "affirmation", "감사 일기", "감사 저널", "긍정 확언", "행복 일기", "마음 챙김 일기"],
        "mood": ["mood", "감정", "기분", "무드", "emotion", "무드 트래커", "기분 트래커", "감정 트래커", "감정 기록", "기분 기록"],
        "study": ["study", "스터디", "공부", "시험", "학습", "수험생", "공부 계획", "공부 플래너", "공부 플레너", "스터디 플래너", "스터디 플레너", "시험 대비"],
        "time_blocking": ["time block", "시간 블록", "타임 블록", "시간 관리", "시간 계획", "타임 블로킹", "시간 블로킹", "24시간 타임라인", "시간표"],
        "routine": ["routine", "루틴", "습관 형성", "루틴 관리", "루틴 플래너", "루틴 플레너", "모닝 루틴", "나이트 루틴", "아침 루틴", "저녁 루틴"],
        "mindmap": ["mind map", "마인드맵", "브레인스토밍", "생각 정리", "idea", "아이디어", "생각 그물", "아이디어 맵", "생각 매핑"],
        "retrospective": ["review", "retrospective", "회고", "성찰", "kpt", "피드백", "주간 회고", "월간 회고", "셀프 피드백", "회고록"],
        "budget": ["budget", "wishlist", "예산", "위시리스트", "저축", "savings", "위시 리스트", "구매 계획", "저축 트래커", "용돈 계획", "예산안"],
        "recipe": ["recipe", "레시피", "요리법", "조리법", "cooking", "chef", "요리 기록", "레시피 기록", "쿡북", "recipe book"],
        "pet": ["pet", "animal", "반려동물", "강아지", "고양이", "집사", "동물 케어", "반려견 일지", "반려묘 일지", "펫 다이어리", "펫 다이얼리", "댕댕이", "냥냥이"],
        "sleep": ["sleep", "energy", "수면", "에너지", "컨디션", "잠", "dream", "꿈", "수면 패턴", "수면 일기", "잠 기록", "꿈 일기"],
        "blank_note": ["blank", "grid note", "dot note", "lined note", "메모", "모눈", "도트", "노트 패드", "free note", "무지 노트", "유선 노트", "그리드 노트", "줄 노트", "메모지", "자유 노트"]
    };
    const styleThemeSelect = document.getElementById('styleTheme');
    const designModeRadios = document.querySelectorAll('input[name="designMode"]');

    async function loadConfigAndLayouts() {
        try {
            // Load configuration dynamically from server
            const configRes = await fetch('/api/config');
            if (configRes.ok) {
                const configData = await configRes.json();
                themeConfig = configData.themes;
                categoryMappings = configData.category_mappings;
            }

            // Load pre-generated layouts
            const layoutsRes = await fetch('/static/pre_generated_layouts.json');
            if (layoutsRes.ok) {
                preGeneratedLayouts = await layoutsRes.json();
                updatePreview('');
                adjustPreviewScale();
            }
        } catch (e) {
            console.error('설정 및 레이아웃 데이터 로드 실패:', e);
        }
    }
    loadConfigAndLayouts();

    function getLayoutCategory(title) {
        const text = title.toLowerCase().replace(/\s+/g, '');
        if (!text) return 'cornell';
        
        // Direct matching for exact generic terms
        if (['플래너', '플레너', 'planner'].includes(text)) return 'daily';
        if (['노트', 'note', 'notes'].includes(text)) return 'cornell';
        
        // Define generic keywords that should have lower priority
        const genericKeywords = ['플래너', '플레너', 'planner', '노트', 'note', 'notes', '스케줄러', '스케쥴러', 'scheduler'];
        
        let bestMatch = null;
        let bestLength = 0;
        let bestPriority = 0;
        
        for (const [key, keywords] of Object.entries(categoryMappings)) {
            for (const kw of keywords) {
                const cleanKw = kw.toLowerCase().replace(/\s+/g, '');
                if (text.includes(cleanKw)) {
                    const isGeneric = genericKeywords.includes(cleanKw);
                    const priority = isGeneric ? 1 : 2;
                    const length = cleanKw.length;
                    
                    // Prefer higher priority first, then longer keyword length
                    if (!bestMatch || 
                        priority > bestPriority || 
                        (priority === bestPriority && length > bestLength)) {
                        bestMatch = key;
                        bestLength = length;
                        bestPriority = priority;
                    }
                }
            }
        }
        
        return bestMatch || 'cornell';
    }

    function updatePreview(title) {
        const warningBubble = document.getElementById('preview-warning-bubble');
        if (!title) {
            previewIframe.classList.remove('is-loaded');
            previewIframe.onload = null; // Unbind onload to prevent blank document load from showing warning
            previewIframe.srcdoc = '';
            clearTimeout(typewriterTimeout);
            if (warningBubble) {
                warningBubble.classList.remove('show-warning', 'draw-arrow');
                const warningMsgEl = document.getElementById('warning-message');
                if (warningMsgEl) warningMsgEl.textContent = '';
            }
            return;
        }
        
        const category = getLayoutCategory(title);
        const designMode = document.querySelector('input[name="designMode"]:checked').value;
        const styleTheme = styleThemeSelect.value;
        
        let html = preGeneratedLayouts[category] || preGeneratedLayouts['cornell'];
        if (!html) return;
        
        let theme = themeConfig[styleTheme] || themeConfig['Minimal'];
        let modifiedHtml = html;
        
        // 테마 스타일 주입
        if (designMode !== 'guide') {
            modifiedHtml = modifiedHtml.replace(/#333/g, theme.border_color);
            if (theme.soften_borders) {
                modifiedHtml = modifiedHtml.replace(/border-radius:\s*0/g, 'border-radius: 12px');
            }
            const fontsHtml = theme.fonts ? theme.fonts : (theme.fonts_css ? `<style>${theme.fonts_css}</style>` : '');
            const themeCss = `<style>${theme.css}</style>`;
            modifiedHtml = modifiedHtml.replace('</head>', fontsHtml + themeCss + '</head>');
        }
        
        // 테마 배경 라인색 주입
        const lineColor = designMode === 'guide' ? '#333' : (theme.line_color || '#e5e7eb');
        const lined_svg = `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='0' y='19' width='20' height='1' fill='${encodeURIComponent(lineColor)}'/></svg>`;
        const grid_svg = `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><path d='M 20 0 L 20 20 L 0 20' fill='none' stroke='${encodeURIComponent(lineColor)}' stroke-width='1'/></svg>`;
        const dot_pattern_svg = `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><circle cx='1' cy='1' r='1' fill='${encodeURIComponent(lineColor)}'/></svg>`;

        const bgCss = `
        <style>
        .lined-bg {
            background-image: url("data:image/svg+xml,${lined_svg}") !important;
        }
        .grid-bg {
            background-image: url("data:image/svg+xml,${grid_svg}") !important;
        }
        .dot-bg {
            background-image: url("data:image/svg+xml,${dot_pattern_svg}") !important;
        }
        </style>
        `;
        modifiedHtml = modifiedHtml.replace('</head>', bgCss + '</head>');
        
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
        /* Chrome iframe scale 버그 방지용 (서브픽셀 테두리 실종 방지) */
        table { border-collapse: separate !important; border-spacing: 0 !important; }

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
        
        // Clear previous typewriter and reset warning bubble before loading new preview
        clearTimeout(typewriterTimeout);
        if (warningBubble) {
            warningBubble.classList.remove('show-warning', 'draw-arrow');
            const warningMsgEl = document.getElementById('warning-message');
            if (warningMsgEl) warningMsgEl.textContent = '';
        }

        previewIframe.classList.remove('is-loaded');
        previewIframe.srcdoc = modifiedHtml;
        
        previewIframe.onload = () => {
            // Safety check: if user cleared the input while loading, do not show warning
            if (!titleInput || !titleInput.value.trim()) {
                previewIframe.classList.remove('is-loaded');
                if (warningBubble) {
                    warningBubble.classList.remove('show-warning', 'draw-arrow');
                    const warningMsgEl = document.getElementById('warning-message');
                    if (warningMsgEl) warningMsgEl.textContent = '';
                }
                return;
            }
            
            previewIframe.classList.add('is-loaded');
            adjustPreviewScale();
            
            // Wait 1.5 seconds for the preview rendering animations to complete
            typewriterTimeout = setTimeout(() => {
                // Safety check: if user cleared the input during the delay, do not show warning
                if (!titleInput || !titleInput.value.trim()) return;
                
                if (warningBubble) {
                    warningBubble.classList.add('show-warning');
                    const warningMsgEl = document.getElementById('warning-message');
                    if (warningMsgEl) {
                        typeWriter(warningMsgEl, "양식명만 입력 했을 때의 미리보기입니다.\n원하는 방향으로 커스텀 해보세요!", 50, () => {
                            warningBubble.classList.add('draw-arrow');
                        });
                    }
                }
            }, 1500);
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
            const category = getLayoutCategory(title);
            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, description, pageSize, designMode, styleTheme, category })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '알 수 없는 에러가 발생했습니다.');
            }

            const resData = await response.json();
            const taskId = resData.task_id;

            // Connect to SSE stream
            const eventSource = new EventSource(`/api/task-stream/${taskId}`);

            const handleStreamError = (err) => {
                eventSource.close();
                alert(`오류: ${err.message}`);
                canvasStatusText.classList.add('hidden');
                document.body.classList.remove('is-generating-mode');
                if (blueprintContainer && loadingAnimationContainer) {
                    blueprintContainer.classList.remove('fly-away', 'hidden');
                    loadingAnimationContainer.classList.add('hidden');
                }
                generateBtn.disabled = false;
                btnText.textContent = 'PDF 생성하기';
            };

            eventSource.onmessage = (event) => {
                try {
                    const taskData = JSON.parse(event.data);
                    
                    if (taskData.status === 'success') {
                        eventSource.close();
                        currentFileId = taskData.file_id;

                        const encodedTitle = encodeURIComponent(taskData.title);
                        downloadLink.href = `/api/download-pdf/${currentFileId}?title=${encodedTitle}&page_size=${taskData.page_size}`;
                        downloadLink.download = `${taskData.title}_${taskData.page_size}.pdf`;
                        
                        // 결과창으로 전환
                        interactiveCanvas.classList.add('hidden');
                        resultContainer.classList.remove('hidden');
                        
                        generateBtn.disabled = false;
                        btnText.textContent = 'PDF 생성하기';
                        document.body.classList.remove('is-generating-mode');
                    } else if (taskData.status === 'failed') {
                        handleStreamError(new Error(taskData.message || '생성에 실패했습니다.'));
                    } else if (taskData.status === 'retrying') {
                        // AI self-healing state
                        canvasStatusText.innerHTML = `<span style="color: #e63946; font-weight: 600; text-align: center; display: block; line-height: 1.6; font-size: 1.1rem; animation: pulse 1.5s infinite;">⚠️ AI가 도면의 어긋남/실수를 감지했습니다!<br>완벽한 레이아웃을 위해 자동으로 도면을 수정 중입니다...</span>`;
                        btnText.textContent = '자가 수정 중...';
                    } else {
                        // Normal progress
                        canvasStatusText.textContent = taskData.message || '템플릿을 생성 중입니다...';
                        btnText.textContent = '생성 중...';
                    }
                } catch (parseError) {
                    handleStreamError(parseError);
                }
            };

            eventSource.onerror = (err) => {
                console.error('SSE Error:', err);
                handleStreamError(new Error('서버와의 실시간 연결이 끊어졌거나 에러가 발생했습니다.'));
            };

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
            generateBtn.disabled = false;
            btnText.textContent = 'PDF 생성하기';
        }
    });
});

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
    const loadingAnimationContainer = document.getElementById('loading-animation-container');
    const sketchOuterBox = document.getElementById('sketch-outer-box');
    const sketchLinesContainer = document.getElementById('sketch-lines-container');
    const sketchTitleText = document.getElementById('sketch-title-text');
    
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

    // 2. Interactive Blueprint 로직
    let hasRedrawnLines = false;

    // 제목 입력 시 테두리 그리기, 제목 각인, 그리고 **노트 가로선까지 한 번에 그리기**
    if (titleInput && sketchOuterBox && sketchLinesContainer) {
        titleInput.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            sketchTitleText.textContent = val;
            
            if (val !== '') {
                sketchOuterBox.classList.add('is-active');
                
                // 제목만 입력해도 캔버스가 꽉 차 보이도록 선을 같이 그려줍니다.
                if (!hasRedrawnLines && !sketchLinesContainer.classList.contains('is-active')) {
                    sketchLinesContainer.classList.add('is-active');
                }
            } else {
                sketchOuterBox.classList.remove('is-active');
            }
        });
    }

    // 상세 내용 최초 입력 시, 기존 줄 날려버리고 새로 그리기 (Redraw Sequence)
    if (descInput && sketchLinesContainer) {
        descInput.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            if (val !== '' && !hasRedrawnLines && sketchLinesContainer.classList.contains('is-active')) {
                hasRedrawnLines = true; // 1회만 발동
                
                // 1. 기존 노트 줄들을 우측으로 휙 날려버림
                sketchLinesContainer.classList.add('fly-away-lines');
                
                // 2. 날아가는 시간(0.4초) 대기 후, 초기화하고 다시 그림
                setTimeout(() => {
                    sketchLinesContainer.classList.remove('is-active', 'fly-away-lines');
                    // 강제 리플로우 (애니메이션 재시작을 위함)
                    void sketchLinesContainer.offsetWidth;
                    sketchLinesContainer.classList.add('is-active');
                }, 400);
            }
        });
    }

    // 아날로그 모드일 때 디자인 스타일 선택 비활성화
    const designModeRadios = document.querySelectorAll('input[name="designMode"]');
    const styleThemeSelect = document.getElementById('styleTheme');
    
    designModeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'guide') {
                styleThemeSelect.disabled = true;
                // 시각적으로도 비활성화됨을 표시하기 위해 부모에 클래스 추가 가능
                styleThemeSelect.parentElement.style.opacity = '0.5';
            } else {
                styleThemeSelect.disabled = false;
                styleThemeSelect.parentElement.style.opacity = '1';
            }
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

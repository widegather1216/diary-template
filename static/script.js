document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const titleInput = document.getElementById('title');
    const descInput = document.getElementById('description');
    const pageSizeSelect = document.getElementById('pageSize');
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
                // 고무줄 먼저 풀기
                diaryBand.classList.add('is-unbanding');
                // 고무줄 튕겨져 나가는 시간(400ms) 대기 후 책 펼치기
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

    // 2. Interactive Blueprint 로직
    let hasRedrawnLines = false;

    // 제목 입력 시 테두리 그리기, 제목 각인, 그리고 **노트 가로선까지 한 번에 그리기**
    if (titleInput && sketchOuterBox && sketchLinesContainer) {
        titleInput.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            if (val !== '') {
                sketchOuterBox.classList.add('is-active');
                sketchTitleText.textContent = val;
                
                // 제목만 입력해도 캔버스가 꽉 차 보이도록 선을 같이 그려줍니다.
                if (!hasRedrawnLines && !sketchLinesContainer.classList.contains('is-active')) {
                    sketchLinesContainer.classList.add('is-active');
                }
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
        const pageSize = pageSizeSelect.value;
        const designMode = document.querySelector('input[name="designMode"]:checked').value;

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
                body: JSON.stringify({ title, description, pageSize, designMode })
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

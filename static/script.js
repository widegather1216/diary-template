document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const titleInput = document.getElementById('title');
    const descInput = document.getElementById('description');
    const pageSizeSelect = document.getElementById('pageSize');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const statusMessage = document.getElementById('status-message');

    const resultContainer = document.getElementById('result-container');
    const downloadLink = document.getElementById('download-link');
    
    let currentFileId = null;

    // 사용자가 페이지를 떠날 때 파일 삭제 요청 전송
    window.addEventListener('beforeunload', () => {
        if (currentFileId) {
            navigator.sendBeacon('/api/cleanup-pdf', JSON.stringify({ file_id: currentFileId }));
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = titleInput.value.trim();
        const description = descInput.value.trim();
        const pageSize = pageSizeSelect.value;

        if (!title) {
            alert('양식명은 필수 입력 항목입니다.');
            return;
        }

        // 이전 결과 초기화
        resultContainer.classList.add('hidden');
        if (currentFileId) {
            // 이전에 생성한 파일이 있으면 지워줌
            navigator.sendBeacon('/api/cleanup-pdf', JSON.stringify({ file_id: currentFileId }));
            currentFileId = null;
        }

        // UI 상태 업데이트 (로딩)
        generateBtn.disabled = true;
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        statusMessage.classList.remove('hidden');

        try {
            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, description, pageSize })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '알 수 없는 에러가 발생했습니다.');
            }

            const data = await response.json();
            currentFileId = data.file_id;

            // 다운로드 버튼 설정
            const encodedTitle = encodeURIComponent(data.title);
            downloadLink.href = `/api/download-pdf/${currentFileId}?title=${encodedTitle}&page_size=${data.page_size}`;
            downloadLink.download = `${data.title}_${data.page_size}.pdf`;
            
            // 결과 버튼 노출
            resultContainer.classList.remove('hidden');

        } catch (error) {
            console.error('Error:', error);
            alert(`오류: ${error.message}`);
        } finally {
            // UI 상태 복구
            generateBtn.disabled = false;
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            statusMessage.classList.add('hidden');
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const titleInput = document.getElementById('title');
    const descInput = document.getElementById('description');
    const pageSizeSelect = document.getElementById('pageSize');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const statusMessage = document.getElementById('status-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = titleInput.value.trim();
        const description = descInput.value.trim();
        const pageSize = pageSizeSelect.value;

        if (!title) {
            alert('양식명은 필수 입력 항목입니다.');
            return;
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

            // PDF 파일 다운로드
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `${title}_${pageSize}.pdf`;
            document.body.appendChild(a);
            a.click();
            
            // 정리
            setTimeout(() => {
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
            }, 100);

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

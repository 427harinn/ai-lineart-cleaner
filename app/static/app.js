const fileInput = document.querySelector('#image');
const range = document.querySelector('#threshold-range');
const number = document.querySelector('#threshold-number');
const source = document.querySelector('#source-preview');
const result = document.querySelector('#result-preview');
const button = document.querySelector('#extract');
const loading = document.querySelector('#loading');
const error = document.querySelector('#error');
const download = document.querySelector('#download');
let sourceUrl; let resultUrl;
function sync(sourceInput, target) { target.value = sourceInput.value; }
range.addEventListener('input', () => sync(range, number));
number.addEventListener('input', () => { const value = Math.min(255, Math.max(0, Number(number.value) || 0)); number.value = value; sync(number, range); });
fileInput.addEventListener('change', () => { error.textContent = ''; const file = fileInput.files[0]; if (!file) return; if (sourceUrl) URL.revokeObjectURL(sourceUrl); sourceUrl = URL.createObjectURL(file); source.src = sourceUrl; });
button.addEventListener('click', async () => { const file = fileInput.files[0]; if (!file) { error.textContent = 'PNGまたはJPEG画像を選択してください。'; return; } error.textContent = ''; button.disabled = true; loading.hidden = false; const form = new FormData(); form.append('image', file); form.append('threshold', range.value); try { const response = await fetch('/api/extract', { method: 'POST', body: form }); if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || '線画化に失敗しました。'); } const blob = await response.blob(); if (resultUrl) URL.revokeObjectURL(resultUrl); resultUrl = URL.createObjectURL(blob); result.src = resultUrl; download.href = resultUrl; download.hidden = false; } catch (exception) { error.textContent = exception.message; } finally { button.disabled = false; loading.hidden = true; } });

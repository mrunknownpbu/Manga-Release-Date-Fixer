let chapterData = [];

async function fetchChapters() {
  const resp = await fetch('/api/chapters');
  chapterData = await resp.json();
  renderChapters();
}

function renderChapters() {
  const tb = document.querySelector('#chapterTable tbody');
  tb.innerHTML = '';
  const searchVal = document.getElementById('search').value.trim().toLowerCase();
  const statusVal = document.querySelector('input[name="statusFilter"]:checked').value;

  let toFixCount = 0;

  for (const chap of chapterData) {
    // Filter by search
    const rowText = [
      chap.title, chap.alt_titles?.join(' '), chap.filename,
      chap.parsed_volume, chap.parsed_chapter, chap.comicinfo_date,
      chap.official_date, chap.file_mod_date
    ].map(x => (x ?? '').toString().toLowerCase()).join(' ');
    if (searchVal && !rowText.includes(searchVal)) continue;

    // Filter by status
    if (statusVal !== 'all' && chap.status !== statusVal) continue;

    // Count chapters eligible for batch fix
    if (['wrong', 'missing'].includes(chap.status)) toFixCount++;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        ${chap.cover_url ? `<img src="${chap.cover_url}" alt="cover" class="cover-img">` : ''}
      </td>
      <td>
        ${chap.title ? `<a href="${chap.series_url || '#'}" target="_blank">${chap.title}</a>` : ''}
      </td>
      <td class="small">${(chap.alt_titles || []).join('<br>')}</td>
      <td>${chap.filename}</td>
      <td>${chap.parsed_volume ?? ''}</td>
      <td>${chap.parsed_chapter ?? ''}</td>
      <td>${chap.comicinfo_date ?? ''}</td>
      <td>${chap.official_date ?? ''}</td>
      <td><span class="text-muted small">${chap.file_mod_date}</span></td>
      <td class="status-cell">${renderStatusIcon(chap.status)}</td>
      <td>
        <button class="btn btn-sm btn-warning fix-btn" data-path="${chap.path}" ${chap.status === 'ok' ? 'disabled' : ''}>Fix</button>
      </td>
    `;
    tb.appendChild(tr);
  }

  // Update batch fix count in modal
  document.getElementById('toFixCount').textContent = toFixCount;
}

function renderStatusIcon(status) {
  if (status === 'ok') return '<span class="text-success fw-bold">✅</span>';
  if (status === 'wrong') return '<span class="text-warning fw-bold">⚠</span>';
  if (status === 'missing') return '<span class="text-danger fw-bold">❌</span>';
  return '';
}

function addTableEventListeners() {
  document.getElementById('chapterTable').addEventListener('click', async (e) => {
    if (e.target.classList.contains('fix-btn') && !e.target.disabled) {
      const path = e.target.getAttribute('data-path');
      e.target.disabled = true;
      e.target.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;
      await fetch('/api/fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chapter_path: path })
      });
      await fetchChapters();
    }
  });
}

document.getElementById('fixAllBtn').onclick = function() {
  const modal = new bootstrap.Modal(document.getElementById('fixAllModal'));
  modal.show();
};

document.getElementById('confirmFixAll').onclick = async function() {
  document.getElementById('confirmFixAll').disabled = true;
  document.getElementById('confirmFixAll').innerHTML = `<span class="spinner-border spinner-border-sm"></span> Fixing...`;
  await fetch('/api/fixall', { method: 'POST' });
  document.getElementById('confirmFixAll').disabled = false;
  document.getElementById('confirmFixAll').innerHTML = 'Fix All';
  bootstrap.Modal.getInstance(document.getElementById('fixAllModal')).hide();
  await fetchChapters();
};

['search', 'filterAll', 'filterOk', 'filterWrong', 'filterMissing'].forEach(id =>
  document.getElementById(id)?.addEventListener('input', renderChapters)
);

addTableEventListeners();
fetchChapters();
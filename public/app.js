const input = document.getElementById('symptoms');
const btn = document.getElementById('submit');
const results = document.getElementById('results');

btn.addEventListener('click', predict);
input.addEventListener('keypress', e => {
  if (e.key === 'Enter') predict();
});

async function predict() {
  const symptoms = input.value.trim();
  
  if (!symptoms) {
    showError('Please enter symptoms');
    return;
  }
  
  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms })
    });
    
    if (!res.ok) {
      const err = await res.json();
      showError(err.error || 'Request failed');
      return;
    }
    
    const data = await res.json();
    showResults(data);
  } catch (err) {
    showError('Network error');
  }
}

function showResults(data) {
  results.classList.add('visible');
  
  if (data.predictions.length === 0) {
    results.innerHTML = '<div class="no-match">No matching diseases found</div>';
    return;
  }
  
  let html = '';
  data.predictions.forEach(p => {
    const pct = Math.round(p.score * 100);
    html += `
      <div class="disease-item">
        <div class="disease-name">${p.disease}</div>
        <div class="disease-score">Confidence: ${pct}%</div>
        <div class="confidence-bar">
          <div class="confidence-fill" style="width: ${pct}%"></div>
        </div>
      </div>
    `;
  });
  
  results.innerHTML = html;
}

function showError(msg) {
  results.classList.add('visible');
  results.innerHTML = `<div class="error">${msg}</div>`;
}



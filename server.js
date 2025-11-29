const express = require('express');
const fs = require('fs');
const { parse } = require('csv-parse/sync');
const path = require('path');

const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('public'));

let diseases = [];

function loadData() {
  const csv = fs.readFileSync('archive/dataset.csv', 'utf8');
  const records = parse(csv, { columns: true, skip_empty_lines: true, to: 5000 });
  
  const diseaseMap = {};
  
  for (let r of records) {
    const diseaseName = r.diseases;
    if (!diseaseMap[diseaseName]) {
      diseaseMap[diseaseName] = new Set();
    }
    
    for (let symptom in r) {
      if (symptom !== 'diseases' && r[symptom] === '1') {
        diseaseMap[diseaseName].add(symptom.toLowerCase().trim());
      }
    }
  }
  
  diseases = Object.keys(diseaseMap).map(name => ({
    disease: name,
    symptomsSet: diseaseMap[name]
  }));
  
  console.log(`Loaded ${diseases.length} unique diseases from 5000 records`);
}

function jaccard(a, b) {
  const intersection = new Set([...a].filter(x => b.has(x)));
  const union = new Set([...a, ...b]);
  return union.size === 0 ? 0 : intersection.size / union.size;
}

function predict(symptoms) {
  const input = new Set(symptoms.toLowerCase().split(',').map(s => s.trim()).filter(s => s));
  if (input.size === 0) return [];
  
  const scores = diseases.map(d => ({
    disease: d.disease,
    score: parseFloat(jaccard(input, d.symptomsSet).toFixed(2))
  }));
  
  scores.sort((a, b) => b.score - a.score);
  return scores.slice(0, 5).filter(s => s.score > 0);
}

app.post('/api/predict', (req, res) => {
  const symptoms = req.body.symptoms;
  
  if (!symptoms || symptoms.trim() === '') {
    return res.status(400).json({ error: 'Symptoms cannot be empty' });
  }
  
  const predictions = predict(symptoms);
  
  if (predictions.length === 0) {
    return res.json({ predictions: [], message: 'No match' });
  }
  
  res.json({ predictions });
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

loadData();

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});


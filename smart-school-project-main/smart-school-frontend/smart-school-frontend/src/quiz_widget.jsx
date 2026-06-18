/**
 * Minimal Quiz widget — talks to backend /api/generate-quiz
 * Backend generates MCQs; this file only handles UI.
 */
const { useState, useEffect } = React;

const DEFAULT_QS = 5;
const API_BASE = 'http://127.0.0.1:5000';

function pickAnswerIndex(item) {
  if (typeof item.answer_index === 'number') return item.answer_index;
  if (typeof item.answerIndex === 'number') return item.answerIndex;
  return 0;
}

function shuffleWithAnswer(options, answerIdx) {
  const entries = options.map((text, idx) => ({ text, correct: idx === answerIdx }));
  for (let i = entries.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const temp = entries[i]; entries[i] = entries[j]; entries[j] = temp;
  }
  const newIndex = entries.findIndex(e => e.correct);
  return { options: entries.map(e => e.text), answer_index: newIndex >= 0 ? newIndex : 0 };
}

function normalizeMcqs(list) {
  return (list || []).map(item => {
    let options = Array.isArray(item.options) && item.options.length ? item.options.slice(0,4) : null;
    let answerIdx = pickAnswerIndex(item);
    if (!options) {
      const answer = item.answer_text || 'Correct';
      const built = [answer, 'True', 'False', 'Not mentioned'];
      options = built.slice(0,4);
      answerIdx = 0;
    }
    const shuffled = shuffleWithAnswer(options, answerIdx);
    return { ...item, options: shuffled.options, answer_index: shuffled.answer_index };
  });
}

function QuizRenderer({ mcqs }) {
  const [selected, setSelected] = useState(Array(mcqs.length).fill(null));
  const [score, setScore] = useState(null);
  useEffect(()=>{ setSelected(Array(mcqs.length).fill(null)); setScore(null); }, [mcqs]);
  function pick(qidx, choiceIdx){ setSelected(s=>{ const n=s.slice(); n[qidx]=choiceIdx; return n; }); setScore(null); }
  function check(){ let correct=0; for (let i=0;i<mcqs.length;i++){ const optionCount = Array.isArray(mcqs[i].options)?mcqs[i].options.length:1; const ans = pickAnswerIndex(mcqs[i]); const bounded = Math.min(Math.max(ans,0), optionCount-1); if (selected[i]===bounded) correct++; } setScore(`${correct} / ${mcqs.length}`); }
  return (
    <div className="mcq-list">
      {mcqs.map((m,idx)=>{
        const optionCount = Array.isArray(m.options)?m.options.length:1;
        const correctIdx = Math.min(Math.max(pickAnswerIndex(m),0), optionCount-1);
        return (
          <div className="mcq" key={idx}>
            <p className="q">{idx+1}. {m.question}</p>
            <div className="choices">{m.options.map((c,i)=> (
              <button key={i} className={"choice" + (selected[idx]===i? ' selected':'')} onClick={()=>pick(idx,i)}>{String.fromCharCode(65+i)}. {c}</button>
            ))}</div>
            {score!==null && selected[idx]===correctIdx && <p className="note ok">Correct</p>}
            {score!==null && selected[idx]!==correctIdx && <p className="note wrong">Answer: {(m.options && m.options[correctIdx]) || m.answer_text || '—'}</p>}
            {m.explanation && <p className="note explain">{m.explanation}</p>}
          </div>
        );
      })}
      <div className="score-row"><button onClick={check}>Check Answers</button>{score!==null && <span> Score: <strong>{score}</strong></span>}</div>
    </div>
  );
}

function QuizWidget() {
  const [input, setInput] = useState('');
  const [mcqs, setMcqs] = useState([]);
  const [status, setStatus] = useState('Paste a paragraph and click Generate');
  async function onGenerate(){
    if (!input.trim()) {
      setStatus('Please paste a paragraph first');
      return;
    }
    setStatus('Contacting backend...');
    try {
      const res = await fetch(`${API_BASE}/api/generate-quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paragraph: input, num_questions: DEFAULT_QS }),
      });
      if (!res.ok) throw new Error('Backend error');
      const data = await res.json();
      if (!Array.isArray(data.mcqs) || !data.mcqs.length) {
        throw new Error('Empty quiz from backend');
      }
      const g = normalizeMcqs(data.mcqs).slice(0, DEFAULT_QS);
      setMcqs(g);
      setStatus(`Received ${g.length} questions from backend`);
    } catch (err) {
      console.error('Quiz request failed', err);
      setStatus('Backend unreachable or error — check server on port 5000');
    }
  }
  return (
    <div className="card quiz-panel" style={{maxWidth:760, margin:'24px auto'}}>
      <div className="section-heading"><div><p className="tag">Quiz Generator</p><h3>Quiz Widget</h3><p className="muted">Connected to backend /api/generate-quiz</p></div></div>
      <label className="input-label">Source paragraph</label>
      <textarea value={input} onChange={e=>setInput(e.target.value)} placeholder="Paste or type study material" style={{minHeight:120}} />
      <div className="button-row"><button onClick={onGenerate}>Generate Quiz</button><button className="ghost" onClick={()=>{ setInput('Photosynthesis is the process by which plants use chlorophyll to convert light into chemical energy, producing glucose and oxygen.'); }}>Load sample</button></div>
      <div className="status-chip">{status}</div>
      <QuizRenderer mcqs={mcqs} />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<QuizWidget />);

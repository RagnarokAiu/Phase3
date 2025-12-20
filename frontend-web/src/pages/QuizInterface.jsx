import React, { useState } from 'react';
import { BrainCircuit, CheckCircle, AlertCircle } from 'lucide-react';

const QuizInterface = () => {
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);

  const [topic, setTopic] = useState("");

  const generateQuiz = async () => {
    setLoading(true);
    setScore(null);
    setQuiz(null);
    setAnswers({});

    try {
      const query = topic ? `?topic=${encodeURIComponent(topic)}` : "";
      const response = await fetch(`/api/quiz/generate${query}`);
      if (response.ok) {
        const data = await response.json();
        setQuiz(data);
      } else {
        alert("Failed to generate quiz. Is the backend running?");
      }
    } catch (error) {
      console.warn("Backend offline, using demo quiz data");
      setQuiz({
        "quiz_id": "demo_quiz",
        "questions": [
          {
            "id": 1,
            "text": "What is the primary benefit of Cloud Computing?",
            "options": ["Cost savings", "Scalability", "Accessibility", "All of the above"],
            "answer": "All of the above"
          },
          {
            "id": 2,
            "text": "Which AWS service is used for storage?",
            "options": ["EC2", "S3", "RDS", "Lambda"],
            "answer": "S3"
          }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (questionId, option) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: option
    }));
  };

  const submitQuiz = () => {
    let correctCount = 0;
    quiz.questions.forEach(q => {
      if (answers[q.id] === q.answer) {
        correctCount++;
      }
    });
    setScore(correctCount);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', gap: '1rem', flexWrap: 'wrap' }}>
        <h1 className="gradient-text" style={{ fontSize: '2rem', margin: 0 }}>Quiz & Assessment</h1>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter topic (e.g. AWS S3)"
            style={{
              padding: '0.75rem',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              background: 'var(--bg-dark)',
              color: 'white',
              outline: 'none',
              minWidth: '200px'
            }}
          />
          <button
            onClick={generateQuiz}
            disabled={loading}
            style={{
              background: 'var(--primary)',
              color: 'white',
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: '600',
              opacity: loading ? 0.7 : 1
            }}
          >
            <BrainCircuit size={20} />
            {loading ? 'Generating...' : 'Generate New Quiz'}
          </button>
        </div>
      </div>

      {!quiz && !loading && (
        <div style={{ background: 'var(--bg-card)', padding: '3rem', borderRadius: '12px', border: '1px solid var(--border)', textAlign: 'center', color: 'var(--text-muted)' }}>
          Click "Generate New Quiz" to start testing your knowledge.
        </div>
      )}

      {quiz && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {quiz.questions.map((q, index) => (
            <div key={q.id} style={{ background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border)' }}>
              <h3 style={{ marginTop: 0, marginBottom: '1rem' }}>{index + 1}. {q.text}</h3>
              <div style={{ display: 'grid', gap: '0.75rem' }}>
                {q.options.map(option => (
                  <label key={option} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    background: answers[q.id] === option ? 'rgba(79, 70, 229, 0.1)' : 'var(--bg-dark)',
                    border: `1px solid ${answers[q.id] === option ? 'var(--primary)' : 'var(--border)'}`,
                    cursor: 'pointer'
                  }}>
                    <input
                      type="radio"
                      name={`q-${q.id}`}
                      value={option}
                      checked={answers[q.id] === option}
                      onChange={() => handleOptionSelect(q.id, option)}
                      disabled={score !== null}
                    />
                    {option}
                    {score !== null && option === q.answer && <CheckCircle size={16} color="#22c55e" style={{ marginLeft: 'auto' }} />}
                    {score !== null && answers[q.id] === option && option !== q.answer && <AlertCircle size={16} color="#ef4444" style={{ marginLeft: 'auto' }} />}
                  </label>
                ))}
              </div>
            </div>
          ))}

          {!score && (
            <button
              onClick={submitQuiz}
              style={{
                background: '#22c55e',
                color: 'white',
                padding: '1rem',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                cursor: 'pointer',
                marginTop: '1rem'
              }}
            >
              Submit Answers
            </button>
          )}

          {score !== null && (
            <div style={{
              background: 'var(--bg-card)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid var(--border)',
              textAlign: 'center',
              marginTop: '1rem'
            }}>
              <h2 style={{ margin: 0 }}>You scored {score} out of {quiz.questions.length}!</h2>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QuizInterface;

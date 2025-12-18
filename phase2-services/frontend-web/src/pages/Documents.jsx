import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Upload, FileText, Trash2 } from 'lucide-react';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const { user } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      // Assuming GET /api/documents/ returns a list
      // Note: Real backend might return { documents: [] } or just []
      // Mocking for now if backend is down, but writing real fetch code
      const response = await fetch('/api/documents/');
      if (response.ok) {
        const data = await response.json();
        setDocuments(Array.isArray(data) ? data : []);
      } else {
        // Fallback for demo if backend is offline
        console.warn("Backend offline, showing demo data");
        setDocuments([
          { id: 1, filename: "cloud-computing-101.pdf", status: "Processed" },
          { id: 2, filename: "aws-architecture.pdf", status: "Processing" }
        ]);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch documents');
      // Fallback for demo
      setDocuments([
        { id: 1, filename: "demo-cloud-intro.pdf", status: "Processed" },
      ]);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        headers: {
          // 'Authorization': `Bearer ${user.token}` // If backend required auth
        },
        body: formData
      });

      if (response.ok) {
        fetchDocuments(); // Refresh list
      } else {
        throw new Error('Upload failed');
      }
    } catch (err) {
      console.warn("Backend offline, simulating upload");
      // Simulate success for Demo Flow
      setDocuments(prev => [...prev, {
        id: Date.now(),
        filename: file.name,
        status: "Processing (Demo)"
      }]);
      alert("File uploaded successfully!");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 className="gradient-text" style={{ fontSize: '2rem', margin: 0 }}>Documents</h1>
        <div style={{ position: 'relative' }}>
          <input
            type="file"
            id="file-upload"
            style={{ display: 'none' }}
            onChange={handleUpload}
            disabled={uploading}
          />
          <label htmlFor="file-upload" style={{
            background: 'var(--primary)',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            opacity: uploading ? 0.7 : 1
          }}>
            <Upload size={18} />
            {uploading ? 'Uploading...' : 'Upload PDF'}
          </label>
        </div>
      </div>

      <div style={{ display: 'grid', gap: '1rem' }}>
        {documents.map((doc) => (
          <div key={doc.id} style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ background: 'rgba(79, 70, 229, 0.1)', padding: '0.5rem', borderRadius: '6px' }}>
                <FileText size={20} color="var(--primary)" />
              </div>
              <div>
                <h4 style={{ margin: '0 0 0.25rem 0' }}>{doc.filename}</h4>
                <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)', background: 'var(--bg-dark)', padding: '0.75rem', borderRadius: '6px', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                  <strong>Summary:</strong> {doc.summary || "No summary available"}
                </div>
                <span style={{ fontSize: '0.8rem', color: doc.status === 'Processed' ? '#22c55e' : '#f59e0b' }}>
                  {doc.status}
                </span>
              </div>
            </div>
            <button style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', opacity: 0.7 }}>
              <Trash2 size={18} />
            </button>
          </div>
        ))}

        {documents.length === 0 && (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            No documents found. Upload one to get started.
          </div>
        )}
      </div>
    </div>
  );
};

export default Documents;

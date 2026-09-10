import { useEffect, useState } from 'react';

type Investigation = {
  root_cause: string;
  category: string;
  confidence: number;
  evidence: string[];
  recommended_fix: string;
  risk: string;
  requires_approval: boolean;
  engine: string;
};

export default function InvestigationPanel({ apiBaseUrl, incidentId }: { apiBaseUrl: string; incidentId: string }) {
  const [data, setData] = useState<Investigation | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [error, setError] = useState('');

  async function investigate() {
    setStatus('loading');
    setError('');
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/incidents/${incidentId}/investigation`);
      if (!response.ok) throw new Error(`Investigation API returned ${response.status}`);
      const payload = await response.json();
      if (payload.status !== 'ANALYZED') throw new Error(payload.error || `Incident status: ${payload.status}`);
      setData(payload.investigation);
      setStatus('ready');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Investigation failed');
      setStatus('error');
    }
  }

  useEffect(() => {
    void investigate();
  }, [incidentId]);

  if (status === 'loading') return <div className="investigation-card panel"><div className="empty-state">AI investigation running… collecting evidence and analyzing the failure.</div></div>;
  if (status === 'error') return <div className="investigation-card panel"><div className="api-error">{error}</div><button className="primary" onClick={() => void investigate()}>Retry investigation →</button></div>;
  if (!data) return null;

  return (
    <section className="investigation-card panel">
      <div className="panel-header">
        <div><p className="eyebrow">AI INVESTIGATION</p><h2>Diagnosis</h2></div>
        <span className="status success"><i/> {data.engine.toUpperCase()}</span>
      </div>
      <div className="diagnosis-grid">
        <div><span>Category</span><strong>{data.category}</strong></div>
        <div><span>Confidence</span><strong>{Math.round(data.confidence * 100)}%</strong></div>
        <div><span>Risk</span><strong>{data.risk}</strong></div>
        <div><span>Approval</span><strong>{data.requires_approval ? 'Human approval required' : 'Not required'}</strong></div>
      </div>
      <div className="diagnosis-block"><span>Root cause</span><p>{data.root_cause}</p></div>
      <div className="diagnosis-block"><span>Evidence</span><ul>{data.evidence.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul></div>
      <div className="diagnosis-block recommendation"><span>Recommended remediation</span><p>{data.recommended_fix}</p></div>
      <button className="secondary" onClick={() => void investigate()}>Re-run investigation</button>
    </section>
  );
}

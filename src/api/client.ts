const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

async function handleResponse(res: Response) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || '解析に失敗しました');
  }
  return res.json();
}

export async function analyzeImage(file: File) {
  const body = new FormData();
  body.append('file', file);
  return handleResponse(await fetch(`${API_BASE}/analyze`, { method: 'POST', body }));
}

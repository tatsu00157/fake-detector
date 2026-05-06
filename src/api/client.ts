import { supabase } from '../lib/supabase';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

async function getAuthHeader(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return {};
  return { Authorization: `Bearer ${session.access_token}` };
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || '解析に失敗しました');
  }
  return res.json();
}

export async function analyzeImage(file: File) {
  const headers = await getAuthHeader();
  const body = new FormData();
  body.append('file', file);
  return handleResponse(await fetch(`${API_BASE}/analyze`, { method: 'POST', headers, body }));
}

export async function compareImages(file1: File, file2: File) {
  const headers = await getAuthHeader();
  const body = new FormData();
  body.append('file1', file1);
  body.append('file2', file2);
  return handleResponse(await fetch(`${API_BASE}/compare`, { method: 'POST', headers, body }));
}

export async function createCheckoutSession() {
  const headers = await getAuthHeader();
  return handleResponse(await fetch(`${API_BASE}/stripe/checkout`, {
    method: 'POST',
    headers,
  }));
}

export async function createPortalSession() {
  const headers = await getAuthHeader();
  return handleResponse(await fetch(`${API_BASE}/stripe/portal`, {
    method: 'POST',
    headers,
  }));
}

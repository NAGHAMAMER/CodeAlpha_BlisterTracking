const API_PREFIX = '/api';

export async function requestJson(path, options = {}, fetcher = fetch) {
  let response;
  try {
    response = await fetcher(API_PREFIX + path, options);
  } catch (error) {
    if (options.signal?.aborted) throw error;
    throw new Error('Cannot reach FastAPI on port 8003.');
  }

  const data = await response.json().catch(() => null);
  if (!response.ok || !data) {
    throw new Error(
      typeof data?.detail === 'string'
        ? data.detail
        : 'The server could not complete the request.',
    );
  }
  return data;
}

export function startSession(config) {
  return requestJson('/tracking/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
}

export function getSessionStatus(sessionId, signal) {
  return requestJson(
    '/tracking/status?session_id=' + encodeURIComponent(sessionId),
    { signal },
  );
}

export function stopSession(sessionId) {
  return requestJson(
    '/tracking/stop?session_id=' + encodeURIComponent(sessionId),
    { method: 'POST', keepalive: true },
  );
}

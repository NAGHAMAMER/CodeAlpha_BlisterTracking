import test from 'node:test';
import assert from 'node:assert/strict';
import { requestJson } from './api.js';

test('requestJson uses the API prefix', async () => {
  const result = await requestJson('/health', {}, async (url) => {
    assert.equal(url, '/api/health');
    return Response.json({ status: 'ok' });
  });
  assert.equal(result.status, 'ok');
});

test('requestJson returns a readable server error', async () => {
  await assert.rejects(
    requestJson('/tracking/start', {}, async () =>
      Response.json({ detail: 'Camera busy' }, { status: 409 })),
    /Camera busy/,
  );
});

test('requestJson handles invalid JSON', async () => {
  await assert.rejects(
    requestJson('/health', {}, async () => new Response('bad gateway', { status: 502 })),
    /server/,
  );
});

test('requestJson reports network errors', async () => {
  await assert.rejects(
    requestJson('/health', {}, async () => { throw new Error('network'); }),
    /8003/,
  );
});

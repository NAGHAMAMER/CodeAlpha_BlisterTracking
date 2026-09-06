import { useEffect, useRef, useState } from 'react';
import { getSessionStatus, startSession, stopSession } from '../services/api';

export default function useTracking() {
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [frame, setFrame] = useState(null);
  const activeRun = useRef(null);

  function release(run, stopRemote = true) {
    run.active = false;
    clearTimeout(run.pollTimer);
    clearTimeout(run.startTimer);
    run.abortController.abort();
    if (stopRemote && run.sessionId) {
      stopSession(run.sessionId).catch(() => {});
    }
    if (activeRun.current === run) activeRun.current = null;
  }

  useEffect(() => {
    const cleanup = () => {
      if (activeRun.current) release(activeRun.current);
    };
    window.addEventListener('pagehide', cleanup);
    return () => {
      window.removeEventListener('pagehide', cleanup);
      cleanup();
    };
  }, []);

  async function start(config) {
    if (activeRun.current) return;
    const run = {
      active: true,
      abortController: new AbortController(),
      stopping: false,
    };
    activeRun.current = run;
    setError('');
    setFrame(null);
    setStatus('connecting');

    const fail = (message) => {
      if (!run.active) return;
      release(run);
      setError(message);
      setStatus('error');
    };

    run.startTimer = setTimeout(
      () => fail('The camera took too long to start. Check the backend terminal.'),
      120000,
    );

    try {
      const started = await startSession(config);
      run.sessionId = started.session_id;
      if (!run.active) {
        stopSession(run.sessionId).catch(() => {});
        return;
      }

      clearTimeout(run.startTimer);
      setFrame({
        streamUrl: started.stream_url,
        frame: 0,
        tracks: [],
      });

      const poll = async () => {
        if (!run.active) return;
        try {
          const data = await getSessionStatus(
            run.sessionId,
            run.abortController.signal,
          );
          if (!run.active) return;
          setFrame((previous) => ({
            ...previous,
            ...data,
            streamUrl: started.stream_url,
          }));
          if (data.status === 'error') {
            fail(data.error || 'Camera processing failed.');
            return;
          }
          setStatus(run.stopping && data.active ? 'stopping' : data.status);
          if (!data.active && data.status === 'stopped') {
            release(run, false);
            return;
          }
          run.pollTimer = setTimeout(poll, 400);
        } catch (cause) {
          if (run.active) fail(cause.message);
        }
      };
      poll();
    } catch (cause) {
      if (run.active) fail(cause.message || 'Could not start the camera.');
    }
  }

  function stop() {
    const run = activeRun.current;
    if (!run) return;
    run.stopping = true;
    setStatus('stopping');
    if (!run.sessionId) {
      release(run);
      setStatus('stopped');
      return;
    }
    stopSession(run.sessionId).catch((cause) => {
      if (run.active) failStop(run, cause.message);
    });
  }

  function failStop(run, message) {
    release(run, false);
    setError(message);
    setStatus('error');
  }

  return {
    status,
    error,
    frame,
    start,
    stop,
    busy: ['connecting', 'running', 'stopping'].includes(status),
  };
}

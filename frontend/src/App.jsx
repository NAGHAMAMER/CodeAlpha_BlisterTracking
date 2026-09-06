import { useState } from 'react';
import { Alert, Box, Chip, Container, Stack, Typography } from '@mui/material';
import FilterCenterFocusRounded from '@mui/icons-material/FilterCenterFocusRounded';
import SourceControls from './components/SourceControls';
import TrackingView from './components/TrackingView';
import TrackList from './components/TrackList';
import useTracking from './hooks/useTracking';

export default function App() {
  const [config, setConfig] = useState({
    confidence: 0.35,
    trails: true,
    camera_fps: 10,
    camera_index: 0,
    mirror: true,
  });
  const tracking = useTracking();
  return <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 } }}>
    <Stack component="header" direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 4 }}>
      <Stack direction="row" spacing={1.5} alignItems="center">
        <Box sx={{ p: 1.4, bgcolor: 'primary.main', color: 'white', borderRadius: 3, display: 'flex' }}><FilterCenterFocusRounded /></Box>
        <Box><Typography variant="h4" component="h1" sx={{ fontSize: 28 }}>TrackLab</Typography><Typography variant="caption" color="text.secondary">CodeAlpha · Object detection & tracking</Typography></Box>
      </Stack>
      <Chip label="YOLO + BoT-SORT" variant="outlined" sx={{ display: { xs: 'none', sm: 'flex' } }} />
    </Stack>
    <Typography variant="h4" component="h2" sx={{ fontSize: { xs: 27, md: 36 }, mb: 1 }}>From detection to motion.</Typography>
    <Typography color="text.secondary" sx={{ mb: 3 }}>Detect blister packs and follow their movement with persistent track IDs.</Typography>
    {tracking.error && <Alert severity="error" sx={{ mb: 2 }}>{tracking.error}</Alert>}
    <Box component="main" sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '300px minmax(0, 1fr)' }, gap: 3 }}>
      <SourceControls config={config} setConfig={setConfig} busy={tracking.busy}
        start={() => tracking.start(config)} stop={tracking.stop} />
      <Box sx={{ minWidth: 0 }}><TrackingView frame={tracking.frame} status={tracking.status} />
        <TrackList tracks={tracking.frame?.tracks || []} status={tracking.status} /></Box>
    </Box>
    <Typography component="footer" variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 3 }}>
      Local processing · No audio capture · Detection only, not medicine identification or safety inspection
    </Typography>
  </Container>;
}

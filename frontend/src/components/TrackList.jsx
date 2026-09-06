import { Box, Chip, Paper, Stack, Typography } from '@mui/material';

export default function TrackList({ tracks, status }) {
  return <Paper variant="outlined" sx={{ p: 2.5, mt: 2 }}>
    <Typography fontWeight={700} sx={{ mb: 1.5 }}>{status === 'running' ? 'Visible tracks' : 'Tracks in the last frame'}</Typography>
    <Stack direction="row" useFlexGap flexWrap="wrap" gap={1}>
      {tracks.length ? tracks.map((track) => <Chip key={track.id} label={`ID ${track.id} · ${track.label} · ${track.confidence.toFixed(2)}`} variant="outlined" />)
        : <Typography variant="body2" color="text.secondary">No blister track is visible in this frame.</Typography>}
    </Stack>
    <Box sx={{ mt: 2 }}><Typography variant="caption" color="text.secondary">BoT-SORT combines motion, detection confidence and camera-motion compensation. IDs can still change after long occlusions or re-entry.</Typography></Box>
  </Paper>;
}

import {
  Box,
  Chip,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import CenterFocusStrongOutlined from '@mui/icons-material/CenterFocusStrongOutlined';

export default function TrackingView({ frame, status }) {
  const connecting = status === 'connecting';

  return (
    <Paper variant="outlined" sx={{ overflow: 'hidden' }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ px: 2.5, py: 2 }}>
        <Box>
          <Typography fontWeight={700}>Live tracking</Typography>
          <Typography variant="caption" color="text.secondary">
            Blister box · Track ID · Confidence · Movement trail
          </Typography>
        </Box>
        <Chip size="small" label={status} color={status === 'running' ? 'success' : 'default'}
          variant="outlined" sx={{ textTransform: 'capitalize' }} />
      </Stack>

      <Box sx={{ position: 'relative', bgcolor: '#102337', minHeight: { xs: 270, md: 430 },
        aspectRatio: '16/10', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {frame ? (
          <Box component="img" alt="Camera frame with a tracked blister pack" src={frame.streamUrl}
            sx={{ width: '100%', height: '100%', position: 'absolute', objectFit: 'contain' }} />
        ) : (
          <Stack alignItems="center" spacing={2} sx={{ color: '#acbfce', px: 3, textAlign: 'center' }}>
            {connecting ? <CircularProgress color="inherit" /> :
              <CenterFocusStrongOutlined sx={{ fontSize: 56, color: '#5dbbb4' }} />}
            <Typography variant="h6" sx={{ color: '#eef5fa' }}>
              {connecting ? 'Opening the camera' : 'Track a blister pack in real time'}
            </Typography>
            <Typography variant="body2">
              {connecting ? 'Loading the detector and starting the local camera…' :
                'Place one complete blister pack in view, then start tracking.'}
            </Typography>
          </Stack>
        )}
      </Box>

      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          {frame ? 'Processed frame ' + frame.frame + '. ' : ''}
          {status === 'running' ? 'Live processing speed depends on your device.' :
            'The last processed frame remains visible after stopping.'}
        </Typography>
      </Box>
    </Paper>
  );
}

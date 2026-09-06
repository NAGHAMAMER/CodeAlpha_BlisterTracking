import {
  Button,
  Divider,
  FormControlLabel,
  MenuItem,
  Paper,
  Slider,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import PlayArrowRounded from '@mui/icons-material/PlayArrowRounded';
import StopRounded from '@mui/icons-material/StopRounded';

export default function SourceControls({
  config,
  setConfig,
  busy,
  start,
  stop,
}) {
  const change = (key, value) => {
    setConfig((previous) => ({ ...previous, [key]: value }));
  };

  return (
    <Paper variant="outlined" sx={{ p: 3, height: 'fit-content' }}>
      <Typography variant="overline" color="text.secondary">
        01 / CAMERA
      </Typography>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Camera source
      </Typography>
      <TextField
        select
        fullWidth
        size="small"
        label="Camera"
        value={config.camera_index}
        disabled={busy}
        onChange={(event) => change('camera_index', Number(event.target.value))}
      >
        {[0, 1, 2, 3].map((index) => (
          <MenuItem key={index} value={index}>Camera {index}</MenuItem>
        ))}
      </TextField>
      <FormControlLabel
        control={
          <Switch
            checked={config.mirror}
            disabled={busy}
            onChange={(event) => change('mirror', event.target.checked)}
          />
        }
        label="Mirror camera"
      />
      <Typography variant="body2" color="text.secondary">
        OpenCV opens the webcam on the computer running FastAPI.
      </Typography>

      <Divider sx={{ my: 3 }} />
      <Typography variant="overline" color="text.secondary">
        02 / TRACKING
      </Typography>
      <TextField
        select
        fullWidth
        size="small"
        label="Object"
        value="blister"
        disabled
        sx={{ mt: 1.5 }}
      >
        <MenuItem value="blister">Blister packs</MenuItem>
      </TextField>

      <Stack direction="row" justifyContent="space-between" sx={{ mt: 3 }}>
        <Typography variant="body2">Detection threshold</Typography>
        <Typography variant="body2" fontWeight={700}>
          {config.confidence.toFixed(2)}
        </Typography>
      </Stack>
      <Slider
        value={config.confidence}
        min={0.25}
        max={0.80}
        step={0.05}
        disabled={busy}
        aria-label="Detection confidence threshold"
        onChange={(_, value) => change('confidence', value)}
      />
      <Typography variant="caption" color="text.secondary">
        Start at 0.35. Raise it only when false detections appear.
      </Typography>

      <FormControlLabel
        sx={{ mt: 1 }}
        control={
          <Switch
            checked={config.trails}
            disabled={busy}
            onChange={(event) => change('trails', event.target.checked)}
          />
        }
        label="Show movement trail"
      />

      <Stack spacing={1.2} sx={{ mt: 3 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<PlayArrowRounded />}
          disabled={busy}
          onClick={start}
        >
          Start tracking
        </Button>
        <Button
          variant="outlined"
          startIcon={<StopRounded />}
          disabled={!busy}
          onClick={stop}
        >
          Stop
        </Button>
      </Stack>
    </Paper>
  );
}

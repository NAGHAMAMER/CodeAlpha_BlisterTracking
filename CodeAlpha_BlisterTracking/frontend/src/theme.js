import { createTheme } from '@mui/material/styles';

export default createTheme({
  palette: {
    primary: { main: '#127d79' }, secondary: { main: '#d87942' },
    background: { default: '#f1f4f7', paper: '#ffffff' },
    text: { primary: '#173249', secondary: '#63798b' }, divider: '#e0e7ed',
  },
  shape: { borderRadius: 14 },
  typography: {
    fontFamily: '"Segoe UI", Arial, sans-serif',
    h4: { fontWeight: 750, letterSpacing: '-1px' },
    h6: { fontWeight: 700 }, button: { textTransform: 'none', fontWeight: 650 },
  },
  components: {
    MuiPaper: { defaultProps: { elevation: 0 } },
    MuiButton: { defaultProps: { disableElevation: true } },
    MuiCssBaseline: { styleOverrides: { body: { minWidth: 320 } } },
  },
});

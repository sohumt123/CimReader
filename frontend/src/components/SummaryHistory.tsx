import { useState, useEffect } from 'react';
import { Box, Paper, Typography, Button, Grid, CircularProgress } from '@mui/material';
import { useAuth } from './Auth';
import { toast } from 'react-toastify';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';

interface Summary {
  id: string;
  title: string;
  summary_pdf_url: string;
}

export function SummaryHistory() {
  const { session } = useAuth();
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummaries = async () => {
      if (!session) return;

      try {
        const response = await fetch('http://localhost:8000/summaries', {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch summaries');
        }

        const data = await response.json();
        setSummaries(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch summaries');
        toast.error('Failed to fetch summaries');
      } finally {
        setLoading(false);
      }
    };

    fetchSummaries();
  }, [session]);

  const handleDelete = async (summaryId: string) => {
    if (!session) return;

    try {
      const response = await fetch(`http://localhost:8000/summaries/${summaryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete summary');
      }

      setSummaries(summaries.filter(summary => summary.id !== summaryId));
      toast.success('Summary deleted successfully');
    } catch (err) {
      toast.error('Failed to delete summary');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (summaries.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography>No summaries found. Convert a PDF to get started!</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      maxWidth: 1200, 
      mx: 'auto', 
      p: { xs: 2, sm: 3, md: 4 },
      minHeight: 'calc(100vh - 200px)'
    }}>
      <Typography 
        variant="h4" 
        component="h1"
        sx={{ 
          mb: 4,
          textAlign: 'center',
          fontWeight: 600,
          color: 'var(--text-primary)',
          fontSize: { xs: '1.75rem', sm: '2rem', md: '2.25rem' }
        }}
      >
        My CIM<Box component="span" sx={{ color: '#10b981', fontWeight: 600, display: 'inline' }}>ez</Box> Summaries
      </Typography>
      
      <Grid container spacing={{ xs: 2, sm: 3 }}>
        {summaries.map((summary) => (
          <Grid item xs={12} sm={6} lg={4} key={summary.id}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                minHeight: '200px',
                backgroundColor: 'var(--bg-tertiary)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-lg)',
                color: 'var(--text-primary)',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 'var(--shadow-xl)',
                  borderColor: 'var(--border-secondary)',
                }
              }}
            >
              <Typography 
                variant="h6" 
                component="h2"
                sx={{ 
                  mb: 2,
                  fontWeight: 500,
                  color: 'var(--text-primary)',
                  fontSize: 'var(--font-size-lg)',
                  lineHeight: 'var(--leading-tight)',
                  // Fix text overflow
                  wordBreak: 'break-word',
                  overflowWrap: 'break-word',
                  hyphens: 'auto',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}
                title={summary.title} // Show full title on hover
              >
                {summary.title}
              </Typography>
              
              <Box sx={{ 
                mt: 'auto', 
                display: 'flex', 
                gap: 1.5,
                flexDirection: { xs: 'column', sm: 'row' }
              }}>
                <Button
                  variant="contained"
                  href={summary.summary_pdf_url}
                  download
                  startIcon={<DownloadIcon />}
                  sx={{
                    flex: 1,
                    backgroundColor: 'var(--primary-600)',
                    color: 'white',
                    fontWeight: 500,
                    borderRadius: 'var(--radius-md)',
                    textTransform: 'none',
                    fontSize: 'var(--font-size-sm)',
                    py: 1,
                    '&:hover': {
                      backgroundColor: 'var(--primary-700)',
                      transform: 'translateY(-1px)',
                    }
                  }}
                >
                  Download
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  onClick={() => handleDelete(summary.id)}
                  startIcon={<DeleteIcon />}
                  sx={{
                    backgroundColor: 'var(--error)',
                    color: 'white',
                    fontWeight: 500,
                    borderRadius: 'var(--radius-md)',
                    textTransform: 'none',
                    fontSize: 'var(--font-size-sm)',
                    py: 1,
                    minWidth: { xs: 'auto', sm: '100px' },
                    '&:hover': {
                      backgroundColor: '#dc2626',
                      transform: 'translateY(-1px)',
                    }
                  }}
                >
                  Delete
                </Button>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
} 
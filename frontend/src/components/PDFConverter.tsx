import { useState, useCallback } from 'react';
import { Box, Paper, Typography, CircularProgress, Button, LinearProgress, Grid } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import axios from 'axios';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import { useAuth } from './Auth';
import PDFChat from './PDFChat';
import { createApiUrl, createAuthHeadersMultipart } from '../lib/api.ts';

const PDFConverter = () => {
  const { session } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [converting, setConverting] = useState(false);
  const [convertedPdfUrl, setConvertedPdfUrl] = useState<string | null>(null);
  const [showLoadingBar, setShowLoadingBar] = useState(false);
  const [summaryId, setSummaryId] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setConvertedPdfUrl(null);
    } else {
      toast.error('Please upload a PDF file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  const handleConvert = async () => {
    if (!file || !session) return;

    setConverting(true);
    setShowLoadingBar(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(createApiUrl('convert-pdf'), formData, {
        headers: createAuthHeadersMultipart(session.access_token)
      });

      // The backend now returns JSON with public_url to a PDF and summary_id
      if (response.data && response.data.public_url) {
        setConvertedPdfUrl(response.data.public_url);
        setSummaryId(response.data.summary_id);
        toast.success('PDF summary generated successfully!');
      } else {
        throw new Error('No public URL received from server');
      }
    } catch (error) {
      let errorMessage = 'Error converting PDF';
      if (axios.isAxiosError(error) && error.response?.data) {
        // Handle JSON error response
        if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
      console.error('Conversion error:', error);
    } finally {
      setConverting(false);
      setShowLoadingBar(false);
    }
  };

  return (
    <Box sx={{ 
      maxWidth: 900, 
      mx: 'auto',
      p: { xs: 2, sm: 3, md: 4 },
      minHeight: 'calc(100vh - 200px)'
    }}>
      <Typography 
        variant="h3" 
        component="h1"
        sx={{ 
          mb: 4,
          textAlign: 'center',
          fontWeight: 600,
          color: 'var(--text-primary)',
          fontSize: { xs: '1.875rem', sm: '2.25rem', md: '3rem' }
        }}
      >
        CIM<Box component="span" sx={{ color: '#10b981', fontWeight: 600, display: 'inline' }}>ez</Box> PDF Summary Generator
      </Typography>
      
      {showLoadingBar && (
        <LinearProgress 
          sx={{ 
            height: 6, 
            borderRadius: 'var(--radius-md)', 
            mb: 3,
            backgroundColor: 'var(--bg-tertiary)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: 'var(--primary-500)',
              borderRadius: 'var(--radius-md)'
            }
          }} 
        />
      )}
      
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, sm: 4, md: 6 },
          textAlign: 'center',
          backgroundColor: isDragActive ? 'var(--bg-quaternary)' : 'var(--bg-secondary)',
          border: '2px dashed',
          borderColor: isDragActive ? 'var(--primary-500)' : 'var(--border-primary)',
          borderRadius: 'var(--radius-xl)',
          cursor: 'pointer',
          color: 'var(--text-primary)',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            borderColor: 'var(--primary-600)',
            backgroundColor: 'var(--bg-tertiary)',
            transform: 'translateY(-2px)',
            boxShadow: 'var(--shadow-lg)'
          }
        }}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon 
          sx={{ 
            fontSize: { xs: 48, sm: 56, md: 64 }, 
            color: 'var(--primary-500)', 
            mb: 2,
            transition: 'transform 0.2s ease-in-out',
            transform: isDragActive ? 'scale(1.1)' : 'scale(1)'
          }} 
        />
        <Typography 
          variant="h5" 
          sx={{
            mb: 2,
            fontWeight: 500,
            fontSize: { xs: 'var(--font-size-lg)', sm: 'var(--font-size-xl)', md: 'var(--font-size-2xl)' },
            color: 'var(--text-primary)'
          }}
        >
          {isDragActive
            ? 'Drop the PDF here'
            : 'Drag and drop a PDF file here, or click to select'}
        </Typography>
        {file && (
          <Typography 
            variant="body1" 
            sx={{
              color: 'var(--text-secondary)',
              fontSize: 'var(--font-size-base)',
              fontWeight: 500,
              backgroundColor: 'var(--bg-tertiary)',
              px: 3,
              py: 1,
              borderRadius: 'var(--radius-lg)',
              display: 'inline-block',
              mt: 2
            }}
          >
            Selected: {file.name}
          </Typography>
        )}
      </Paper>

      {file && !convertedPdfUrl && (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            variant="contained"
            onClick={handleConvert}
            disabled={converting}
            startIcon={converting ? <CircularProgress size={20} color="inherit" /> : null}
            sx={{
              backgroundColor: 'var(--primary-600)',
              color: 'white',
              fontWeight: 600,
              fontSize: 'var(--font-size-lg)',
              px: 4,
              py: 1.5,
              borderRadius: 'var(--radius-lg)',
              textTransform: 'none',
              minWidth: '200px',
              '&:hover': {
                backgroundColor: 'var(--primary-700)',
                transform: 'translateY(-2px)',
                boxShadow: 'var(--shadow-lg)'
              },
              '&:disabled': {
                backgroundColor: 'var(--bg-quaternary)',
                color: 'var(--text-muted)'
              }
            }}
          >
            {converting ? 'Converting...' : 'Convert PDF'}
          </Button>
        </Box>
      )}

      {convertedPdfUrl && (
        <Box sx={{ mt: 4 }}>
          <Box sx={{ 
            textAlign: 'center', 
            mb: 3, 
            display: 'flex', 
            gap: 2, 
            justifyContent: 'center', 
            flexWrap: 'wrap' 
          }}>
            <Button
              variant="outlined"
              href={convertedPdfUrl}
              download
              startIcon={<DownloadIcon />}
              sx={{
                borderColor: 'var(--primary-500)',
                color: 'var(--primary-500)',
                fontWeight: 500,
                fontSize: 'var(--font-size-base)',
                px: 3,
                py: 1,
                borderRadius: 'var(--radius-md)',
                textTransform: 'none',
                '&:hover': {
                  borderColor: 'var(--primary-600)',
                  backgroundColor: 'var(--primary-600)',
                  color: 'white',
                  transform: 'translateY(-1px)',
                }
              }}
            >
              Download PDF Summary
            </Button>
          </Box>
          
          {/* PDF Viewer and Chat Side by Side */}
          <Grid container spacing={3}>
            {/* PDF Viewer */}
            <Grid item xs={12} lg={6}>
              <Paper 
                elevation={3} 
                sx={{ 
                  backgroundColor: 'var(--bg-secondary)', 
                  border: '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-xl)',
                  overflow: 'hidden',
                  boxShadow: 'var(--shadow-xl)'
                }}
              >
                <Box sx={{ 
                  p: 3, 
                  borderBottom: '1px solid var(--border-primary)', 
                  backgroundColor: 'var(--bg-tertiary)' 
                }}>
                  <Typography 
                    variant="h6"
                    sx={{
                      color: 'var(--text-primary)',
                      fontWeight: 600,
                      fontSize: 'var(--font-size-lg)'
                    }}
                  >
                    📄 PDF Summary Preview
                  </Typography>
                </Box>
                <Box sx={{ height: '600px', width: '100%' }}>
                  <iframe
                    src={convertedPdfUrl}
                    style={{
                      width: '100%',
                      height: '100%',
                      border: 'none',
                      backgroundColor: '#fff'
                    }}
                    title="PDF Summary Preview"
                  />
                </Box>
              </Paper>
            </Grid>

            {/* Chat Component */}
            <Grid item xs={12} lg={6}>
              <PDFChat 
                documentId={summaryId || undefined}
                documentTitle={file?.name ? `Summary of ${file.name}` : undefined}
              />
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default PDFConverter; 
import { useState, useCallback } from 'react';
import { Box, Paper, Typography, CircularProgress, Button, LinearProgress } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import axios from 'axios';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';

const PDFConverter = () => {
  const [file, setFile] = useState<File | null>(null);
  const [converting, setConverting] = useState(false);
  const [convertedPdfUrl, setConvertedPdfUrl] = useState<string | null>(null);
  const [showLoadingBar, setShowLoadingBar] = useState(false);

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
    if (!file) return;

    setConverting(true);
    setShowLoadingBar(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/convert', formData, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      setConvertedPdfUrl(url);
      toast.success('PDF converted successfully!');
    } catch (error) {
      let errorMessage = 'Error converting PDF';
      if (axios.isAxiosError(error) && error.response?.data) {
        // Try to read the error message from the response
        const reader = new FileReader();
        reader.onload = () => {
          const errorDetail = reader.result as string;
          toast.error(`Error: ${errorDetail}`);
        };
        reader.readAsText(error.response.data);
      } else {
        toast.error(errorMessage);
      }
      console.error('Conversion error:', error);
    } finally {
      setConverting(false);
      setShowLoadingBar(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      {showLoadingBar && <LinearProgress color="primary" sx={{ height: 4, borderRadius: 2, mb: 2, bgcolor: '#23272f' }} />}
      <Paper
        elevation={3}
        sx={{
          p: 4,
          textAlign: 'center',
          backgroundColor: isDragActive ? '#23272f' : '#181c24',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.800',
          cursor: 'pointer',
          color: '#fff',
        }}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          {isDragActive
            ? 'Drop the PDF here'
            : 'Drag and drop a PDF file here, or click to select'}
        </Typography>
        {file && (
          <Typography variant="body1" color="#b0b8c1">
            Selected file: {file.name}
          </Typography>
        )}
      </Paper>

      {file && !convertedPdfUrl && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            onClick={handleConvert}
            disabled={converting}
            startIcon={converting ? <CircularProgress size={20} /> : null}
          >
            {converting ? 'Converting...' : 'Convert PDF'}
          </Button>
        </Box>
      )}

      {convertedPdfUrl && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<DownloadIcon />}
            href={convertedPdfUrl}
            download="converted.pdf"
            sx={{ mb: 2 }}
          >
            Download Converted PDF
          </Button>
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
            <iframe
              src={convertedPdfUrl}
              title="PDF Preview"
              width="100%"
              height="600px"
              style={{ background: '#23272f', border: '1px solid #333', borderRadius: 8 }}
            />
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default PDFConverter; 
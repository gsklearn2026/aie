import axios from 'axios';

const API_BASE_URL = '/api/v1/export';

class ExportService {
  async createExport(exportRequest) {
    try {
      const response = await axios.post(`${API_BASE_URL}/create`, exportRequest);
      return response.data;
    } catch (error) {
      console.error('Export creation failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create export');
    }
  }

  async getExportStatus(jobId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/status/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get export status:', error);
      throw new Error('Failed to get export status');
    }
  }

  async getExports() {
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs`);
      return response.data;
    } catch (error) {
      console.error('Failed to load exports:', error);
      return [];
    }
  }

  async downloadExport(jobId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/download/${jobId}`, {
        responseType: 'blob'
      });
      
      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition'];
      let filename = `export_${jobId}.dat`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      // Create download link
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Download failed:', error);
      throw new Error('Failed to download export');
    }
  }
}

export const exportService = new ExportService();

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../client';
import axios from 'axios';

// Mock axios client
const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: mockGet,
      post: mockPost,
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    })
  }
}));

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Use Case Operations', () => {
    it('extracts from text', async () => {
      const mockData = { text: 'test requirements' };
      mockPost.mockResolvedValueOnce({ data: { results: [] } });

      await api.extractFromText(mockData);
      expect(mockPost).toHaveBeenCalledWith('/parse_use_case_rag/', mockData);
    });

    it('extracts from document', async () => {
      const mockFormData = new FormData();
      mockPost.mockResolvedValueOnce({ data: { results: [] } });

      await api.extractFromDocument(mockFormData);
      expect(mockPost).toHaveBeenCalledWith(
        '/parse_use_case_document/',
        mockFormData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
    });

    it('refines use case', async () => {
      const mockData = { id: '123', type: 'detail' };
      mockPost.mockResolvedValueOnce({ data: {} });

      await api.refineUseCase(mockData);
      expect(mockPost).toHaveBeenCalledWith('/use-case/refine', mockData);
    });

    it('gets session use cases', async () => {
      const sessionId = 'test-session';
      mockGet.mockResolvedValueOnce({ data: [] });

      await api.getSessionUseCases(sessionId);
      expect(mockGet).toHaveBeenCalledWith(`/session/${sessionId}/history`);
    });
  });

  describe('Query Operations', () => {
    it('queries requirements', async () => {
      const mockData = { session_id: '123', question: 'test?' };
      mockPost.mockResolvedValueOnce({ data: { answer: 'test answer' } });

      await api.queryRequirements(mockData);
      expect(mockPost).toHaveBeenCalledWith('/query', mockData);
    });
  });

  describe('Export Operations', () => {
    it('exports to DOCX', async () => {
      const sessionId = 'test-session';
      mockGet.mockResolvedValueOnce({ data: new Blob() });

      await api.exportDOCX(sessionId);
      expect(mockGet).toHaveBeenCalledWith(
        `/session/${sessionId}/export/docx`,
        { responseType: 'blob' }
      );
    });

    it('exports to Markdown', async () => {
      const sessionId = 'test-session';
      mockGet.mockResolvedValueOnce({ data: new Blob() });

      await api.exportMarkdown(sessionId);
      expect(mockGet).toHaveBeenCalledWith(
        `/session/${sessionId}/export/markdown`,
        { responseType: 'blob' }
      );
    });

    it('exports to PlantUML', async () => {
      const sessionId = 'test-session';
      mockGet.mockResolvedValueOnce({ data: '' });

      await api.exportPlantUML(sessionId);
      expect(mockGet).toHaveBeenCalledWith(`/session/${sessionId}/export/plantuml`);
    });
  });

  it('checks health status', async () => {
    mockGet.mockResolvedValueOnce({ data: { status: 'healthy' } });

    await api.health();
    expect(mockGet).toHaveBeenCalledWith('/health');
  });

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      mockPost.mockRejectedValueOnce(new Error('Network Error'));

      await expect(api.queryRequirements({ session_id: '123', question: 'test?' }))
        .rejects.toThrow('Network Error');
    });

    it('handles API errors', async () => {
      mockPost.mockRejectedValueOnce({
        response: { data: { message: 'Invalid request' } }
      });

      await expect(api.queryRequirements({ session_id: '123', question: 'test?' }))
        .rejects.toThrow();
    });
  });
});
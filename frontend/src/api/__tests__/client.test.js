import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../client';

// Mock axios client
const mocks = vi.hoisted(() => ({
  get: vi.fn(), 
  post: vi.fn()
}));

vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: mocks.get,
      post: mocks.post,
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
      mocks.post.mockResolvedValueOnce({ data: { results: [] } });

      await api.extractFromText(mockData);
      expect(mocks.post).toHaveBeenCalledWith('/parse_use_case_rag/', mockData);
    });

    it('extracts from document', async () => {
      const mockFormData = new FormData();
      mocks.post.mockResolvedValueOnce({ data: { results: [] } });

      await api.extractFromDocument(mockFormData);
      expect(mocks.post).toHaveBeenCalledWith(
        '/parse_use_case_document/',
        mockFormData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
    });

    it('refines use case', async () => {
      const mockData = { id: '123', type: 'detail' };
      mocks.post.mockResolvedValueOnce({ data: {} });

      await api.refineUseCase(mockData);
      expect(mocks.post).toHaveBeenCalledWith('/use-case/refine', mockData);
    });

    it('gets session use cases', async () => {
      const sessionId = 'test-session';
      mocks.get.mockResolvedValueOnce({ data: [] });

      await api.getSessionUseCases(sessionId);
      expect(mocks.get).toHaveBeenCalledWith(`/session/${sessionId}/history`);
    });
  });

  describe('Query Operations', () => {
    it('queries requirements', async () => {
      const mockData = { session_id: '123', question: 'test?' };
      mocks.post.mockResolvedValueOnce({ data: { answer: 'test answer' } });

      await api.queryRequirements(mockData);
      expect(mocks.post).toHaveBeenCalledWith('/query', mockData);
    });
  });

  describe('Export Operations', () => {
    it('exports to DOCX', async () => {
      const sessionId = 'test-session';
      mocks.get.mockResolvedValueOnce({ data: new Blob() });

      await api.exportDOCX(sessionId);
      expect(mocks.get).toHaveBeenCalledWith(
        `/session/${sessionId}/export/docx`,
        { responseType: 'blob' }
      );
    });

    it('exports to Markdown', async () => {
      const sessionId = 'test-session';
      mocks.get.mockResolvedValueOnce({ data: new Blob() });

      await api.exportMarkdown(sessionId);
      expect(mocks.get).toHaveBeenCalledWith(
        `/session/${sessionId}/export/markdown`,
        { responseType: 'blob' }
      );
    });

    it('exports to PlantUML', async () => {
      const sessionId = 'test-session';
      mocks.get.mockResolvedValueOnce({ data: '' });

      await api.exportPlantUML(sessionId);
      expect(mocks.get).toHaveBeenCalledWith(`/session/${sessionId}/export/plantuml`);
    });
  });

  it('checks health status', async () => {
    mocks.get.mockResolvedValueOnce({ data: { status: 'healthy' } });

    await api.health();
    expect(mocks.get).toHaveBeenCalledWith('/health');
  });

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      mocks.post.mockRejectedValueOnce(new Error('Network Error'));

      await expect(api.queryRequirements({ session_id: '123', question: 'test?' }))
        .rejects.toThrow('Network Error');
    });

    it('handles API errors', async () => {
      mocks.post.mockRejectedValueOnce({
        response: { data: { message: 'Invalid request' } }
      });

      await expect(api.queryRequirements({ session_id: '123', question: 'test?' }))
        .rejects.toThrow();
    });
  });
});
import { describe, it, expect, beforeEach } from 'vitest';
import { act } from '@testing-library/react';
import useSessionStore from '../useSessionStore';

describe('useSessionStore', () => {
  beforeEach(() => {
    // Clear the store before each test
    act(() => {
      useSessionStore.getState().clearSession();
    });
  });

  it('initializes with default values', () => {
    const state = useSessionStore.getState();
    expect(state.currentSessionId).toBeNull();
    expect(state.projectContext).toBe('');
    expect(state.domain).toBe('');
    expect(state.useCases).toEqual([]);
  });

  it('sets current session', () => {
    act(() => {
      useSessionStore.getState().setCurrentSession('test-session-123');
    });
    
    expect(useSessionStore.getState().currentSessionId).toBe('test-session-123');
  });

  it('sets project context', () => {
    act(() => {
      useSessionStore.getState().setProjectContext('Test Project');
    });
    
    expect(useSessionStore.getState().projectContext).toBe('Test Project');
  });

  it('sets domain', () => {
    act(() => {
      useSessionStore.getState().setDomain('Test Domain');
    });
    
    expect(useSessionStore.getState().domain).toBe('Test Domain');
  });

  it('clears session data', () => {
    act(() => {
      const store = useSessionStore.getState();
      store.setCurrentSession('test-session');
      store.setProjectContext('Test Project');
      store.setDomain('Test Domain');
      store.setUseCases([{ id: 1, title: 'Test Case' }]);
      store.clearSession();
    });

    const state = useSessionStore.getState();
    expect(state.currentSessionId).toBeNull();
    expect(state.projectContext).toBe('');
    expect(state.domain).toBe('');
    expect(state.useCases).toEqual([]);
  });

  it('sets use cases', () => {
    const testCases = [
      { id: 1, title: 'Test Case 1' },
      { id: 2, title: 'Test Case 2' }
    ];

    act(() => {
      useSessionStore.getState().setUseCases(testCases);
    });

    expect(useSessionStore.getState().useCases).toEqual(testCases);
  });
});
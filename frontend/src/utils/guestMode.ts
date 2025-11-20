/**
 * Guest Mode Utilities
 * Handles guest session management and data persistence
 */

export const getOrCreateGuestSession = (): string => {
  let sessionId = localStorage.getItem('guest_session_id');
  
  if (!sessionId) {
    // Generate new guest session ID
    sessionId = `guest-${crypto.randomUUID()}`;
    localStorage.setItem('guest_session_id', sessionId);
    
    // Create session in backend
    createGuestSessionInBackend(sessionId);
  }
  
  return sessionId;
};

export const createGuestSessionInBackend = async (sessionId: string) => {
  try {
    await fetch('http://localhost:8000/api/guest/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });
  } catch (error) {
    console.error('Failed to create guest session:', error);
  }
};

export const isGuest = (): boolean => {
  return !localStorage.getItem('access_token');
};

export const isLoggedIn = (): boolean => {
  return !!localStorage.getItem('access_token');
};

export const getGuestSessionId = (): string | null => {
  return localStorage.getItem('guest_session_id');
};

export const clearGuestSession = () => {
  localStorage.removeItem('guest_session_id');
};

export const migrateGuestData = async (userId: string) => {
  const guestSessionId = getGuestSessionId();
  
  if (!guestSessionId) {
    return { migrated_tasks: 0, migrated_courses: 0 };
  }
  
  try {
    const response = await fetch(
      `http://localhost:8000/api/guest/migrate/${guestSessionId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      }
    );
    
    if (response.ok) {
      const data = await response.json();
      clearGuestSession();
      return data;
    }
  } catch (error) {
    console.error('Failed to migrate guest data:', error);
  }
  
  return { migrated_tasks: 0, migrated_courses: 0 };
};

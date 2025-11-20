import React from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // Allow both logged-in users and guests
  // Guests will have guest_session_id in localStorage
  // Logged-in users will have access_token in localStorage
  const token = localStorage.getItem('access_token');
  const guestSession = localStorage.getItem('guest_session_id');

  if (!token && !guestSession) {
    // No token and no guest session - shouldn't happen as App.tsx creates guest session
    // But just in case, allow access anyway (guest mode will be initialized)
    return <>{children}</>;
  }

  return <>{children}</>;
};

export default ProtectedRoute;

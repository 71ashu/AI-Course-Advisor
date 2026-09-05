import React, { useState, useEffect } from 'react';
import { api } from './api';
import CourseAdvisor from './CourseAdvisor';
import AuthPage from './components/auth/AuthPage';

export default function App() {
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authMode, setAuthModeState] = useState('login'); // 'login' | 'register' | 'forgot' | 'reset'
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [universities, setUniversities] = useState(['Santa Clara University']);
  const [programs, setPrograms] = useState(['MS Computer Science and Engineering']);
  const [courses, setCourses] = useState([]);
  const [selectedUniversity, setSelectedUniversity] = useState('Santa Clara University');
  const [forgotMessage, setForgotMessage] = useState('');
  const [devResetLink, setDevResetLink] = useState('');
  const [resetToken, setResetToken] = useState(null);

  useEffect(() => {
    api.me()
      .then(({ student }) => setStudent(student))
      .catch(() => setStudent(null))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get('reset_token');
    if (t) {
      setResetToken(t);
      setAuthModeState('reset');
      setAuthError('');
      window.history.replaceState({}, '', window.location.pathname + window.location.hash);
    }
  }, []);

  useEffect(() => {
    api.getPrograms()
      .then(({ programs: catalogPrograms }) => {
        const programRows = Array.isArray(catalogPrograms) ? catalogPrograms : [];

        const uniquePrograms = [...new Set(
          programRows
            .map((p) => p.program_name)
            .filter(Boolean)
        )];

        const uniqueUniversities = [...new Set(
          programRows
            .map((p) => p.university)
            .filter(Boolean)
        )];

        if (uniquePrograms.length > 0) {
          setPrograms(uniquePrograms);
        }

        if (uniqueUniversities.length > 0) {
          setUniversities(uniqueUniversities);
          setSelectedUniversity(uniqueUniversities[0]);
        }
      })
      .catch(() => {
        // Keep fallback dropdown options if program catalog is unavailable.
      });
  }, []);

  useEffect(() => {
    api.getCourses()
      .then(({ courses: catalogCourses }) => setCourses(Array.isArray(catalogCourses) ? catalogCourses : []))
      .catch(() => {
        // Transcript course picker is optional; leave it empty if unavailable.
      });
  }, []);

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    const form = e.target;
    const data = {
      email: form.email.value,
      password: form.password.value,
      name: form.name?.value,
      university: form.university?.value,
      program: form.program?.value,
      major: form.major?.value || 'Computer Science',
      year: form.year?.value || 'Sophomore',
      interests: (form.interests?.value || '').split(',').map(s => s.trim()).filter(Boolean),
      careerGoals: form.careerGoals?.value || '',
    };

    if (form.transcript?.value) {
      try {
        const completedCourses = JSON.parse(form.transcript.value);
        if (Array.isArray(completedCourses) && completedCourses.length > 0) {
          data.completedCourses = completedCourses;
        }
      } catch {
        // Ignore a malformed transcript payload rather than blocking registration.
      }
    }

    try {
      const res = authMode === 'login'
        ? await api.login(data)
        : await api.register(data);
      setStudent(res.student);
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    try {
      const res = await api.forgotPassword({ email: e.target.email.value });
      setForgotMessage(res.message || '');
      setDevResetLink(res.devResetLink || '');
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleBackFromForgot = () => {
    setAuthModeState('login');
    setAuthError('');
    setForgotMessage('');
    setDevResetLink('');
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setAuthError('');
    const p = e.target.password.value;
    const c = e.target.confirm.value;
    if (p !== c) {
      setAuthError('Passwords do not match');
      return;
    }
    if (!resetToken) {
      setAuthError('Missing reset token. Open the link from your email again.');
      return;
    }
    setAuthLoading(true);
    try {
      const res = await api.resetPassword({ token: resetToken, password: p });
      setStudent(res.student);
      setResetToken(null);
      setAuthModeState('login');
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSwitchToLogin = () => {
    setAuthModeState('login');
    setAuthError('');
    setResetToken(null);
  };

  const handleLogout = async () => {
    await api.logout();
    setStudent(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-app-shell flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!student) {
    return (
      <AuthPage
        authMode={authMode}
        setAuthMode={(mode) => {
          setAuthModeState(mode);
          setForgotMessage('');
          setDevResetLink('');
          if (mode !== 'reset') setResetToken(null);
        }}
        setAuthError={setAuthError}
        authError={authError}
        authLoading={authLoading}
        handleAuth={handleAuth}
        handleForgotPassword={handleForgotPassword}
        handleResetPassword={handleResetPassword}
        handleBackFromForgot={handleBackFromForgot}
        onSwitchToLogin={handleSwitchToLogin}
        universities={universities}
        programs={programs}
        courses={courses}
        selectedUniversity={selectedUniversity}
        setSelectedUniversity={setSelectedUniversity}
        forgotMessage={forgotMessage}
        devResetLink={devResetLink}
      />
    );
  }

  return <CourseAdvisor student={student} onLogout={handleLogout} onProfileUpdate={setStudent} />;
}

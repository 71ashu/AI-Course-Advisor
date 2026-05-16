import React, { useState, useEffect } from 'react';
import { api } from './api';
import CourseAdvisor from './CourseAdvisor';
import AuthPage from './components/auth/AuthPage';

export default function App() {
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [universities, setUniversities] = useState(['Santa Clara University']);
  const [programs, setPrograms] = useState(['MS Computer Science and Engineering']);
  const [selectedUniversity, setSelectedUniversity] = useState('Santa Clara University');

  useEffect(() => {
    api.me()
      .then(({ student }) => setStudent(student))
      .catch(() => setStudent(null))
      .finally(() => setLoading(false));
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
        setAuthMode={setAuthMode}
        setAuthError={setAuthError}
        authError={authError}
        authLoading={authLoading}
        handleAuth={handleAuth}
        universities={universities}
        programs={programs}
        selectedUniversity={selectedUniversity}
        setSelectedUniversity={setSelectedUniversity}
      />
    );
  }

  return <CourseAdvisor student={student} onLogout={handleLogout} onProfileUpdate={setStudent} />;
}

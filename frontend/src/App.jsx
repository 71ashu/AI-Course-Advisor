import React, { useState, useEffect } from 'react';
import { LogIn, UserPlus } from 'lucide-react';
import { api } from './api';
import CourseAdvisor from './CourseAdvisor';

export default function App() {
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  useEffect(() => {
    api.me()
      .then(({ student }) => setStudent(student))
      .catch(() => setStudent(null))
      .finally(() => setLoading(false));
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
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!student) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <h1 className="text-4xl font-black mb-2 bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent text-center">
            AI Course Advisor
          </h1>
          <p className="text-slate-400 text-center mb-8">Your intelligent academic planning companion</p>

          <div className="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-6">
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => { setAuthMode('login'); setAuthError(''); }}
                className={`flex-1 py-2 rounded-lg font-semibold transition-all ${authMode === 'login' ? 'bg-violet-500 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                <LogIn className="w-4 h-4 inline mr-2" />
                Login
              </button>
              <button
                onClick={() => { setAuthMode('register'); setAuthError(''); }}
                className={`flex-1 py-2 rounded-lg font-semibold transition-all ${authMode === 'register' ? 'bg-violet-500 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                <UserPlus className="w-4 h-4 inline mr-2" />
                Register
              </button>
            </div>

            <form onSubmit={handleAuth} className="space-y-4">
              {authMode === 'register' && (
                <input name="name" placeholder="Full name" required className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50" />
              )}
              <input name="email" type="email" placeholder="Email" required className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50" />
              <input name="password" type="password" placeholder="Password" required className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50" />
              {authMode === 'register' && (
                <>
                  <input name="major" placeholder="Major (e.g. Computer Science)" className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50" />
                  <select name="year" className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50">
                    <option value="Freshman">Freshman</option>
                    <option value="Sophomore">Sophomore</option>
                    <option value="Junior">Junior</option>
                    <option value="Senior">Senior</option>
                  </select>
                  <input name="interests" placeholder="Interests (comma-separated, e.g. AI, Web Dev)" className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50" />
                  <input name="careerGoals" placeholder="Career goals" className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50" />
                </>
              )}
              {authError && <p className="text-rose-400 text-sm">{authError}</p>}
              <button type="submit" disabled={authLoading} className="w-full py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 rounded-xl font-semibold disabled:opacity-50">
                {authLoading ? 'Please wait...' : authMode === 'login' ? 'Login' : 'Register'}
              </button>
            </form>

            {authMode === 'login' && (
              <p className="mt-4 text-slate-500 text-sm text-center">
                Demo: alex@demo.edu / demo123
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return <CourseAdvisor student={student} onLogout={handleLogout} onProfileUpdate={setStudent} />;
}

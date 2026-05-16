import { LogIn, UserPlus } from 'lucide-react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

export default function AuthPage({
  authMode,
  setAuthMode,
  setAuthError,
  authError,
  authLoading,
  handleAuth,
  universities,
  programs,
  selectedUniversity,
  setSelectedUniversity
}) {
  return (
    <div className="min-h-screen bg-app-shell flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <h1 className="text-4xl font-black mb-2 bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent text-center">
          AI Course Advisor
        </h1>
        <p className="text-slate-400 text-center mb-8">Your intelligent academic planning companion</p>

        <div className="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-6">
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => {
                setAuthMode('login');
                setAuthError('');
              }}
              className={`flex-1 py-2 rounded-lg font-semibold transition-all ${authMode === 'login' ? 'bg-violet-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              <LogIn className="w-4 h-4 inline mr-2" />
              Login
            </button>
            <button
              onClick={() => {
                setAuthMode('register');
                setAuthError('');
              }}
              className={`flex-1 py-2 rounded-lg font-semibold transition-all ${authMode === 'register' ? 'bg-violet-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              <UserPlus className="w-4 h-4 inline mr-2" />
              Register
            </button>
          </div>

          {authMode === 'login' ? (
            <LoginForm
              onSubmit={handleAuth}
              authError={authError}
              authLoading={authLoading}
            />
          ) : (
            <RegisterForm
              onSubmit={handleAuth}
              authError={authError}
              authLoading={authLoading}
              universities={universities}
              programs={programs}
              selectedUniversity={selectedUniversity}
              setSelectedUniversity={setSelectedUniversity}
            />
          )}
        </div>
      </div>
    </div>
  );
}

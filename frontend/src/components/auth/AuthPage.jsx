import { LogIn, UserPlus } from 'lucide-react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import ForgotPasswordForm from './ForgotPasswordForm';
import ResetPasswordForm from './ResetPasswordForm';

export default function AuthPage({
  authMode,
  setAuthMode,
  setAuthError,
  authError,
  authLoading,
  handleAuth,
  handleForgotPassword,
  handleResetPassword,
  handleBackFromForgot,
  onSwitchToLogin,
  universities,
  programs,
  selectedUniversity,
  setSelectedUniversity,
  forgotMessage,
  devResetLink,
}) {
  const showTabs = authMode === 'login' || authMode === 'register';

  return (
    <div className="min-h-screen bg-app-shell flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <h1 className="text-4xl font-black mb-2 bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent text-center">
          AI Course Advisor
        </h1>
        <p className="text-slate-400 text-center mb-8">Your intelligent academic planning companion</p>

        <div className="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-6">
          {showTabs && (
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
          )}

          {authMode === 'forgot' && (
            <h2 className="text-lg font-semibold text-white mb-4">Reset password</h2>
          )}
          {authMode === 'reset' && (
            <h2 className="text-lg font-semibold text-white mb-4">Set new password</h2>
          )}

          {authMode === 'login' && (
            <LoginForm
              onSubmit={handleAuth}
              authError={authError}
              authLoading={authLoading}
              onForgotPassword={() => {
                setAuthMode('forgot');
                setAuthError('');
              }}
            />
          )}
          {authMode === 'register' && (
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
          {authMode === 'forgot' && (
            <ForgotPasswordForm
              onBack={handleBackFromForgot}
              onSubmit={handleForgotPassword}
              authError={authError}
              authLoading={authLoading}
              forgotMessage={forgotMessage}
              devResetLink={devResetLink}
            />
          )}
          {authMode === 'reset' && (
            <ResetPasswordForm
              onSubmit={handleResetPassword}
              authError={authError}
              authLoading={authLoading}
              onCancel={onSwitchToLogin}
            />
          )}
        </div>
      </div>
    </div>
  );
}

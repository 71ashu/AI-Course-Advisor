export default function ForgotPasswordForm({
  onBack,
  onSubmit,
  authError,
  authLoading,
  forgotMessage,
  devResetLink,
}) {
  if (forgotMessage) {
    return (
      <div className="space-y-4">
        <p className="text-slate-300 text-sm">{forgotMessage}</p>
        {devResetLink && (
          <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 px-4 py-3 text-amber-200/90 text-xs break-all">
            <p className="font-semibold text-amber-100 mb-1">Development mode</p>
            <p className="mb-1">Email is not configured; open this link to reset:</p>
            <a href={devResetLink} className="text-violet-300 underline hover:text-violet-200">
              {devResetLink}
            </a>
          </div>
        )}
        <button
          type="button"
          onClick={onBack}
          className="w-full py-3 rounded-xl font-semibold bg-slate-700/80 hover:bg-slate-600 text-white"
        >
          Back to login
        </button>
      </div>
    );
  }

  return (
    <>
      <p className="text-slate-400 text-sm mb-4">
        Enter your email and we will send you a link to reset your password.
      </p>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          name="email"
          type="email"
          placeholder="Email"
          required
          autoComplete="email"
          className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
        />
        {authError && <p className="text-rose-400 text-sm">{authError}</p>}
        <button
          type="submit"
          disabled={authLoading}
          className="w-full py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 rounded-xl font-semibold disabled:opacity-50"
        >
          {authLoading ? 'Please wait...' : 'Send reset link'}
        </button>
      </form>
      <button
        type="button"
        onClick={onBack}
        className="mt-4 w-full py-2 text-slate-400 hover:text-white text-sm"
      >
        Back to login
      </button>
    </>
  );
}

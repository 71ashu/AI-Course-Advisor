export default function ResetPasswordForm({ onSubmit, authError, authLoading, onCancel }) {
  return (
    <>
      <p className="text-slate-400 text-sm mb-4">Choose a new password (at least 8 characters).</p>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          name="password"
          type="password"
          placeholder="New password"
          required
          minLength={8}
          autoComplete="new-password"
          className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
        />
        <input
          name="confirm"
          type="password"
          placeholder="Confirm new password"
          required
          minLength={8}
          autoComplete="new-password"
          className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
        />
        {authError && <p className="text-rose-400 text-sm">{authError}</p>}
        <button
          type="submit"
          disabled={authLoading}
          className="w-full py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 rounded-xl font-semibold disabled:opacity-50"
        >
          {authLoading ? 'Please wait...' : 'Update password'}
        </button>
      </form>
      {onCancel && (
        <button
          type="button"
          onClick={onCancel}
          className="mt-4 w-full py-2 text-slate-400 hover:text-white text-sm"
        >
          Cancel
        </button>
      )}
    </>
  );
}

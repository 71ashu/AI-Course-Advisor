export default function LoginForm({ onSubmit, authError, authLoading }) {
  return (
    <>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          name="email"
          type="email"
          placeholder="Email"
          required
          className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
        />
        <input
          name="password"
          type="password"
          placeholder="Password"
          required
          className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
        />
        {authError && <p className="text-rose-400 text-sm">{authError}</p>}
        <button
          type="submit"
          disabled={authLoading}
          className="w-full py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 rounded-xl font-semibold disabled:opacity-50"
        >
          {authLoading ? 'Please wait...' : 'Login'}
        </button>
      </form>

      <p className="mt-4 text-slate-500 text-sm text-center">
        Demo: alex@demo.edu / demo123
      </p>
    </>
  );
}

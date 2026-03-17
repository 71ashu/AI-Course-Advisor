export default function RegisterForm({
  onSubmit,
  authError,
  authLoading,
  universities,
  programs,
  selectedUniversity,
  setSelectedUniversity
}) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <input
        name="name"
        placeholder="Full name"
        required
        className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      />
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
      <select
        name="university"
        required
        value={selectedUniversity}
        onChange={(e) => setSelectedUniversity(e.target.value)}
        className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      >
        {universities.map((university) => (
          <option key={university} value={university}>
            {university}
          </option>
        ))}
      </select>
      <select
        name="program"
        required
        defaultValue=""
        className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      >
        <option value="" disabled>
          Select program
        </option>
        {programs.map((program) => (
          <option key={program} value={program}>
            {program}
          </option>
        ))}
      </select>
      <input
        name="major"
        placeholder="Major (e.g. Computer Science)"
        className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      />
      <select
        name="year"
        className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      >
        <option value="Freshman">Freshman</option>
        <option value="Sophomore">Sophomore</option>
        <option value="Junior">Junior</option>
        <option value="Senior">Senior</option>
      </select>
      <input
        name="interests"
        placeholder="Interests (comma-separated, e.g. AI, Web Dev)"
        className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      />
      <input
        name="careerGoals"
        placeholder="Career goals"
        className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      />
      {authError && <p className="text-rose-400 text-sm">{authError}</p>}
      <button
        type="submit"
        disabled={authLoading}
        className="w-full py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 rounded-xl font-semibold disabled:opacity-50"
      >
        {authLoading ? 'Please wait...' : 'Register'}
      </button>
    </form>
  );
}

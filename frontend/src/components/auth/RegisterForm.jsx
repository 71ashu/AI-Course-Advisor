import { FileText } from 'lucide-react';

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

      <div className="border border-slate-600/50 rounded-xl p-4 space-y-2">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-violet-400" />
          <h3 className="text-sm font-semibold text-slate-200">Academic transcript (optional)</h3>
        </div>
        <p className="text-xs text-slate-500">
          Upload a PDF of your transcript and we'll pull in your completed courses and
          grades so your profile starts off reflecting your real progress.
        </p>
        <input
          type="file"
          name="transcript"
          accept="application/pdf"
          className="w-full text-sm text-slate-300 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-violet-500/20 file:text-violet-300 file:font-medium file:cursor-pointer hover:file:bg-violet-500/30 cursor-pointer"
        />
      </div>

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

import { useState } from 'react';
import { Plus, X } from 'lucide-react';

const GRADE_POINTS = {
  'A+': 4.0, 'A': 4.0, 'A-': 3.7,
  'B+': 3.3, 'B': 3.0, 'B-': 2.7,
  'C+': 2.3, 'C': 2.0, 'C-': 1.7,
  'D+': 1.3, 'D': 1.0, 'D-': 0.7,
  'F': 0.0,
};

const GRADE_OPTIONS = Object.keys(GRADE_POINTS);

export default function RegisterForm({
  onSubmit,
  authError,
  authLoading,
  universities,
  programs,
  courses = [],
  selectedUniversity,
  setSelectedUniversity
}) {
  const [transcriptRows, setTranscriptRows] = useState([]);

  const addTranscriptRow = () => {
    setTranscriptRows((prev) => [...prev, { courseId: '', grade: '' }]);
  };

  const updateTranscriptRow = (index, field, value) => {
    setTranscriptRows((prev) =>
      prev.map((row, i) => (i === index ? { ...row, [field]: value } : row))
    );
  };

  const removeTranscriptRow = (index) => {
    setTranscriptRows((prev) => prev.filter((_, i) => i !== index));
  };

  const transcriptPayload = transcriptRows
    .filter((row) => row.courseId && row.grade)
    .map((row) => ({
      courseId: row.courseId,
      finalLetter: row.grade,
      courseGPA: GRADE_POINTS[row.grade],
    }));

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <input type="hidden" name="transcript" value={JSON.stringify(transcriptPayload)} readOnly />
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

      <div className="border border-slate-600/50 rounded-xl p-4 space-y-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Academic transcript (optional)</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Add courses you've already completed and the grades you earned, so your profile
            starts off reflecting your real progress.
          </p>
        </div>

        {transcriptRows.map((row, index) => (
          <div key={index} className="flex gap-2 items-center">
            <select
              value={row.courseId}
              onChange={(e) => updateTranscriptRow(index, 'courseId', e.target.value)}
              className="flex-1 bg-slate-700/50 border border-slate-600/50 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            >
              <option value="" disabled>
                Select course
              </option>
              {courses.map((course) => (
                <option key={course.course_number} value={course.course_number}>
                  {course.course_number} - {course.course_name}
                </option>
              ))}
            </select>
            <select
              value={row.grade}
              onChange={(e) => updateTranscriptRow(index, 'grade', e.target.value)}
              className="w-24 bg-slate-700/50 border border-slate-600/50 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            >
              <option value="" disabled>
                Grade
              </option>
              {GRADE_OPTIONS.map((grade) => (
                <option key={grade} value={grade}>
                  {grade}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => removeTranscriptRow(index)}
              className="p-2 text-slate-400 hover:text-rose-400 transition-colors"
              aria-label="Remove course"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}

        <button
          type="button"
          onClick={addTranscriptRow}
          className="flex items-center gap-1.5 text-sm text-violet-400 hover:text-violet-300 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add completed course
        </button>
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

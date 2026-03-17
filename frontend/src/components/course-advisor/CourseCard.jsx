import { BookOpen, Check, X, Sparkles } from 'lucide-react';
import DifficultyBadge from './DifficultyBadge';

export default function CourseCard({ course }) {
  const courseName = course.name || course.course_name || 'Unnamed Course';
  const courseId = course.id || course.course_number || 'N/A';
  const courseCredits = course.credits ?? course.units ?? 0;
  const courseDifficulty = course.difficulty || course.level || 'intermediate';

  return (
    <div className="group relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-xl p-5 hover:border-violet-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-violet-500/10 hover:-translate-y-1">
      <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/5 rounded-full blur-3xl group-hover:bg-violet-500/10 transition-all duration-500" />

      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-xl font-bold text-white mb-1">{courseName}</h3>
            <p className="text-sm text-violet-400 font-mono">{courseId}</p>
          </div>
          <DifficultyBadge level={courseDifficulty} />
        </div>

        <p className="text-slate-300 text-sm mb-4 leading-relaxed">{course.description}</p>

        <div className="flex items-center gap-2 mb-4 text-sm">
          <div className="flex items-center gap-1 text-slate-400">
            <BookOpen className="w-4 h-4" />
            <span>{courseCredits} credits</span>
          </div>
          {course.eligible !== undefined && (
            <div className={`flex items-center gap-1 ${course.eligible ? 'text-emerald-400' : 'text-rose-400'}`}>
              {course.eligible ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
              <span>{course.eligible ? 'Eligible' : 'Prerequisites needed'}</span>
            </div>
          )}
        </div>

        {course.matchReason && (
          <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg p-3 mb-3">
            <div className="flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-violet-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-violet-200">{course.matchReason}</p>
            </div>
          </div>
        )}

        {course.prerequisites && course.prerequisites.length > 0 && (
          <div className="text-xs text-slate-500">
            Prerequisites: {course.prerequisites.join(', ')}
          </div>
        )}
      </div>
    </div>
  );
}

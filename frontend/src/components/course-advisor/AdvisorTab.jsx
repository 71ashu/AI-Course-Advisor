import { Brain, User } from 'lucide-react';
import CourseCard from './CourseCard';

export default function AdvisorTab({
  chatHistory,
  isLoading,
  query,
  setQuery,
  handleKeyPress,
  handleAskAdvisor,
}) {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 min-h-[400px] max-h-[500px] overflow-y-auto">
        {chatHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 rounded-full flex items-center justify-center mb-6">
              <Brain className="w-10 h-10 text-violet-400" />
            </div>
            <h3 className="text-2xl font-bold mb-2">Ask me anything!</h3>
            <p className="text-slate-400 max-w-md">
              I can help you plan your courses, check prerequisites, explore career paths, and optimize your academic journey.
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              <button
                onClick={() => setQuery('What courses should I take next semester?')}
                className="px-4 py-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-sm border border-slate-600/50 transition-colors"
              >
                Next semester courses?
              </button>
              <button
                onClick={() => setQuery('What are the best ML courses for me?')}
                className="px-4 py-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-sm border border-slate-600/50 transition-colors"
              >
                ML course recommendations
              </button>
              <button
                onClick={() => setQuery('Am I on track to graduate on time?')}
                className="px-4 py-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-sm border border-slate-600/50 transition-colors"
              >
                Graduation timeline?
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {chatHistory.map((message, idx) => (
              <div
                key={idx}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center flex-shrink-0">
                    <Brain className="w-5 h-5" />
                  </div>
                )}
                <div className="max-w-2xl space-y-3">
                  <div
                    className={`px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-violet-500 text-white'
                        : 'bg-slate-700/50 text-slate-200'
                    }`}
                  >
                    {message.content}
                  </div>
                  {message.role === 'assistant' && message.recommendations?.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-semibold text-violet-300 px-1">Recommended Courses</div>
                      <div className="grid gap-3 md:grid-cols-2">
                        {message.recommendations.map((course) => (
                          <CourseCard key={`${idx}-${course.id || course.course_number}`} course={course} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
                  <Brain className="w-5 h-5" />
                </div>
                <div className="bg-slate-700/50 px-4 py-3 rounded-2xl">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about courses, prerequisites, career paths..."
            className="flex-1 bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={handleAskAdvisor}
            disabled={isLoading || !query.trim()}
            className="px-6 py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-violet-500/30"
          >
            {isLoading ? 'Thinking...' : 'Ask'}
          </button>
        </div>
      </div>
    </div>
  );
}

import { useEffect, useRef, useState } from 'react';
import { ArrowUp, Plus } from 'lucide-react';
import CourseCard from './CourseCard';

const SUGGESTIONS = [
  'What courses should I take next semester?',
  'What are the best ML courses for me?',
  'Am I on track to graduate on time?',
];

function AssistantBody({ content }) {
  const blocks = String(content || '').trim().split(/\n{2,}/);

  return (
    <div className="space-y-4 text-[15px] leading-7 text-slate-200">
      {blocks.map((block, i) => {
        const lines = block.split('\n').map((line) => line.trim()).filter(Boolean);
        const listLines = lines.filter((line) => /^[-•*]\s+/.test(line) || /^\d+[.)]\s+/.test(line));
        if (listLines.length >= 2 && listLines.length === lines.length) {
          return (
            <ul key={i} className="list-disc space-y-1.5 pl-5 marker:text-slate-500">
              {lines.map((line, j) => (
                <li key={j}>{line.replace(/^[-•*]\s+/, '').replace(/^\d+[.)]\s+/, '')}</li>
              ))}
            </ul>
          );
        }
        return (
          <p key={i} className="whitespace-pre-wrap">
            {block}
          </p>
        );
      })}
    </div>
  );
}

function RecommendationCard({ courses }) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? courses : courses.slice(0, 1);

  return (
    <div className="rounded-2xl bg-slate-800/70 border border-slate-700/50 overflow-hidden">
      <div className="p-4 space-y-3">
        {visible.map((course) => (
          <CourseCard key={course.id || course.course_number} course={course} />
        ))}
      </div>
      {courses.length > 1 && (
        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="w-full px-4 py-2.5 text-sm text-slate-400 hover:text-slate-200 border-t border-slate-700/50 transition-colors"
        >
          {expanded ? 'Show less' : `Show more (${courses.length - 1} more)`}
        </button>
      )}
    </div>
  );
}

export default function AdvisorTab({
  chatHistory,
  isLoading,
  query,
  setQuery,
  handleKeyPress,
  handleAskAdvisor,
}) {
  const endRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [chatHistory, isLoading]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [query]);

  const empty = chatHistory.length === 0 && !isLoading;

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[720px] mx-auto px-4 sm:px-6 pt-16 lg:pt-10 pb-8">
          {empty ? (
            <div className="min-h-[calc(100vh-220px)] flex flex-col items-center justify-center text-center">
              <h2 className="text-2xl font-semibold text-white tracking-tight">Ask the advisor</h2>
              <p className="mt-2 text-slate-400 max-w-md text-[15px] leading-relaxed">
                Plan your courses, check prerequisites, explore career paths, and stay on track to graduate.
              </p>
              <div className="mt-8 flex flex-wrap gap-2 justify-center">
                {SUGGESTIONS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => setQuery(prompt)}
                    className="px-3.5 py-2 rounded-xl text-sm text-slate-300 bg-slate-800/60 border border-slate-700/70 hover:border-slate-500 hover:text-white transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              {chatHistory.map((message, idx) => (
                <div key={idx} className="space-y-4">
                  {message.role === 'user' ? (
                    <div className="rounded-2xl border border-slate-600/70 bg-slate-900/40 px-4 py-3 text-[15px] leading-7 text-slate-100 whitespace-pre-wrap">
                      {message.content}
                    </div>
                  ) : (
                    <>
                      <AssistantBody content={message.content} />
                      {message.recommendations?.length > 0 && (
                        <RecommendationCard courses={message.recommendations} />
                      )}
                    </>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center gap-1.5 py-1" aria-label="Advisor is thinking">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:120ms]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:240ms]" />
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}
        </div>
      </div>

      <div className="shrink-0 px-4 sm:px-6 pb-4 lg:pb-6">
        <div className="max-w-[720px] mx-auto">
          <div className="rounded-2xl border border-slate-600/60 bg-slate-900/80 shadow-2xl shadow-black/30 focus-within:border-slate-500 transition-colors">
            <textarea
              ref={textareaRef}
              rows={1}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Write a message..."
              className="w-full resize-none bg-transparent px-4 pt-3.5 pb-2 text-[15px] leading-6 text-white placeholder-slate-500 focus:outline-none"
              disabled={isLoading}
            />
            <div className="flex items-center justify-between px-2.5 pb-2.5">
              <button
                type="button"
                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors"
                aria-label="Add context"
                disabled
              >
                <Plus className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={handleAskAdvisor}
                disabled={isLoading || !query.trim()}
                className="w-8 h-8 rounded-lg bg-white text-slate-900 flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-200 transition-colors"
                aria-label="Send message"
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            </div>
          </div>
          <p className="mt-2.5 text-center text-xs text-slate-500">
            The advisor can make mistakes. Double-check course requirements with your department.
          </p>
        </div>
      </div>
    </div>
  );
}

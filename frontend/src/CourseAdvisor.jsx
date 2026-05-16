import React, { useState, useEffect } from 'react';
import { TrendingUp, MessageSquare, User, LogOut } from 'lucide-react';
import { api } from './api';
import AdvisorTab from './components/course-advisor/AdvisorTab';
import ProfilePanel from './components/course-advisor/ProfilePanel';
import ProgressPanel from './components/course-advisor/ProgressPanel';
import OnboardingQuiz from './components/course-advisor/OnboardingQuiz';

export default function CourseAdvisor({ student, onLogout }) {
  const [studentProfile, setStudentProfile] = useState(student);
  const [activeTab, setActiveTab] = useState('advisor');
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [degreeProgress, setDegreeProgress] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [progressCoursesTab, setProgressCoursesTab] = useState('current');

  const isColdStart = !studentProfile?.onboardingCompleted
    && (studentProfile?.completedCourses?.length || 0) === 0
    && (studentProfile?.interests?.length || 0) === 0;

  useEffect(() => {
    setStudentProfile(student);
  }, [student]);

  useEffect(() => {
    loadDegreeProgress();
  }, [studentProfile?.id]);

  const loadDegreeProgress = async () => {
    try {
      const progress = await api.getProgress();
      setDegreeProgress(progress);
    } catch {
      setDegreeProgress(null);
    }
  };

  const handleOnboardingComplete = async (answers) => {
    setIsLoading(true);
    try {
      const { student: updated } = await api.submitOnboarding(answers);
      setStudentProfile(updated);
    } catch (err) {
      console.error('Onboarding failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskAdvisor = async () => {
    if (!query.trim()) return;

    const userMessage = { role: 'user', content: query };
    setChatHistory((prev) => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const { recommendations: recs, message } = await api.getRecommendations(query);

      const aiMessage = {
        role: 'assistant',
        content: message,
        recommendations: recs
      };

      setChatHistory((prev) => [...prev, aiMessage]);
    } catch {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setChatHistory((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAskAdvisor();
    }
  };

  if (isColdStart) {
    return (
      <div className="min-h-screen bg-app-shell text-white font-sans">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-20 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-fuchsia-600/10 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
          <header className="mb-12 text-center">
            <h1 className="text-5xl font-black mb-2 bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent">
              AI Course Advisor
            </h1>
            <p className="text-slate-400 text-lg">Welcome, {studentProfile?.name}!</p>
          </header>
          <OnboardingQuiz onComplete={handleOnboardingComplete} isLoading={isLoading} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-app-shell text-white font-sans">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-fuchsia-600/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        <header className="mb-12">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-5xl font-black mb-2 bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent">
                AI Course Advisor
              </h1>
              <p className="text-slate-400 text-lg">Your intelligent academic planning companion</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowProfile(!showProfile)}
                className="flex items-center gap-2 px-4 py-2 bg-violet-500/20 hover:bg-violet-500/30 border border-violet-500/50 rounded-lg transition-colors"
              >
                <User className="w-4 h-4" />
                <span>Profile</span>
              </button>
              <button
                onClick={onLogout}
                className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </header>

        {showProfile && (
          <div className="mb-8">
            <ProfilePanel studentProfile={studentProfile} />
          </div>
        )}

        <div className="flex gap-2 mb-8 bg-slate-800/50 p-1.5 rounded-xl border border-slate-700/50 w-fit">
          <button
            onClick={() => setActiveTab('advisor')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
              activeTab === 'advisor'
                ? 'bg-violet-500 text-white shadow-lg shadow-violet-500/50'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <MessageSquare className="w-4 h-4 inline mr-2" />
            Ask Advisor
          </button>
          <button
            onClick={() => setActiveTab('progress')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
              activeTab === 'progress'
                ? 'bg-violet-500 text-white shadow-lg shadow-violet-500/50'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <TrendingUp className="w-4 h-4 inline mr-2" />
            Progress
          </button>
        </div>

        {activeTab === 'advisor' && (
          <AdvisorTab
            chatHistory={chatHistory}
            isLoading={isLoading}
            query={query}
            setQuery={setQuery}
            handleKeyPress={handleKeyPress}
            handleAskAdvisor={handleAskAdvisor}
          />
        )}

        {activeTab === 'progress' && (
          <div>
            <ProgressPanel
              degreeProgress={degreeProgress}
              progressCoursesTab={progressCoursesTab}
              setProgressCoursesTab={setProgressCoursesTab}
            />
          </div>
        )}
      </div>
    </div>
  );
}

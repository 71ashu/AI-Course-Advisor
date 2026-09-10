import React, { useState, useEffect } from 'react';
import { api } from './api';
import AdvisorTab from './components/course-advisor/AdvisorTab';
import AppSidebar from './components/course-advisor/AppSidebar';
import DashboardPanel from './components/course-advisor/DashboardPanel';
import ProfilePanel from './components/course-advisor/ProfilePanel';
import ProgressPanel from './components/course-advisor/ProgressPanel';
import OnboardingQuiz from './components/course-advisor/OnboardingQuiz';

export default function CourseAdvisor({ student, onLogout }) {
  const [studentProfile, setStudentProfile] = useState(student);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [conversationLoading, setConversationLoading] = useState(false);
  const [degreeProgress, setDegreeProgress] = useState(null);
  const [progressCoursesTab, setProgressCoursesTab] = useState('current');
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const isColdStart = !studentProfile?.onboardingCompleted
    && (studentProfile?.completedCourses?.length || 0) === 0
    && (studentProfile?.interests?.length || 0) === 0;

  useEffect(() => {
    setStudentProfile(student);
  }, [student]);

  useEffect(() => {
    loadDegreeProgress();
    loadConversations();
  }, [studentProfile?.id]);

  const loadDegreeProgress = async () => {
    try {
      const progress = await api.getProgress();
      setDegreeProgress(progress);
    } catch {
      setDegreeProgress(null);
    }
  };

  const loadConversations = async () => {
    try {
      const { conversations: rows } = await api.listConversations();
      setConversations(rows || []);
    } catch {
      setConversations([]);
    }
  };

  const handleSelectConversation = async (id) => {
    if (id === activeConversationId) {
      setActiveTab('advisor');
      setMobileNavOpen(false);
      return;
    }
    setActiveTab('advisor');
    setMobileNavOpen(false);
    setConversationLoading(true);
    try {
      const { conversation } = await api.getConversation(id);
      setChatHistory(
        (conversation.messages || []).map(({ role, content, recommendations }) => ({
          role,
          content,
          recommendations: recommendations || [],
        })),
      );
      setActiveConversationId(conversation.id);
    } catch {
      setChatHistory([]);
    } finally {
      setConversationLoading(false);
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setChatHistory([]);
    setQuery('');
    setActiveTab('advisor');
    setMobileNavOpen(false);
  };

  const handleRenameConversation = async (id, title) => {
    const clean = (title || '').trim();
    if (!clean) return;
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, title: clean } : c)),
    );
    try {
      await api.renameConversation(id, clean);
    } catch {
      loadConversations();
    }
  };

  const handleDeleteConversation = async (id) => {
    try {
      await api.deleteConversation(id);
    } catch {
      // ignore; refresh below reflects real state
    }
    if (id === activeConversationId) {
      setActiveConversationId(null);
      setChatHistory([]);
    }
    loadConversations();
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
    const priorTurns = chatHistory
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map(({ role, content }) => ({ role, content }));
    setChatHistory((prev) => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const { recommendations: recs, message, conversationId } = await api.getRecommendations(query, {
        conversationId: activeConversationId,
        history: priorTurns,
      });

      const aiMessage = {
        role: 'assistant',
        content: message,
        recommendations: recs
      };

      setChatHistory((prev) => [...prev, aiMessage]);
      if (conversationId && conversationId !== activeConversationId) {
        setActiveConversationId(conversationId);
      }
      loadConversations();
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

  const goToAdvisorWithPrompt = (prompt) => {
    setQuery(prompt);
    setActiveTab('advisor');
    setMobileNavOpen(false);
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
    <div className="min-h-screen bg-app-shell text-white font-sans flex">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-fuchsia-600/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <AppSidebar
        studentProfile={studentProfile}
        degreeProgress={degreeProgress}
        activeTab={activeTab}
        onNavigate={setActiveTab}
        onLogout={onLogout}
        mobileOpen={mobileNavOpen}
        onCloseMobile={() => setMobileNavOpen(false)}
        onOpenMobile={() => setMobileNavOpen(true)}
      />

      <main
        className={`relative z-10 flex-1 min-h-screen min-w-0 ${
          activeTab === 'advisor' ? 'flex flex-col overflow-hidden h-screen' : 'overflow-y-auto'
        }`}
      >
        {activeTab === 'advisor' ? (
          <AdvisorTab
            chatHistory={chatHistory}
            isLoading={isLoading}
            query={query}
            setQuery={setQuery}
            handleKeyPress={handleKeyPress}
            handleAskAdvisor={handleAskAdvisor}
            conversations={conversations}
            activeConversationId={activeConversationId}
            activeConversation={conversations.find((c) => c.id === activeConversationId) || null}
            conversationLoading={conversationLoading}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            onDeleteConversation={handleDeleteConversation}
            onRenameConversation={handleRenameConversation}
          />
        ) : (
          <div className="max-w-6xl mx-auto px-6 pt-16 pb-10 lg:px-10 lg:pt-10">
            {activeTab === 'dashboard' && (
              <DashboardPanel
                studentProfile={studentProfile}
                degreeProgress={degreeProgress}
                onAskAdvisor={() => goToAdvisorWithPrompt('What courses should I take next semester?')}
              />
            )}

            {activeTab === 'progress' && (
              <ProgressPanel
                degreeProgress={degreeProgress}
                progressCoursesTab={progressCoursesTab}
                setProgressCoursesTab={setProgressCoursesTab}
              />
            )}

            {activeTab === 'profile' && (
              <ProfilePanel studentProfile={studentProfile} />
            )}
          </div>
        )}
      </main>
    </div>
  );
}

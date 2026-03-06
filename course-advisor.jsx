import React, { useState, useEffect } from 'react';
import { BookOpen, GraduationCap, TrendingUp, Calendar, Check, X, MessageSquare, Sparkles, User, Target, Brain } from 'lucide-react';

// Mock API client (replace with actual backend calls in production)
const mockAPI = {
  async getRecommendations(studentProfile, query) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const completed = new Set(studentProfile.completedCourses);
    const interests = studentProfile.interests;
    
    // Recommend based on profile
    const recommendations = [
      {
        id: "CS301",
        name: "Machine Learning",
        credits: 3,
        difficulty: "advanced",
        description: "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks.",
        matchReason: "Aligns with your AI interest and builds on your data structures knowledge",
        prerequisites: ["CS201", "MATH200"],
        eligible: completed.has("CS201") && completed.has("MATH200")
      },
      {
        id: "CS350",
        name: "Web Development",
        credits: 3,
        difficulty: "intermediate",
        description: "Full-stack web development including HTML, CSS, JavaScript, and modern frameworks.",
        matchReason: "Great for building practical projects and complements your programming skills",
        prerequisites: ["CS101"],
        eligible: completed.has("CS101")
      },
      {
        id: "CS250",
        name: "Database Systems",
        credits: 3,
        difficulty: "intermediate",
        description: "Database design, SQL, normalization, and transaction management.",
        matchReason: "Essential for backend development and data management",
        prerequisites: ["CS201"],
        eligible: completed.has("CS201")
      }
    ];
    
    return recommendations;
  },
  
  async getDegreeProgress(studentProfile) {
    await new Promise(resolve => setTimeout(resolve, 500));
    const totalCredits = studentProfile.completedCourses.length * 3 + studentProfile.currentCourses.length * 3;
    return {
      totalCredits,
      requiredCredits: 120,
      progressPercentage: Math.min((totalCredits / 120) * 100, 100),
      majorCredits: Math.floor(totalCredits * 0.6),
      completedCoursesCount: studentProfile.completedCourses.length
    };
  }
};

export default function CourseAdvisor() {
  const [studentProfile, setStudentProfile] = useState({
    name: "Alex Johnson",
    major: "Computer Science",
    year: "Junior",
    completedCourses: ["CS101", "CS201", "MATH100", "MATH200", "ENG101"],
    currentCourses: ["PHY101"],
    interests: ["AI", "Web Development", "Machine Learning"],
    careerGoals: "Software Engineer at a tech company"
  });
  
  const [activeTab, setActiveTab] = useState('advisor');
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [degreeProgress, setDegreeProgress] = useState(null);
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    loadDegreeProgress();
  }, []);

  const loadDegreeProgress = async () => {
    const progress = await mockAPI.getDegreeProgress(studentProfile);
    setDegreeProgress(progress);
  };

  const handleAskAdvisor = async () => {
    if (!query.trim()) return;
    
    const userMessage = { role: 'user', content: query };
    setChatHistory(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const recs = await mockAPI.getRecommendations(studentProfile, query);
      setRecommendations(recs);
      
      const aiMessage = {
        role: 'assistant',
        content: `Based on your profile as a ${studentProfile.year} majoring in ${studentProfile.major}, I've found ${recs.length} courses that align perfectly with your goals. Check out the recommendations below!`,
        recommendations: recs
      };
      
      setChatHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setChatHistory(prev => [...prev, errorMessage]);
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

  const DifficultyBadge = ({ level }) => {
    const colors = {
      beginner: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      intermediate: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      advanced: 'bg-rose-500/20 text-rose-300 border-rose-500/30'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${colors[level]}`}>
        {level}
      </span>
    );
  };

  const CourseCard = ({ course }) => (
    <div className="group relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-xl p-5 hover:border-violet-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-violet-500/10 hover:-translate-y-1">
      <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/5 rounded-full blur-3xl group-hover:bg-violet-500/10 transition-all duration-500" />
      
      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-xl font-bold text-white mb-1">{course.name}</h3>
            <p className="text-sm text-violet-400 font-mono">{course.id}</p>
          </div>
          <DifficultyBadge level={course.difficulty} />
        </div>
        
        <p className="text-slate-300 text-sm mb-4 leading-relaxed">{course.description}</p>
        
        <div className="flex items-center gap-2 mb-4 text-sm">
          <div className="flex items-center gap-1 text-slate-400">
            <BookOpen className="w-4 h-4" />
            <span>{course.credits} credits</span>
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

  const ProfilePanel = () => (
    <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-2xl font-bold text-white">
          {studentProfile.name.split(' ').map(n => n[0]).join('')}
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">{studentProfile.name}</h2>
          <p className="text-slate-400">{studentProfile.year} • {studentProfile.major}</p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-violet-400" />
            <h3 className="text-sm font-semibold text-slate-300">Career Goals</h3>
          </div>
          <p className="text-slate-400 text-sm">{studentProfile.careerGoals}</p>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <Brain className="w-4 h-4 text-violet-400" />
            <h3 className="text-sm font-semibold text-slate-300">Interests</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {studentProfile.interests.map((interest, idx) => (
              <span key={idx} className="px-3 py-1 bg-violet-500/20 border border-violet-500/30 rounded-full text-xs text-violet-300">
                {interest}
              </span>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <Check className="w-4 h-4 text-violet-400" />
            <h3 className="text-sm font-semibold text-slate-300">Completed Courses</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {studentProfile.completedCourses.map((course, idx) => (
              <span key={idx} className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded text-xs text-emerald-300 font-mono">
                {course}
              </span>
            ))}
          </div>
        </div>

        {studentProfile.currentCourses.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-violet-400" />
              <h3 className="text-sm font-semibold text-slate-300">Current Courses</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {studentProfile.currentCourses.map((course, idx) => (
                <span key={idx} className="px-2 py-1 bg-amber-500/10 border border-amber-500/20 rounded text-xs text-amber-300 font-mono">
                  {course}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const ProgressPanel = () => {
    if (!degreeProgress) return null;
    
    const progressWidth = `${degreeProgress.progressPercentage}%`;
    
    return (
      <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <GraduationCap className="w-6 h-6 text-violet-400" />
          <h2 className="text-2xl font-bold text-white">Degree Progress</h2>
        </div>

        <div className="mb-6">
          <div className="flex justify-between items-baseline mb-2">
            <span className="text-sm text-slate-400">Overall Progress</span>
            <span className="text-2xl font-bold text-white">{degreeProgress.progressPercentage.toFixed(1)}%</span>
          </div>
          <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full transition-all duration-1000 ease-out"
              style={{ width: progressWidth }}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
            <div className="text-3xl font-bold text-white mb-1">{degreeProgress.totalCredits}</div>
            <div className="text-sm text-slate-400">Credits Earned</div>
          </div>
          <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
            <div className="text-3xl font-bold text-white mb-1">{degreeProgress.requiredCredits - degreeProgress.totalCredits}</div>
            <div className="text-sm text-slate-400">Credits Remaining</div>
          </div>
          <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
            <div className="text-3xl font-bold text-white mb-1">{degreeProgress.majorCredits}</div>
            <div className="text-sm text-slate-400">Major Credits</div>
          </div>
          <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
            <div className="text-3xl font-bold text-white mb-1">{degreeProgress.completedCoursesCount}</div>
            <div className="text-sm text-slate-400">Courses Completed</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 text-white font-sans">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-fuchsia-600/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <header className="mb-12">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-5xl font-black mb-2 bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent">
                AI Course Advisor
              </h1>
              <p className="text-slate-400 text-lg">Your intelligent academic planning companion</p>
            </div>
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-2 px-4 py-2 bg-violet-500/20 hover:bg-violet-500/30 border border-violet-500/50 rounded-lg transition-colors"
            >
              <User className="w-4 h-4" />
              <span>Profile</span>
            </button>
          </div>
        </header>

        {/* Profile Sidebar */}
        {showProfile && (
          <div className="mb-8">
            <ProfilePanel />
          </div>
        )}

        {/* Tab Navigation */}
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

        {/* Content Area */}
        {activeTab === 'advisor' && (
          <div className="space-y-6">
            {/* Chat Interface */}
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
                      onClick={() => setQuery("What courses should I take next semester?")}
                      className="px-4 py-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-sm border border-slate-600/50 transition-colors"
                    >
                      Next semester courses?
                    </button>
                    <button
                      onClick={() => setQuery("What are the best ML courses for me?")}
                      className="px-4 py-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-sm border border-slate-600/50 transition-colors"
                    >
                      ML course recommendations
                    </button>
                    <button
                      onClick={() => setQuery("Am I on track to graduate on time?")}
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
                      <div
                        className={`max-w-2xl px-4 py-3 rounded-2xl ${
                          message.role === 'user'
                            ? 'bg-violet-500 text-white'
                            : 'bg-slate-700/50 text-slate-200'
                        }`}
                      >
                        {message.content}
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

            {/* Input Area */}
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

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <Sparkles className="w-6 h-6 text-violet-400" />
                  Recommended Courses
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {recommendations.map((course) => (
                    <CourseCard key={course.id} course={course} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'progress' && (
          <div>
            <ProgressPanel />
          </div>
        )}
      </div>
    </div>
  );
}

import { useState } from 'react';
import { Sparkles, ArrowRight, ArrowLeft, Check } from 'lucide-react';

const INTEREST_OPTIONS = [
  { id: 'AI', label: 'Artificial Intelligence' },
  { id: 'Machine Learning', label: 'Machine Learning' },
  { id: 'Web Development', label: 'Web Development' },
  { id: 'Data Science', label: 'Data Science' },
  { id: 'Databases', label: 'Databases & Data Management' },
  { id: 'Mathematics', label: 'Mathematics & Theory' },
  { id: 'Systems', label: 'Systems & Networking' },
  { id: 'Security', label: 'Cybersecurity' },
];

const EXPERIENCE_OPTIONS = [
  { id: 'beginner', label: 'Beginner', desc: 'New to programming' },
  { id: 'intermediate', label: 'Intermediate', desc: 'Comfortable with basics' },
  { id: 'advanced', label: 'Advanced', desc: 'Experienced developer' },
];

const CAREER_OPTIONS = [
  { id: 'Software Engineer', label: 'Software Engineer' },
  { id: 'ML Engineer', label: 'ML / AI Engineer' },
  { id: 'Data Scientist', label: 'Data Scientist' },
  { id: 'Full-Stack Developer', label: 'Full-Stack Developer' },
  { id: 'Backend Engineer', label: 'Backend Engineer' },
  { id: 'Data Engineer', label: 'Data Engineer' },
  { id: 'Research Scientist', label: 'Research Scientist' },
  { id: 'other', label: 'Other / Not Sure' },
];

const LOAD_OPTIONS = [
  { id: 'light', label: '2-3 courses', desc: 'Light workload' },
  { id: 'normal', label: '4-5 courses', desc: 'Standard workload' },
  { id: 'heavy', label: '5+ courses', desc: 'Heavy workload' },
];

export default function OnboardingQuiz({ onComplete, isLoading }) {
  const [step, setStep] = useState(0);
  const [interests, setInterests] = useState([]);
  const [experience, setExperience] = useState('');
  const [career, setCareer] = useState('');
  const [courseLoad, setCourseLoad] = useState('');

  const toggleInterest = (id) => {
    setInterests((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleSubmit = () => {
    onComplete({
      interests,
      experienceLevel: experience,
      careerGoals: career === 'other' ? '' : career,
      targetJobTitle: career === 'other' ? '' : career,
      courseLoad,
    });
  };

  const canAdvance = () => {
    if (step === 0) return interests.length > 0;
    if (step === 1) return !!experience;
    if (step === 2) return !!career;
    if (step === 3) return !!courseLoad;
    return true;
  };

  const steps = [
    {
      title: 'What areas interest you most?',
      subtitle: 'Select all that apply',
      content: (
        <div className="grid grid-cols-2 gap-3">
          {INTEREST_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => toggleInterest(opt.id)}
              className={`p-3 rounded-xl border text-sm font-medium transition-all duration-200 text-left ${
                interests.includes(opt.id)
                  ? 'bg-violet-500/20 border-violet-500/50 text-violet-200'
                  : 'bg-slate-800/50 border-slate-700/50 text-slate-300 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center gap-2">
                {interests.includes(opt.id) && <Check className="w-4 h-4 text-violet-400" />}
                <span>{opt.label}</span>
              </div>
            </button>
          ))}
        </div>
      ),
    },
    {
      title: "What's your programming experience?",
      subtitle: 'This helps us calibrate difficulty',
      content: (
        <div className="space-y-3">
          {EXPERIENCE_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => setExperience(opt.id)}
              className={`w-full p-4 rounded-xl border text-left transition-all duration-200 ${
                experience === opt.id
                  ? 'bg-violet-500/20 border-violet-500/50'
                  : 'bg-slate-800/50 border-slate-700/50 hover:border-slate-600'
              }`}
            >
              <div className="font-medium text-white">{opt.label}</div>
              <div className="text-sm text-slate-400 mt-1">{opt.desc}</div>
            </button>
          ))}
        </div>
      ),
    },
    {
      title: 'What career path are you considering?',
      subtitle: "We'll align courses with job market skills",
      content: (
        <div className="grid grid-cols-2 gap-3">
          {CAREER_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => setCareer(opt.id)}
              className={`p-3 rounded-xl border text-sm font-medium transition-all duration-200 text-left ${
                career === opt.id
                  ? 'bg-amber-500/20 border-amber-500/50 text-amber-200'
                  : 'bg-slate-800/50 border-slate-700/50 text-slate-300 hover:border-slate-600'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      ),
    },
    {
      title: 'How many courses per semester?',
      subtitle: 'Helps us pace our recommendations',
      content: (
        <div className="space-y-3">
          {LOAD_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => setCourseLoad(opt.id)}
              className={`w-full p-4 rounded-xl border text-left transition-all duration-200 ${
                courseLoad === opt.id
                  ? 'bg-violet-500/20 border-violet-500/50'
                  : 'bg-slate-800/50 border-slate-700/50 hover:border-slate-600'
              }`}
            >
              <div className="font-medium text-white">{opt.label}</div>
              <div className="text-sm text-slate-400 mt-1">{opt.desc}</div>
            </button>
          ))}
        </div>
      ),
    },
  ];

  const currentStep = steps[step];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-8 h-8 text-violet-400" />
          </div>
          <h2 className="text-2xl font-bold mb-1">Let's personalize your experience</h2>
          <p className="text-slate-400">Answer a few questions so we can give you great recommendations right away</p>
        </div>

        <div className="flex gap-1.5 mb-8">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`flex-1 h-1.5 rounded-full transition-colors duration-300 ${
                i <= step ? 'bg-violet-500' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-1">{currentStep.title}</h3>
          <p className="text-sm text-slate-400 mb-4">{currentStep.subtitle}</p>
          {currentStep.content}
        </div>

        <div className="flex justify-between">
          <button
            onClick={() => setStep(Math.max(0, step - 1))}
            disabled={step === 0}
            className="flex items-center gap-2 px-4 py-2 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          {step < steps.length - 1 ? (
            <button
              onClick={() => setStep(step + 1)}
              disabled={!canAdvance()}
              className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Next
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!canAdvance() || isLoading}
              className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isLoading ? 'Saving...' : 'Get Started'}
              <Check className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

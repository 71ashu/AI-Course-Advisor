"""Seed real SCU non-CSEN electives (EMGT, ENGR, plus two CSEN Engineering & Society
courses) and link them to the MS-CSEN program as eligible electives.

Sourced from Santa Clara University's Graduate Engineering Bulletin (Chapters 2, 6, 10, 13)
and the department's current EMGT course description sheet. Course numbering/titles were
cross-checked against multiple sources; where a course is cross-listed under more than one
department code (e.g. EMGT 269 is also ENGR 269), it is stored as a single row with the
other codes in `alt_codes` rather than duplicated.

Run directly: `python seed_engr_emgt.py` (idempotent - safe to re-run).
"""
from app import app
from models import db, Course, Program, ProgramCourse

MS_CSEN_ID = 'MS-CSEN'

# ---------------------------------------------------------------------------
# EMGT courses (Department of Engineering Management & Leadership).
# MS-CSEN accepts a maximum of 6 units of EMGT courses as electives.
# ---------------------------------------------------------------------------
EMGT_COURSES = [
    {"id": "EMGT 201", "name": "Applications of Reinforcement Learning in Operations", "units": 2,
     "description": "Sequential decision-making and reinforcement learning applied to supply chain, logistics, and transportation domains, including MDPs and implementation with OpenAI Gym.",
     "topics": ["reinforcement learning", "operations", "supply chain"]},
    {"id": "EMGT 202", "name": "Supply Chain Management for Engineering Managers", "units": 2,
     "description": "Supply chain design, planning, and optimization for engineering and technology companies, including logistics, inventory, procurement, and distribution.",
     "topics": ["supply chain", "operations", "management"]},
    {"id": "EMGT 224", "name": "Human Factors Engineering", "units": 4, "alt_codes": ["ENGR 124"],
     "description": "Cognitive systems, human information processing, workload/fatigue modeling, and applied ML/CV techniques for ergonomic and usability evaluation.",
     "topics": ["human factors", "ergonomics", "usability"]},
    {"id": "EMGT 249", "name": "Civil Systems Engineering", "units": 4, "alt_codes": ["CENG 149", "CENG 249"],
     "description": "Engineering systems analysis applied to civil engineering problems: transportation, assignment, critical path, linear/nonlinear programming, and queuing theory.",
     "topics": ["systems engineering", "civil engineering", "optimization"]},
    {"id": "EMGT 253", "name": "Operations and Production Systems", "units": 2,
     "description": "Operations strategy, process management, forecasting, capacity planning, TQM, Lean, Just-in-Time, and supply-chain/inventory management.",
     "topics": ["operations", "production", "quality"]},
    {"id": "EMGT 254", "name": "Usability Engineering", "units": 2,
     "description": "Principles and practices of usability engineering for designing and evaluating interfaces and AI-driven systems, including user research and iterative design.",
     "topics": ["usability", "human-computer interaction", "design"]},
    {"id": "EMGT 255", "name": "Managerial Accounting for Operating Managers", "units": 2,
     "description": "Underlying principles of managerial accounting and financial analysis from the perspective of an operating manager interpreting financial data.",
     "topics": ["accounting", "finance", "management"]},
    {"id": "EMGT 269", "name": "Human Resource Development and the Engineering Manager", "units": 2, "alt_codes": ["ENGR 269"],
     "description": "Human resource management concepts for tech companies, including staffing, performance management, and people development.",
     "topics": ["human resources", "leadership", "management"]},
    {"id": "EMGT 270", "name": "Effective Oral Technical Presentations", "units": 2, "alt_codes": ["ENGR 270"],
     "description": "The role of communication in the workplace: persuasive communication, organizing and leading meetings, and interviewing skills.",
     "topics": ["communication", "presentations", "professional development"]},
    {"id": "EMGT 271A", "name": "Effective Written Technical Communication I", "units": 2, "alt_codes": ["ENGR 271A"],
     "description": "Clustering, the pyramid technique, audience analysis, and proposal presentation methods for technical writing.",
     "topics": ["technical writing", "communication"]},
    {"id": "EMGT 271B", "name": "Effective Written Technical Communication II", "units": 2, "alt_codes": ["ENGR 271B"],
     "description": "Intensive writing practicum covering mechanics of style, editing techniques, and digital communications.",
     "topics": ["technical writing", "communication"]},
    {"id": "EMGT 277", "name": "Organizational Leadership and Change Management", "units": 2,
     "description": "Building high-performing teams, cultivating company culture, and leading organizations through reorganizations, AI adoption, and other transformations.",
     "topics": ["leadership", "organizational behavior", "change management"]},
    {"id": "EMGT 284", "name": "Product Management", "units": 2,
     "description": "Structured overview of product strategy and go-to-market principles across B2B, B2C, hardware, software, and service environments.",
     "topics": ["product management", "strategy"]},
    {"id": "EMGT 285", "name": "Managing Business Relationships", "units": 2, "alt_codes": ["ENGR 285"],
     "description": "Leadership skills for managing relationships at manager, director, and executive levels.",
     "topics": ["leadership", "management", "communication"]},
    {"id": "EMGT 287", "name": "Applications of Artificial Intelligence in Manufacturing Systems", "units": 4, "alt_codes": ["ENGR 187"],
     "description": "AI applied to the manufacturing ecosystem: predicting production rates, analyzing machinery performance, and preventive maintenance using ML and deep learning.",
     "topics": ["artificial intelligence", "manufacturing", "machine learning"]},
    {"id": "EMGT 288", "name": "Risk and Reliability Engineering", "units": 2, "alt_codes": ["ENGR 182"],
     "description": "Probabilistic risk assessment models for evaluating and quantifying engineering and management system risk, both analytically and via simulation.",
     "topics": ["risk management", "reliability engineering"]},
    {"id": "EMGT 289", "name": "Fundamentals of Statistical Quality Engineering", "units": 4, "alt_codes": ["ENGR 183"],
     "description": "Six-Sigma quality systems for design, production, and business processes, including statistical methods in quality control and continuous improvement.",
     "topics": ["quality engineering", "statistics", "six sigma"]},
    {"id": "EMGT 290", "name": "Cost Estimation", "units": 3, "alt_codes": ["CENG 185", "CENG 285"],
     "description": "Types of construction cost estimates, direct/indirect costs, cost budgeting and control, quantity takeoff, and detailed estimates of main building systems.",
     "topics": ["cost estimation", "construction management"]},
    {"id": "EMGT 291", "name": "Engineering Decision and Risk Analysis", "units": 4, "alt_codes": ["CENG 288"],
     "description": "Epistemic and aleatory uncertainty, probabilistic risk assessment, decision trees, sensitivity analysis, and reliability analysis methods.",
     "topics": ["risk analysis", "decision theory"]},
    {"id": "EMGT 292", "name": "Managing Capital Assets in the Smart Machine Era", "units": 2,
     "description": "Managing capital assets in technical firms in the era of Industry 4.0, robotics, IoT, AI, and ML.",
     "topics": ["asset management", "industry 4.0"]},
    {"id": "EMGT 295", "name": "Project Planning Under Conditions of Uncertainty", "units": 2,
     "description": "Managerial decision-making in project management under varying degrees of certainty, risk, and uncertainty.",
     "topics": ["project management", "decision making"]},
    {"id": "EMGT 296", "name": "Project Risk Management", "units": 2,
     "description": "Risk analysis, evaluation, and mitigation strategies, including defining acceptable risk thresholds.",
     "topics": ["project management", "risk management"]},
    {"id": "EMGT 299", "name": "Directed Research", "units": 1,
     "description": "Individual directed research arranged with an instructor. Limited to a single enrollment.",
     "topics": ["research"]},
    {"id": "EMGT 307", "name": "Medical Device Product Development", "units": 2, "alt_codes": ["BIOE 207"],
     "description": "Tools and processes for identifying clinical needs, selecting medical device concepts, and planning implementation.",
     "topics": ["medical devices", "product development"]},
    {"id": "EMGT 308", "name": "Solutions Architecture and the Cloud", "units": 2,
     "description": "System design foundations and best practices for cloud services and microservices, with hands-on labs on AWS, Azure, and GCP.",
     "topics": ["cloud computing", "solutions architecture"]},
    {"id": "EMGT 311", "name": "Data Science in Systems Management", "units": 3, "alt_codes": ["ENGR 184"],
     "description": "Applications of data science in systems management: data mining, decision trees, regression/classification, and big data for industrial decision-making.",
     "topics": ["data science", "systems management"]},
    {"id": "EMGT 318", "name": "Strategies for Career and Academic Success (Foreign-born Technical Professionals)", "units": 2,
     "description": "Helps foreign-born engineers develop knowledge and skills to be more effective in American academic and corporate environments.",
     "topics": ["professional development", "career strategy"]},
    {"id": "EMGT 319", "name": "Human Interaction I", "units": 2,
     "description": "Individuals interacting in groups to solve problems, using electronic and personal interaction elements.",
     "topics": ["communication", "group dynamics"]},
    {"id": "EMGT 320", "name": "Human Interaction II", "units": 2,
     "description": "A closer look at communication, personal limits, electronic interfacing, and communication skills.",
     "topics": ["communication", "group dynamics"]},
    {"id": "EMGT 322", "name": "Organizational Behavior", "units": 2,
     "description": "Skills required in transitioning from technical contributor to technical manager or team leader, blending technical and interpersonal dialogue.",
     "topics": ["organizational behavior", "leadership"]},
    {"id": "EMGT 323", "name": "Management of Technological Innovation: Opportunities and Challenges", "units": 2,
     "description": "Innovation as the process of commercializing new technologies: sources and models of innovation, disruptive innovation, and IP strategy.",
     "topics": ["innovation", "technology management"]},
    {"id": "EMGT 324", "name": "Engineering Leadership", "units": 2, "prerequisites": ["EMGT 322"],
     "description": "Facilitates the transition from technical team management to corporate leadership positions.",
     "topics": ["leadership", "management"]},
    {"id": "EMGT 329", "name": "Parallel Thinking", "units": 2,
     "description": "Workshop-style program on tools for harnessing group brainpower, drawing on precision questioning and high-performance systems research.",
     "topics": ["leadership", "problem solving"]},
    {"id": "EMGT 330", "name": "Project Management Basics", "units": 2,
     "description": "Fundamental concepts in project management: triple constraints, project life cycle, scheduling, budgeting, and monitoring/controls.",
     "topics": ["project management"]},
    {"id": "EMGT 331", "name": "Strategic Technology Management", "units": 2,
     "description": "Translating strategic plans into action plans across organizational boundaries, including competitive positioning and technology transfer.",
     "topics": ["strategy", "technology management"]},
    {"id": "EMGT 333", "name": "Computer-Aided Project Management Scheduling and Control", "units": 2,
     "description": "Project scheduling, budgeting, and control using Microsoft Project and Jira, including earned value analysis and corrective action.",
     "topics": ["project management", "scheduling"]},
    {"id": "EMGT 335", "name": "Advanced Project Management and Leadership", "units": 2, "prerequisites": ["EMGT 330"],
     "description": "Strategic view of project classification and portfolio management, focusing on project leadership, teamwork, and problem-solving.",
     "topics": ["project management", "leadership"]},
    {"id": "EMGT 336", "name": "Global Software Management (Introduction)", "units": 2,
     "description": "Software development techniques and issues related to offshore outsourcing, with case studies on project management best practices.",
     "topics": ["software management", "global teams"]},
    {"id": "EMGT 338", "name": "Software Product Management I", "units": 2,
     "description": "Introduction to product management, agile planning, customer analysis, value propositions, and product requirements.",
     "topics": ["product management", "agile"]},
    {"id": "EMGT 339", "name": "Software Product Management II: From Product to Company", "units": 4, "prerequisites": ["EMGT 338"],
     "description": "Product-market fit, MVP development, business model validation, hiring, and fundraising strategies for early-stage startups.",
     "topics": ["product management", "entrepreneurship"]},
    {"id": "EMGT 345", "name": "Program Management", "units": 2,
     "description": "Fundamentals of program and portfolio management and their application across businesses of varying size.",
     "topics": ["program management"]},
    {"id": "EMGT 346", "name": "Engineering Economics", "units": 2,
     "description": "Valuating and selecting engineering projects based on risk, available information, and time horizon, using capital budgeting techniques.",
     "topics": ["engineering economics", "finance"]},
    {"id": "EMGT 349", "name": "Ethical Decision Making for Technology Leaders", "units": 2, "alt_codes": ["ENGR 349"],
     "description": "A holistic view of leadership integrating concepts from psychology, ethics, philosophy, and sociology.",
     "topics": ["ethics", "leadership"]},
    {"id": "EMGT 352", "name": "Marketing of High-Tech Products and Innovations", "units": 2,
     "description": "The strategic role marketing plays in developing and promoting high-technology products and systems.",
     "topics": ["marketing", "technology products"]},
    {"id": "EMGT 353", "name": "Introduction to Total Quality Management", "units": 2,
     "description": "The basic tenets of TQM: customer focus, continuous improvement, and total participation, applied to new product development.",
     "topics": ["quality management"]},
    {"id": "EMGT 354", "name": "Innovation, Creativity, and Engineering Design", "units": 2,
     "description": "Research, discovery, technological feasibility, marketability, and the environment for innovation.",
     "topics": ["innovation", "design"]},
    {"id": "EMGT 357", "name": "Root Cause Analysis (RCA) Effective Problem Solving", "units": 2, "alt_codes": ["BIOE 357"],
     "description": "A step-by-step problem-solving approach covering proper methods of problem description, identification, correction, and containment.",
     "topics": ["problem solving", "root cause analysis"]},
    {"id": "EMGT 358", "name": "Global Technology Development", "units": 2, "alt_codes": ["ENGR 358"],
     "description": "Developing global technology from the perspective of an engineering manager, in corporate or entrepreneurial contexts.",
     "topics": ["global technology", "management"]},
    {"id": "EMGT 360", "name": "Current Papers in Engineering Management and Leadership", "units": 2,
     "description": "Individual topics selected in concurrence with the instructor.",
     "topics": ["engineering management"]},
    {"id": "EMGT 362", "name": "Topics in Engineering Management", "units": 2,
     "description": "Topics of current interest in engineering management and leadership; may be repeated as topics change.",
     "topics": ["engineering management"]},
    {"id": "EMGT 370", "name": "International (Global) Technology Operations", "units": 2,
     "description": "Managing operations when customers, facilities, and suppliers are located across the globe.",
     "topics": ["global operations", "management"]},
    {"id": "EMGT 373", "name": "Technology Entrepreneurship", "units": 2, "alt_codes": ["ENGR 373"],
     "description": "Moving from an idea to a profitable business, covering intellectual property, team formation, funding, and startup execution.",
     "topics": ["entrepreneurship", "startups"]},
    {"id": "EMGT 378", "name": "New Product Planning and Development", "units": 2,
     "description": "Blends marketing, engineering, and manufacturing perspectives into a single approach to new product development.",
     "topics": ["product development", "marketing"]},
    {"id": "EMGT 380", "name": "Introduction to Systems Engineering Management", "units": 2,
     "description": "Fundamental principles and methods of systems engineering and their application to complex systems.",
     "topics": ["systems engineering"]},
    {"id": "EMGT 381", "name": "Managing System Conceptual Design", "units": 2, "prerequisites": ["EMGT 380"],
     "description": "The systems engineer's responsibilities in the concept development stage, including needs analysis and risk assessment.",
     "topics": ["systems engineering", "design"]},
    {"id": "EMGT 382", "name": "Managing System Design, Integration, Test and Evaluation", "units": 2, "prerequisites": ["EMGT 380"],
     "description": "Engineering development and post-development stages of the system life cycle, including integration and evaluation.",
     "topics": ["systems engineering", "testing"]},
    {"id": "EMGT 388", "name": "System Supportability and Logistics", "units": 2,
     "description": "The ability of a system to be supported cost-effectively and in a timely manner with minimum logistics resources.",
     "topics": ["systems engineering", "logistics"]},
    {"id": "EMGT 389", "name": "Design for Reliability, Maintainability, and Supportability", "units": 2,
     "description": "Tools and techniques used early in the design phase, including Quality Function Deployment and Parameter Taxonomy.",
     "topics": ["reliability engineering", "design"]},
    {"id": "EMGT 390", "name": "System Architecture and Design", "units": 2,
     "description": "Fundamentals of system architecting, with an emphasis on practical heuristics and case studies.",
     "topics": ["systems architecture", "design"]},
    {"id": "EMGT 395", "name": "Intrapreneurship – Innovation from Within", "units": 2,
     "description": "Creating an innovative business opportunity within an existing organization, using small independent development teams.",
     "topics": ["intrapreneurship", "innovation"]},
]

# ---------------------------------------------------------------------------
# ENGR courses without a distinct EMGT-numbered equivalent (GREN folded into
# ENGR). Satisfy the 8-unit Graduate Core Enrichment Experience requirement.
# ---------------------------------------------------------------------------
ENGR_COURSES = [
    {"id": "ENGR 232", "name": "New Mobility and Society", "units": 2,
     "description": "Emerging mobility technologies (autonomous vehicles, micromobility, EVs) and their societal implications.",
     "topics": ["mobility", "society", "transportation"]},
    {"id": "ENGR 245", "name": "Innovation, Entrepreneurship and the Evolution of Silicon Valley", "units": 3,
     "description": "The history and dynamics of Silicon Valley's innovation ecosystem and what drives entrepreneurial success.",
     "topics": ["innovation", "entrepreneurship", "silicon valley"]},
    {"id": "ENGR 256", "name": "Introduction to Nanobioengineering", "units": 2,
     "description": "Foundational concepts at the intersection of nanotechnology and bioengineering.",
     "topics": ["nanotechnology", "bioengineering"]},
    {"id": "ENGR 260", "name": "Nanoscale Science and Technology", "units": 2,
     "description": "Fundamentals of nanoscale materials, devices, and fabrication techniques.",
     "topics": ["nanotechnology", "materials science"]},
    {"id": "ENGR 261", "name": "Nanotechnology and Society", "units": 2,
     "description": "Societal, ethical, and policy implications of nanotechnology.",
     "topics": ["nanotechnology", "society", "ethics"]},
    {"id": "ENGR 272", "name": "Energy Public Policy", "units": 2,
     "description": "Energy policy frameworks and their impact on technology development and deployment.",
     "topics": ["energy", "public policy"]},
    {"id": "ENGR 273", "name": "Sustainable Energy and Ethics", "units": 2,
     "description": "Ethical dimensions of sustainable energy systems and the transition away from fossil fuels.",
     "topics": ["sustainable energy", "ethics"]},
    {"id": "ENGR 302", "name": "Managing in the Multicultural Environment", "units": 2,
     "description": "Managing and leading teams across cultural boundaries in global technology organizations.",
     "topics": ["multicultural management", "leadership"]},
    {"id": "ENGR 303", "name": "Gender and Engineering", "units": 2,
     "description": "The role of gender in engineering practice, education, and the technology workforce.",
     "topics": ["gender", "engineering", "society"]},
    {"id": "ENGR 304", "name": "Building Global Teams", "units": 2,
     "description": "Strategies for building and leading effective globally distributed engineering teams.",
     "topics": ["global teams", "leadership"]},
    {"id": "ENGR 306", "name": "Engineering and the Law", "units": 2,
     "description": "Legal issues relevant to engineering practice, including liability, contracts, and regulation.",
     "topics": ["law", "engineering ethics"]},
    {"id": "ENGR 330", "name": "Law, Technology, and Intellectual Property", "units": 2,
     "description": "Intellectual property law as it applies to technology development and commercialization.",
     "topics": ["intellectual property", "law", "technology"]},
    {"id": "ENGR 332", "name": "How Engineers, Businesspeople, and Lawyers Communicate With Each Other", "units": 3,
     "description": "Cross-disciplinary communication between engineering, business, and legal stakeholders on technology projects.",
     "topics": ["communication", "interdisciplinary"]},
    {"id": "ENGR 334", "name": "Energy, Climate Change, and Social Justice", "units": 2,
     "description": "The intersection of energy systems, climate change, and social/environmental justice.",
     "topics": ["energy", "climate change", "social justice"]},
    {"id": "ENGR 336", "name": "Engineering for the Developing World", "units": 2,
     "description": "Engineering design and technology solutions tailored to resource-constrained, developing-world contexts.",
     "topics": ["appropriate technology", "developing world"]},
    {"id": "ENGR 337", "name": "Social Entrepreneurship: Innovating with Impact", "units": 2,
     "description": "Building ventures that pursue social impact alongside financial sustainability.",
     "topics": ["social entrepreneurship", "innovation"]},
    {"id": "ENGR 338", "name": "Mobile Applications for Emerging Markets", "units": 2,
     "description": "Designing and building mobile applications suited to the constraints of emerging markets.",
     "topics": ["mobile applications", "emerging markets"]},
    {"id": "ENGR 340", "name": "Distributed & Renewable Energy for the Developing World", "units": 2,
     "description": "Distributed and renewable energy system design for underserved regions.",
     "topics": ["renewable energy", "developing world"]},
    {"id": "ENGR 341", "name": "Innovation, Design and Spirituality", "units": 2,
     "description": "Exploring the relationship between design thinking, innovation, and spiritual/reflective practice.",
     "topics": ["design thinking", "innovation"]},
    {"id": "ENGR 342", "name": "3D Print Technology and Society", "units": 2,
     "description": "Additive manufacturing technology and its economic and societal impact.",
     "topics": ["3D printing", "manufacturing", "society"]},
    {"id": "ENGR 343", "name": "Science, Religion and the Limits of Knowledge", "units": 2,
     "description": "Examines the boundaries between scientific inquiry and religious/philosophical understanding.",
     "topics": ["philosophy of science", "ethics"]},
    {"id": "ENGR 344", "name": "Artificial Intelligence and Ethics", "units": 2,
     "description": "Ethical questions raised by the development and deployment of AI systems.",
     "topics": ["artificial intelligence", "ethics"]},
    {"id": "ENGR 345", "name": "Space Ethics", "units": 2,
     "description": "Ethical considerations in space exploration, commercialization, and governance.",
     "topics": ["space", "ethics"]},
    {"id": "ENGR 350", "name": "Success in Global Emerging Markets", "units": 2,
     "description": "Strategies for launching and scaling technology products in emerging global markets.",
     "topics": ["global markets", "strategy"]},
    {"id": "ENGR 351", "name": "New Paradigm for Technology-Global Mindfulness Leadership", "units": 2,
     "description": "Leadership approaches for technology organizations operating in a globally interconnected world.",
     "topics": ["leadership", "global mindset"]},
    {"id": "ENGR 371", "name": "Space Systems Design and Engineering I", "units": 2,
     "description": "Fundamentals of space systems design, covering mission architecture and subsystem engineering.",
     "topics": ["space systems", "systems design"]},
    {"id": "ENGR 372", "name": "Space Systems Design and Engineering II", "units": 2, "prerequisites": ["ENGR 371"],
     "description": "Continuation of space systems design, with emphasis on integration, testing, and mission operations.",
     "topics": ["space systems", "systems design"]},
]

# ---------------------------------------------------------------------------
# CSEN electives that satisfy the Engineering & Society requirement area
# ---------------------------------------------------------------------------
CSEN_SOCIETY_COURSES = [
    {"id": "CSEN 269", "name": "Computing for Good: Project Design and Implementation", "units": 2,
     "description": "Designing and implementing computing projects that address social good, in partnership with community organizations.",
     "topics": ["computing for good", "social impact"], "department": "Computer Science and Engineering"},
    {"id": "CSEN 288", "name": "Software Ethics", "units": 2,
     "description": "Ethical issues in software engineering practice, including privacy, bias, and responsible design.",
     "topics": ["software ethics", "responsible computing"], "department": "Computer Science and Engineering"},
]

# Course codes that count toward the Enrichment Experience (Engineering &
# Society / Professional Development areas), including EMGT-primary rows
# that are cross-listed under ENGR.
ENRICHMENT_ELIGIBLE_IDS = sorted(
    {c["id"] for c in ENGR_COURSES}
    | {c["id"] for c in EMGT_COURSES if "ENGR" in " ".join(c.get("alt_codes", []))}
    | {c["id"] for c in CSEN_SOCIETY_COURSES}
)


def _insert_courses(course_defs, default_department, default_level="Graduate"):
    inserted = []
    for c in course_defs:
        if db.session.get(Course, c["id"]):
            continue
        db.session.add(Course(
            id=c["id"],
            name=c["name"],
            units=c["units"],
            level=default_level,
            description=c.get("description", ""),
            department=c.get("department", default_department),
            prerequisites=c.get("prerequisites", []),
            alt_codes=c.get("alt_codes", []),
            topics=c.get("topics", []),
        ))
        inserted.append(c["id"])
    return inserted


def seed_engr_emgt():
    from config import Config
    if Config.FLASK_ENV == 'production':
        raise RuntimeError(
            'Refusing to run seed_engr_emgt.py against a production database '
            '(FLASK_ENV=production).'
        )

    with app.app_context():
        inserted = []
        inserted += _insert_courses(EMGT_COURSES, "Engineering Management and Leadership")
        inserted += _insert_courses(ENGR_COURSES, "School of Engineering (Interdisciplinary)")
        inserted += _insert_courses(CSEN_SOCIETY_COURSES, "Computer Science and Engineering")
        db.session.flush()

        program = db.session.get(Program, MS_CSEN_ID)
        if program is None:
            print(f"WARNING: program {MS_CSEN_ID} not found, skipping ProgramCourse links")
            db.session.commit()
            return

        all_new_ids = (
            [c["id"] for c in EMGT_COURSES]
            + [c["id"] for c in ENGR_COURSES]
            + [c["id"] for c in CSEN_SOCIETY_COURSES]
        )
        linked = 0
        for course_id in all_new_ids:
            exists = db.session.get(ProgramCourse, {"program_id": MS_CSEN_ID, "course_id": course_id})
            if not exists:
                db.session.add(ProgramCourse(program_id=MS_CSEN_ID, course_id=course_id))
                linked += 1

        # Structured, real MS-CSEN elective rules (Graduate Engineering Bulletin,
        # Chapters 2, 6, 10). Non-CSEN electives are allowed toward the 46-unit
        # total; EMGT is capped; the Enrichment Experience is a separate 8-unit
        # requirement layered on top, not part of the 46.
        requirements = dict(program.requirements or {})
        requirements.update({
            "core_courses": ["CSEN 210", "CSEN 279", "CSEN 283"],
            "min_csen_elective_units": 8,
            "min_csen_graduate_units": 36,
            "non_csen_elective_caps": {
                "EMGT": 6,
            },
            "enrichment_experience": {
                "required_units": 8,
                "min_core_units": 4,
                "min_areas": 2,
                "areas": [
                    "Emerging Topics in Engineering",
                    "Engineering and Business/Entrepreneurship",
                    "Engineering and Society",
                ],
                "eligible_course_ids": ENRICHMENT_ELIGIBLE_IDS,
                "note": "Mandatory for all MS students; cannot be waived or substituted.",
            },
        })
        program.requirements = requirements

        db.session.commit()
        print(f"Inserted {len(inserted)} new courses "
              f"({len(EMGT_COURSES)} EMGT, {len(ENGR_COURSES)} ENGR, {len(CSEN_SOCIETY_COURSES)} CSEN).")
        print(f"Linked {linked} new ProgramCourse rows to {MS_CSEN_ID}.")
        print(f"Updated {MS_CSEN_ID} requirements with EMGT cap + Enrichment Experience rules.")


if __name__ == "__main__":
    seed_engr_emgt()

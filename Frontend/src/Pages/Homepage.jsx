import { Link } from "react-router-dom";
import Button from "../components/ui/Button";
import { 
  Shield, 
  UserCheck, 
  Activity, 
  FileText, 
  Smile, 
  LayoutDashboard,
  ArrowRight,
  CheckCircle,
  Star,
  ChevronDown,
  Menu,
  X
} from "lucide-react";
import { useState } from "react";

const Homepage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-neutral-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 flex items-center justify-center">
                <img src="/src/Assets/Logo.png" alt="NeuroProctor" className="w-full h-full object-contain" />
              </div>
              <span className="font-semibold text-neutral-900">NeuroProctor</span>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors">How It Works</a>
              <a href="#testimonials" className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors">Testimonials</a>
              <a href="#faq" className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors">FAQ</a>
            </div>

            <div className="hidden md:flex items-center gap-4">
              <Link to="/login" className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors">Sign In</Link>
              <Link to="/register">
                <Button size="sm">Get Started</Button>
              </Link>
            </div>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-neutral-600 hover:text-neutral-900"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-neutral-200 bg-white">
            <div className="px-4 py-4 space-y-4">
              <a href="#features" className="block text-sm text-neutral-600 hover:text-neutral-900">Features</a>
              <a href="#how-it-works" className="block text-sm text-neutral-600 hover:text-neutral-900">How It Works</a>
              <a href="#testimonials" className="block text-sm text-neutral-600 hover:text-neutral-900">Testimonials</a>
              <a href="#faq" className="block text-sm text-neutral-600 hover:text-neutral-900">FAQ</a>
              <div className="pt-4 border-t border-neutral-200 space-y-3">
                <Link to="/login" className="block text-sm text-neutral-600 hover:text-neutral-900">Sign In</Link>
                <Link to="/register">
                  <Button className="w-full">Get Started</Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent/10 rounded-full mb-6">
              <span className="text-sm font-medium text-accent">AI-Powered Examination Security</span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold text-neutral-900 mb-6 leading-tight">
              Secure Online Examinations with Intelligent Proctoring
            </h1>
            <p className="text-lg text-neutral-600 mb-8 max-w-2xl mx-auto">
              NeuroProctor enables educational institutions and organizations to conduct remote assessments with confidence, ensuring academic integrity through AI-powered monitoring and real-time supervision.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register">
                <Button size="lg" className="w-full sm:w-auto">
                  Start Free Trial
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  View Demo
                </Button>
              </Link>
            </div>
          </div>

          {/* Hero Illustration */}
          <div className="mt-16 relative">
            <div className="bg-gradient-to-br from-neutral-100 to-neutral-50 rounded-2xl p-8 lg:p-12 border border-neutral-200">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl p-6 shadow-sm border border-neutral-200">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                      <Shield className="w-5 h-5 text-accent" />
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900">AI Monitoring</p>
                      <p className="text-sm text-neutral-500">Real-time detection</p>
                    </div>
                  </div>
                  <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div className="h-full bg-accent w-3/4 rounded-full" />
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 shadow-sm border border-neutral-200">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <UserCheck className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900">Face Verification</p>
                      <p className="text-sm text-neutral-500">Identity confirmed</p>
                    </div>
                  </div>
                  <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 w-full rounded-full" />
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 shadow-sm border border-neutral-200">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Activity className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900">Live Supervision</p>
                      <p className="text-sm text-neutral-500">Active monitoring</p>
                    </div>
                  </div>
                  <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 w-2/3 rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className="py-16 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-neutral-500 mb-8">Trusted by leading educational institutions</p>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 items-center opacity-60">
            <div className="text-center text-neutral-400 font-semibold">University A</div>
            <div className="text-center text-neutral-400 font-semibold">College B</div>
            <div className="text-center text-neutral-400 font-semibold">Institute C</div>
            <div className="text-center text-neutral-400 font-semibold">School D</div>
            <div className="text-center text-neutral-400 font-semibold">Training E</div>
            <div className="text-center text-neutral-400 font-semibold">Certify F</div>
          </div>
        </div>
      </section>

      {/* Why Choose Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold text-neutral-900 mb-4">
              Why Choose NeuroProctor
            </h2>
            <p className="text-lg text-neutral-600">
              We combine advanced AI technology with user-friendly design to deliver examination security that works for everyone.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Shield className="w-8 h-8 text-accent" />
              </div>
              <h3 className="text-xl font-semibold text-neutral-900 mb-3">Secure & Reliable</h3>
              <p className="text-neutral-600">
                Enterprise-grade security protocols protect examination integrity while maintaining system stability.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-neutral-900 mb-3">Accurate Detection</h3>
              <p className="text-neutral-600">
                AI algorithms trained on real examination scenarios provide precise monitoring with minimal false positives.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Smile className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-neutral-900 mb-3">Student-Friendly</h3>
              <p className="text-neutral-600">
                Clean, distraction-free interface designed to reduce anxiety and help students focus on their assessments.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-neutral-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold text-neutral-900 mb-4">
              Core Features
            </h2>
            <p className="text-lg text-neutral-600">
              Comprehensive tools designed to secure every aspect of online examinations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl p-6 border border-neutral-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">AI-Powered Proctoring</h3>
              <p className="text-sm text-neutral-600">
                Intelligent monitoring continuously observes the examination environment and detects suspicious activities.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-neutral-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <UserCheck className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">Face Verification</h3>
              <p className="text-sm text-neutral-600">
                Verifies candidate identity before and throughout the examination to reduce impersonation risks.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-neutral-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Activity className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">Real-Time Monitoring</h3>
              <p className="text-sm text-neutral-600">
                Live supervision of examination sessions with instant alerts for unusual behavior detection.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-neutral-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">Comprehensive Reports</h3>
              <p className="text-sm text-neutral-600">
                Detailed examination summaries and incident reports for thorough session review.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-neutral-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                <Smile className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">Student-Friendly</h3>
              <p className="text-sm text-neutral-600">
                Clean, distraction-free environment designed for ease of use across different devices.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-neutral-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
                <LayoutDashboard className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">Institution Dashboard</h3>
              <p className="text-sm text-neutral-600">
                Centralized workspace for managing examinations, monitoring sessions, and reviewing reports.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Helps Section */}
      <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold text-neutral-900 mb-4">
              How It Helps
            </h2>
            <p className="text-lg text-neutral-600">
              Benefits for institutions, instructors, and students alike.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="bg-neutral-50 rounded-xl p-8">
              <h3 className="text-xl font-semibold text-neutral-900 mb-4">For Institutions</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Maintain academic integrity at scale</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Reduce examination logistics costs</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Expand reach to remote candidates</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Comprehensive audit trails</span>
                </li>
              </ul>
            </div>

            <div className="bg-neutral-50 rounded-xl p-8">
              <h3 className="text-xl font-semibold text-neutral-900 mb-4">For Instructors</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Focus on content, not monitoring</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Quick incident review and resolution</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Flexible examination scheduling</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Data-driven insights</span>
                </li>
              </ul>
            </div>

            <div className="bg-neutral-50 rounded-xl p-8">
              <h3 className="text-xl font-semibold text-neutral-900 mb-4">For Students</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Take exams from anywhere</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Fair and transparent process</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Reduced examination anxiety</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">Immediate results availability</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-neutral-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <p className="text-4xl sm:text-5xl font-semibold mb-2">50K+</p>
              <p className="text-neutral-400">Exams Conducted</p>
            </div>
            <div className="text-center">
              <p className="text-4xl sm:text-5xl font-semibold mb-2">200+</p>
              <p className="text-neutral-400">Institutions</p>
            </div>
            <div className="text-center">
              <p className="text-4xl sm:text-5xl font-semibold mb-2">99.2%</p>
              <p className="text-neutral-400">Monitoring Accuracy</p>
            </div>
            <div className="text-center">
              <p className="text-4xl sm:text-5xl font-semibold mb-2">95%</p>
              <p className="text-neutral-400">Satisfied Users</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold text-neutral-900 mb-4">
              What Our Users Say
            </h2>
            <p className="text-lg text-neutral-600">
              Trusted by educators and organizations worldwide.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-6 border border-neutral-200">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-neutral-600 mb-6">
                "NeuroProctor has transformed how we conduct remote examinations. The AI monitoring is incredibly accurate and has given us confidence in online assessments."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-neutral-200 rounded-full" />
                <div>
                  <p className="font-medium text-neutral-900">Dr. Sarah Johnson</p>
                  <p className="text-sm text-neutral-500">University Dean</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 border border-neutral-200">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-neutral-600 mb-6">
                "The platform is intuitive for both instructors and students. We've seen a significant reduction in examination logistics while maintaining high integrity standards."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-neutral-200 rounded-full" />
                <div>
                  <p className="font-medium text-neutral-900">Prof. Michael Chen</p>
                  <p className="text-sm text-neutral-500">Training Director</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 border border-neutral-200">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-neutral-600 mb-6">
                "Implementation was seamless and the support team was exceptional. Our certification exams are now more secure and accessible to candidates worldwide."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-neutral-200 rounded-full" />
                <div>
                  <p className="font-medium text-neutral-900">Emily Rodriguez</p>
                  <p className="text-sm text-neutral-500">Certification Manager</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8 bg-neutral-50">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold text-neutral-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-neutral-600">
              Common questions about NeuroProctor
            </p>
          </div>

          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-neutral-200 p-6">
              <h3 className="font-semibold text-neutral-900 mb-2">How does AI proctoring work?</h3>
              <p className="text-sm text-neutral-600">
                Our AI system monitors video feeds, audio, and screen activity in real-time. It uses machine learning to detect suspicious behaviors like unauthorized persons, unusual movements, or prohibited activities.
              </p>
            </div>

            <div className="bg-white rounded-xl border border-neutral-200 p-6">
              <h3 className="font-semibold text-neutral-900 mb-2">Is student data secure?</h3>
              <p className="text-sm text-neutral-600">
                Yes, we employ enterprise-grade encryption and security protocols. All data is stored securely and access is strictly controlled. We comply with major data protection regulations including GDPR and FERPA.
              </p>
            </div>

            <div className="bg-white rounded-xl border border-neutral-200 p-6">
              <h3 className="font-semibold text-neutral-900 mb-2">What devices are supported?</h3>
              <p className="text-sm text-neutral-600">
                NeuroProctor works on most modern devices including laptops, desktops, and tablets. We recommend using a device with a webcam and stable internet connection for the best experience.
              </p>
            </div>

            <div className="bg-white rounded-xl border border-neutral-200 p-6">
              <h3 className="font-semibold text-neutral-900 mb-2">Can I try before committing?</h3>
              <p className="text-sm text-neutral-600">
                Absolutely! We offer a free trial period so you can experience the platform's features and determine if it meets your institution's needs before making a commitment.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-accent text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold mb-4">
            Ready to Secure Your Examinations?
          </h2>
          <p className="text-lg opacity-90 mb-8">
            Join hundreds of institutions trust NeuroProctor for their online assessment needs.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="bg-white text-accent hover:bg-neutral-100">
                Start Free Trial
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                Contact Sales
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 flex items-center justify-center">
                  <img src="/src/Assets/Logo.png" alt="NeuroProctor" className="w-full h-full object-contain" />
                </div>
                <span className="font-semibold">NeuroProctor</span>
              </div>
              <p className="text-sm text-neutral-400 mb-4">
                AI-powered examination security for educational institutions and organizations.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Integrations</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-neutral-800 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-neutral-400">
              © 2024 NeuroProctor. All rights reserved.
            </p>
            <div className="flex items-center gap-6 text-sm text-neutral-400">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Cookies</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;

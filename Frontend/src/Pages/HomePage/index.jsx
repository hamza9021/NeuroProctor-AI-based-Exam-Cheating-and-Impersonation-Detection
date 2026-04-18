import React from 'react';
import HeroSection from './components/HeroSection';
import Features from './components/Features';
import Workflow from './components/Workflow';
import Analytics from './components/Analytics';
import Compliance from './components/Compliance';
import Trust from './components/Trust';
import FooterCTA from './components/FooterCTA';

const HomePage = () => {
    return (
        <div className="relative w-full min-h-screen bg-black text-white overflow-x-hidden font-inter selection:bg-white selection:text-black">
            <HeroSection />
            <Features />
            <Workflow />
            <Analytics />
            <Compliance />
            <Trust />
            <FooterCTA />
        </div>
    );
};

export default HomePage;

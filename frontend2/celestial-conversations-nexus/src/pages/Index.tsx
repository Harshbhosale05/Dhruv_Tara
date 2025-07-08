
import React from 'react';
import ChatBot from '@/components/ChatBot';
import SolarSystem from '@/components/SolarSystem';
import FloatingSatellites from '@/components/FloatingSatellites';
import SpaceBackground from '@/components/SpaceBackground';
import { Satellite, Earth, Rocket, Globe, Activity } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Enhanced Space Background */}
      <SpaceBackground />
      
      {/* Solar System Animation */}
      <SolarSystem />
      
      {/* Floating Satellites */}
      <FloatingSatellites />
      
      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4">
        {/* Enhanced Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="flex items-center justify-center gap-6 mb-6">
            <div className="relative">
              <Satellite className="w-14 h-14 text-primary satellite-float satellite-glow" />
              <div className="absolute -top-2 -right-2 w-4 h-4 bg-green-400 rounded-full pulse-glow"></div>
              <div className="absolute -bottom-1 -left-1 w-3 h-3 bg-blue-400 rounded-full pulse-glow" style={{animationDelay: '1s'}}></div>
            </div>
            <div className="text-center">
              <h1 className="text-6xl md:text-8xl font-bold text-gradient mb-2 tracking-wider">
                Dhruv_Tara
              </h1>
              <div className="flex items-center justify-center gap-2 text-sm text-primary/60">
                <div className="w-8 h-0.5 bg-gradient-to-r from-transparent to-primary/60"></div>
                <span className="font-mono">EST. 1969</span>
                <div className="w-8 h-0.5 bg-gradient-to-l from-transparent to-primary/60"></div>
              </div>
            </div>
            <div className="relative">
              <Earth className="w-14 h-14 text-blue-400 orbital-animation earth-glow" style={{animationDuration: '12s'}} />
              <div className="absolute inset-0 border border-blue-400/20 rounded-full animate-spin" style={{animationDuration: '8s'}}></div>
            </div>
          </div>
          
          <div className="space-y-4">
            <p className="text-xl md:text-3xl text-muted-foreground font-light">
              Advanced Space Exploration Assistant
            </p>
            <p className="text-sm md:text-base text-muted-foreground/80 max-w-3xl mx-auto leading-relaxed">
              Pioneering India's journey to the stars. Explore our missions, satellites, and groundbreaking discoveries 
              through our AI-powered mission control assistant.
            </p>
          </div>
        </div>
        
        {/* Enhanced Chat Bot */}
        <div className="w-full max-w-4xl animate-scale-in">
          <ChatBot />
        </div>
        
        {/* Enhanced Footer */}
        <div className="mt-8 text-center animate-fade-in" style={{animationDelay: '0.5s'}}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-muted-foreground/60 mb-4">
            <div className="flex items-center justify-center gap-3 p-3 rounded-lg bg-primary/5 backdrop-blur-sm border border-primary/10">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <Activity className="w-4 h-4" />
              <span>Live Mission Data</span>
            </div>
            <div className="flex items-center justify-center gap-3 p-3 rounded-lg bg-primary/5 backdrop-blur-sm border border-primary/10">
              <Rocket className="w-4 h-4" />
              <span>100+ Satellites Launched</span>
            </div>
            <div className="flex items-center justify-center gap-3 p-3 rounded-lg bg-primary/5 backdrop-blur-sm border border-primary/10">
              <Globe className="w-4 h-4" />
              <span>Deep Space Network Active</span>
            </div>
          </div>
          
          <div className="text-xs text-muted-foreground/40 font-mono">
            Mission Control • Bangalore • India • {new Date().getFullYear()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;

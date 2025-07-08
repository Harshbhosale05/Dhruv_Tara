
import React from 'react';

const SpaceBackground = () => {
  return (
    <div className="fixed inset-0 pointer-events-none">
      {/* Enhanced Starfield with multiple layers */}
      <div className="stars absolute inset-0"></div>
      <div className="stars-secondary absolute inset-0"></div>
      <div className="stars-distant absolute inset-0"></div>
      
      {/* Enhanced Nebula effects with more colors */}
      <div className="absolute top-0 left-0 w-full h-full">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/15 rounded-full blur-3xl animate-pulse nebula-drift"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-500/12 rounded-full blur-3xl animate-pulse nebula-drift-reverse" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-3/4 left-1/3 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl animate-pulse nebula-drift" style={{animationDelay: '4s'}}></div>
        <div className="absolute top-1/6 right-1/3 w-72 h-72 bg-cyan-400/8 rounded-full blur-3xl animate-pulse nebula-drift-reverse" style={{animationDelay: '6s'}}></div>
        <div className="absolute bottom-1/3 left-1/6 w-56 h-56 bg-indigo-500/12 rounded-full blur-3xl animate-pulse nebula-drift" style={{animationDelay: '8s'}}></div>
      </div>
      
      {/* Enhanced Shooting stars with trails */}
      <div className="absolute top-1/4 left-0 shooting-star" style={{animationDelay: '3s'}}></div>
      <div className="absolute top-3/4 right-1/4 shooting-star" style={{animationDelay: '7s'}}></div>
      <div className="absolute top-1/2 left-1/4 shooting-star" style={{animationDelay: '10s'}}></div>
      <div className="absolute top-1/6 right-1/6 shooting-star" style={{animationDelay: '12s'}}></div>
      <div className="absolute bottom-1/4 left-1/2 shooting-star" style={{animationDelay: '15s'}}></div>
      
      {/* Space dust particles */}
      <div className="absolute inset-0 space-dust"></div>
      
      {/* Cosmic radiation effect */}
      <div className="absolute inset-0 cosmic-rays"></div>
    </div>
  );
};

export default SpaceBackground;

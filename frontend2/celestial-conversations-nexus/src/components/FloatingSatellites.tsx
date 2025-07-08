
import React from 'react';
import { Satellite, Radio, Zap } from 'lucide-react';

const FloatingSatellites = () => {
  const satellites = [
    { id: 1, top: '15%', left: '10%', delay: '0s', size: 'w-6 h-6', type: 'communication' },
    { id: 2, top: '25%', right: '15%', delay: '2s', size: 'w-5 h-5', type: 'navigation' },
    { id: 3, top: '60%', left: '5%', delay: '4s', size: 'w-7 h-7', type: 'observation' },
    { id: 4, bottom: '20%', right: '20%', delay: '1s', size: 'w-5 h-5', type: 'communication' },
    { id: 5, top: '40%', left: '85%', delay: '3s', size: 'w-6 h-6', type: 'weather' },
    { id: 6, bottom: '40%', left: '15%', delay: '5s', size: 'w-4 h-4', type: 'navigation' },
    { id: 7, top: '80%', right: '40%', delay: '6s', size: 'w-5 h-5', type: 'research' },
    { id: 8, top: '10%', left: '60%', delay: '7s', size: 'w-6 h-6', type: 'observation' },
  ];

  const getSatelliteIcon = (type: string) => {
    switch (type) {
      case 'communication': return Satellite;
      case 'navigation': return Radio;
      case 'observation': return Zap;
      default: return Satellite;
    }
  };

  const getSatelliteColor = (type: string) => {
    switch (type) {
      case 'communication': return 'text-blue-400';
      case 'navigation': return 'text-green-400';
      case 'observation': return 'text-purple-400';
      case 'weather': return 'text-cyan-400';
      case 'research': return 'text-pink-400';
      default: return 'text-primary';
    }
  };

  return (
    <div className="fixed inset-0 pointer-events-none">
      {satellites.map((satellite) => {
        const IconComponent = getSatelliteIcon(satellite.type);
        const colorClass = getSatelliteColor(satellite.type);
        
        return (
          <div
            key={satellite.id}
            className={`absolute satellite-float-enhanced ${satellite.size}`}
            style={{
              top: satellite.top,
              left: satellite.left,
              right: satellite.right,
              bottom: satellite.bottom,
              animationDelay: satellite.delay,
            }}
          >
            <div className="relative satellite-container">
              <IconComponent className={`${satellite.size} ${colorClass} satellite-spin`} />
              <div className={`absolute inset-0 bg-current/20 rounded-full blur-md animate-pulse satellite-glow`}></div>
              
              {/* Enhanced Signal waves */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className={`w-8 h-8 border border-current/20 rounded-full animate-ping signal-wave`}></div>
              </div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className={`w-12 h-12 border border-current/10 rounded-full animate-ping signal-wave`} style={{animationDelay: '1s'}}></div>
              </div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className={`w-16 h-16 border border-current/5 rounded-full animate-ping signal-wave`} style={{animationDelay: '2s'}}></div>
              </div>
              
              {/* Data transmission beams */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className="data-beam data-beam-1"></div>
                <div className="data-beam data-beam-2"></div>
                <div className="data-beam data-beam-3"></div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default FloatingSatellites;

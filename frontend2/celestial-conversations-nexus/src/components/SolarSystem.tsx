
import React from 'react';
import { Sun, Moon, Earth } from 'lucide-react';

const SolarSystem = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* Central Sun */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="relative">
          <Sun className="w-16 h-16 text-yellow-400 animate-spin" style={{animationDuration: '20s'}} />
          <div className="absolute inset-0 bg-yellow-400/20 rounded-full blur-xl animate-pulse"></div>
        </div>
      </div>

      {/* Earth Orbit */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="orbital-animation">
          <div className="relative">
            <Earth className="w-8 h-8 text-blue-400" />
            <div className="absolute inset-0 bg-blue-400/30 rounded-full blur-lg"></div>
          </div>
        </div>
      </div>

      {/* Moon Orbit around Earth */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="orbital-animation" style={{animationDuration: '8s', animationDirection: 'reverse'}}>
          <div className="orbital-animation" style={{animationDuration: '4s'}}>
            <div className="relative">
              <Moon className="w-4 h-4 text-gray-300" />
              <div className="absolute inset-0 bg-gray-300/30 rounded-full blur-md"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Planets */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="orbital-animation" style={{animationDuration: '30s'}}>
          <div className="w-6 h-6 bg-red-500 rounded-full opacity-80"></div>
        </div>
      </div>

      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="orbital-animation" style={{animationDuration: '45s', transform: 'scale(1.5)'}}>
          <div className="w-10 h-10 bg-orange-400 rounded-full opacity-70"></div>
        </div>
      </div>

      {/* Orbit Rings */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="w-72 h-72 border border-primary/10 rounded-full"></div>
      </div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="w-96 h-96 border border-primary/5 rounded-full"></div>
      </div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="w-[32rem] h-[32rem] border border-primary/5 rounded-full"></div>
      </div>
    </div>
  );
};

export default SolarSystem;

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheckIcon, PlayIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const Navigation = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">
              Quiz Platform Security
            </span>
          </div>
          
          <div className="flex space-x-8 items-center">
            <Link
              to="/"
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <ShieldCheckIcon className="h-4 w-4 mr-1" />
              Dashboard
            </Link>
            
            <Link
              to="/audit"
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/audit') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <PlayIcon className="h-4 w-4 mr-1" />
              Run Audit
            </Link>
            
            <Link
              to="/scanner"
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/scanner') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <MagnifyingGlassIcon className="h-4 w-4 mr-1" />
              Vulnerability Scanner
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;

import React from 'react';
import { BookOpen, Brain } from 'lucide-react';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-100">
      <header className="bg-gradient-to-r from-emerald-600 to-teal-600 shadow-lg border-b border-teal-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-white" />
              <BookOpen className="h-8 w-8 text-emerald-100" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI Engineering Quiz Platform</h1>
              <p className="text-sm text-emerald-100">Day 46: Interactive Quiz Taking Interface</p>
            </div>
          </div>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;

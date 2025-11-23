import React from 'react';
import { RefreshCw, ArrowUp, ArrowDown, HelpCircle } from 'lucide-react';

const actions = [
  { icon: RefreshCw, label: 'Refresh', color: '#99dbc4' },
  { icon: ArrowUp, label: 'Top', color: '#78d39e' },
  { icon: ArrowDown, label: 'Bottom', color: '#fac1c1' },
  { icon: HelpCircle, label: 'Help', color: '#f8d9a4' },
];

export function FloatingActionButtons() {
  return (
    <div className="fixed right-6 bottom-24 flex flex-col space-y-3 z-40">
      {actions.map((action, index) => {
        const Icon = action.icon;
        return (
          <button
            key={index}
            className="w-14 h-14 rounded-full shadow-lg hover:opacity-90 transition-all hover:scale-105 flex items-center justify-center"
            style={{ backgroundColor: action.color }}
            title={action.label}
          >
            <Icon size={24} color="#FFFFFF" />
          </button>
        );
      })}
    </div>
  );
}

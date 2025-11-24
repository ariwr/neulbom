import React from 'react';
import { AlertTriangle, Phone } from 'lucide-react';
import { Card } from './ui/ThemedCard';
import { Button } from './ui/ThemedButton';
import { colors } from '../styles/design-tokens';

export function CrisisPanel() {
  return (
    <Card variant="elevated" padding="md">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center space-x-2">
          <div 
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: colors.error + '20' }}
          >
            <AlertTriangle size={20} style={{ color: colors.error }} />
          </div>
          <h3 className="text-base" style={{ color: colors.error }}>
            위기 감지됨
          </h3>
        </div>

        {/* Content */}
        <div className="space-y-2">
          <p className="text-sm" style={{ color: colors.textDark }}>
            대화 내용에서 위기 상황이 감지되었습니다.
          </p>
          <p className="text-sm" style={{ color: colors.textSub }}>
            전문 상담이 필요하신 경우 아래 연락처로 도움을 요청하세요.
          </p>
        </div>

        {/* Emergency Contact */}
        <div 
          className="p-4 rounded-xl space-y-3"
          style={{ backgroundColor: colors.lightGray }}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm" style={{ color: colors.textDark }}>
              긴급 상담 전화
            </span>
            <span className="text-lg" style={{ color: colors.mainGreen2 }}>
              129
            </span>
          </div>
          <Button 
            variant="primary" 
            size="sm" 
            fullWidth
            icon={<Phone size={16} />}
          >
            전화 걸기
          </Button>
        </div>

        {/* Resources */}
        <div className="space-y-2">
          <p className="text-xs" style={{ color: colors.textSub }}>
            추가 도움말
          </p>
          <ul className="space-y-1">
            <li className="text-xs" style={{ color: colors.textSub }}>
              • 복지상담 전화: 1577-xxxx
            </li>
            <li className="text-xs" style={{ color: colors.textSub }}>
              • 정신건강 위기상담: 1577-xxxx
            </li>
          </ul>
        </div>
      </div>
    </Card>
  );
}

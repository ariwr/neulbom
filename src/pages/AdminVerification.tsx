import React, { useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, User } from 'lucide-react';
import { Card } from '../components/ui/ThemedCard';
import { Button } from '../components/ui/ThemedButton';
import { Badge } from '../components/ui/Badge';
import { colors } from '../styles/design-tokens';

export function AdminVerification() {
  const [selectedUser, setSelectedUser] = useState<number | null>(null);

  const pendingUsers = [
    {
      id: 1,
      name: '김OO',
      email: 'kim***@example.com',
      submitDate: '2025.11.22',
      currentLevel: 2,
      requestLevel: 3,
      hasCrisisFlag: false,
      answers: {
        q1: '저는 현재 80세 어머니를 돌보고 있습니다. 일상생활 지원과 병원 동행 등을 하고 있습니다.',
        q2: '돌봄 경험을 공유하고, 비슷한 상황의 분들과 정보를 나누고 싶어 신청합니다.',
      },
    },
    {
      id: 2,
      name: '이OO',
      email: 'lee***@example.com',
      submitDate: '2025.11.21',
      currentLevel: 2,
      requestLevel: 3,
      hasCrisisFlag: true,
      answers: {
        q1: '발달장애가 있는 자녀를 돌보고 있습니다. 매일 힘들고 지치지만 계속하고 있습니다.',
        q2: '같은 상황의 부모님들과 소통하고 싶습니다. 너무 외롭고 힘듭니다.',
      },
    },
    {
      id: 3,
      name: '박OO',
      email: 'park***@example.com',
      submitDate: '2025.11.20',
      currentLevel: 2,
      requestLevel: 3,
      hasCrisisFlag: false,
      answers: {
        q1: '뇌졸중으로 쓰러지신 아버지를 3년째 돌보고 있습니다.',
        q2: '실질적인 돌봄 노하우와 복지 정보를 다른 분들과 나누고 싶습니다.',
      },
    },
  ];

  const selectedUserData = pendingUsers.find(u => u.id === selectedUser);

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.lightGray }}>
      {/* Header */}
      <div className="bg-white border-b" style={{ borderColor: colors.lightGray }}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-xl" style={{ color: colors.textDark }}>
            관리자 - 사용자 인증 검토
          </h1>
          <p className="text-sm mt-1" style={{ color: colors.textSub }}>
            Level 3 인증 대기 중인 사용자 목록
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* User Queue List */}
          <div className="lg:col-span-1 space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base" style={{ color: colors.textDark }}>
                대기 목록 ({pendingUsers.length})
              </h2>
            </div>

            {pendingUsers.map((user) => (
              <Card
                key={user.id}
                variant={selectedUser === user.id ? 'elevated' : 'outlined'}
                padding="md"
                onClick={() => setSelectedUser(user.id)}
                style={{
                  borderLeft: selectedUser === user.id ? `4px solid ${colors.mainGreen2}` : undefined,
                }}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <User size={16} style={{ color: colors.textSub }} />
                      <span className="text-sm" style={{ color: colors.textDark }}>
                        {user.name}
                      </span>
                    </div>
                    {user.hasCrisisFlag && (
                      <AlertTriangle size={16} style={{ color: colors.error }} />
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Badge variant="level2" size="sm">L{user.currentLevel}</Badge>
                    <span className="text-xs" style={{ color: colors.textSub }}>→</span>
                    <Badge variant="level3" size="sm">L{user.requestLevel}</Badge>
                  </div>

                  <p className="text-xs" style={{ color: colors.textSub }}>
                    신청일: {user.submitDate}
                  </p>
                </div>
              </Card>
            ))}
          </div>

          {/* Review Panel */}
          <div className="lg:col-span-2">
            {selectedUserData ? (
              <div className="space-y-6">
                {/* User Info */}
                <Card variant="elevated" padding="lg">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h2 className="text-lg" style={{ color: colors.textDark }}>
                        사용자 정보
                      </h2>
                      {selectedUserData.hasCrisisFlag && (
                        <Badge variant="crisis" size="md">
                          위기 감지됨
                        </Badge>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                          이름
                        </p>
                        <p className="text-sm" style={{ color: colors.textDark }}>
                          {selectedUserData.name}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                          이메일
                        </p>
                        <p className="text-sm" style={{ color: colors.textDark }}>
                          {selectedUserData.email}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                          현재 등급
                        </p>
                        <Badge variant="level2" size="sm">
                          Level {selectedUserData.currentLevel}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-xs mb-1" style={{ color: colors.textSub }}>
                          요청 등급
                        </p>
                        <Badge variant="level3" size="sm">
                          Level {selectedUserData.requestLevel}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Crisis Alert */}
                {selectedUserData.hasCrisisFlag && (
                  <Card 
                    variant="elevated" 
                    padding="md"
                    style={{ backgroundColor: colors.error + '10', borderLeft: `4px solid ${colors.error}` }}
                  >
                    <div className="flex items-start space-x-3">
                      <AlertTriangle size={20} style={{ color: colors.error }} />
                      <div>
                        <h3 className="text-sm mb-1" style={{ color: colors.error }}>
                          위기 상황 감지
                        </h3>
                        <p className="text-xs" style={{ color: colors.textSub }}>
                          답변에서 정서적 위기 신호가 감지되었습니다. 승인 시 추가 모니터링이 권장됩니다.
                        </p>
                      </div>
                    </div>
                  </Card>
                )}

                {/* Answers */}
                <Card variant="elevated" padding="lg">
                  <h2 className="text-lg mb-4" style={{ color: colors.textDark }}>
                    인증 답변
                  </h2>

                  <div className="space-y-4">
                    <div>
                      <p className="text-sm mb-2" style={{ color: colors.textDark }}>
                        Q1. 현재 어떤 돌봄 상황에 계신가요?
                      </p>
                      <div 
                        className="p-4 rounded-xl"
                        style={{ backgroundColor: colors.lightGray }}
                      >
                        <p className="text-sm" style={{ color: colors.textSub }}>
                          {selectedUserData.answers.q1}
                        </p>
                      </div>
                    </div>

                    <div>
                      <p className="text-sm mb-2" style={{ color: colors.textDark }}>
                        Q2. 커뮤니티에서 무엇을 하고 싶으신가요?
                      </p>
                      <div 
                        className="p-4 rounded-xl"
                        style={{ backgroundColor: colors.lightGray }}
                      >
                        <p className="text-sm" style={{ color: colors.textSub }}>
                          {selectedUserData.answers.q2}
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Action Buttons */}
                <Card variant="elevated" padding="lg">
                  <div className="space-y-4">
                    <h3 className="text-base" style={{ color: colors.textDark }}>
                      검토 결과
                    </h3>

                    <div className="grid grid-cols-2 gap-3">
                      <Button 
                        variant="primary" 
                        size="lg"
                        icon={<CheckCircle size={20} />}
                      >
                        승인
                      </Button>
                      <Button 
                        variant="outline" 
                        size="lg"
                        icon={<XCircle size={20} />}
                      >
                        거부
                      </Button>
                    </div>

                    {selectedUserData.hasCrisisFlag && (
                      <div 
                        className="p-3 rounded-lg"
                        style={{ backgroundColor: colors.pointYellow + '30' }}
                      >
                        <p className="text-xs" style={{ color: colors.textDark }}>
                          ⚠️ 위기 플래그가 있는 사용자입니다. 승인 시 추가 지원이 필요할 수 있습니다.
                        </p>
                      </div>
                    )}
                  </div>
                </Card>
              </div>
            ) : (
              <Card variant="elevated" padding="lg">
                <div className="text-center py-12">
                  <User size={48} className="mx-auto mb-4" style={{ color: colors.lightGray }} />
                  <p className="text-sm" style={{ color: colors.textSub }}>
                    사용자를 선택하여 검토를 시작하세요
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

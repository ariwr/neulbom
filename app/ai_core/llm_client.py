from typing import Optional, List, Dict
import requests
import json
from app.core.config import settings

# Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Upstage API 설정
UPSTAGE_API_URL = "https://api.upstage.ai/v1/chat/completions"


class LLMClient:
    """LLM API 호출 래퍼 클래스 (Gemini, Upstage 지원)"""
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.upstage_api_key = settings.UPSTAGE_API_KEY
        self.default_provider = settings.DEFAULT_LLM_PROVIDER
        
        # Gemini 초기화
        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Gemini 초기화 실패: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
    
    def generate_chat_response(
        self,
        message: str,
        history: List[Dict],
        system_prompt: str,
        provider: Optional[str] = None
    ) -> str:
        """
        챗봇 응답 생성
        - provider: "gemini" 또는 "upstage" (None이면 기본값 사용)
        """
        provider = provider or self.default_provider
        
        if provider == "gemini":
            return self._generate_with_gemini(message, history, system_prompt)
        elif provider == "upstage":
            return self._generate_with_upstage(message, history, system_prompt)
        else:
            raise ValueError(f"지원하지 않는 provider: {provider}")
    
    def _generate_with_gemini(
        self,
        message: str,
        history: List[Dict],
        system_prompt: str
    ) -> str:
        """Gemini API를 사용한 응답 생성"""
        if not self.gemini_model:
            return self._fallback_response(message)
        
        try:
            # Gemini는 system prompt를 첫 메시지에 포함
            full_prompt = f"{system_prompt}\n\n"
            
            # 히스토리 추가
            for h in history:
                role = h.get("role", "user")
                content = h.get("content", "")
                if role == "user":
                    full_prompt += f"사용자: {content}\n"
                elif role == "assistant":
                    full_prompt += f"늘봄: {content}\n"
            
            # 현재 메시지 추가
            full_prompt += f"사용자: {message}\n늘봄:"
            
            # API 호출
            response = self.gemini_model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API 오류: {e}")
            return self._fallback_response(message)
    
    def _generate_with_upstage(
        self,
        message: str,
        history: List[Dict],
        system_prompt: str
    ) -> str:
        """Upstage API를 사용한 응답 생성"""
        if not self.upstage_api_key:
            return self._fallback_response(message)
        
        try:
            # 메시지 포맷 변환
            messages = [{"role": "system", "content": system_prompt}]
            
            # 히스토리 추가
            for h in history:
                role = h.get("role", "user")
                content = h.get("content", "")
                if role in ["user", "assistant"]:
                    messages.append({"role": role, "content": content})
            
            # 현재 메시지 추가
            messages.append({"role": "user", "content": message})
            
            # API 호출
            headers = {
                "Authorization": f"Bearer {self.upstage_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "solar-1-mini-chat",  # Upstage 모델명
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                UPSTAGE_API_URL,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Upstage API 오류: {response.status_code} - {response.text}")
                return self._fallback_response(message)
        except Exception as e:
            print(f"Upstage API 오류: {e}")
            return self._fallback_response(message)
    
    def summarize_text(
        self,
        text: str,
        target_level: str = "17세",
        provider: Optional[str] = None
    ) -> str:
        """
        텍스트 요약 생성
        - target_level: 요약 대상 수준 (예: "17세", "초등학생")
        """
        provider = provider or self.default_provider
        
        prompt = f"""다음 복지 정보를 {target_level} 청소년이 이해하기 쉽도록 간단하고 명확하게 요약해주세요.

요약 시 포함할 내용:
1. 지원 대상 (누가 받을 수 있는지)
2. 지원 내용 (무엇을 받는지, 금액 등)
3. 신청 방법 (어떻게 신청하는지)
4. 신청 기간 (언제까지인지)

원문:
{text}

위 내용을 핵심만 간단하게 요약해주세요."""
        
        return self.generate_chat_response(
            message=prompt,
            history=[],
            system_prompt="당신은 복지 정보를 쉽게 설명하는 전문가입니다.",
            provider=provider
        )
    
    def analyze_sentiment(self, text: str, provider: Optional[str] = None) -> Dict:
        """
        감정 분석
        - 긍정/부정/중립 판단
        """
        provider = provider or self.default_provider
        
        prompt = f"""다음 텍스트의 감정을 분석해주세요. 
긍정, 부정, 중립 중 하나로 분류하고, 감정 점수를 0.0(매우 부정)부터 1.0(매우 긍정)까지 숫자로 제공해주세요.

텍스트: {text}

응답 형식: JSON 형식으로 {{"sentiment": "긍정/부정/중립", "score": 0.0~1.0}}"""
        
        try:
            response = self.generate_chat_response(
                message=prompt,
                history=[],
                system_prompt="당신은 감정 분석 전문가입니다.",
                provider=provider
            )
            
            # JSON 파싱 시도
            try:
                result = json.loads(response)
                return result
            except:
                # JSON이 아닌 경우 텍스트에서 추출
                if "긍정" in response:
                    return {"sentiment": "positive", "score": 0.7}
                elif "부정" in response:
                    return {"sentiment": "negative", "score": 0.3}
                else:
                    return {"sentiment": "neutral", "score": 0.5}
        except Exception as e:
            print(f"감정 분석 오류: {e}")
            return {"sentiment": "neutral", "score": 0.5}
    
    def _fallback_response(self, message: str) -> str:
        """API 실패 시 기본 응답"""
        if any(word in message for word in ["힘들", "어려", "스트레스"]):
            return "지금 힘든 상황이시군요. 그런 감정을 느끼는 것은 당연해요. 혹시 이 상황에서 작은 변화를 만들어볼 수 있는 부분이 있을까요?"
        elif any(word in message for word in ["고마", "감사", "좋"]):
            return "좋은 감정을 느끼고 계시는군요! 그런 긍정적인 순간들을 기록해보시는 것도 좋을 것 같아요."
        else:
            return "말씀해주셔서 감사해요. 더 자세히 들려주실 수 있나요?"


# 싱글톤 인스턴스
llm_client = LLMClient()

"""
복지로 크롤링 유틸리티 함수
"""
from datetime import datetime
import re
from typing import Optional, Tuple


def parse_date_range(date_text: str) -> Tuple[Optional[datetime], Optional[datetime], bool]:
    """
    복지로의 날짜 텍스트를 파싱하여 시작일, 종료일, 상시신청 여부를 반환
    
    Args:
        date_text: 날짜 텍스트 (예: "2025.01.01 ~ 2025.12.31", "상시신청")
    
    Returns:
        (start_date, end_date, is_always): 시작일, 종료일, 상시신청 여부
    """
    if not date_text:
        return None, None, False
    
    date_text = date_text.strip()
    
    # Case 1: "상시신청" 또는 "연중"이 포함된 경우
    if "상시" in date_text or "연중" in date_text or "무기한" in date_text:
        return None, None, True
    
    # Case 2: 날짜 범위 파싱 (예: 2025.01.01 ~ 2025.12.31 또는 2025-01-01 ~ 2025-12-31)
    # 정규식으로 날짜 패턴(YYYY.MM.DD 또는 YYYY-MM-DD) 찾기
    dates = re.findall(r'\d{4}[.-]\d{2}[.-]\d{2}', date_text)
    
    if len(dates) >= 2:
        # 시작일과 종료일이 모두 있는 경우
        start_date_str = dates[0].replace('.', '-')
        end_date_str = dates[-1].replace('.', '-')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            return start_date, end_date, False
        except ValueError:
            return None, None, False
    
    elif len(dates) == 1:
        # 마감일만 있는 경우
        end_date_str = dates[0].replace('.', '-')
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            return None, end_date, False
        except ValueError:
            return None, None, False
    
    return None, None, False


def check_is_active(date_text: str) -> bool:
    """
    복지로의 날짜 텍스트를 받아 현재 유효한지 판단하는 함수
    
    Args:
        date_text: 날짜 텍스트
    
    Returns:
        True(유효함), False(만료됨)
    """
    today = datetime.now().date()
    
    start_date, end_date, is_always = parse_date_range(date_text)
    
    # 상시신청인 경우
    if is_always:
        return True
    
    # 종료일이 있고 오늘보다 이전이면 만료
    if end_date and end_date < today:
        return False
    
    # 시작일이 있고 오늘보다 이후면 아직 시작 안함 (유효하지 않음)
    if start_date and start_date > today:
        return False
    
    return True


def determine_status(date_text: str) -> str:
    """
    날짜 텍스트를 기반으로 status를 결정
    
    Args:
        date_text: 날짜 텍스트
    
    Returns:
        'active', 'closed', 'expired' 중 하나
    """
    if not date_text:
        return 'active'
    
    start_date, end_date, is_always = parse_date_range(date_text)
    today = datetime.now().date()
    
    if is_always:
        return 'active'
    
    if end_date and end_date < today:
        return 'expired'
    
    if start_date and start_date > today:
        return 'closed'
    
    return 'active'


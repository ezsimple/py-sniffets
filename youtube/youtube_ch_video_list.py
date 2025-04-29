import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os
import sys
from dotenv import load_dotenv
from googleapiclient.discovery import build
from urllib.parse import parse_qs, urlparse

def clean_filename(username):
    """특수문자를 제거하고 소문자로 변환하는 함수"""
    # @ 및 기타 특수문자 제거
    cleaned = re.sub(r'[^\w\s]', '', username)
    # 언더스코어를 공백으로 변환
    cleaned = cleaned.replace('_', '')
    # 소문자로 변환
    return cleaned.lower()

def get_channel_videos_with_api(channel_id, api_key, max_results=500):
    """YouTube API를 사용하여 채널의 모든 동영상 정보 가져오기"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 채널의 업로드 재생목록 ID 가져오기
    channel_response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # 업로드된 동영상 목록 가져오기
    videos = []
    next_page_token = None
    
    print("동영상 데이터 수집 중...")
    page_count = 0
    
    while True:
        page_count += 1
        print(f"페이지 {page_count} 로딩 중...")
        
        playlist_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=50,  # API 한 번 요청당 최대 50개
            pageToken=next_page_token
        ).execute()
        
        for item in playlist_response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            url = f"https://www.youtube.com/watch?v={video_id}"
            # 작성 날짜 추가
            published_at = item['snippet']['publishedAt'][:10]  # YYYY-MM-DD 형식으로 가져오기
            
            videos.append({
                'title': title,
                'url': url,
                'video_id': video_id,
                'published_at': published_at
            })
        
        next_page_token = playlist_response.get('nextPageToken')
        print(f"현재까지 {len(videos)}개의 동영상 수집됨")
        
        if not next_page_token or len(videos) >= max_results:
            break
    
    print(f"총 {len(videos)}개의 동영상 데이터 수집 완료")
    
    # 쇼츠 영상 필터링
    shorts = []
    normal_videos = []
    
    # 쇼츠 여부 확인을 위한 동영상 정보 추가 요청
    video_ids = [video['video_id'] for video in videos]
    total_videos = len(video_ids)
    processed = 0
    
    print("쇼츠 영상 식별 중...")
    
    # 50개씩 나누어 요청 (API 제한)
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        processed += len(chunk)
        print(f"진행 중: {processed}/{total_videos} ({processed/total_videos*100:.1f}%)")
        
        video_response = youtube.videos().list(
            part='snippet,contentDetails',
            id=','.join(chunk)
        ).execute()
        
        for item in video_response.get('items', []):
            video_id = item['id']
            duration = item['contentDetails']['duration']
            
            # PT1M이하의 세로 비율 동영상을 쇼츠로 간주
            # 실제로는 더 정확한 판별이 필요할 수 있음
            is_short = 'M' not in duration or (int(re.search(r'PT(\d+)M', duration).group(1)) <= 1 if re.search(r'PT(\d+)M', duration) else False)
            
            video_info = next((v for v in videos if v['video_id'] == video_id), None)
            if video_info:
                if is_short:
                    video_info['url'] = f"https://www.youtube.com/shorts/{video_id}"
                    shorts.append(video_info)
                else:
                    normal_videos.append(video_info)
    
    return shorts, normal_videos

def get_channel_id_from_username(username, api_key):
    """채널 사용자 이름으로 채널 ID 찾기"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 채널 username으로 검색
    try:
        response = youtube.search().list(
            part='snippet',
            q=username,
            type='channel',
            maxResults=1
        ).execute()
        
        if 'items' in response and response['items']:
            return response['items'][0]['id']['channelId']
    except Exception as e:
        print(f"채널 검색 중 오류: {str(e)}")
    
    print("채널 ID를 찾을 수 없습니다. 직접 입력해주세요.")
    channel_id = input("채널 ID를 입력하세요 (예: UCp-vBtwvBmDiGqjvLjChaJw): ")
    return channel_id

def extract_videos_without_api(channel_url):
    """
    API 없이 웹 페이지 스크래핑으로 동영상 정보 추출 (참고용)
    YouTube는 동적 콘텐츠를 사용하므로 이 방법은 Selenium 등이 필요할 수 있음
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    response = requests.get(channel_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    videos = []
    
    # 초기 데이터 추출 시도 (YouTube의 내부 구조가 바뀌면 작동하지 않을 수 있음)
    scripts = soup.find_all('script')
    for script in scripts:
        if 'var ytInitialData' in script.text:
            json_str = re.search(r'var ytInitialData = (.+);</script>', script.text)
            if json_str:
                data = json.loads(json_str.group(1))
                # 여기서 데이터 구조를 파싱해야 하지만 YouTube의 내부 구조가 자주 변경됨
    
    print("스크래핑 결과: YouTube의 동적 콘텐츠 구조상 API 사용이 권장됩니다.")
    return videos

def save_to_csv(videos, filename):
    """동영상 정보를 CSV 파일로 저장"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['published_at', 'title', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for video in videos:
            writer.writerow({
                'published_at': video['published_at'],
                'title': video['title'],
                'url': video['url']
            })
    print(f"{filename}에 {len(videos)}개의 동영상 정보가 저장되었습니다.")

def main():
    # .env 파일에서 API 키 로드
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API")
    
    username = "@ZeroChoTV"
    if len(sys.argv) > 1:
        # 첫 번째 인수를 채널 이름으로 사용
        username = sys.argv[1]
        # '@' 접두사가 없으면 추가
        if not username.startswith('@'):
            username = '@' + username

    channel_url = f"https://www.youtube.com/{username}/shorts"
    filename = clean_filename(username)
    
    print("YouTube 동영상 정보 추출 도구")
    print("-" * 40)
    print(f"채널: {username}")
    
    # API 키가 .env 파일에 없으면 사용자 입력 요청
    if not api_key:
        api_key = input("YouTube API 키를 입력하세요 (API 키가 없으면 Enter): ")
    
    if api_key:
        try:
            # 사용자에게 가져올 동영상 수 입력받기
            max_videos = input("가져올 최대 동영상 수를 입력하세요 (기본값: 500, 모두 가져오려면 0 입력): ")
            max_videos = int(max_videos) if max_videos and max_videos.isdigit() else 500
            if max_videos == 0:
                max_videos = 10000  # 사실상 제한 없음
            
            channel_id = get_channel_id_from_username(username, api_key)
            if channel_id:
                print(f"채널 ID: {channel_id}")
                print(f"최대 {max_videos}개의 동영상을 가져옵니다...")
                shorts, videos = get_channel_videos_with_api(channel_id, api_key, max_videos)
                
                # 작성일 기준으로 정렬 (최신순)
                shorts.sort(key=lambda x: x['published_at'], reverse=True)
                videos.sort(key=lambda x: x['published_at'], reverse=True)
                
                print(f"\n총 {len(shorts)} 개의 쇼츠 동영상과 {len(videos)} 개의 일반 동영상을 찾았습니다.")
                
                # 쇼츠 동영상 정보 저장
                if shorts:
                    save_to_csv(shorts, f"{filename}_shorts.csv")
                    print("\n쇼츠 미리보기 (최대 5개):")
                    for video in shorts[:5]:
                        print(f"제목: {video['title']}")
                        print(f"URL: {video['url']}")
                        print(f"작성일: {video['published_at']}")
                        print("-" * 40)
                
                # 일반 동영상 정보 저장
                if videos:
                    save_to_csv(videos, f"{filename}_videos.csv")
                    print("\n일반 동영상 미리보기 (최대 5개):")
                    for video in videos[:5]:
                        print(f"제목: {video['title']}")
                        print(f"URL: {video['url']}")
                        print(f"작성일: {video['published_at']}")
                        print("-" * 40)
            else:
                print("채널 ID를 찾을 수 없습니다.")
        except Exception as e:
            print(f"API 사용 중 오류 발생: {str(e)}")
            print("오류 세부 정보:", e)
            import traceback
            traceback.print_exc()
            print("API 없이 계속하려면 Enter를 누르세요.")
    else:
        print("API 키가 제공되지 않았습니다. 웹 스크래핑 방법은 YouTube의 정책 및 기술적 제한으로 인해 정확하지 않을 수 있습니다.")
        print("YouTube Data API를 사용하는 것이 권장됩니다: https://developers.google.com/youtube/v3/getting-started")
        
        choice = input("계속 진행하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            videos = extract_videos_without_api(channel_url)

if __name__ == "__main__":
    main()

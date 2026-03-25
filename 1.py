import os
import re
import shutil
import subprocess

# --- [사용자 설정 구간] ---

# 1. 옵시디언 원본 파일 및 이미지 폴더 (이 경로는 고정되어 있으니 그대로 둡니다)
SOURCE_FILE = r'C:\Users\win\Documents\my_obisidan_vault\강의\운영체제\COMPUTER SYSTEM OVERVIEW 1-1.md'
SOURCE_IMAGE_FOLDER = r'C:\Users\win\Documents\my_obisidan_vault\image'

# 2. GitHub 저장소 경로 자동 설정
# 현재 실행 중인 1.py 파일이 있는 폴더를 저장소 경로로 인식합니다.
GITHUB_REPO_PATH = os.path.dirname(os.path.abspath(__file__))

# 3. 저장소 내 이미지가 들어갈 폴더 이름
REL_IMAGE_DIR = 'images'

# ----------------------------------------------

def sync_to_github():
    # 저장소 폴더 존재 확인
    if not os.path.exists(GITHUB_REPO_PATH):
        print(f"오류: 저장소 경로를 찾을 수 없습니다: {GITHUB_REPO_PATH}")
        return

    target_img_dir = os.path.join(GITHUB_REPO_PATH, REL_IMAGE_DIR)
    os.makedirs(target_img_dir, exist_ok=True)

    # 1. 문서 읽기
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"오류: 원본 문서를 찾을 수 없습니다: {SOURCE_FILE}")
        return

    # 2. 이미지 링크 추출 및 처리
    img_pattern = re.compile(r'!\[\[(.*?\.(?:png|jpg|jpeg|gif|svg))\]\]')
    matches = img_pattern.findall(content)

    print(f"--- 작업 시작: {os.path.basename(SOURCE_FILE)} ---")

    for img_name in matches:
        src_path = os.path.join(SOURCE_IMAGE_FOLDER, img_name)
        dst_path = os.path.join(target_img_dir, img_name)

        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            new_link = f'![{img_name}]({REL_IMAGE_DIR}/{img_name})'
            content = content.replace(f'![[{img_name}]]', new_link)
            print(f" - 이미지 복사 완료: {img_name}")
        else:
            print(f" - [경고] 이미지 파일을 찾을 수 없음: {img_name}")

    # 3. 변환된 문서를 GitHub 저장소에 저장 (이미지가 있는 폴더와 같은 위치)
    target_file_name = os.path.basename(SOURCE_FILE)
    target_file_path = os.path.join(GITHUB_REPO_PATH, target_file_name)
    
    with open(target_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f" - 문서 변환 완료: {target_file_name}")

    # 4. Git 명령 실행
    try:
        os.chdir(GITHUB_REPO_PATH)
        # .git 폴더가 있는지 확인
        if not os.path.exists(os.path.join(GITHUB_REPO_PATH, '.git')):
            print("오류: 이 폴더는 Git 저장소가 아닙니다. 'git init'이나 클론이 필요합니다.")
            return

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Update: {target_file_name}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("\n[성공] 모든 작업이 완료되어 GitHub에 업로드되었습니다!")
    except subprocess.CalledProcessError as e:
        print(f"\n[알림] Git 업로드 중 오류 발생 (변경사항이 없거나 인증 문제): {e}")
    except Exception as e:
        print(f"\n[오류] 예상치 못한 오류: {e}")

if __name__ == "__main__":
    sync_to_github()
import os
import yaml

def generate_front_matter(file_name):
    front_matter = {
        'layout': 'post',  # 레이아웃 설정 (예: post, page 등)
        'title': 'Your Title',  # 제목 설정
        # 추가적인 메타데이터 필드를 여기에 추가할 수 있습니다.
    }
    return '---\n' + yaml.dump(front_matter, default_flow_style=False) + '---\n'

def add_front_matter_to_files(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith('.md'):  # 마크다운 파일만 처리
            file_path = os.path.join(directory, file_name)
            with open(file_path, 'r+') as file:
                content = file.read()
                if not content.startswith('---'):  # YAML Front Matter가 없는 경우에만 추가
                    file.seek(0, 0)
                    file.write(generate_front_matter(file_name) + content)

# 지정된 디렉토리 내의 파일들에 대해 YAML Front Matter를 추가합니다.
add_front_matter_to_files('/path/to/your/directory')

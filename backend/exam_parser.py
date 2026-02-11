"""
考卷 Markdown 解析器
解析 Markdown 格式的考卷，提取題目、選項和答案
"""

import re
from typing import List, Dict, Optional
from pathlib import Path


class ExamParser:
    """考卷解析器"""
    
    def __init__(self, markdown_content: str):
        self.content = markdown_content
        self.questions = []
        self.answers = {}
        
    def parse(self) -> Dict:
        """
        解析考卷
        返回: {
            'title': str,
            'subject': str,
            'questions': [
                {
                    'id': int,
                    'subject': str,
                    'question': str,
                    'options': [
                        {'label': 'A', 'text': '...'},
                        {'label': 'B', 'text': '...'},
                        {'label': 'C', 'text': '...'},
                        {'label': 'D', 'text': '...'}
                    ],
                    'correct_answer': str
                }
            ]
        }
        """
        # 解析標題
        title = self._extract_title()
        
        # 解析題目
        self._parse_questions()
        
        # 解析答案
        self._parse_answers()
        
        # 合併題目和答案
        for q in self.questions:
            q_id = q['id']
            if q_id in self.answers:
                q['correct_answer'] = self.answers[q_id]
        
        # 判斷科目（如果是綜合卷，根據題目數量判斷）
        subject = self._determine_subject()
        
        return {
            'title': title,
            'subject': subject,
            'questions': self.questions,
            'total_questions': len(self.questions)
        }
    
    def _extract_title(self) -> str:
        """提取標題"""
        match = re.search(r'^#\s+(.+)', self.content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "模擬考試"
    
    def _determine_subject(self) -> str:
        """判斷科目"""
        if '國語' in self.content[:500]:
            if '英語' in self.content[:500] or '數學' in self.content[:500]:
                return "綜合科"
            return "國語科"
        elif '英語' in self.content[:500] or 'English' in self.content[:500]:
            return "英語科"
        elif '數學' in self.content[:500]:
            return "數學科"
        return "綜合科"
    
    def _parse_questions(self):
        """解析題目區"""
        # 找到題目區（在 "參考答案" 或 "### 答案" 之前的內容）
        question_section = re.split(r'##\s+參考答案|###\s+.*答案', self.content)[0]
        
        current_subject = "綜合科"
        
        # 更精確的解析方式
        lines = question_section.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 檢測科目標題（保留中文數字）
            if re.match(r'##\s+[一二三四五六七八九十]、(.+科)', line):
                subject_match = re.search(r'##\s+[一二三四五六七八九十]、(.+科)', line)
                if subject_match:
                    current_subject = subject_match.group(1)
                i += 1
                continue
            
            # 檢測題目開頭（數字. 開頭，但要小心縮排）
            # 題目可能有縮排空格
            question_match = re.match(r'^(\d+)\.\s+(.+)', line)
            if question_match:
                q_id = int(question_match.group(1))
                q_text = question_match.group(2)
                
                # 移除 <br> 標籤
                q_text = q_text.replace('<br>', '').strip()
                
                # 向下查找選項（選項前面可能有空格縮排）
                i += 1
                options = []
                
                while i < len(lines):
                    # 不要 strip，保留原始格式以檢查縮排
                    option_line = lines[i]
                    option_line_stripped = option_line.strip()
                    
                    # 如果是空行，跳過
                    if not option_line_stripped:
                        i += 1
                        # 空行可能代表選項結束
                        if len(options) >= 4:
                            break
                        continue
                    
                    # 匹配選項 (A) ... 或 (B) ... 等（允許前面有空格）
                    option_match = re.match(r'^\s*\(([A-D])\)\s+(.+)', option_line)
                    if option_match:
                        label = option_match.group(1)
                        text = option_match.group(2).strip()
                        options.append({
                            'label': label,
                            'text': text
                        })
                        i += 1
                        
                        # 如果已經收集到 4 個選項，結束
                        if len(options) >= 4:
                            break
                    elif option_line_stripped.startswith('#'):
                        # 遇到新的標題，結束
                        break
                    elif re.match(r'^\d+\.', option_line_stripped):
                        # 遇到新的題目，結束
                        break
                    else:
                        # 其他情況：可能是題目的延續
                        if not options:
                            q_text += ' ' + option_line_stripped
                        i += 1
                
                # 確保有 4 個選項才加入
                if len(options) == 4:
                    self.questions.append({
                        'id': q_id,
                        'subject': current_subject,
                        'question': q_text,
                        'options': options
                    })
                # 不要 continue，讓 i 保持在當前位置
                continue
            
            i += 1
    
    def _parse_answers(self):
        """解析答案區（從表格中提取）"""
        # 找到答案區
        answer_section_match = re.search(r'##\s+參考答案(.+?)$', self.content, re.DOTALL)
        if not answer_section_match:
            return
        
        answer_section = answer_section_match.group(1)
        
        # 匹配表格中的答案行
        # 格式: | 1 | (B) | 2.5 | ...
        pattern = r'\|\s*(\d+)\s*\|\s*\(([A-D])\)'
        
        for match in re.finditer(pattern, answer_section):
            q_id = int(match.group(1))
            answer = match.group(2)
            self.answers[q_id] = answer


def parse_exam_file(file_path: Path) -> Optional[Dict]:
    """
    解析考卷檔案
    
    Args:
        file_path: 考卷 Markdown 檔案路徑
    
    Returns:
        考卷資料字典，如果解析失敗則返回 None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = ExamParser(content)
        return parser.parse()
    except Exception as e:
        print(f"解析考卷失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """測試解析器"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python exam_parser.py <考卷.md>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"檔案不存在: {file_path}")
        sys.exit(1)
    
    result = parse_exam_file(file_path)
    if result:
        print(f"\n標題: {result['title']}")
        print(f"科目: {result['subject']}")
        print(f"題數: {result['total_questions']}")
        print(f"\n前 3 題:")
        
        for q in result['questions'][:3]:
            print(f"\n{q['id']}. {q['question']}")
            for opt in q['options']:
                print(f"   ({opt['label']}) {opt['text']}")
            if 'correct_answer' in q:
                print(f"   答案: ({q['correct_answer']})")
    else:
        print("解析失敗")


if __name__ == '__main__':
    main()

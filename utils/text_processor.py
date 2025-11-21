"""
文本处理工具模块
用于处理输入文本的格式化和预处理
"""
import re
import logging
from typing import List, Dict, Optional, Tuple
import jieba

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    """
    文本处理器类
    提供文本分段、分行、格式化等功能
    """
    
    def __init__(self):
        """初始化文本处理器"""
        # 中文字符模式
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
        # 标点符号模式
        self.punctuation_pattern = re.compile(r'[\u3002\uff1f\uff01\uff0c\u3001\uff1b\uff1a\u201c\u201d\u2018\u2019\uff08\uff09\u3014\u3015\u300a\u300b\u3008\u3009\uff5e\ufe4f]')
        # 英文标点符号
        self.en_punctuation = '.?!,;:"\'()[]{}\<>'
    
    def split_text_to_paragraphs(self, text: str, max_paragraph_length: int = 200) -> List[str]:
        """
        将文本分割成段落
        
        Args:
            text: 输入文本
            max_paragraph_length: 最大段落长度
            
        Returns:
            段落列表
        """
        if not text:
            return []
        
        paragraphs = []
        current_paragraph = ""
        
        # 按换行符分割
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # 空行通常表示段落结束
            if not line:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                    current_paragraph = ""
                continue
            
            # 如果当前段落加上新行超过最大长度，则分割
            if current_paragraph and len(current_paragraph) + len(line) + 1 > max_paragraph_length:
                # 尝试在标点符号处分割
                split_point = self._find_split_point(current_paragraph + " " + line, max_paragraph_length)
                if split_point > len(current_paragraph):
                    # 如果分割点在新行中，先保存当前段落
                    paragraphs.append(current_paragraph)
                    current_paragraph = line[:split_point - len(current_paragraph) - 1]
                    # 剩余部分放入下一段
                    if split_point - len(current_paragraph) - 1 < len(line):
                        paragraphs.append(line[split_point - len(current_paragraph) - 1:])
                else:
                    # 分割点在当前段落中
                    paragraphs.append(current_paragraph[:split_point])
                    current_paragraph = current_paragraph[split_point:].strip() + " " + line
            else:
                if current_paragraph:
                    current_paragraph += " "
                current_paragraph += line
        
        # 添加最后一段
        if current_paragraph:
            paragraphs.append(current_paragraph)
        
        return paragraphs
    
    def _find_split_point(self, text: str, max_length: int) -> int:
        """
        在适当的位置找到文本分割点
        优先在标点符号后分割
        
        Args:
            text: 输入文本
            max_length: 最大长度
            
        Returns:
            分割点索引
        """
        # 如果文本长度小于最大长度，直接返回
        if len(text) <= max_length:
            return len(text)
        
        # 查找合适的分割点，优先考虑标点符号
        punctuation_marks = ['.', '!', '?', '。', '！', '？', ';', '；', ',', '，']
        
        # 从max_length位置向前查找最近的标点符号
        for i in range(max_length, max_length - 50, -1):
            if i <= 0:
                break
            if text[i-1] in punctuation_marks:
                return i
        
        # 如果没找到合适的标点符号，就直接在max_length处分割
        return max_length
    
    def split_paragraph_to_lines(self, paragraph: str, font_size: int, page_width: int, margin: int = 30) -> List[str]:
        """
        将段落分割成适合页面宽度的行
        
        Args:
            paragraph: 输入段落
            font_size: 字体大小（像素）
            page_width: 页面宽度（像素）
            margin: 边距（像素）
            
        Returns:
            行列表
        """
        if not paragraph:
            return []
        
        # 估算每个字符的宽度（对于等宽字体更准确）
        char_width_estimate = font_size * 0.5  # 粗略估计
        available_width = page_width - 2 * margin
        max_chars_per_line = int(available_width / char_width_estimate)
        
        lines = []
        current_line = ""
        
        # 如果是中文文本，使用jieba分词
        if self._contains_chinese(paragraph):
            words = list(jieba.cut(paragraph))
            
            for word in words:
                # 如果当前行加上新词超过最大字符数，换行
                if len(current_line + word) > max_chars_per_line:
                    # 处理标点符号，避免标点符号在行首
                    if word and word[0] in self.punctuation_pattern.findall(word):
                        # 将标点符号移到上一行
                        if current_line:
                            current_line += word[0]
                            word = word[1:]
                    
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line += word
            
            # 添加最后一行
            if current_line:
                lines.append(current_line)
        else:
            # 对于英文和其他语言，按空格分割
            words = paragraph.split()
            
            for word in words:
                # 如果当前行加上新词超过最大字符数，换行
                if len(current_line + " " + word) > max_chars_per_line and current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    if current_line:
                        current_line += " "
                    current_line += word
            
            # 添加最后一行
            if current_line:
                lines.append(current_line)
        
        return lines
    
    def _contains_chinese(self, text: str) -> bool:
        """
        检查文本是否包含中文字符
        
        Args:
            text: 输入文本
            
        Returns:
            是否包含中文字符
        """
        return bool(self.chinese_pattern.search(text))
    
    def format_text(self, text: str, format_type: str = "normal") -> str:
        """
        格式化文本
        
        Args:
            text: 输入文本
            format_type: 格式化类型 (normal, remove_extra_spaces, remove_newlines, uppercase, lowercase)
            
        Returns:
            格式化后的文本
        """
        if not text:
            return ""
        
        if format_type == "remove_extra_spaces":
            # 移除多余的空格
            text = re.sub(r'\s+', ' ', text).strip()
        elif format_type == "remove_newlines":
            # 移除换行符
            text = text.replace('\n', ' ')
        elif format_type == "uppercase":
            # 转换为大写
            text = text.upper()
        elif format_type == "lowercase":
            # 转换为小写
            text = text.lower()
        elif format_type == "normal":
            # 标准格式化：移除多余空格和空行
            text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        
        return text
    
    def count_characters(self, text: str, include_punctuation: bool = True) -> Dict[str, int]:
        """
        统计文本字符数
        
        Args:
            text: 输入文本
            include_punctuation: 是否包含标点符号
            
        Returns:
            字符统计字典
        """
        if not text:
            return {"total": 0, "chinese": 0, "english": 0, "digits": 0, "punctuation": 0}
        
        # 过滤标点符号（如果需要）
        if not include_punctuation:
            text = self.punctuation_pattern.sub('', text)
            for p in self.en_punctuation:
                text = text.replace(p, '')
        
        # 统计各类字符
        chinese_count = len(self.chinese_pattern.findall(text))
        english_count = len(re.findall(r'[a-zA-Z]', text))
        digit_count = len(re.findall(r'\d', text))
        punctuation_count = len(self.punctuation_pattern.findall(text)) + \
                           sum(1 for char in text if char in self.en_punctuation)
        
        total = len(text)
        
        return {
            "total": total,
            "chinese": chinese_count,
            "english": english_count,
            "digits": digit_count,
            "punctuation": punctuation_count
        }
    
    def add_line_breaks_for_handwriting(self, text: str, font_size: int, page_width: int, 
                                       margin: int = 30, line_spacing: int = 5) -> Tuple[List[str], int]:
        """
        为手写体生成添加适当的换行符
        
        Args:
            text: 输入文本
            font_size: 字体大小
            page_width: 页面宽度
            margin: 边距
            line_spacing: 行距
            
        Returns:
            (处理后的行列表, 总行数)
        """
        paragraphs = self.split_text_to_paragraphs(text)
        all_lines = []
        
        for paragraph in paragraphs:
            lines = self.split_paragraph_to_lines(paragraph, font_size, page_width, margin)
            all_lines.extend(lines)
            # 段落之间添加一个空行
            all_lines.append("")
        
        # 移除最后的空行
        if all_lines and not all_lines[-1]:
            all_lines.pop()
        
        return all_lines, len(all_lines)
    
    def estimate_page_count(self, text: str, font_size: int, page_width: int, page_height: int,
                           margin: int = 30, line_spacing: int = 5) -> int:
        """
        估算需要的页面数
        
        Args:
            text: 输入文本
            font_size: 字体大小
            page_width: 页面宽度
            page_height: 页面高度
            margin: 边距
            line_spacing: 行距
            
        Returns:
            估算的页面数
        """
        # 计算每页可显示的行数
        line_height = font_size + line_spacing
        available_height = page_height - 2 * margin
        max_lines_per_page = int(available_height / line_height)
        
        # 计算总行数
        _, total_lines = self.add_line_breaks_for_handwriting(text, font_size, page_width, margin, line_spacing)
        
        # 计算页数
        page_count = (total_lines + max_lines_per_page - 1) // max_lines_per_page
        
        return max(1, page_count)  # 至少1页
    
    def clean_text(self, text: str) -> str:
        """
        清理文本中的特殊字符
        
        Args:
            text: 输入文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除不可打印字符
        text = ''.join(char for char in text if char.isprintable() or char in '\t\n\r')
        
        # 替换制表符为空格
        text = text.replace('\t', '    ')
        
        # 标准化换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    def process_for_handwriting(self, text: str, config: Dict) -> Dict:
        """
        为手写体生成处理文本
        
        Args:
            text: 输入文本
            config: 配置参数
            
        Returns:
            处理结果字典
        """
        # 清理文本
        cleaned_text = self.clean_text(text)
        
        # 获取配置参数
        font_size = int(config.get("font_size", 16))
        # 根据页面大小计算页面尺寸
        page_size = config.get("page_size", "A5 横版")
        
        # A5尺寸：148 x 210 mm
        # A4尺寸：210 x 297 mm
        # 转换为像素（假设300 DPI）
        dpi = 300
        mm_to_inch = 0.0393701
        
        if page_size == "A5 横版":
            page_width = int(210 * mm_to_inch * dpi)
            page_height = int(148 * mm_to_inch * dpi)
        elif page_size == "A5 竖版":
            page_width = int(148 * mm_to_inch * dpi)
            page_height = int(210 * mm_to_inch * dpi)
        elif page_size == "A4 横版":
            page_width = int(297 * mm_to_inch * dpi)
            page_height = int(210 * mm_to_inch * dpi)
        elif page_size == "A4 竖版":
            page_width = int(210 * mm_to_inch * dpi)
            page_height = int(297 * mm_to_inch * dpi)
        else:
            # 默认为A5横版
            page_width = int(210 * mm_to_inch * dpi)
            page_height = int(148 * mm_to_inch * dpi)
        
        margin = int(config.get("margin", 30))
        line_spacing = int(config.get("line_spacing", 5))
        
        # 分割文本为行
        lines, total_lines = self.add_line_breaks_for_handwriting(
            cleaned_text, font_size, page_width, margin, line_spacing
        )
        
        # 估算页数
        page_count = self.estimate_page_count(
            cleaned_text, font_size, page_width, page_height, margin, line_spacing
        )
        
        # 统计字符
        char_count = self.count_characters(cleaned_text)
        
        return {
            "lines": lines,
            "total_lines": total_lines,
            "page_count": page_count,
            "char_count": char_count,
            "page_size": (page_width, page_height)
        }

# 测试函数
def test_text_processor():
    """测试文本处理器功能"""
    processor = TextProcessor()
    
    # 测试文本
    test_text = "这是一个测试文本，用于测试文本处理器的功能。这个文本包含中文、英文和数字。\n\n"
    test_text += "这是第二段。This is a test in English. 1234567890。\n"
    test_text += "这是第三段，包含一些标点符号：！？，；："'（）[]{}。"
    
    print("原始文本:")
    print(test_text)
    print("\n")
    
    # 测试段落分割
    paragraphs = processor.split_text_to_paragraphs(test_text)
    print("分割后的段落:")
    for i, para in enumerate(paragraphs):
        print(f"段落 {i+1}: {para}")
    print("\n")
    
    # 测试行分割
    print("分割后的行:")
    for i, para in enumerate(paragraphs):
        print(f"段落 {i+1} 的行:")
        lines = processor.split_paragraph_to_lines(para, 16, 800, 30)
        for j, line in enumerate(lines):
            print(f"  行 {j+1}: {line}")
    print("\n")
    
    # 测试字符统计
    char_count = processor.count_characters(test_text)
    print("字符统计:")
    print(char_count)
    print("\n")
    
    # 测试页面数估算
    config = {
        "font_size": 16,
        "page_size": "A5 横版",
        "margin": 30,
        "line_spacing": 5
    }
    result = processor.process_for_handwriting(test_text, config)
    print("手写体处理结果:")
    print(f"总行数: {result['total_lines']}")
    print(f"估算页数: {result['page_count']}")
    print(f"页面尺寸: {result['page_size']}")
    print("\n")

if __name__ == "__main__":
    test_text_processor()
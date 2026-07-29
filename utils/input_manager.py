#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Input Manager - Pop Assistant
Bộ gõ thông minh hỗ trợ Telex và Tự động sửa chính tả (Auto-correct)
"""

import re
from collections import Counter

class SmartInputManager:
    def __init__(self):
        # 1. Quy tắc Telex
        self.telex_map = {
            'aa': 'â', 'aw': 'ă', 'ee': 'ê', 'oo': 'ô', 'ow': 'ơ', 'uw': 'ư', 'dd': 'đ'
        }
        # Bảng tra cứu: Chữ gốc + Dấu khác -> Chữ có dấu mục tiêu
        self.tone_map = {
            's': {'a': 'á', 'à': 'á', 'ả': 'á', 'ã': 'á', 'ạ': 'á', 'â': 'ấ', 'ă': 'ắ', 'ê': 'ế', 'ô': 'ố', 'ơ': 'ớ', 'ư': 'ứ', 'u': 'ú', 'i': 'í', 'o': 'ó', 'e': 'é'},
            'f': {'a': 'à', 'á': 'à', 'ả': 'à', 'ã': 'à', 'ạ': 'à', 'â': 'ầ', 'ă': 'ằ', 'ê': 'ề', 'ô': 'ồ', 'ơ': 'ờ', 'ư': 'ừ', 'u': 'ù', 'i': 'ì', 'o': 'ò', 'e': 'è'},
            'r': {'a': 'ả', 'á': 'ả', 'à': 'ả', 'ã': 'ả', 'ạ': 'ả', 'â': 'ẩ', 'ă': 'ẳ', 'ê': 'ể', 'ô': 'ổ', 'ơ': 'ở', 'ư': 'ử', 'u': 'ủ', 'i': 'ỉ', 'o': 'ỏ', 'e': 'ẻ'},
            'x': {'a': 'ã', 'á': 'ã', 'à': 'ã', 'ả': 'ã', 'ạ': 'ã', 'â': 'ẫ', 'ă': 'ẵ', 'ê': 'ễ', 'ô': 'ỗ', 'ơ': 'ỡ', 'ư': 'ữ', 'u': 'ũ', 'i': 'ĩ', 'o': 'õ', 'e': 'ẽ'},
            'j': {'a': 'ạ', 'á': 'ạ', 'à': 'ạ', 'ả': 'ạ', 'ã': 'ạ', 'â': 'ậ', 'ă': 'ặ', 'ê': 'ệ', 'ô': 'ộ', 'ơ': 'ợ', 'ư': 'ự', 'u': 'ụ', 'i': 'ị', 'o': 'ọ', 'e': 'ẹ'},
        }
        # Bảng tra cứu ngược: Chữ có dấu -> Chữ gốc (dùng để HỦY dấu - Toggle)
        self.reverse_tone_map = {}
        for tone_key, mapping in self.tone_map.items():
            self.reverse_tone_map[tone_key] = {v: k for k, v in mapping.items()}

        self.vowels = 'aeiouyâăêôơư'

        # 2. Từ điển cơ bản để sửa chính tả
        self.dictionary = {
            "tiếng": 10, "việt": 10, "chào": 10, "bạn": 10, "tôi": 10, 
            "là": 10, "của": 10, "được": 10, "không": 10, "có": 10,
            "người": 10, "trường": 10, "đường": 10, "học": 10, "làm": 10
        }

    def _levenshtein_distance(self, s1, s2):
        """Tính khoảng cách chỉnh sửa giữa hai chuỗi để tìm từ gần nhất"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if not s2:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def _get_best_correction(self, word):
        """Tìm từ đúng nhất trong từ điển cho một từ bị sai"""
        if word.lower() in self.dictionary:
            return word
        
        best_word = word
        min_distance = 3 
        
        for dict_word in self.dictionary.keys():
            dist = self._levenshtein_distance(word.lower(), dict_word)
            if dist < min_distance:
                min_distance = dist
                best_word = dict_word
        
        return best_word

    def process_telex(self, text):
        """Xử lý gõ Telex nâng cao với bảng tra cứu ký tự và Toggle dấu"""
        if not text: return text
        
        result = text
        # Xử lý ký tự ghép trước
        for key, val in self.telex_map.items():
            result = result.replace(key, val)
            
        # Xử lý dấu
        if result and result[-1] in self.tone_map:
            tone_key = result[-1]
            base = result[:-1]
            # Tìm nguyên âm cuối cùng để thay thế
            for i in range(len(base)-1, -1, -1):
                char = base[i].lower()
                
                # LOGIC TOGGLE: Nếu ký tự đã có dấu này -> Hủy dấu (trở về chữ gốc)
                if char in self.reverse_tone_map[tone_key]:
                    replacement = self.reverse_tone_map[tone_key][char]
                    if base[i].isupper():
                        replacement = replacement.upper()
                    return base[:i] + replacement + base[i+1:]
                
                # Nếu chưa có dấu này -> Áp dụng dấu mới
                if char in self.tone_map[tone_key]:
                    replacement = self.tone_map[tone_key][char]
                    if base[i].isupper():
                        replacement = replacement.upper()
                    return base[:i] + replacement + base[i+1:]
            return result
        return result

    def handle_input(self, current_text, new_char, language='vi'):
        """
        Hàm xử lý chính:
        - Nếu là phím Space: Thực hiện Auto-correct từ vừa gõ.
        - Nếu là ký tự: Xử lý bộ gõ (Telex).
        """
        if new_char == ' ':
            words = current_text.split()
            if not words:
                return current_text + ' '
            
            last_word = words[-1]
            corrected = self._get_best_correction(last_word)
            
            words[-1] = corrected
            return ' '.join(words) + ' '

        if language == 'vi' and new_char.isalpha():
            return self.process_telex(current_text + new_char)
            
        return current_text + new_char

# Singleton
input_manager = SmartInputManager()

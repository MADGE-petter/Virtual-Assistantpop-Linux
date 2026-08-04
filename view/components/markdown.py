"""Markdown Renderer - Convert markdown to HTML for Qt."""

import re
from PyQt6.QtGui import QColor
from view.styles.colors import COLORS


class MarkdownRenderer:
    """Convert markdown text to HTML for Qt rich text display."""
    
    # CSS styles for rendered HTML
    CSS = f"""
        <style>
            body {{
                font-family: 'Noto Sans', 'DejaVu Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: {COLORS['text_primary'].name()};
                margin: 0;
                padding: 0;
            }}
            p {{
                margin: 0 0 12px 0;
            }}
            p:last-child {{
                margin-bottom: 0;
            }}
            strong, b {{
                font-weight: 600;
                color: {COLORS['text_primary'].name()};
            }}
            em, i {{
                font-style: italic;
            }}
            code {{
                font-family: 'IBM Plex Mono', 'Fira Code', monospace;
                font-size: 12px;
                background: {COLORS['bg_deep'].name()};
                color: {COLORS['accent_start'].name()};
                padding: 2px 6px;
                border-radius: 4px;
            }}
            pre {{
                font-family: 'IBM Plex Mono', 'Fira Code', monospace;
                font-size: 12px;
                line-height: 1.5;
                background: {COLORS['bg_deep'].name()};
                color: {COLORS['text_primary'].name()};
                padding: 16px;
                border-radius: 12px;
                overflow-x: auto;
                margin: 12px 0;
                border: 1px solid {COLORS['border'].name()};
            }}
            pre code {{
                background: transparent;
                color: inherit;
                padding: 0;
                font-size: inherit;
            }}
            blockquote {{
                border-left: 3px solid {COLORS['accent_start'].name()};
                padding-left: 16px;
                margin: 12px 0;
                color: {COLORS['text_secondary'].name()};
                font-style: italic;
            }}
            ul, ol {{
                margin: 8px 0;
                padding-left: 24px;
            }}
            li {{
                margin: 4px 0;
            }}
            h1, h2, h3, h4 {{
                margin: 16px 0 8px 0;
                font-weight: 600;
                color: {COLORS['text_primary'].name()};
            }}
            h1 {{ font-size: 24px; }}
            h2 {{ font-size: 20px; }}
            h3 {{ font-size: 18px; }}
            h4 {{ font-size: 16px; }}
            a {{
                color: {COLORS['accent_start'].name()};
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            hr {{
                border: none;
                border-top: 1px solid {COLORS['border'].name()};
                margin: 16px 0;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 12px 0;
                font-size: 13px;
            }}
            th, td {{
                border: 1px solid {COLORS['border'].name()};
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background: {COLORS['bg_card'].name()};
                font-weight: 600;
            }}
            tr:nth-child(even) td {{
                background: {COLORS['bg_deep'].name()};
            }}
        </style>
    """
    
    @classmethod
    def render(cls, text: str) -> str:
        """Convert markdown to HTML."""
        if not text:
            return ""
        
        html = text
        
        # Escape HTML first
        html = cls._escape_html(html)
        
        # Process in order
        html = cls._parse_code_blocks(html)
        html = cls._parse_inline_code(html)
        html = cls._parse_bold_italic(html)
        html = cls._parse_headers(html)
        html = cls._parse_blockquotes(html)
        html = cls._parse_lists(html)
        html = cls._parse_links(html)
        html = cls._parse_hr(html)
        html = cls._parse_tables(html)
        html = cls._parse_paragraphs(html)
        
        return f"<html><head>{cls.CSS}</head><body>{html}</body></html>"
    
    @staticmethod
    def _escape_html(text: str) -> str:
        return (text
            .replace("&", "&")
            .replace("<", "<")
            .replace(">", ">")
            .replace('"', '"').replace("'", "'"))
    
    @classmethod
    def _parse_code_blocks(cls, text: str) -> str:
        """Parse ```code blocks```."""
        def replace_code(match):
            lang = match.group(1) or ""
            code = match.group(2)
            return f"<pre><code class='language-{lang}'>{code}</code></pre>"
        
        pattern = r"```(\w*)\n([\s\S]*?)```"
        return re.sub(pattern, replace_code, text)
    
    @classmethod
    def _parse_inline_code(cls, text: str) -> str:
        """Parse `inline code`."""
        return re.sub(r"`([^`\n]+)`", r"<code>\1</code>", text)
    
    @classmethod
    def _parse_bold_italic(cls, text: str) -> str:
        """Parse **bold**, *italic*, ***bold italic***."""
        # Bold italic
        text = re.sub(r"\*\*\*([^*\n]+)\*\*\*", r"<strong><em>\1</em></strong>", text)
        # Bold
        text = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", text)
        # Italic
        text = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", text)
        # Underscore variants
        text = re.sub(r"___([^_\n]+)___", r"<strong><em>\1</em></strong>", text)
        text = re.sub(r"__([^_\n]+)__", r"<strong>\1</strong>", text)
        text = re.sub(r"_([^_\n]+)_", r"<em>\1</em>", text)
        return text
    
    @classmethod
    def _parse_headers(cls, text: str) -> str:
        """Parse # headers."""
        text = re.sub(r"^####\s+(.+)$", r"<h4>\1</h4>", text, flags=re.MULTILINE)
        text = re.sub(r"^###\s+(.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
        text = re.sub(r"^##\s+(.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
        text = re.sub(r"^#\s+(.+)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)
        return text
    
    @classmethod
    def _parse_blockquotes(cls, text: str) -> str:
        """Parse > blockquotes."""
        lines = text.split('\n')
        in_quote = False
        result = []
        
        for line in lines:
            if line.startswith('> '):
                if not in_quote:
                    result.append("<blockquote>")
                    in_quote = True
                result.append(line[2:])
            else:
                if in_quote:
                    result.append("</blockquote>")
                    in_quote = False
                result.append(line)
        
        if in_quote:
            result.append("</blockquote>")
        
        return '\n'.join(result)
    
    @classmethod
    def _parse_lists(cls, text: str) -> str:
        """Parse - and 1. lists."""
        lines = text.split('\n')
        result = []
        in_ul = False
        in_ol = False
        
        for line in lines:
            ul_match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
            
            if ul_match:
                if in_ol:
                    result.append("</ol>")
                    in_ol = False
                if not in_ul:
                    result.append("<ul>")
                    in_ul = True
                result.append(f"<li>{ul_match.group(2)}</li>")
            elif ol_match:
                if in_ul:
                    result.append("</ul>")
                    in_ul = False
                if not in_ol:
                    result.append("<ol>")
                    in_ol = True
                result.append(f"<li>{ol_match.group(2)}</li>")
            else:
                if in_ul:
                    result.append("</ul>")
                    in_ul = False
                if in_ol:
                    result.append("</ol>")
                    in_ol = False
                result.append(line)
        
        if in_ul:
            result.append("</ul>")
        if in_ol:
            result.append("</ol>")
        
        return '\n'.join(result)
    
    @classmethod
    def _parse_links(cls, text: str) -> str:
        """Parse [link](url)."""
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    @classmethod
    def _parse_hr(cls, text: str) -> str:
        """Parse --- horizontal rules."""
        return re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
    
    @classmethod
    def _parse_tables(cls, text: str) -> str:
        """Parse simple markdown tables."""
        lines = text.split('\n')
        result = []
        in_table = False
        is_header = True
        
        for line in lines:
            if '|' in line and line.count('|') >= 2:
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if not in_table:
                    result.append("<table>")
                    in_table = True
                
                if is_header and all(re.match(r'^[-:]+$', c) for c in cells):
                    is_header = False
                    continue
                
                tag = "th" if is_header else "td"
                row = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
                result.append(f"<tr>{row}</tr>")
                is_header = False
            else:
                if in_table:
                    result.append("</table>")
                    in_table = False
                    is_header = True
                result.append(line)
        
        if in_table:
            result.append("</table>")
        
        return '\n'.join(result)
    
    @classmethod
    def _parse_paragraphs(cls, text: str) -> str:
        """Wrap remaining text in paragraphs."""
        lines = text.split('\n')
        result = []
        in_para = False
        
        for line in lines:
            stripped = line.strip()
            # Skip empty lines
            if not stripped:
                if in_para:
                    result.append("</p>")
                    in_para = False
                result.append("")
                continue
            
            # Skip lines that are already HTML blocks
            if (stripped.startswith(('<h', '<p', '<ul', '<ol', '<blockquote', '<pre', '<table', '<hr', '</')) or
                stripped.endswith(('</h1>', '</h2>', '</h3>', '</h4>', '</p>', '</ul>', '</ol>', '</blockquote>', '</pre>', '</table>'))):
                if in_para:
                    result.append("</p>")
                    in_para = False
                result.append(line)
                continue
            
            if not in_para:
                result.append("<p>")
                in_para = True
            result.append(line)
        
        if in_para:
            result.append("</p>")
        
        return '\n'.join(result)
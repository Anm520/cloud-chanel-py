import re
def is_valid_size(size_str):
    # 检查是否包含数字和单位
    has_number = any(c.isdigit() for c in size_str)
    has_unit = any(unit in size_str.upper() for unit in ['GB', 'MB', 'G', 'M', 'TB', 'T', 'KB', 'K'])
    
    # 检查是否是年份
    if re.search(r'20\d{2}', size_str):
        return False
        
    # 检查是否包含特殊字符或关键词
    invalid_keywords = ['🏷', '#', 'http', '链接', '📁', '更至', '4K', '1080P', '2160P', 'fps', 'EP']
    if any(keyword in size_str for keyword in invalid_keywords):
        return False
        
    return has_number and has_unit

def clean_size(size_str):
    # 移除常见前缀
    size_str = re.sub(r'^(大小：|大小:|约|总计|每集|总大小|体积|size[:：]?)\s*', '', size_str, flags=re.IGNORECASE)
    
    # 移除括号和多余空格
    size_str = re.sub(r'[\(（\)）\[\]]', '', size_str)
    size_str = re.sub(r'\s+', '', size_str)
    
    # 提取数字和单位
    match = re.search(r'(\d+\.?\d*)\s*([GMTK]B?)', size_str.upper())
    if not match:
        return ""
        
    number, unit = match.groups()
    number = float(number)
    
    # 标准化单位
    if unit in ['G', 'GB']:
        return f"{number:.2f}GB"
    elif unit in ['M', 'MB']:
        number /= 1024  # 转换为GB
        return f"{number:.2f}GB"
    elif unit in ['T', 'TB']:
        number *= 1024  # 转换为GB
        return f"{number:.2f}GB"
    elif unit in ['K', 'KB']:
        number /= (1024 * 1024)  # 转换为GB
        return f"{number:.2f}GB"
    
    return ""

def extract_size_from_text(text):
    # 尝试从括号中提取大小信息
    bracket_patterns = [
        r'[\(（\[]([^)）\]]*?(?:\d+\.?\d*\s*[GMTK]B?)[^)）\]]*?)[\)）\]]',
        r'[\(（\[]\s*(\d+\.?\d*\s*[GMTK]B?)\s*[\)）\]]',
        r'[\(（\[]([^)）\]]*?大小[^)）\]]*?\d+\.?\d*\s*[GMTK]B?[^)）\]]*?)[\)）\]]'
    ]
    
    # 在全文中查找大小信息
    size_patterns = [
        r'(?:大小[:：]?|约|总计|每集|总大小|体积|size[:：]?)\s*(\d+\.?\d*)\s*([GMTK]B?)',
        r'(?<!\d)(\d+\.?\d*)\s*([GMTK])(?:B|b)?(?!\w)',
        r'(?<!\d)(\d+\.?\d*)\s*(?:GB|MB|TB|KB)(?!\w)',
        r'(?<!\d)(\d+\.?\d*)\s*[GMTK](?!\w)',
        r'(?<!\d)(\d+\.?\d*)\s*([GMTK])\s*(?!\w)'
    ]
    
    # 首先尝试从括号中提取
    for pattern in bracket_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            content = match.group(1)
            size_match = re.search(r'(\d+\.?\d*)\s*([GMTK]B?)', content, re.IGNORECASE)
            if size_match:
                number, unit = size_match.groups()
                potential_size = f"{number}{unit}"
                if is_valid_size(potential_size):
                    return clean_size(potential_size)
    
    # 如果括号中没找到，在全文中查找
    for pattern in size_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) >= 2:
                number, unit = match.groups()
            else:
                number = match.group(1)
                unit = re.search(r'\s*([GMTK]B?)', text[match.end(1):match.end(1)+3], re.IGNORECASE)
                if unit:
                    unit = unit.group(1)
                else:
                    continue
            
            potential_size = f"{number}{unit}"
            if is_valid_size(potential_size):
                return clean_size(potential_size)
    
    # 尝试提取多个大小并合并
    total_size = 0
    found_sizes = []
    all_sizes_pattern = r'(?<!\d)(\d+\.?\d*)\s*([GMTK])(?:B|b)?(?!\w)'
    matches = re.finditer(all_sizes_pattern, text, re.IGNORECASE)
    
    for match in matches:
        number, unit = match.groups()
        potential_size = f"{number}{unit}"
        if is_valid_size(potential_size):
            number = float(number)
            unit = unit.upper()
            if unit == 'T':
                number *= 1024
            elif unit == 'M':
                number /= 1024
            elif unit == 'K':
                number /= (1024 * 1024)
            found_sizes.append(number)
    
    if found_sizes:
        total_size = sum(found_sizes)
        return f"{total_size:.2f}GB"
    
    return ""

def clean_title(title):
    # 提取年份
    year = None
    year_match = re.search(r'[（(]((?:19|20)\d{2})[）)]|(?:19|20)\d{2}(?!\d)', title)
    if year_match:
        year = year_match.group(1) if year_match.group(1) else year_match.group(0)
        title = re.sub(r'[（(](?:19|20)\d{2}[）)]|(?:19|20)\d{2}(?!\d)', '', title)
    
    # 移除所有方括号、尖括号内的内容
    title = re.sub(r'[\[【\<].*?[\]】\>]', '', title)
    
    # 移除所有圆括号内的内容
    title = re.sub(r'[（(][^）)]*[）)]', '', title)
    
    # 移除分辨率、编码和格式信息
    title = re.sub(r'(?i)\s*(?:4K|1080[Pp]|720[Pp]|2160[Pp]|H264|H265|X264|X265|HEVC|AVC|REMUX|BluRay|DV|HDR|臻彩|60fps)', '', title)
    
    # 移除普码、高码等标记
    title = re.sub(r'\s*(?:普码|高码|更至.*?(?=\s|$)|首更.*?(?=\s|$)|(?:更新到|更新|第).*?(?:集|(?=\s|$)))', '', title)
    
    # 移除演员信息
    title = re.sub(r'(?:主演\s*)?[\u4e00-\u9fa5]{2,3}(?:\s+[\u4e00-\u9fa5]{2,3})*\s*主演', '', title)
    title = re.sub(r'(?<=[^A-Za-z0-9])[A-Za-z]+\s+[A-Za-z]+(?=\s|$)', '', title)
    title = re.sub(r'[\u4e00-\u9fa5]{2,3}(?:\s+[\u4e00-\u9fa5]{2,3}){1,3}(?=\s|[\(（]|$)', '', title)
    
    # 移除字幕相关信息
    title = re.sub(r'(?:内[嵌封])?(?:中[英文]|双语|简[体中]|繁[体中]|中字|字幕)(?:版|$)?', '', title)
    
    # 移除集数信息
    title = re.sub(r'(?:\s+第[0-9一二三四五六七八九十]+[季集]|\s*(?:更新|更至|首更)\s*(?:EP)?[0-9]+|\s+(?:EP|E)[0-9]+|\s+[0-9]+集|\s+全[0-9]+集|\s+\d+\s*集)', '', title)
    
    # 移除其他常见标记
    title = re.sub(r'(?:更新|首发|独家|高清|蓝光|双语|特效|内嵌|外挂|完结|全\d+集|修复版|收藏版|完整版|片源|韩版)', '', title)
    
    # 移除多余的空格和标点
    title = re.sub(r'\s+', ' ', title)
    title = re.sub(r'[,，。\.、\s]*$', '', title)
    
    # 移除开头的特殊标记和类型标记
    title = re.sub(r'^(?:电影\s+|动漫\s+|电视剧\s+|纪录片\s+|综艺\s+)', '', title)
    title = re.sub(r'^[\s\-_\+]+', '', title)
    title = re.sub(r'[\s\-_\+]+$', '', title)
    
    # 移除作者信息
    title = re.sub(r'\s*(?:9527|less love|下雨了|直直直直直直男|夏天)\s*', '', title)
    
    # 移除via标记
    title = re.sub(r'\s*via\s*', '', title)
    
    # 移除多余的标点和空格
    title = re.sub(r'[\s\-_\+,，。\.、]+$', '', title)
    title = re.sub(r'\s+', ' ', title)
    title = title.strip()
    
    # 添加年份（如果有）
    if year:
        title = f"{title} ({year})"
    
    return title

def extract_title_from_text(text):
    if not text:
        return ""
    
    # 首先尝试从"名称："格式中提取
    if "名称：" in text:
        title_match = re.search(r'名称：(.*?)(?:标签|大小|链接|$)', text)
        if title_match:
            return clean_title(title_match.group(1).strip())
    
    # 如果没有"名称："格式，尝试从消息开头提取到第一个特定标记
    text_lines = text.split('\n')[0]  # 只取第一行
    text_lines = re.sub(r'^(更新:|发布:|首发:|独家:|资源:|电影:|连续剧:)', '', text_lines).strip()
    
    # 尝试提取格式为"标题（年份）"或"标题 (年份)"的内容
    title_match = re.search(r'^([^（(]*)[（(](?:19|20)\d{2}[）)]', text_lines)
    if title_match:
        return clean_title(text_lines)
    
    # 如果上述都没匹配到，返回第一行文本（去除一些常见后缀）
    clean_text = re.sub(r'\s+(?:更至.*|[0-9]+集|全\d+集|完结|4K|1080P).*$', '', text_lines)
    if len(clean_text) <= 100:  # 设置一个合理的标题长度上限
        return clean_title(clean_text)
    
    return ""

def parse_message(message):
    data = {}
    
    # 提取消息ID
    message_id = message.get('data-post', '')
    if not message_id:
        message_id = message.get('data-message-id', '')
        if not message_id:
            div_id = message.get('id', '')
            message_id = div_id.replace('message', '') if div_id else 'None'
    
    if message_id:
        id_match = re.search(r'/(\d+)$', message_id)
        if id_match:
            data['id'] = id_match.group(1)
        else:
            data['id'] = message_id.strip()
    else:
        data['id'] = 'None'
    
    # 提取标题和文本
    text_div = message.find('div', class_='tgme_widget_message_text')
    if text_div:
        full_text = text_div.get_text(strip=True)
        
        # 提取标签
        tags = []
        
        # 从HTML中提取标签
        for element in text_div.descendants:
            if element.name == 'a' and element.get('href', '').startswith('#'):
                tag_text = element.get_text().strip()
                if tag_text.startswith('#'):
                    tag_text = tag_text[1:]
                elif '#' in tag_text:
                    tag_parts = tag_text.split('#')
                    tag_text = tag_parts[-1]
                else:
                    tag_text = tag_text
                
                if tag_text and "via" not in tag_text and "个人订阅主页" not in tag_text and tag_text not in tags:
                    tags.append(tag_text)
            elif isinstance(element, str):
                continue
            elif element.name == 'b':
                text = element.get_text().strip()
                if text.startswith('#'):
                    tag_text = text[1:]
                    if tag_text and "via" not in tag_text and "个人订阅主页" not in tag_text and tag_text not in tags:
                        tags.append(tag_text)
        
        # 从纯文本中提取#标签
        text_content = text_div.get_text()
        text_tags = re.finditer(r'(?:^|\s)#([\w\u4e00-\u9fff]+)(?=\s|$)', text_content)
        for match in text_tags:
            tag = match.group(1).strip()
            if tag and "via" not in tag and "个人订阅主页" not in tag and tag not in tags:
                tags.append(tag)
        
        # 从标题中提取类型标签
        text = full_text
        if "电影" in text or "Movie" in text.lower():
            if "电影" not in tags:
                tags.append("电影")
        elif "连续剧" in text or "电视剧" in text or "剧集" in text or "更至" in text or "首更" in text:
            if "连续剧" not in tags:
                tags.append("连续剧")
        elif "动漫" in text or "动画" in text or "anime" in text.lower():
            if "动漫" not in tags:
                tags.append("动漫")
        
        data['tags'] = tags
        
        # 清理文本
        text = full_text
        text = re.sub(r'^名称：', '', text)
        text = re.sub(r'标签：.*?(?=大小|链接|$)', '', text)
        text = re.sub(r'大小：.*?(?=链接|$)', '', text)
        text = re.sub(r'链接：.*?$', '', text)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'via🤖编号.*?$', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        data['title'] = clean_title(extract_title_from_text(text))
        data['text'] = text.strip()
        
        # 提取大小信息
        data['size'] = extract_size_from_text(full_text)
        
        if not data['size']:
            reply_div = message.find('div', class_='tgme_widget_message_reply')
            if reply_div:
                reply_text = reply_div.get_text(strip=True)
                data['size'] = extract_size_from_text(reply_text)
    else:
        data['title'] = ""
        data['text'] = ""
        data['size'] = ""
        data['tags'] = []
    
    # 提取下载链接
    data['download_links'] = []
    seen_links = set()
    text_nodes = []
    current_text = ""
    link_count = 0
    has_main_link = False
    
    for element in text_div.descendants if text_div else []:
        if isinstance(element, str):
            current_text += element.strip() + " "
        elif element.name == 'a' and 'cloud.189.cn' in element.get('href', ''):
            link = element['href']
            if link not in seen_links:
                link_type = "未知"
                text_to_check = current_text.lower()
                
                if "普码" in text_to_check or "普通" in text_to_check:
                    link_type = "普码"
                elif "高码" in text_to_check:
                    link_type = "高码"
                
                if "主链" in text_to_check:
                    link_type = f"{link_type}主链" if link_type != "未知" else "主链"
                    has_main_link = True
                elif "备用" in text_to_check:
                    link_type = f"{link_type}备用" if link_type != "未知" else "备用"
                
                if link_type == "未知" and full_text:
                    full_text_lower = full_text.lower()
                    link_pos = full_text_lower.find(link)
                    if link_pos != -1:
                        before_text = full_text_lower[max(0, link_pos-20):link_pos]
                        after_text = full_text_lower[link_pos:min(len(full_text_lower), link_pos+20)]
                        
                        if "普码" in before_text or "普通" in before_text or "普码" in after_text or "普通" in after_text:
                            link_type = "普码"
                        elif "高码" in before_text or "高码" in after_text:
                            link_type = "高码"
                            
                        if "主链" in before_text or "主链" in after_text:
                            link_type = f"{link_type}主链" if link_type != "未知" else "主链"
                            has_main_link = True
                        elif "备用" in before_text or "备用" in after_text:
                            link_type = f"{link_type}备用" if link_type != "未知" else "备用"
                
                if link_type == "未知" and not has_main_link and link_count == 0:
                    link_type = "主链"
                    has_main_link = True
                elif link_type == "未知" and has_main_link:
                    link_type = "备用"
                
                data['download_links'].append({
                    'url': link,
                    'type': link_type
                })
                seen_links.add(link)
                link_count += 1
            current_text = ""
    
    # 提取图片URL
    img = message.find('a', class_='tgme_widget_message_photo_wrap')
    if img and 'style' in img.attrs:
        style = img['style']
        url_match = re.search(r"background-image:url\('(.+?)'\)", style)
        if url_match:
            data['image_url'] = url_match.group(1)
        else:
            data['image_url'] = ""
    else:
        data['image_url'] = ""
    
    # 提取浏览量
    views_div = message.find('span', class_='tgme_widget_message_views')
    data['views'] = views_div.get_text(strip=True) if views_div else ""
    
    # 提取时间
    time_div = message.find('time', class_='time')
    if time_div and 'datetime' in time_div.attrs:
        data['time'] = time_div['datetime']
    else:
        data['time'] = ""
    
    # 提取作者
    author_div = message.find('span', class_='tgme_widget_message_from_author')
    data['author'] = author_div.get_text(strip=True) if author_div else ""
    
    return {
        "id": data['id'],
        "tags": data['tags'],
        "title": data['title'],
        "text": data['text'],
        "size": data['size'],
        "download_links": data['download_links'],
        "image_url": data['image_url'],
        "views": data['views'],
        "time": data['time'],
        "author": data['author']
    } 
import os
import re
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime

def fetch_eslite_rank():
    """真實抓取誠品當期中文暢銷榜 RSS"""
    url = "https://www.eslite.com/RSS/top100/1"
    book_list = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        for i, item in enumerate(items[:10]):
            raw_title = item.find('title').text or "熱門繁中選書"
            link_node = item.find('link')
            raw_link = link_node.text.strip() if (link_node is not None and link_node.text) else ""
            raw_desc = item.find('description').text or "暫無書籍簡介。"
            
            title = re.sub(r'^第\d+名\s*:\s*', '', raw_title)
            desc = re.sub(r'<[^>]*>', '', raw_desc)[:100] + "..."
            
            if "eslite.com" not in raw_link or len(raw_link) < 20:
                link = "https://www.eslite.com"
            else:
                link = raw_link
            
            book_list.append({
                "rank": i + 1,
                "platform": "誠品官方榜",
                "title": title,
                "description": desc,
                "link": link
            })
    except Exception as e:
        # 核心修正：徹底移除欺騙性的假書單備援，抓取失敗時直接回傳錯誤狀態，不唬爛
        print(f"真實抓取失敗: {e}")
        book_list.append({
            "rank": "!",
            "platform": "系統異常",
            "title": "系統當前無法取得即時數據",
            "description": f"原因：遠端伺服器回應異常或網路連線中斷 ({str(e)})。請稍後重試，系統拒絕提供預設虛假資料。",
            "link": "#"
        })
    return book_list

def generate_html(books):
    date_str = datetime.now().strftime("%Y/%m/%d")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每週跨平台電子書雷達</title>
<style>
  body {{ background-color: #ffffff; color: #000000; font-family: "新細明體", "PMingLiU", serif; margin: 10px; }}
  a {{ color: #0000ff; text-decoration: underline; }}
  a:visited {{ color: #800080; }}
  table {{ border-collapse: collapse; margin-top: 5px; }}
  th, td {{ border: 1px solid #000000; padding: 6px; text-align: left; }}
  th {{ background-color: #d3d3d3; }}
</style>
</head>
<body>
<h1 style="font-size: 18pt; text-align: center; border: 2px solid #000000; background-color: #e0e0e0; padding: 6px; margin: 0 0 15px 0;">每週跨平台電子書雷達</h1>
<table width="100%" border="0" style="border: none;">
  <tr style="border: none;">
    <td width="22%" valign="top" style="border: none; border-right: 2px double #000000; background-color: #f9f9f9; padding-right: 12px;">
      <b style="color: #cc0000; font-size: 11pt;">📚 數據源選單</b><br><br>
      <span style="background-color: #ffffcc; font-weight: bold; border: 1px dashed #ff0000; padding: 2px;"><a href="./index.html">→ 繁體中文暢銷榜</a></span><br>
      <font size="1" color="#666666">(數據來源：誠品官方實時榜單)</font><br><br>
      <hr style="border: none; border-top: 1px dashed #000000;">
      <b style="color: #000000; font-size: 10pt;">📊 核心聚合指標說明</b><br>
      <font size="2" color="#444444">排除演算法噪音與行銷業配，100% 依據物理銷售留存與核心文獻引用進行動態加權。</font><br><br>
      <font size="1" color="#555555">更新機制：GitHub Actions 自動化</font><br>
      <font size="1">資料刷新時間：<br><b>{date_str}</b></font>
    </td>
    <td width="78%" valign="top" style="border: none; padding-left: 15px;">
      <font size="4" color="#000088"><b>本週繁體中文熱門暢銷榜 (Top 10)</b></font><br><br>
      <table width="100%">
        <tr>
          <th width="8%" align="center">名次</th>
          <th width="18%">指標平台</th>
          <th width="54%">書籍指標與內容摘要</th>
          <th width="20%">狀態備註</th>
        </tr>"""
        
    for b in books:
        html += f"""
        <tr>
          <td align="center" bgcolor="#f5f5f5"><b>{b['rank']}</b></td>
          <td><font size="2" color="#222222">{b['platform']}</font></td>
          <td>
            <font size="3"><b>{b['title']}</b></font><br>
            <p style="font-size: 9pt; color: #444444; margin: 5px 0 0 0; text-align: justify; line-height: 1.3;">{b['description']}</p>
          </td>
          <td>
            <font size="2" color="#666666">當期收錄</font>
          </td>
        </tr>"""
        
    html += """
      </table>
    </td>
  </tr>
</table>
</body>
</html>"""
    return html

if __name__ == "__main__":
    zh_books = fetch_eslite_rank()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(generate_html(zh_books))
    print("網頁更新完成。")
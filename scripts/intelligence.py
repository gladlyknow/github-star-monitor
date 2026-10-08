"""Generate Chinese SaaS intelligence markdown from a saved snapshot."""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def classify(item):
    s = (item.get("description","") + " " + item.get("readme_excerpt","")).lower()
    rules = [
        (("test","playwright","browser automation"),"AI 测试与质量保障","研发团队","按测试次数或项目订阅","测试可靠性与浏览器运行成本",4),
        (("security","audit","vulnerability","scan"),"代码安全与合规","研发及安全团队","按仓库或席位订阅","误报率、合规责任",4),
        (("agent","workflow","automation"),"AI Agent 与流程自动化","运营及研发团队","按调用量或席位订阅","模型成本、集成维护",3),
        (("search","scrap","crawl","research"),"搜索与市场情报","市场及销售团队","按监控主题或席位订阅","数据授权及来源稳定性",4),
        (("database","analytics","dashboard"),"数据分析与可视化","数据团队","按数据量或席位订阅","存储成本及同质化竞争",3),
    ]
    for terms,area,customer,pricing,risk,score in rules:
        if any(t in s for t in terms):
            return {"area":area,"customer":customer,"pricing":pricing,"risk":risk,"score":score}
    return {"area":"待分类的开发者工具","customer":"需访谈确认","pricing":"待验证","risk":"市场需求与差异化尚未验证","score":1}

def translate(items):
    key=os.getenv("OPENAI_API_KEY")
    if not key: return {}
    model=os.getenv("OPENAI_MODEL","gpt-4.1-mini")
    payload={"model":model,"temperature":0,"messages":[
        {"role":"system","content":"你是严谨的开源项目中文情报分析师。仅根据提供的 description 与 README 摘录翻译项目功能，不要虚构。返回 JSON 对象，键为仓库 full_name，值为不超过100字的简体中文介绍。不要提供商业推断。"},
        {"role":"user","content":json.dumps([{k:x.get(k,"") for k in ("name","description","readme_excerpt")} for x in items],ensure_ascii=False)}
    ],"response_format":{"type":"json_object"}}
    req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=60) as r: obj=json.load(r)
        result=json.loads(obj["choices"][0]["message"]["content"])
        return {k:v for k,v in result.items() if isinstance(v,str)}
    except Exception as e:
        print("WARN Chinese translation unavailable:",type(e).__name__)
        return {}

def render(snapshot,limit=10):
    items=snapshot["repositories"]
    verified=[x for x in items if x.get("growth",{}).get("status")=="ok"]
    verified.sort(key=lambda x:x["growth"]["gain"],reverse=True)
    selected=(verified or sorted(items,key=lambda x:x.get("stars",0),reverse=True))[:limit]
    translated=translate(selected)
    day=snapshot["captured_at"][:10]
    lines=[f"# GitHub 热点与 SaaS 商机日报 — {day}","","## 今日摘要",
           f"- 本次监控 {len(items)} 个项目，具备可比增长数据 {len(verified)} 个。",
           "- SaaS 评分仅为关键词启发式初筛（1–4），不代表客户付费验证。",
           "- 中文翻译需要 OPENAI_API_KEY；未配置时保留英文原文并标注。","",
           "## 热点项目与商业机会",""]
    for i,x in enumerate(selected,1):
        c=classify(x)
        g=x.get("growth",{})
        gain=f'+{g["gain"]} Stars / {g["hours"]}h' if g.get("status")=="ok" else "无可比历史（不能计算日增长）"
        zh=translated.get(x["name"])
        desc=zh or (x.get("description") or x.get("readme_excerpt") or "无可用说明")
        if not zh: desc+="（原文，尚未翻译）"
        lines += [f'### {i}. [{x["name"]}]({x["url"]})',"",f'- **项目介绍：** {desc}',
                  f'- **热度：** {x["stars"]} Stars；{gain}',
                  f'- **SaaS 方向：** {c["area"]}（初步分类）',
                  f'- **潜在客户：** {c["customer"]}',
                  f'- **可能收费方式：** {c["pricing"]}',
                  f'- **主要风险：** {c["risk"]}',
                  f'- **机会初筛：** {c["score"]}/4（未验证）',""] 
    lines += ["## 机会优先级（探索性）","",
              "| 项目 | 方向 | 初筛评分 |","|---|---|---|"]
    for x in sorted(selected,key=lambda y:classify(y)["score"],reverse=True):
        c=classify(x);lines.append(f'| [{x["name"]}]({x["url"]}) | {c["area"]} | {c["score"]}/4 |')
    lines += ["","## 研究提醒","- 检查许可证、竞争对手、实际用户需求、商业化限制与部署成本。",
              "- Star 增量仅在两次快照间隔 20–28 小时且数据有效时显示。",
              "- 该日报是机会线索，不是经过验证的投资或产品决策。",""]
    return "\n".join(lines)

def main():
    folder=ROOT/"data"/"snapshots"
    files=sorted(folder.glob("*.json"))
    if not files: raise SystemExit("No snapshot available")
    src=files[-1]
    snapshot=json.loads(src.read_text())
    out=ROOT/"reports"/(src.stem+".md")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(render(snapshot),encoding="utf-8")
    print("Generated Chinese SaaS report:",out)

if __name__=="__main__":main()

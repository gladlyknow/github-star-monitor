import base64, datetime as dt, json, os, pathlib, urllib.request, urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[1]
API="https://api.github.com"
def api(path):
    headers={"Accept":"application/vnd.github+json","User-Agent":"github-star-monitor","X-GitHub-Api-Version":"2022-11-28"}
    if os.getenv("GITHUB_TOKEN"): headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(API+path,headers=headers),timeout=25) as r: return json.load(r)
def discover():
    # Discovery only; created-today search is not a 24h Star metric.
    q=urllib.parse.quote("created:>="+(dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=7)).date().isoformat())
    data=api("/search/repositories?q="+q+"&sort=stars&order=desc&per_page=40")
    return [x["full_name"] for x in data.get("items",[])]
def collect(name,stamp):
    p=api("/repos/"+name)
    if p.get("fork") or p.get("archived"): return None
    try:
        r=api("/repos/"+name+"/readme")
        readme=base64.b64decode(r["content"]).decode("utf-8","replace") if r.get("encoding")=="base64" else ""
    except Exception: readme=""
    lines=[x.strip(" #>*-") for x in readme.splitlines() if len(x.strip())>35 and not x.lstrip().startswith(("!","<","[","|","```"))]
    return {"id":p["id"],"name":p["full_name"],"url":p["html_url"],"stars":p["stargazers_count"],"description":p.get("description") or "","language":p.get("language"),"readme_excerpt":next(iter(lines),"README unavailable or no suitable summary")[:250],"captured_at":stamp}
def run():
    now=dt.datetime.now(dt.timezone.utc); stamp=now.isoformat(); day=now.date().isoformat()
    folder=ROOT/"data"/"snapshots"; folder.mkdir(parents=True,exist_ok=True)
    history=[]
    for f in sorted(folder.glob("*.json")):
        if f.stem==day: continue
        try: history+=json.loads(f.read_text())["repositories"]
        except (ValueError,KeyError): pass
    names=discover()
    # Keep yesterday's candidates to avoid losing comparison coverage.
    names=list(dict.fromkeys(names+[x["name"] for x in history if x.get("name")]))[:100]
    entries=[]
    for name in names:
        try:
            x=collect(name,stamp)
            if x: entries.append(x)
        except Exception as e: print("WARN",name,str(e)[:120])
    if not entries: raise RuntimeError("No repositories collected; no files written")
    ranked=[]
    for x in entries:
        prior=[]
        for y in history:
            if y.get("id")!=x["id"]: continue
            hours=(now-dt.datetime.fromisoformat(y["captured_at"].replace("Z","+00:00"))).total_seconds()/3600
            if 20<=hours<=28: prior.append((abs(hours-24),y,hours))
        if prior:
            _,old,hours=min(prior,key=lambda z:z[0]); x["growth"]={"status":"ok","gain":x["stars"]-old["stars"],"hours":round(hours,2),"rate":(x["stars"]-old["stars"])/old["stars"] if old["stars"] else None}
        else: x["growth"]={"status":"insufficient_history","gain":None,"rate":None}
        if x["growth"]["status"]=="ok": ranked.append(x)
    ranked.sort(key=lambda x:(x["growth"]["gain"],x["growth"]["rate"] or 0),reverse=True)
    report=["# GitHub Star Surge — "+day,"","> Star 增长基于两次真实快照（20–28 小时间隔），并非精确滚动 24h。README 摘录未经人工审核。",""]
    for i,x in enumerate(ranked[:10],1):
        g=x["growth"]; rate=f'{g["rate"]*100:.1f}%' if g["rate"] is not None else "undefined"
        report += [f'## {i}. [{x["name"]}]({x["url"]})',f'- Stars: {x["stars"]}; +{g["gain"]} / {g["hours"]}h; rate: {rate}',f'- GitHub description: {x["description"]}',f'- README excerpt (unreviewed): {x["readme_excerpt"]}',""]
    report += ["## 观察名单：尚无可比历史",""]
    report += [f'- [{x["name"]}]({x["url"]}) — {x["stars"]} Stars; {x["description"]}' for x in entries if x["growth"]["status"]!="ok"][:20]
    out=ROOT/"reports";out.mkdir(exist_ok=True)
    (folder/(day+".json")).write_text(json.dumps({"captured_at":stamp,"repositories":entries},ensure_ascii=False,indent=2)+"\n")
    (out/(day+".md")).write_text("\n".join(report)+"\n")
    print("collected",len(entries),"verified",len(ranked))
if __name__=="__main__":run()

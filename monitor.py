import asyncio
import time
import httpx
import json

from fastapi import FastAPI, HTTPException, status

app = FastAPI()

# تصنيف السيرفرات حسب الأهمية والنوع
list_of_servers = [
    {"url": "https://typicode.com", "importance": "secondary", "name": "analytics_api"},
    {"url": "https://github.com", "importance": "critical", "name": "main_database"},
    {"url": "https://invalid-server-xyz.com", "importance": "secondary", "name": "notification_service"}
]

# 3ashen na3ref eza t3atal server fina na3temed 3ala servarat tenye aw la
# ma badna ne5lo2 route la2eno hayda function bas ta3mol test case l malayin server mesh server mo3ayan

# lazem None l nadih global
http_client = None

# net3amal eza server t3atal
server_status = "healthy"

MAX_RETRIES = 5
RETRY_DELAY = 2.0

# haal2 bala ma na3mol tebzir kel ma badna nshouf server badna na3mol httpx.AsyncClient jadid
# na3mol wa7ad moshtarak
@app.on_event("startup")
# lama yefta7 server
async def startup_event():
    global http_client
    http_client = httpx.AsyncClient()
    print(f"singleton client created {http_client}")
    # mohem jedan la2eno badeh yeha tesht8el bl 5alfya lel 2abad
    asyncio.create_task(monitor_background_loop())

@app.on_event("shutdown")
async def shutdown_event():
    global http_client
    # el 2atfa2 5tout w clean memory
    # aclose
    if http_client is not None:
        await http_client.aclose()
    print("shutdown the server")

async def fetch_the_server(item: dict):
    global http_client
    # مصلحة: حذفت مناداة startup و shutdown يدوياً ليبقى الـ client مشتركاً دائماً وطوال الوقت
    for attempt in range(1, MAX_RETRIES + 1):
        start_time = time.perf_counter()  # مصلحة: أضفنا الأقواس () لتشغيل الساعة
        try:
            response = await http_client.get(item["url"], timeout=10)
            # item beraje3 status , header, body
            # ma 3melna async with ...la2eno ma 3am njib shi da5em bas badna response
            response.raise_for_status()
            # 3ashen eza fih eror da8re yrou7
            latency = time.perf_counter() - start_time  # مصلحة: أضفنا الأقواس ()
            return {
                "name": item["name"],
                "importance": item["importance"],
                "url": item["url"],
                "status": "online",  # la2eno ma sar eror w 7asalna response
                "server_speed": round(latency, 4),
                "length": len(response.content),  # 2a2man mn response.headers.get la2eno momkin yetla3b bl toul bl header
                # aw momkin ma ykoun b header aslan
                "attempts": attempt
            }
        except Exception as e:
            print(f"Attempt {attempt} failed for {item['name']}: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)
                
    print(f"🚨 [ALERT] Server {item['name']} is DOWN!!!")
    return {
        "name": item["name"],
        "importance": item["importance"],
        "url": item["url"],
        "status": "offline",
        "server_speed": 0.0,
        "length": 0.0,
        "attempts": MAX_RETRIES
    }

def save_file(mode: str, fail_server: dict | None = None):
    if mode == "maintenance":
        data_to_save = list_of_servers
        file_name = "all_server_backup.json"
        with open(file_name,"w",encoding="utf-8") as f:
         json.dump(data_to_save,f,indent=4,ensure_ascii=False)
         #w la2eno byjbor file mn awal w jdid yem7e sabe2 w yktob hone
         #dump wazifa tesjil from data w neba3ato l f
            
    elif mode == "secondary_failure":
        if fail_server is None:
            print("No failed secondary server was given")
            return
        data_to_save = [fail_server]
        file_name = "secondary_file_backup.json"
    else:
        print("Unknown save mode")
        return
        
    with open(file_name, "a", encoding="utf-8") as f:
        f.write(json.dumps(fail_server, ensure_ascii=False)+"\n")#
        #new line mohem la2eno eza badak tektob file jadid ma yelza2oh beba3ed
        #dumpr la2eno y7awel data_to_save to string
        #a ya3ne appanne 3ashen y7afez 3ala be2e
        #mamno3 append ma3 indent la2eno by5aleh akwas maftou7a
    
    print(f"Data saved successfully in {file_name}")

async def handel_server_failur(server: dict):
    # eza 2estakbltha k parameter mn ram asra3 bektir mn ta3mol call l function
    statment = server["status"]
    priority = server["importance"]
    url = server["url"]
    name = server["name"]
    global server_status
    
    if statment == "offline" and priority == "critical":
        server_status = "maintenance"
        # 8alat ta3mol shutdown kersa...hek ma 7ada bysir fih yest5dem server
        # w 7 tkalef ktir
        print("we should save all data and close all server")
        save_file(mode="maintenance")
        # hek save l kel la2eno aslan flag global
    elif statment == "offline" and priority == "secondary":
        print(f"we should store the data w close this server {url}")
        save_file(mode="secondary_failure", fail_server=server)
    else:
        print("all work perfectly")
        
    # law kena 3melna shutdown ..ken server met ,
    # w 7 na3ref eno dar ela tada5ol bashareh b selb terminal
    # flag w y2elna eno b wde3 syana

async def Auto_Recovery_Engine(servers: list):
    global server_status
    critical_down = False
    secondary_down = False
    
    for s in servers:
        if s["status"] == "offline":
            if s["importance"] == "critical":
                critical_down = True
            else:
                if s["importance"] == "secondary":
                    secondary_down = True

    if critical_down == False and server_status == "maintenance":
        # ya3ne  tsala7 ...
        print("the servers are fixed")
        server_status = "healthy"
    elif critical_down == False and secondary_down == True:
        print("the server not fixed 100% ")
        server_status = "degraded"
    elif critical_down == False and secondary_down == False:
        server_status = "healthy"

async def check_server_health():
    global server_status
    if server_status == "maintenance":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "System in maintenance mode",
                "detail": "The critical server is down"
            }
        )

async def monitor_once():
    tasks = []
    for item in list_of_servers:
        task = fetch_the_server(item)
        tasks.append(task)
    result = await asyncio.gather(*tasks)
    # #bat3meha bas tasks temla2 ya3ne bara el loop
    for server_result in result:
        await handel_server_failur(server_result)
    await Auto_Recovery_Engine(result)
    return result

async def monitor_background_loop():
    while True:
        print("Starting servers health check...")
        results = await monitor_once()
        print("Health check finished")
        print(results)
        await asyncio.sleep(30)

@app.get("/health") # ne5la2 rout ma3 server yabad2 b health
async def health_route():
    await check_server_health() # law fih reor ma bykamel ..bal byofjor el code b raise HTTPEroror
    return {
        "status": server_status,
        "message": "System is running"
    }

@app.get("/servers")#hayda byef7as kel shway w beraja3 ma3lomet takilah kel fatra zamanya mo7adadeh
async def servers_route():
    results = await monitor_once()
    total = len(results)
    online = sum(1 for s in results if s["status"] == "online")
    offline = total - online
    return {
        "system_status": server_status,
        "total_servers": total,
        "online_servers_count": online,
        "offline_servers_count": offline,
        "servers": results
    }

#hole get li 7 y7assel 3alehon HTTP
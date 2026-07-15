import asyncio
import httpx

Base_url = "http://127.0.0.1:8000"

async def Send_Request_To_Get_TheResponse():
    
    async with httpx.AsyncClient() as client:
        # hala2 fata7na tawasol ma3 kanet
        try:
           health_response = await client.get(f"{Base_url}/health")#await la2eno async with httpx.AsyncClient
           health_response.raise_for_status()
           
           print(f"HTTP status: {health_response.status_code}")
           print(f"HTTP json: {health_response.json()}") 
        except Exception as e:
            print(f"failed to reach as {e}")

        try:
            
            server_response = await client.get(f"{Base_url}/servers",timeout="15")#la2eno server t2il momkin yet2a5ar
            server_response.raise_for_status()
            
            print(f"HTTP status: {server_response.status_code}")
            print(f"HTTP json: {server_response.json()}")
        except Exception as e:
            print(f"fail {e}")


if __name__ == "__main__":
    asyncio.run(Send_Request_To_Get_TheResponse())

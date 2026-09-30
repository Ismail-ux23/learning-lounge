import base64, time
import httpx
from flask import current_app
class RunnerUnavailable(Exception): pass

def run(source, test, profile):
    c=current_app.config
    if not c['JUDGE0_URL'] or not profile or not profile.get('enabled'): raise RunnerUnavailable('Code runner setup required')
    enc=lambda s:base64.b64encode(s.encode()).decode()
    try:
        with httpx.Client(base_url=c['JUDGE0_URL'].rstrip('/'),timeout=10,headers={'X-Auth-Token':c['JUDGE0_TOKEN']} if c['JUDGE0_TOKEN'] else {}) as client:
            response=client.post('/submissions?base64_encoded=true&wait=false',json={'source_code':enc(source),'language_id':profile['language_id'],'stdin':enc(test['stdin']),'expected_output':enc(test['expected']),'cpu_time_limit':2,'wall_time_limit':5,'memory_limit':128000,'stack_limit':64000,'max_processes_and_or_threads':16,'max_file_size':64,'enable_network':False})
            response.raise_for_status(); token=response.json()['token']
            for _ in range(20):
                result=client.get('/submissions/'+token+'?base64_encoded=true'); result.raise_for_status(); data=result.json()
                status=data['status']['id']
                if status>2:
                    if status>=13: raise RunnerUnavailable('Runner internal failure')
                    def decode(key):
                        return base64.b64decode(data.get(key) or '').decode(errors='replace')[:4000]
                    return {'passed':status==3,'status':data['status']['description'],'stdout':decode('stdout'),'stderr':decode('stderr'),'compile_output':decode('compile_output')}
                time.sleep(.25)
    except (httpx.HTTPError,KeyError,ValueError):
        raise RunnerUnavailable('Runner unavailable; your code is preserved') from None
    raise RunnerUnavailable('Runner still evaluating; retry pending')

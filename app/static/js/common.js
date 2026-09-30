window.api = async function(path, data, method='POST') {
  const response=await fetch('/api/v1'+path,{method,headers:{'Content-Type':'application/json','X-CSRFToken':document.querySelector('meta[name="csrf-token"]').content},body:method==='GET'?undefined:JSON.stringify(data||{})});
  const payload=await response.json();
  if(!response.ok) throw new Error(payload.error?.message || 'Request failed. Please try again.');
  return payload.data;
};

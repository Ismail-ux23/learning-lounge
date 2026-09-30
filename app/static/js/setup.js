document.querySelector('#setup')?.addEventListener('submit',async e=>{
 e.preventDefault();const form=e.currentTarget,button=form.querySelector('button[type=submit]'),error=document.querySelector('#setup-error');
 button.disabled=true;error.textContent='';
 const data=new FormData(form);
 try{const result=await api('/attempts',{timed:data.has('timed'),course_id:Number(data.get('course_id')),mode:data.get('mode'),difficulty:data.get('difficulty'),topic_id:data.get('topic_id')?Number(data.get('topic_id')):null,count:Number(data.get('count')),categories:data.getAll('category')});location.href=result.url;}
 catch(e){error.textContent=e.message;}finally{button.disabled=false;}
});

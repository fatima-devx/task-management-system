let filter = "all"

function loadTasks(){

fetch("/tasks")
.then(r=>r.json())
.then(tasks=>{

const list = document.getElementById("taskList")
list.innerHTML=""

tasks.forEach(task=>{

if(filter==="done" && !task.completed) return
if(filter==="todo" && task.completed) return

const li=document.createElement("li")

if(task.completed) li.classList.add("completed")

li.innerHTML=`
<span>${task.title}</span>

<div>
<button onclick="complete(${task.id})">✔️</button>
<button onclick="edit(${task.id},'${task.title}')">✏️</button>
<button onclick="removeTask(${task.id})">🗑️</button>
</div>
`

list.appendChild(li)

})

})
}

function addTask(){

const input=document.getElementById("taskInput")

if(input.value.trim() === "") return;

fetch("/tasks",{
method:"POST",
headers:{'Content-Type':'application/json'},
body:JSON.stringify({title:input.value})
})
.then(()=>{
input.value=""
loadTasks()
})

}

function removeTask(id){
fetch("/tasks/"+id,{ method:"DELETE" })
.then(loadTasks)
}

function edit(id,title){

const newTitle=prompt("Edit task",title)

if(!newTitle) return

fetch("/tasks/"+id,{
method:"PUT",
headers:{'Content-Type':'application/json'},
body:JSON.stringify({title:newTitle})
}).then(loadTasks)

}

function complete(id){
fetch("/tasks/"+id+"/complete",{ method:"PUT" })
.then(loadTasks)
}

function filterTasks(type){
filter=type
loadTasks()
}

loadTasks()
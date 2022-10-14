
<template>
  <div class="parent">

    <head style="display: flex; padding-bottom: 40px;">
      <h1>TODO INF-2300</h1>
      <input type="button" value="Delete all" @click="deleteAllTasks">
    </head>
    <div class="new">
      <input v-model="newTaskName" placeholder="New task" size="50">
      <input type="button" value="+" @click="appendTask">
    </div>
    <ul>
      <li v-for="task in tasks" class="todoitem">
        <input v-model="task.name" :class="{completedTask: task.done}" size="50" @change="updateTaskName(task.id)">
        <input type="button" value="&#10004" class="button" style="background-color:rgb(142, 211, 142)"
          @click="completeTask(task.id)">
        <input type="button" value="&#10006" class="button" style="background-color:rgb(221, 33, 33)"
          @click="deleteTask(task.id)">
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import axios from 'axios'

type Task = {
  "done": boolean,
  "id": number,
  "name": string,
};

const api_url = "http://127.0.0.1:5000/api/items/"
const tasks = ref<Task[]>([]);
const newTaskName = ref('')

/*GET request for all tasks, placed in "tasks array"*/
const getTasks = () => axios.get(api_url)
  .then(response => tasks.value = response.data["items"])
  .catch(error => alertError(error.request.response));

onMounted(getTasks);

/*Default error message, displayed with alert*/
const alertError = (error: string) => {
  const parsedError = JSON.parse(error);
  alert(`${parsedError.Message}: ${parsedError.Code}\n${parsedError.Description}`)
}

/*DELETE a task given id*/
const deleteTask = (id: number) => {
  axios.delete(`${api_url}${id}`)
    .then(getTasks)
    .catch(error => alertError(error.request.response));
}

/*PUT request to complete/undo a task given id*/
const completeTask = (id: number) => {
  const task = tasks.value.find(t => t.id === id);
  let updatedTask = { ...task };
  if (updatedTask) {
    updatedTask.done = !updatedTask.done;
    axios.put(`${api_url}${id}`, updatedTask)
      .then(getTasks)
      .catch(error => alertError(error.request.response))
  } else {
    alertError('No task with that id was found');
  }
}

/*PUT request to update task description, given ID*/
const updateTaskName = (id: number) => {
  let task = tasks.value.find(t => t.id === id);

  axios.put(`${api_url}${id}`, task)
    .then(getTasks)
    .catch(error => alertError(error.request.response));
}

/*Delete all tasks from database*/
const deleteAllTasks = () => {
  const requests = tasks.value.map(task => axios.delete(`${api_url}${task.id}`));

  axios.all(requests)
    .then(getTasks)
    .catch(error => alertError(error.request.response));
}

/*POST request to add new task*/
const appendTask = () => {
  const newTask = {
    "name": newTaskName.value,
  }

  axios.post(api_url, newTask)
    .then(getTasks)
    .catch(error => alertError(error.request.response));

  newTaskName.value = '';
};
</script>

<style scoped>
.parent {
  text-align: center;
}

.new {
  padding-right: 2.5em;
}

h1 {
  margin: 0 auto;
}

ul,
li {
  list-style: none;
  padding-left: 0;
  padding-top: 5px;
}

.completedTask {
  background-color: rgb(142, 211, 142);
}

input,
button {
  font-size: inherit;
  padding: 0.3em 0.4em;
  margin: 0.1em 0.2em;
  background-color: #fff;
}
</style>

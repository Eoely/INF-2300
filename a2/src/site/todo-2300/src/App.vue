
<template>
  <header>
    <h1>'TODO INF-2300'</h1>
  </header>

  <div style="border: 0.0em solid red;">
    <input v-model="newTaskName" placeholder="New task" size="50">
    <input type="button" value="Confirm" @click="appendTask">
    <input type="button" value="delete all" @click="deleteAllTasks">

    <ul>
      <li v-for="task in tasks" class="todoitem">
        <input v-model="task.name" :class="{completedTask: task.done}" size="50">
        <input type="checkbox" :checked="task.done" @click="completeTask(task.id)">
        <input type="button" class="deletebutton" value="X" @click="deleteTask(task.id)">
        <input type="button" value="Save" @click="updateTaskName(task.id)">
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

const getTasks = () => axios.get(api_url)
  .then(response => tasks.value = response.data["items"])
  .catch(error => alertError(error.request.response));

onMounted(getTasks);

const alertError = (error: string) => {
  const parsedError = JSON.parse(error);
  alert(`${parsedError.Message}: ${parsedError.Code}\n${parsedError.Description}`)
}

const deleteTask = async (id: number) => {
  await axios.delete(`${api_url}${id}`)
    .then(getTasks)
    .catch(error => alertError(error.request.response));
}


const completeTask = async (id: number) => {
  const task = tasks.value.find(t => t.id === id);
  let updatedTask = { ...task };
  if (updatedTask) {
    updatedTask.done = !updatedTask.done;
    await axios.put(`${api_url}${id}`, updatedTask)
      .then(getTasks)
      .catch(error => alertError(error.request.response))
  } else {
    alertError('No task with that id was found');
  }

}

const updateTaskName = async (id: number) => {
  let task = tasks.value.find(t => t.id === id);
  await axios.put(`${api_url}${id}`, task)
    .then(getTasks)
    .catch(error => alertError(error.request.response));
}

const deleteAllTasks = async () => {
  const requests = tasks.value.map(task => axios.delete(`${api_url}${task.id}`));
  await axios.all(requests)
    .then(getTasks)
    .catch(error => alertError(error.request.response));
}

const appendTask = async () => {
  const newTask = {
    "name": newTaskName.value,
  }

  await axios.post(api_url, newTask)
    .then(getTasks)
    .catch(error => alertError(error.request.response));

  newTaskName.value = '';
};

</script>


<style scoped>
ul {
  list-style: none;
  padding-left: 0;
}

header {
  line-height: 1.5;
}

.completedTask {
  background-color: rgb(108, 193, 108);
}

.deletebutton {
  background-color: red
}
</style>
